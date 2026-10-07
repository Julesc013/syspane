#include <gtk/gtk.h>
#include <dlfcn.h>
extern "C" gboolean gtk_init_check(int* argc,char*** argv){
    using Init=gboolean(*)(int*,char***);const auto ok=reinterpret_cast<Init>(dlsym(RTLD_NEXT,"gtk_init_check"))(argc,argv);
    if(ok)g_object_set(gtk_settings_get_default(),"gtk-enable-animations",FALSE,nullptr);
    return ok;
}
