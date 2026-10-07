#define _GNU_SOURCE
#include <gtk/gtk.h>
#include <dlfcn.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
static FILE *trace;
static gint64 start,pending;
static guint paints;
static int target,slow;
static const char *description(GtkWidget *w){if(!w)return "none";const char *s=atk_object_get_description(gtk_widget_get_accessible(w));return s?s:G_OBJECT_TYPE_NAME(w);}
static void emit(const char *kind,GtkWidget *w){
 if(!trace)return;
 gboolean atk=FALSE;if(w){AtkStateSet *s=atk_object_ref_state_set(gtk_widget_get_accessible(w));atk=atk_state_set_contains_state(s,ATK_STATE_FOCUSED);g_object_unref(s);}
 fprintf(trace,"%s\t%lld\t%s\t%d\t%d\t%lld\t%u\n",kind,(long long)(g_get_monotonic_time()-start),description(w),w?gtk_widget_has_focus(w):0,atk,(long long)(pending?g_get_monotonic_time()-pending:0),paints);fflush(trace);
}
static gboolean idle(gpointer p){(void)p;emit("idle",NULL);pending=0;return G_SOURCE_REMOVE;}
static gboolean sample(gpointer p){
 (void)p;GList *rows=gtk_window_list_toplevels();
 for(GList *r=rows;r;r=r->next){GtkWindow *w=GTK_WINDOW(r->data);if(g_strcmp0(gtk_window_get_title(w),"SysPane Editor")==0)emit("sample",gtk_window_get_focus(w));}
 g_list_free(rows);if(!pending){pending=g_get_monotonic_time();g_idle_add_full(G_PRIORITY_DEFAULT_IDLE,idle,NULL,NULL);}return G_SOURCE_CONTINUE;
}
static gboolean event_hook(GSignalInvocationHint *hint,guint n,const GValue *values,gpointer p){
 (void)hint;(void)n;(void)p;GtkWidget *w=GTK_WIDGET(g_value_get_object(values));
 if(g_strcmp0(description(w),"editor.apply")==0||g_strcmp0(description(w),"editor.undo")==0){emit("focus-in",w);if(getenv("SYSPANE_PROBE_SLOW"))slow=1;}return TRUE;
}
static gboolean draw_hook(GSignalInvocationHint *hint,guint n,const GValue *values,gpointer p){
 (void)hint;(void)n;(void)p;GtkWidget *w=GTK_WIDGET(g_value_get_object(values));
 if(g_strcmp0(description(w),"editor.canvas")==0){++paints;if(slow)g_usleep(60000);}return TRUE;
}
gboolean gtk_init_check(int *argc,char ***argv){
 typedef gboolean(*Fn)(int*,char***);Fn real=(Fn)dlsym(RTLD_NEXT,"gtk_init_check");gboolean ok=real(argc,argv);
 char exe[4096];ssize_t count=readlink("/proc/self/exe",exe,sizeof(exe)-1);if(count<=0)return ok;exe[count]=0;
 target=ok&&g_str_has_suffix(exe,"/syspane_editor_window");const char *prefix=getenv("SYSPANE_PROBE_TRACE");
 if(target&&prefix){char path[8192];snprintf(path,sizeof(path),"%s-%ld.tsv",prefix,(long)getpid());trace=fopen(path,"wx");if(!trace)abort();start=g_get_monotonic_time();
  g_signal_add_emission_hook(g_signal_lookup("focus-in-event",GTK_TYPE_WIDGET),0,event_hook,NULL,NULL);
  g_signal_add_emission_hook(g_signal_lookup("draw",GTK_TYPE_WIDGET),0,draw_hook,NULL,NULL);
  g_timeout_add_full(G_PRIORITY_DEFAULT,50,sample,NULL,NULL);emit("start",NULL);
 }return ok;
}
guint g_timeout_add(guint interval,GSourceFunc function,gpointer data){
 typedef guint(*Fn)(guint,GSourceFunc,gpointer);Fn real=(Fn)dlsym(RTLD_NEXT,"g_timeout_add");Dl_info caller;
 int editor=target&&interval==40&&dladdr(__builtin_return_address(0),&caller)&&g_str_has_suffix(caller.dli_fname,"/syspane_editor_window");
 if(editor){emit(getenv("SYSPANE_PROBE_LOW")?"refresh-low":"refresh-default",NULL);if(getenv("SYSPANE_PROBE_LOW"))return g_timeout_add_full(G_PRIORITY_LOW,interval,function,data,NULL);}
 return real(interval,function,data);
}
