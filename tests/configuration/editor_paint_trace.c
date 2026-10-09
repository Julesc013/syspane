#define _GNU_SOURCE
#include <dlfcn.h>
#include <execinfo.h>
#include <link.h>
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

/* Experiment only. No authored data and no I/O until process exit. */
struct stack { uintptr_t frames[32]; unsigned depth; uint64_t calls,first,last; };
static struct stack stacks[128];
static uintptr_t base,low,high;
static unsigned count,overflow;
static uint64_t sequence;
static pthread_mutex_t mutex=PTHREAD_MUTEX_INITIALIZER;
static _Thread_local int observing;
static void (*original)(void*,void*);

static int executable(struct dl_phdr_info* info,size_t size,void* data){
    (void)size;(void)data;
    if(info->dlpi_name[0])return 0;
    base=info->dlpi_addr;low=UINTPTR_MAX;
    for(unsigned i=0;i<info->dlpi_phnum;++i){
        const ElfW(Phdr)* p=&info->dlpi_phdr[i];
        if(p->p_type==PT_LOAD&&(p->p_flags&PF_X)){
            const uintptr_t a=base+p->p_vaddr,b=a+p->p_memsz;
            if(a<low)low=a;
            if(b>high)high=b;
        }
    }
    return 1;
}
__attribute__((constructor)) static void initialize(void){
    dl_iterate_phdr(executable,NULL);
    *(void**)(&original)=dlsym(RTLD_NEXT,"pango_cairo_show_layout");
    /* Helpers without Pango may inherit the probe; they make no observed call. */
}
void pango_cairo_show_layout(void* cairo,void* layout){
    if(!original)_exit(125);
    const uintptr_t caller=(uintptr_t)__builtin_return_address(0);
    if(!observing&&caller>=low&&caller<high){
        observing=1;void* raw[256];uintptr_t frames[32];unsigned depth=0;
        const int n=backtrace(raw,256);unsigned truncated=n==256;
        for(int i=0;i<n;++i){
            const uintptr_t pc=(uintptr_t)raw[i];
            if(pc>=low&&pc<high){if(depth<32)frames[depth++]=pc-base;else truncated=1;}
        }
        pthread_mutex_lock(&mutex);
        if(truncated)overflow=1;
        if(depth){
            if(++sequence==0)overflow=1;
            unsigned i=0;
            while(i<count&&(stacks[i].depth!=depth||memcmp(stacks[i].frames,frames,depth*sizeof(*frames))))++i;
            if(i==count&&count<128){stacks[i].depth=depth;memcpy(stacks[i].frames,frames,depth*sizeof(*frames));stacks[i].first=sequence;++count;}
            if(i==count)overflow=1;
            else {if(++stacks[i].calls==0)overflow=1;stacks[i].last=sequence;}
        }
        pthread_mutex_unlock(&mutex);observing=0;
    }
    original(cairo,layout);
}
static void emit(const char* row,size_t length){
    while(length){const ssize_t n=write(STDERR_FILENO,row,length);if(n<=0)_exit(125);row+=n;length-=(size_t)n;}
}
__attribute__((destructor)) static void finish(void){
    char line[1024];pthread_mutex_lock(&mutex);
    int n=snprintf(line,sizeof(line),"paint-trace-begin %ld %u %llu %u\n",(long)getpid(),count,(unsigned long long)sequence,overflow);
    emit(line,(size_t)n);
    for(unsigned i=0;i<count;++i){
        const struct stack* s=&stacks[i];
        n=snprintf(line,sizeof(line),"paint-trace %u %llu %llu %llu %u",i,(unsigned long long)s->calls,(unsigned long long)s->first,(unsigned long long)s->last,s->depth);
        for(unsigned j=0;j<s->depth;++j)n+=snprintf(line+n,sizeof(line)-(size_t)n," %llx",(unsigned long long)s->frames[j]);
        line[n++]='\n';emit(line,(size_t)n);
    }
    n=snprintf(line,sizeof(line),"paint-trace-end %ld %u %llu\n",(long)getpid(),count,(unsigned long long)sequence);emit(line,(size_t)n);
    pthread_mutex_unlock(&mutex);
}
