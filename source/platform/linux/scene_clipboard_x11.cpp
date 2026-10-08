#include "scene_clipboard_x11.hpp"
#include <gdk/gdkx.h>
#include <X11/Xatom.h>
#include <algorithm>
#include <cstdint>
#include <map>
#include <stdexcept>
#include <utility>

namespace syspane::platform {
namespace {
constexpr std::size_t ceiling=262144,chunk=16384,slots=8;
constexpr const char* mime="application/vnd.syspane.scene-fragment+json";
using Key=std::pair<Window,Atom>;
std::int64_t now(){return g_get_monotonic_time()/1000;}
bool expired(std::int64_t start,std::int64_t progress){const auto n=now();return n-start>=5000||n-progress>=1000;}
struct Trap {
    GdkDisplay* display;bool done=false;
    explicit Trap(GdkDisplay* d):display(d){gdk_x11_display_error_trap_push(d);}
    ~Trap(){if(!done)gdk_x11_display_error_trap_pop_ignored(display);}
    bool ok(){done=true;return gdk_x11_display_error_trap_pop(display)==0;}
};
struct Property {
    Atom type=None;int format=0;unsigned long count=0,after=0;unsigned char* data=nullptr;
    ~Property(){if(data)XFree(data);}
};
}
struct SceneClipboardX11::Impl {
    Callbacks callbacks;GdkDisplay* display=nullptr;Display* x=nullptr;GdkWindow *owner=nullptr,*receiver=nullptr;
    Atom selection=None,target=None,targets=None,timestamp=None,incr=None,property=None;
    Time offered=0,requested=0;Window source=None;guint timer=0;bool incremental=false,notified=false,closed=false;
    std::string incoming;std::int64_t started=0,progress=0;
    struct Send {std::size_t offset=0,size=0;std::int64_t started=0,progress=0;};
    std::map<Key,Send> sends;
    explicit Impl(Callbacks c):callbacks(std::move(c)){
        if(!callbacks.permitted||!callbacks.borrow||!callbacks.lost||!callbacks.received)throw std::invalid_argument("clipboard.callbacks");
        auto* current=gdk_display_get_default();if(!current||!GDK_IS_X11_DISPLAY(current))return;
        // Private connection: event masks on foreign requestors cannot interfere
        // with another GDK component's subscriptions on the primary connection.
        display=gdk_display_open(gdk_display_get_name(current));if(!display)return;
        x=gdk_x11_display_get_xdisplay(display);
        selection=atom("CLIPBOARD");target=atom(mime);targets=atom("TARGETS");timestamp=atom("TIMESTAMP");incr=atom("INCR");property=atom("_SYSPANE_SCENE_FRAGMENT");
        gdk_window_add_filter(nullptr,filter,this);
        timer=g_timeout_add(20,+[](gpointer data)->gboolean{auto& o=*static_cast<Impl*>(data);try{o.tick();}catch(...){o.invalidate();}return G_SOURCE_CONTINUE;},this);
    }
    ~Impl(){close();}
    Atom atom(const char* name){return XInternAtom(x,name,False);}
    Window id(GdkWindow* w)const{return w?gdk_x11_window_get_xid(w):None;}
    GdkWindow* window(){
        GdkWindowAttr a{};a.window_type=GDK_WINDOW_TEMP;a.wclass=GDK_INPUT_ONLY;a.width=a.height=1;a.event_mask=GDK_PROPERTY_CHANGE_MASK|GDK_STRUCTURE_MASK;
        return gdk_window_new(gdk_screen_get_root_window(gdk_display_get_default_screen(display)),&a,0);
    }
    void destroy(GdkWindow*& w){if(w){auto* old=w;w=nullptr;gdk_window_destroy(old);}}
    bool live()const{return !closed&&display&&!gdk_display_is_closed(display);}
    bool allowed()const{return live()&&callbacks.permitted();}
    // borrow reauthorizes the snapshot. Do not repeat full draft validation via
    // permitted as well; every outgoing callback still gets a fresh checked view.
    std::string_view bytes(){if(!live())throw std::runtime_error("clipboard.denied");const auto b=callbacks.borrow();if(b.empty()||b.size()>ceiling)throw std::runtime_error("clipboard.bounds");return b;}
    bool put(Window w,Atom p,Atom type,int format,const void* bytes,int count){
        Trap trap(display);XChangeProperty(x,w,p,type,format,PropModeReplace,static_cast<const unsigned char*>(bytes),count);return trap.ok();
    }
    void notify(const XSelectionRequestEvent& q,Atom p){
        XEvent e{};e.xselection.type=SelectionNotify;e.xselection.display=x;e.xselection.requestor=q.requestor;e.xselection.selection=q.selection;e.xselection.target=q.target;e.xselection.property=p;e.xselection.time=q.time;
        Trap trap(display);XSendEvent(x,q.requestor,False,0,&e);(void)trap.ok();
    }
    void erase_send(Key key,bool terminate){
        if(!sends.erase(key))return;
        if(terminate)(void)put(key.first,key.second,target,8,nullptr,0);
        if(std::none_of(sends.begin(),sends.end(),[&](const auto& p){return p.first.first==key.first;})){
            Trap trap(display);XSelectInput(x,key.first,0);(void)trap.ok();
        }
    }
    void relinquish(bool erase=true){
        while(!sends.empty())erase_send(sends.begin()->first,true);
        destroy(owner);offered=0;
        if(erase)callbacks.lost();
    }
    void stop_receive(){destroy(receiver);incoming.clear();source=None;incremental=false;notified=false;requested=0;}
    void finish(ClipboardResult result){
        auto payload=result==ClipboardResult::received?std::move(incoming):std::string{};
        stop_receive();callbacks.received(result,std::move(payload));
    }
    void invalidate(){stop_receive();relinquish();}
    void close(){
        if(closed)return;
        closed=true;if(timer){g_source_remove(timer);timer=0;}
        // gdk_display_open returns a GDK-owned reference. close releases it.
        if(display){gdk_window_remove_filter(nullptr,filter,this);invalidate();gdk_display_close(display);display=nullptr;x=nullptr;}
    }
    bool offer(){
        if(!live())return false;
        (void)bytes();relinquish(false);owner=window();if(!owner)return false;
        offered=gdk_x11_get_server_time(owner);XSetSelectionOwner(x,selection,id(owner),offered);
        if(XGetSelectionOwner(x,selection)==id(owner))return true;
        relinquish();return false;
    }
    bool request(){
        if(!allowed()||receiver)return false;
        source=XGetSelectionOwner(x,selection);if(source==None)return false;
        receiver=window();if(!receiver)return false;
        requested=gdk_x11_get_server_time(receiver);started=progress=now();incremental=false;notified=false;incoming.clear();
        XConvertSelection(x,selection,target,property,id(receiver),requested);XFlush(x);return true;
    }
    bool get(Property& p,long length,Atom type=AnyPropertyType){
        Trap trap(display);const auto status=XGetWindowProperty(x,id(receiver),property,0,length,False,type,&p.type,&p.format,&p.count,&p.after,&p.data);return trap.ok()&&status==Success;
    }
    void consume(bool first){
        if(expired(started,progress)){finish(ClipboardResult::timeout);return;}
        if(!allowed()||XGetSelectionOwner(x,selection)!=source){finish(ClipboardResult::rejected);return;}
        Property size;
        if(!get(size,0)){finish(ClipboardResult::rejected);return;}
        if(first&&size.type==incr){
            Property header;
            if(size.format!=32||size.after!=4||!get(header,1,incr)||header.type!=incr||header.format!=32||header.count!=1||header.after||*reinterpret_cast<unsigned long*>(header.data)>ceiling){finish(ClipboardResult::rejected);return;}
            incremental=true;progress=now();XDeleteProperty(x,id(receiver),property);XFlush(x);return;
        }
        const auto remaining=ceiling-incoming.size();Property data;
        if(size.type!=target||size.format!=8||size.after>remaining||!get(data,static_cast<long>((remaining+3)/4),target)||data.type!=target||data.format!=8||data.after||data.count>remaining){finish(ClipboardResult::rejected);return;}
        if(expired(started,progress)){finish(ClipboardResult::timeout);return;}
        if(data.count)incoming.append(reinterpret_cast<char*>(data.data),data.count);
        progress=now();XDeleteProperty(x,id(receiver),property);XFlush(x);
        if(!incremental||!data.count){finish(incoming.empty()?ClipboardResult::rejected:ClipboardResult::received);}
    }
    void serve(const XSelectionRequestEvent& q){
        const auto p=q.property==None?q.target:q.property;
        if(!live())return;
        if(q.selection!=selection||q.owner!=id(owner)||!owner||XGetSelectionOwner(x,selection)!=id(owner)||(q.time!=CurrentTime&&static_cast<std::int32_t>(static_cast<std::uint32_t>(q.time-offered))<0)){notify(q,None);return;}
        const Key key{q.requestor,p};
        // Metadata conversions must not overwrite an active payload property.
        if(sends.count(key)){notify(q,None);return;}
        std::string_view b;
        try{b=bytes();}catch(...){notify(q,None);relinquish();return;}
        bool ok=false;
        if(q.target==targets){const Atom list[]={targets,timestamp,target};ok=put(q.requestor,p,XA_ATOM,32,list,3);}
        else if(q.target==timestamp){const unsigned long time=offered;ok=put(q.requestor,p,XA_INTEGER,32,&time,1);}
        else if(q.target==target){
            if(b.size()<=chunk)ok=put(q.requestor,p,target,8,b.data(),static_cast<int>(b.size()));
            else if(sends.size()<slots){
                Trap trap(display);XSelectInput(x,q.requestor,PropertyChangeMask|StructureNotifyMask);
                if(trap.ok()){
                    const unsigned long length=b.size();sends.emplace(key,Send{0,b.size(),now(),now()});
                    ok=put(q.requestor,p,incr,32,&length,1);if(!ok)erase_send(key,false);
                }
            }
        }
        notify(q,ok?p:None);
    }
    void send(const Key& key){
        auto it=sends.find(key);if(it==sends.end())return;
        if(!owner||XGetSelectionOwner(x,selection)!=id(owner)||expired(it->second.started,it->second.progress)){erase_send(key,true);return;}
        const auto b=bytes();auto& s=it->second;
        if(b.size()!=s.size||expired(s.started,s.progress)){erase_send(key,true);return;}
        const auto n=std::min(chunk,s.size-s.offset);
        const bool ok=put(key.first,key.second,target,8,b.data()+s.offset,static_cast<int>(n));
        s.offset+=n;s.progress=now();if(!ok||!n)erase_send(key,false);
    }
    void tick(){
        if(closed||!display)return;
        if(receiver&&expired(started,progress))finish(ClipboardResult::timeout);
        for(auto it=sends.begin();it!=sends.end();){const auto key=it->first;const bool dead=expired(it->second.started,it->second.progress);++it;if(dead)erase_send(key,true);}
    }
    bool event(const XEvent& e){
        if(e.xany.display!=x)return false;
        if(e.type==SelectionRequest&&owner&&e.xselectionrequest.owner==id(owner)){serve(e.xselectionrequest);return true;}
        if(e.type==SelectionClear&&owner&&e.xselectionclear.window==id(owner)&&e.xselectionclear.selection==selection){relinquish();return true;}
        if(e.type==SelectionNotify&&receiver&&e.xselection.requestor==id(receiver)){
            if(e.xselection.selection!=selection||e.xselection.target!=target||e.xselection.time!=requested)return true;
            if(notified)return true;
            notified=true;
            if(e.xselection.property!=property){finish(ClipboardResult::rejected);return true;}
            consume(true);return true;
        }
        if(e.type==PropertyNotify){
            const auto& p=e.xproperty;
            if(receiver&&p.window==id(receiver)&&p.atom==property){if(incremental&&p.state==PropertyNewValue)consume(false);return true;}
            const Key key{p.window,p.atom};if(sends.count(key)){if(p.state==PropertyDelete)send(key);return true;}
        }
        if(e.type==DestroyNotify){for(auto it=sends.begin();it!=sends.end();){const auto key=it->first;++it;if(key.first==e.xdestroywindow.window)erase_send(key,false);}}
        return false;
    }
    static GdkFilterReturn filter(GdkXEvent* event,GdkEvent*,gpointer data){
        auto& o=*static_cast<Impl*>(data);
        try{return o.event(*static_cast<XEvent*>(event))?GDK_FILTER_REMOVE:GDK_FILTER_CONTINUE;}
        catch(...){o.invalidate();return GDK_FILTER_REMOVE;}
    }
};
SceneClipboardX11::SceneClipboardX11(Callbacks c):impl_(std::make_unique<Impl>(std::move(c))){}
SceneClipboardX11::~SceneClipboardX11()=default;
bool SceneClipboardX11::available()const{return impl_->display&&!impl_->closed;}
bool SceneClipboardX11::busy()const{return impl_->receiver!=nullptr;}
bool SceneClipboardX11::offer(){return impl_->offer();}
bool SceneClipboardX11::request(){return impl_->request();}
void SceneClipboardX11::cancel(){if(busy())impl_->finish(ClipboardResult::cancelled);}
void SceneClipboardX11::invalidate(){impl_->invalidate();}
void SceneClipboardX11::close(){impl_->close();}
}
