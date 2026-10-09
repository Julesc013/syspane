#define _GNU_SOURCE
#include <glib-object.h>
#include <dlfcn.h>
#include <link.h>
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/syscall.h>
#include <time.h>
#include <unistd.h>

/* Diagnostic only. Fixed storage, no application values, output only at exit. */
enum { SLOTS=2048, ROWS=32768, DEPTH=64 };
struct slot {
    unsigned used,kind,label,interval; int priority;
    uint64_t serial,ordinal; uintptr_t offset;
    GSourceFunc callback; gpointer data; GDestroyNotify destroy;
};
struct row {
    uint64_t parent,tid,serial,ordinal,start,end,cpu_start,cpu;
    uintptr_t offset; unsigned kind,label,interval; int priority;
};
static struct slot slots[SLOTS];
static struct row rows[ROWS];
static unsigned count,invalid;
static uint64_t serial;
static uintptr_t base,low,high;
static pthread_mutex_t mutex=PTHREAD_MUTEX_INITIALIZER;
static _Thread_local unsigned depth,stack[DEPTH];
static gulong (*connect_data)(gpointer,const gchar*,GCallback,gpointer,GClosureNotify,GConnectFlags);
static guint (*timeout_full)(gint,guint,GSourceFunc,gpointer,GDestroyNotify);
static guint (*timeout_add)(guint,GSourceFunc,gpointer);

