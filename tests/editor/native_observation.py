"""Error-reporting AT-SPI observations for the owned editor laboratory.

Cache only object addresses, never text, interfaces, state or geometry. Libatspi
convenience APIs can turn failed state/interface calls into absence. Use explicit
wire replies here so unavailable observations cannot satisfy negative assertions.
"""
from collections import namedtuple
import time
from gi.repository import Gio,GLib

Rect=namedtuple('Rect','x y width height')
PREFIX='org.a11y.atspi.'

class Unavailable(RuntimeError):pass

class Observations:
    def __init__(self,report):
        self.report=report;self.addresses={};self.deadline=None
        session=Gio.bus_get_sync(Gio.BusType.SESSION,None)
        address=session.call_sync('org.a11y.Bus','/org/a11y/bus','org.a11y.Bus','GetAddress',None,GLib.VariantType.new('(s)'),Gio.DBusCallFlags.NONE,200,None).unpack()[0]
        self.bus=Gio.DBusConnection.new_for_address_sync(address,Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT|Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION,None,None)

    def identity(self,obj):
        if obj is None:raise Unavailable('No accessible object was observed')
        if isinstance(obj,tuple):
            assert len(obj)==2 and obj[0].startswith(':') and obj[1].startswith('/org/a11y/atspi/')
            if obj[1]=='/org/a11y/atspi/null':raise Unavailable('No accessible child was observed')
            return obj
        if obj not in self.addresses:
            if obj.app is None:raise Unavailable('Accessible object has no recorded owner')
            assert len(self.addresses)<4096,'accessible address bound'
            self.addresses[obj]=(obj.app.bus_name,obj.path)
        return self.addresses[obj]

    def call(self,obj,interface,method,args=None,signature=None):
        name,path=self.identity(obj);timeout=200
        if self.deadline is not None:
            remaining=int((self.deadline-time.monotonic())*1000)
            if remaining<1:raise Unavailable('Observation deadline reached before call')
            timeout=min(timeout,remaining)
        started=time.monotonic()
        try:
            reply=self.bus.call_sync(name,path,interface,method,args,GLib.VariantType.new(signature),Gio.DBusCallFlags.NONE,timeout,None)
            if self.deadline is not None and time.monotonic()>self.deadline:raise Unavailable('Observation reply arrived after deadline')
            return reply.unpack()
        except GLib.GError as error:
            rows=self.report.setdefault('observation_errors',[])
            assert len(rows)<128,'observation error bound'
            rows.append(dict(name=name,path=path,interface=interface,method=method,error=str(error),remote=Gio.DBusError.get_remote_error(error),duration_ms=(time.monotonic()-started)*1000))
            raise

    def interfaces(self,obj):return self.call(obj,PREFIX+'Accessible','GetInterfaces',signature='(as)')[0]
    def text(self,obj):
        if PREFIX+'Text' in self.interfaces(obj):return self.call(obj,PREFIX+'Text','GetText',GLib.Variant('(ii)',(0,-1)),'(s)')[0]
        return self.call(obj,'org.freedesktop.DBus.Properties','Get',GLib.Variant('(ss)',(PREFIX+'Accessible','Name')),'(v)')[0]
    def state(self,obj,state):
        words=self.call(obj,PREFIX+'Accessible','GetState',signature='(au)')[0]
        assert len(words)==2,'invalid AT-SPI state reply'
        bit=int(state);return bool(words[bit//32]&(1<<(bit%32)))
    def extents(self,obj):return Rect(*self.call(obj,PREFIX+'Component','GetExtents',GLib.Variant('(u)',(0,)),'((iiii))')[0])
    def focus(self,obj):return self.call(obj,PREFIX+'Component','GrabFocus',signature='(b)')[0]
    def selected_text(self,obj):
        count=self.call(obj,'org.freedesktop.DBus.Properties','Get',GLib.Variant('(ss)',(PREFIX+'Selection','NSelectedChildren')),'(v)')[0]
        assert type(count) is int and 0<=count<=1,'invalid single-selection reply'
        if count==0:return ''
        child=self.call(obj,PREFIX+'Selection','GetSelectedChild',GLib.Variant('(i)',(0,)),'((so))')[0]
        try:return self.text(tuple(child))
        except GLib.GError as error:
            # A selection can change between these read-only replies. Re-read the
            # whole selection within the caller's deadline; never infer empty.
            if self.removed(error):raise Unavailable('Selected child was replaced during observation') from error
            raise

    @staticmethod
    def retryable(error):
        return isinstance(error,Unavailable) or isinstance(error,GLib.GError) and (error.matches(Gio.io_error_quark(),Gio.IOErrorEnum.TIMED_OUT) or Gio.DBusError.get_remote_error(error) in ('org.freedesktop.DBus.Error.NoReply','org.freedesktop.DBus.Error.Timeout'))

    @staticmethod
    def removed(error):
        # Only an explicit missing-object reply, never a missing service, no reply,
        # denied call or local libatspi DEFUNCT fallback, can prove this boundary.
        return isinstance(error,GLib.GError) and Gio.DBusError.get_remote_error(error)=='org.freedesktop.DBus.Error.UnknownObject'
