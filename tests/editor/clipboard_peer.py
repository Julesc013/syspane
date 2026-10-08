"""Independent Xlib selection owner/requestor; never imports product codecs."""
import ctypes as C
import time
from native_oracle import Display

U=C.c_ulong;P=C.c_void_p;I=C.c_int
COMMON=[('type',I),('serial',U),('send_event',I),('display',P)]
class Request(C.Structure):
    _fields_=COMMON+[(n,U) for n in ('owner','requestor','selection','target','property','time')]
class Notify(C.Structure):
    _fields_=COMMON+[(n,U) for n in ('requestor','selection','target','property','time')]
class PropertyEvent(C.Structure):
    _fields_=COMMON+[(n,U) for n in ('window','atom','time')]+[('state',I)]
class Event(C.Union):
    _fields_=[('type',I),('request',Request),('notify',Notify),('property',PropertyEvent),('padding',C.c_long*24)]
class Error(C.Structure):
    _fields_=[('type',I),('display',P),('resourceid',U),('serial',U),('error_code',C.c_ubyte),('request_code',C.c_ubyte),('minor_code',C.c_ubyte)]

class Peer(Display):
    def __init__(self):
        super().__init__()
        signatures={'XNextEvent':([P,P],I),'XPending':([P],I),'XSelectInput':([P,U,C.c_long],I),
            'XGetSelectionOwner':([P,U],U),'XSetSelectionOwner':([P,U,U,U],I),
            'XConvertSelection':([P,U,U,U,U,U],I),'XDeleteProperty':([P,U,U],I),
            'XChangeProperty':([P,U,U,U,I,I,P,I],I),'XExtendedMaxRequestSize':([P],C.c_long)}
        for name,(args,result) in signatures.items():getattr(self.x,name).argtypes=args;getattr(self.x,name).restype=result
        self.x.XExtendedMaxRequestSize(self.handle)
        self.errors=[]
        callback=C.CFUNCTYPE(I,P,C.POINTER(Error))
        self.error_handler=callback(lambda d,e:self.errors.append(dict(code=e.contents.error_code,resource=e.contents.resourceid,request=e.contents.request_code)) or 0)
        self.x.XSetErrorHandler.argtypes=[callback];self.x.XSetErrorHandler(self.error_handler)
        self.clipboard=self.atom('CLIPBOARD');self.mime=self.atom('application/vnd.syspane.scene-fragment+json');self.incr=self.atom('INCR')
        self.windows=[];self.reads={};self.requests=[];self.refusals=[];self.sends={};self.current=None;self.serial=0
    def sync(self):self.x.XSync(self.handle,False)
    def window(self):
        w=self.x.XCreateSimpleWindow(self.handle,self.root,0,0,1,1,0,0,0);assert w
        self.x.XSelectInput(self.handle,w,1<<22);self.windows.append(w);self.sync();return w
    def owner(self,selection=None):return self.x.XGetSelectionOwner(self.handle,selection or self.clipboard)
    def own(self,payload=b'',mode='direct',hint=None,chunk=128,kind=None,selection=None,interval=0,fmt=8):
        w=self.window();self.current=dict(window=w,payload=payload,mode=mode,hint=len(payload) if hint is None else hint,chunk=chunk,kind=self.mime if kind is None else kind,interval=interval,fmt=fmt)
        self.x.XSetSelectionOwner(self.handle,selection or self.clipboard,w,0);self.sync();assert self.owner(selection)==w;return w
    def put(self,w,p,kind,fmt,data):
        if fmt==32:buffer=(U*len(data))(*data);count=len(data)
        else:buffer=C.create_string_buffer(data);count=len(data)
        self.x.XChangeProperty(self.handle,w,p,kind,fmt,0,buffer,count);self.sync()
    def read(self,w,p):
        kind,fmt,count,after,data=U(),I(),U(),U(),P()
        code=self.x.XGetWindowProperty(self.handle,w,p,0,70000,False,0,C.byref(kind),C.byref(fmt),C.byref(count),C.byref(after),C.byref(data))
        try:
            assert code==0 and after.value==0 and count.value<=280000
            payload=C.string_at(data,count.value) if fmt.value==8 else list(C.cast(data,C.POINTER(U))[:count.value]) if fmt.value==32 else None
            return kind.value,fmt.value,payload
        finally:
            if data:self.x.XFree(data)
    def notify(self,q,property,overrides=None):
        event=Event();event.notify.type=31;event.notify.display=self.handle
        for name in ('requestor','selection','target','time'):setattr(event.notify,name,getattr(q,name))
        event.notify.property=property
        for name,value in (overrides or {}).items():setattr(event.notify,name,value)
        assert self.x.XSendEvent(self.handle,q.requestor,False,0,C.byref(event));self.sync()
    def deliver(self,q,offer=None):
        offer=offer or self.current;p=q.property or q.target
        if offer['mode']=='incr':
            self.x.XSelectInput(self.handle,q.requestor,(1<<22)|(1<<17))
            self.sends[(q.requestor,p)]={**offer,'offset':0}
            self.put(q.requestor,p,self.incr,32,[offer['hint']])
        elif offer['mode']=='bad-incr':self.put(q.requestor,p,self.incr,32,[0,1])
        else:self.put(q.requestor,p,offer['kind'],offer['fmt'],offer['payload'])
        fields={'wrong-time':{'time':q.time+1},'wrong-target':{'target':self.atom('UTF8_STRING')},'wrong-selection':{'selection':self.atom('PRIMARY')},'wrong-property':{'property':self.atom('_WRONG_PROPERTY')}}
        self.notify(q,p,fields.get(offer['mode']))
    def request(self,target=None,automatic=True):
        w=self.window();self.serial+=1;p=self.atom('_PEER_'+str(self.serial));target=target or self.mime
        row=dict(window=w,property=p,target=target,automatic=automatic,notified=False,incremental=False,complete=False,refused=False,data=b'',chunks=[])
        self.reads[w]=row;self.x.XConvertSelection(self.handle,self.clipboard,target,p,w,0);self.sync();return row
    def advance(self,row):self.x.XDeleteProperty(self.handle,row['window'],row['property']);self.sync()
    def duplicate(self,row,target):
        self.x.XConvertSelection(self.handle,self.clipboard,target,row['property'],row['window'],0);self.sync()
    def destroy(self,w):
        self.x.XDestroyWindow(self.handle,w);self.windows.remove(w);self.reads.pop(w,None);self.sync()
    def pump(self):
        for key,offer in list(self.sends.items()):
            if 'due' in offer and time.monotonic()>=offer['due']:
                del offer['due'];self.send_chunk(key,offer)
        for _ in range(128):
            if not self.x.XPending(self.handle):break
            e=Event();self.x.XNextEvent(self.handle,C.byref(e))
            if e.type==30:
                q=Request.from_buffer_copy(e.request);self.requests.append(q)
                if q.target==self.mime and self.current and q.owner==self.current['window']:
                    if self.current['mode']!='hold':self.deliver(q)
                else:self.notify(q,0)
            elif e.type==31 and e.notify.requestor in self.reads:
                row=self.reads[e.notify.requestor]
                if row['notified'] and not e.notify.property:
                    self.refusals.append(dict(window=row['window'],target=e.notify.target));continue
                row['notified']=True
                if not e.notify.property:row.update(complete=True,refused=True);continue
                kind,fmt,data=self.read(row['window'],row['property']);row.update(kind=kind,format=fmt)
                if kind==self.incr:assert fmt==32 and len(data)==1;row['incremental']=True;row['hint']=data[0]
                else:row.update(data=data,complete=True)
                if row['automatic'] or row['complete']:self.advance(row)
            elif e.type==28:
                p=e.property;row=self.reads.get(p.window)
                if row and row['notified'] and row['incremental'] and p.atom==row['property'] and p.state==0:
                    kind,fmt,data=self.read(p.window,p.atom);assert kind==self.mime and fmt==8
                    row['chunks'].append(len(data));row['data']+=data
                    if not data:row['complete']=True
                    if row['automatic'] or row['complete']:self.advance(row)
                if p.state==1 and (p.window,p.atom) in self.sends:
                    key=(p.window,p.atom);offer=self.sends[key]
                    if offer['interval']:offer['due']=time.monotonic()+offer['interval']
                    else:self.send_chunk(key,offer)
    def send_chunk(self,key,offer):
        start=offer['offset'];data=offer['payload'][start:start+offer['chunk']]
        self.put(key[0],key[1],offer['kind'],8,data);offer['offset']+=len(data)
        if not data:del self.sends[key]
    def close(self):
        self.sends.clear();super().close()