static int executable(struct dl_phdr_info* info,size_t size,void* data){
    (void)size;(void)data;
    if(info->dlpi_name[0])return 0;
    base=info->dlpi_addr;low=UINTPTR_MAX;
    for(unsigned i=0;i<info->dlpi_phnum;++i){
        const ElfW(Phdr)* p=&info->dlpi_phdr[i];
        if(p->p_type==PT_LOAD&&(p->p_flags&PF_X)){
            uintptr_t a=base+p->p_vaddr,b=a+p->p_memsz;
            if(a<low)low=a;
            if(b>high)high=b;
        }
    }
    return 1;
}
__attribute__((constructor)) static void initialize(void){
    dl_iterate_phdr(executable,NULL);
    *(void**)(&connect_data)=dlsym(RTLD_NEXT,"g_signal_connect_data");
    *(void**)(&timeout_full)=dlsym(RTLD_NEXT,"g_timeout_add_full");
    *(void**)(&timeout_add)=dlsym(RTLD_NEXT,"g_timeout_add");
    if(!connect_data||!timeout_full||!timeout_add)_exit(125);
}
static int owned(uintptr_t caller,uintptr_t callback){
    return caller>=low&&caller<high&&callback>=low&&callback<high;
}
static uint64_t now(clockid_t clock){
    struct timespec t;
    if(clock_gettime(clock,&t))_exit(125);
    return (uint64_t)t.tv_sec*1000000000+(uint64_t)t.tv_nsec;
}
static struct slot* acquire(uintptr_t callback,unsigned kind,unsigned label,unsigned interval,int priority){
    struct slot* s=NULL;pthread_mutex_lock(&mutex);
    for(unsigned i=0;i<SLOTS;++i)if(!slots[i].used){s=&slots[i];break;}
    if(!s||serial==UINT64_MAX){invalid=1;s=NULL;}
    else {memset(s,0,sizeof(*s));s->used=1;s->serial=++serial;s->offset=callback-base;s->kind=kind;s->label=label;s->interval=interval;s->priority=priority;}
    pthread_mutex_unlock(&mutex);return s;
}
static void release(struct slot* s){pthread_mutex_lock(&mutex);s->used=0;pthread_mutex_unlock(&mutex);}
static void enter(struct slot* s){
    pthread_mutex_lock(&mutex);
    unsigned id=0;
    if(count==ROWS||depth>=DEPTH||s->ordinal==UINT64_MAX)invalid=1;
    else {
        id=++count;struct row* r=&rows[id-1];
        r->parent=depth?stack[depth-1]:0;r->tid=(uint64_t)syscall(SYS_gettid);
        r->serial=s->serial;r->ordinal=++s->ordinal;r->offset=s->offset;
        r->kind=s->kind;r->label=s->label;r->interval=s->interval;r->priority=s->priority;
        r->start=now(CLOCK_MONOTONIC);r->cpu_start=now(CLOCK_THREAD_CPUTIME_ID);
    }
    if(depth<DEPTH)stack[depth]=id;
    ++depth;pthread_mutex_unlock(&mutex);
}
static void leave(struct slot* s){
    uint64_t cpu=now(CLOCK_THREAD_CPUTIME_ID),end=now(CLOCK_MONOTONIC);
    pthread_mutex_lock(&mutex);
    if(!depth)invalid=1;
    else if(--depth<DEPTH){unsigned id=stack[depth];if(id){struct row* r=&rows[id-1];if(r->serial!=s->serial)invalid=1;r->end=end;r->cpu=cpu-r->cpu_start;}}
    pthread_mutex_unlock(&mutex);
}
static void pre(gpointer data,GClosure* closure){(void)closure;enter(data);}
static void post(gpointer data,GClosure* closure){(void)closure;leave(data);}
static void finalized(gpointer data,GClosure* closure){(void)closure;release(data);}
static unsigned label(gpointer instance,const char* signal){
    /* Whitelisted labels only. No instance or user strings enter the record. */
    static const char* actions[]={"apply","undo","redo","recovery-restore","recovery-keep","recovery-discard"};
    if(!strcmp(signal,"clicked")){
        const char* action=g_object_get_data(G_OBJECT(instance),"editor-action");
        for(unsigned i=0;action&&i<G_N_ELEMENTS(actions);++i)if(!strcmp(action,actions[i]))return i+1;
        return 7;
    }
    static const char* signals[]={"draw","changed","toggled","key-press-event","button-press-event","motion-notify-event","button-release-event","focus-out-event","destroy","insert-text","delete-range"};
    for(unsigned i=0;i<G_N_ELEMENTS(signals);++i)if(!strcmp(signal,signals[i]))return i+8;
    return 0;
}
gulong g_signal_connect_data(gpointer instance,const gchar* signal,GCallback callback,gpointer data,GClosureNotify destroy,GConnectFlags flags){
    if(!owned((uintptr_t)__builtin_return_address(0),(uintptr_t)callback)||!instance||!signal)
        return connect_data(instance,signal,callback,data,destroy,flags);
    if(flags&~(G_CONNECT_AFTER|G_CONNECT_SWAPPED)){
        pthread_mutex_lock(&mutex);invalid=1;pthread_mutex_unlock(&mutex);
        return connect_data(instance,signal,callback,data,destroy,flags);
    }
    struct slot* s=acquire((uintptr_t)callback,1,label(instance,signal),0,0);
    if(!s)return connect_data(instance,signal,callback,data,destroy,flags);
    GClosure* closure=(flags&G_CONNECT_SWAPPED)?g_cclosure_new_swap(callback,data,destroy):g_cclosure_new(callback,data,destroy);
    g_closure_add_marshal_guards(closure,s,pre,s,post);
    g_closure_add_finalize_notifier(closure,s,finalized);
    return g_signal_connect_closure(instance,signal,closure,(flags&G_CONNECT_AFTER)!=0);
}
static gboolean tick(gpointer data){struct slot* s=data;enter(s);gboolean keep=s->callback(s->data);leave(s);return keep;}
static void destroyed(gpointer data){struct slot* s=data;if(s->destroy)s->destroy(s->data);release(s);}
static guint timer(gint priority,guint interval,GSourceFunc callback,gpointer data,GDestroyNotify destroy){
    struct slot* s=acquire((uintptr_t)callback,2,0,interval,priority);
    if(!s)return timeout_full(priority,interval,callback,data,destroy);
    s->callback=callback;s->data=data;s->destroy=destroy;
    return timeout_full(priority,interval,tick,s,destroyed);
}
guint g_timeout_add_full(gint priority,guint interval,GSourceFunc callback,gpointer data,GDestroyNotify destroy){
    if(!owned((uintptr_t)__builtin_return_address(0),(uintptr_t)callback))return timeout_full(priority,interval,callback,data,destroy);
    return timer(priority,interval,callback,data,destroy);
}
guint g_timeout_add(guint interval,GSourceFunc callback,gpointer data){
    if(!owned((uintptr_t)__builtin_return_address(0),(uintptr_t)callback))return timeout_add(interval,callback,data);
    return timer(G_PRIORITY_DEFAULT,interval,callback,data,NULL);
}
static void emit(const char* line,int size){
    if(size<0||size>=512)_exit(125);
    while(size){ssize_t n=write(STDERR_FILENO,line,(size_t)size);if(n<=0)_exit(125);line+=n;size-=(int)n;}
}
__attribute__((destructor)) static void finish(void){
    char line[512];pthread_mutex_lock(&mutex);
    for(unsigned i=0;i<count;++i)if(!rows[i].end)invalid=1;
    int n=snprintf(line,sizeof(line),"callback-trace-begin %ld %u %u\n",(long)getpid(),count,invalid);emit(line,n);
    for(unsigned i=0;i<count;++i){const struct row* r=&rows[i];
        n=snprintf(line,sizeof(line),"callback-trace %u %llu %llu %llu %u %u %llx %u %d %llu %llu %llu %llu\n",i+1,
          (unsigned long long)r->parent,(unsigned long long)r->tid,(unsigned long long)r->serial,r->kind,r->label,
          (unsigned long long)r->offset,r->interval,r->priority,(unsigned long long)r->ordinal,
          (unsigned long long)r->start,(unsigned long long)r->end,(unsigned long long)r->cpu);emit(line,n);
    }
    n=snprintf(line,sizeof(line),"callback-trace-end %ld %u\n",(long)getpid(),count);emit(line,n);
    pthread_mutex_unlock(&mutex);
}
