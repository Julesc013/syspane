#include <glib-object.h>
#include <stdio.h>
#include <string.h>

/* Literal behavior oracle for interposition, independent of SysPane timings. */
static int token,query_calls,finalizers,timer_finalizers,timer_calls,low_calls;
static GObject* object;
static GMainLoop* loop;
static guint nested_signal,query_signal,self_timer;
static gulong self_handler;
static char order[64];static unsigned used;
static void mark(char c){g_assert_cmpuint(used,<,sizeof(order)-1);order[used++]=c;}
static void nested(GObject* obj,gpointer data){g_assert(obj==object&&data==&token);mark('N');}
static gint query(GObject* obj,gint value,const gchar* text,gpointer data){
    g_assert(obj==object&&data==&token);g_assert_cmpint(value,==,11);g_assert_cmpstr(text,==,"literal");
    ++query_calls;mark('Q');g_signal_emit(obj,nested_signal,0);return 21;
}
static gint after(GObject* obj,gint value,const gchar* text,gpointer data){
    g_assert(obj==object&&data==&token&&value==11&&!strcmp(text,"literal"));mark('A');return 22;
}
static gint swapped(gpointer data,gint value,const gchar* text,GObject* obj){
    g_assert(obj==object&&data==&token&&value==11&&!strcmp(text,"literal"));mark('S');return 23;
}
static void finalize(gpointer data,GClosure* closure){g_assert(data==&token&&closure->data==&token);++finalizers;}
static void once(GObject* obj,gpointer data){g_assert(obj==object&&data==&token);mark('D');g_signal_handler_disconnect(obj,self_handler);}
static void timer_destroy(gpointer data){g_assert(data==&token);++timer_finalizers;}
static gboolean timer(gpointer data){
    g_assert(data==&token);mark('T');g_signal_emit(object,nested_signal,0);return ++timer_calls<2;
}
static gboolean low_timer(gpointer data){g_assert(data==&token);++low_calls;mark('L');return G_SOURCE_REMOVE;}
static gboolean never(gpointer data){(void)data;g_assert_not_reached();return G_SOURCE_REMOVE;}
static gboolean remove_self(gpointer data){g_assert(data==&token);mark('R');g_assert(g_source_remove(self_timer));return G_SOURCE_CONTINUE;}
static gboolean stop(gpointer data){g_assert(data==&token);g_main_loop_quit(loop);return G_SOURCE_REMOVE;}
int main(void){
    GType params[]={G_TYPE_INT,G_TYPE_STRING};
    query_signal=g_signal_newv("trace-query",G_TYPE_OBJECT,G_SIGNAL_RUN_LAST,NULL,NULL,NULL,g_cclosure_marshal_generic,G_TYPE_INT,2,params);
    nested_signal=g_signal_newv("trace-nested",G_TYPE_OBJECT,G_SIGNAL_RUN_LAST,NULL,NULL,NULL,NULL,G_TYPE_NONE,0,NULL);
    guint clicked=g_signal_newv("clicked",G_TYPE_OBJECT,G_SIGNAL_RUN_LAST,NULL,NULL,NULL,NULL,G_TYPE_NONE,0,NULL);
    object=g_object_new(G_TYPE_OBJECT,NULL);g_object_set_data(object,"editor-action","apply");
    g_signal_connect(object,"trace-nested",G_CALLBACK(nested),&token);
    gulong first=g_signal_connect_data(object,"trace-query",G_CALLBACK(query),&token,finalize,0);
    g_signal_connect_data(object,"trace-query",G_CALLBACK(after),&token,finalize,G_CONNECT_AFTER);
    g_signal_connect_data(object,"trace-query",G_CALLBACK(swapped),&token,finalize,G_CONNECT_SWAPPED);
    gint result=0;g_signal_emit(object,query_signal,0,11,"literal",&result);g_assert_cmpint(result,==,22);
    g_assert_cmpstr(order,==,"QNSA");used=0;memset(order,0,sizeof(order));
    g_signal_handler_block(object,first);g_signal_emit(object,query_signal,0,11,"literal",&result);
    g_assert_cmpstr(order,==,"SA");g_signal_handler_unblock(object,first);
    g_assert_cmpuint(g_signal_handlers_disconnect_by_func(object,after,&token),==,1);
    used=0;memset(order,0,sizeof(order));g_signal_emit(object,query_signal,0,11,"literal",&result);
    g_assert_cmpstr(order,==,"QNS");g_assert_cmpint(result,==,23);g_assert_cmpint(query_calls,==,2);
    g_assert_cmpuint(g_signal_handlers_disconnect_matched(object,G_SIGNAL_MATCH_ID|G_SIGNAL_MATCH_DATA,query_signal,0,NULL,NULL,&token),==,2);
    g_assert_cmpint(finalizers,==,3);
    self_handler=g_signal_connect_data(object,"clicked",G_CALLBACK(once),&token,finalize,0);
    g_signal_emit(object,clicked,0);g_signal_emit(object,clicked,0);g_assert_cmpint(finalizers,==,4);
    puts("signals: arguments returns swapped after nested block disconnect destroy pass");
    used=0;memset(order,0,sizeof(order));loop=g_main_loop_new(NULL,FALSE);
    guint cancelled=g_timeout_add_full(G_PRIORITY_DEFAULT,1000,never,&token,timer_destroy);
    g_assert(g_source_remove(cancelled));g_assert_cmpint(timer_finalizers,==,1);
    g_timeout_add_full(G_PRIORITY_HIGH,0,timer,&token,timer_destroy);
    g_timeout_add_full(G_PRIORITY_DEFAULT,0,low_timer,&token,timer_destroy);
    self_timer=g_timeout_add_full(G_PRIORITY_LOW,0,remove_self,&token,timer_destroy);
    g_timeout_add(5,stop,&token);g_main_loop_run(loop);
    g_assert_cmpstr(order,==,"TNTNLR");g_assert_cmpint(timer_calls,==,2);g_assert_cmpint(low_calls,==,1);
    g_assert_cmpint(timer_finalizers,==,4);g_main_loop_unref(loop);g_object_unref(object);
    puts("timers: priority continue remove cancel self-remove data destroy pass");
    return 0;
}
