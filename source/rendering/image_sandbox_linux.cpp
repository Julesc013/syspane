#include "image_decode.hpp"
#include <cerrno>
#include <cstddef>
#include <cstdlib>
#include <fcntl.h>
#include <linux/audit.h>
#include <linux/filter.h>
#include <linux/landlock.h>
#include <linux/seccomp.h>
#include <sched.h>
#include <sys/prctl.h>
#include <sys/resource.h>
#include <sys/syscall.h>
#include <unistd.h>
namespace syspane::rendering {
namespace {
void need(bool b){if(!b)throw protocol::Error("image.sandbox");}
void limit(int resource,rlim_t value){rlimit r{value,value};need(!::setrlimit(resource,&r));}
}
void restrict_image_worker(){
    need(!::clearenv());need(!::setenv("LANG","C.UTF-8",1)&&!::setenv("RAYON_NUM_THREADS","1",1));
    limit(RLIMIT_CORE,0);limit(RLIMIT_AS,268435456);limit(RLIMIT_CPU,2);limit(RLIMIT_FSIZE,0);
    need(!::prctl(PR_SET_NO_NEW_PRIVS,1,0,0,0));need(!::prctl(PR_SET_DUMPABLE,0,0,0,0));
    need(::syscall(SYS_landlock_create_ruleset,nullptr,0,LANDLOCK_CREATE_RULESET_VERSION)>=3);
    landlock_ruleset_attr rules{};rules.handled_access_fs=(1ULL<<15)-1;
    const int rulefd=static_cast<int>(::syscall(SYS_landlock_create_ruleset,&rules,sizeof rules,0));need(rulefd>=0);
    struct Close {int fd;~Close(){if(fd>=0)::close(fd);}} owner{rulefd};
    const auto allow=[&](const char* path,bool directory){const int fd=::open(path,O_PATH|O_CLOEXEC);need(fd>=0);Close file{fd};landlock_path_beneath_attr entry{};entry.parent_fd=fd;entry.allowed_access=LANDLOCK_ACCESS_FS_READ_FILE|(directory?LANDLOCK_ACCESS_FS_READ_DIR:0);
        need(!::syscall(SYS_landlock_add_rule,rulefd,LANDLOCK_RULE_PATH_BENEATH,&entry,0));};
    for(const char* path:{"/usr/lib/x86_64-linux-gnu","/usr/share/fonts","/etc/fonts","/var/cache/fontconfig","/usr/share/fontconfig"})allow(path,true);
    allow("/etc/ld.so.cache",false);
    need(!::syscall(SYS_landlock_restrict_self,rulefd,0));
    // Exact x86-64 development profile. Deny networking, process creation and
    // cross-process memory/inspection. Native library worker threads may remain.
    std::vector<sock_filter> code;
    const auto stmt=[&](unsigned short op,unsigned value){code.push_back(sock_filter{op,0,0,value});};
    const auto jump=[&](unsigned short op,unsigned value,unsigned char yes,unsigned char no){code.push_back(sock_filter{op,yes,no,value});};
    stmt(BPF_LD|BPF_W|BPF_ABS,offsetof(seccomp_data,arch));jump(BPF_JMP|BPF_JEQ|BPF_K,AUDIT_ARCH_X86_64,1,0);stmt(BPF_RET|BPF_K,SECCOMP_RET_KILL_PROCESS);
    stmt(BPF_LD|BPF_W|BPF_ABS,offsetof(seccomp_data,nr));jump(BPF_JMP|BPF_JGE|BPF_K,0x40000000,0,1);stmt(BPF_RET|BPF_K,SECCOMP_RET_KILL_PROCESS);
    for(unsigned call:{SYS_socket,SYS_socketpair,SYS_connect,SYS_bind,SYS_listen,SYS_accept,SYS_accept4,SYS_ptrace,SYS_process_vm_readv,SYS_process_vm_writev,SYS_kill,SYS_tkill,SYS_tgkill,SYS_pidfd_send_signal,SYS_pidfd_getfd,SYS_execve,SYS_execveat,SYS_fork,SYS_vfork,SYS_unshare,SYS_setns,SYS_mount,SYS_bpf,SYS_io_uring_setup}){
        jump(BPF_JMP|BPF_JEQ|BPF_K,call,0,1);stmt(BPF_RET|BPF_K,SECCOMP_RET_ERRNO|EPERM);}
    jump(BPF_JMP|BPF_JEQ|BPF_K,SYS_clone3,0,1);stmt(BPF_RET|BPF_K,SECCOMP_RET_ERRNO|ENOSYS);
    jump(BPF_JMP|BPF_JEQ|BPF_K,SYS_clone,0,4);stmt(BPF_LD|BPF_W|BPF_ABS,offsetof(seccomp_data,args));stmt(BPF_ALU|BPF_AND|BPF_K,CLONE_THREAD);
    jump(BPF_JMP|BPF_JEQ|BPF_K,CLONE_THREAD,1,0);stmt(BPF_RET|BPF_K,SECCOMP_RET_ERRNO|EPERM);
    stmt(BPF_RET|BPF_K,SECCOMP_RET_ALLOW);sock_fprog program{static_cast<unsigned short>(code.size()),code.data()};need(!::prctl(PR_SET_SECCOMP,SECCOMP_MODE_FILTER,&program));
    ::alarm(3);
}
}
