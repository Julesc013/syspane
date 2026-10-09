"""Strict bounded decoding and non-overlapping attribution of callback records."""
import collections

LABELS=['other','apply','undo','redo','recovery-restore','recovery-keep','recovery-discard',
        'clicked','draw','changed','toggled','key-press-event','button-press-event',
        'motion-notify-event','button-release-event','focus-out-event','destroy','insert-text','delete-range']


def decode(raw):
    assert len(raw)<=16*1024*1024,'transcript bound'
    lines=raw.splitlines()
    assert not lines or not lines[-1].startswith(b'callback-trace') or raw.endswith(b'\n'),'truncated line'
    lines=[v.decode('ascii').split() for v in lines if v.startswith(b'callback-trace')]
    blocks=[];pids=set();i=0
    while i<len(lines):
        header=lines[i];i+=1;assert len(header)==4 and header[0]=='callback-trace-begin'
        pid,count,invalid=map(int,header[1:]);assert 0<pid<2**31 and pid not in pids and 0<=count<=32768 and invalid==0
        pids.add(pid);rows=[];registrations={};active=collections.defaultdict(list)
        for index in range(1,count+1):
            line=lines[i];i+=1;assert len(line)==14 and line[0]=='callback-trace'
            values=[int(v,16 if n==7 else 10) for n,v in enumerate(line) if n]
            rid,parent,tid,serial,kind,label,offset,interval,priority,ordinal,start,end,cpu=values
            assert rid==index and 0<=parent<rid and 0<tid<2**31 and 0<serial<2**64
            assert kind in (1,2) and 0<=label<len(LABELS) and 0<offset<2**64
            assert 0<=interval<2**32 and -(2**31)<=priority<2**31
            assert 0<ordinal<2**64 and 0<start<=end<2**64 and 0<=cpu<2**64
            if rows:assert start>=rows[-1]['start_ns'],'entry order'
            assert (kind==1 and interval==priority==0) or (kind==2 and label==0)
            identity=(kind,label,offset,interval,priority)
            old=registrations.get(serial,(identity,0));assert old==(identity,ordinal-1),'registration drift or missing ordinal'
            registrations[serial]=(identity,ordinal)
            thread=active[tid]
            while thread and thread[-1]['end_ns']<=start:thread.pop()
            assert parent==(thread[-1]['id'] if thread else 0),'overlap or invalid parent'
            if thread:assert end<=thread[-1]['end_ns'],'child outlives parent'
            assert len(thread)<64
            row=dict(id=rid,parent=parent,tid=tid,serial=serial,kind=kind,label=LABELS[label],offset=offset,
                     interval_ms=interval,priority=priority,ordinal=ordinal,start_ns=start,end_ns=end,cpu_ns=cpu,wall_ns=end-start,
                     cpu_over_wall_ns=max(0,cpu-(end-start)))
            rows.append(row);thread.append(row)
        assert lines[i]==['callback-trace-end',str(pid),str(count)];i+=1
        blocks.append(dict(pid=pid,rows=rows))
    assert blocks,'missing transcript';return blocks


def union_ns(intervals):
    total=0;end=0
    for first,last in sorted(intervals):
        assert 0<=first<=last
        total+=max(0,last-max(first,end));end=max(end,last)
    return total


def correlate(block,timings):
    rows=block['rows'];assert rows,'empty frontend trace'
    ticks=[v for v in rows if v['kind']==2 and v['interval_ms']==20 and v['priority']==0]
    assert len({v['serial'] for v in ticks})==1 and len(ticks)==len(timings),'frontend timer coverage'
    assert all(v['ordinal']==i+1 for i,v in enumerate(ticks))
    result=[]
    for i,(tick,observed) in enumerate(zip(ticks,timings)):
        assert observed['pid']==block['pid'] and tick['tid']==block['pid'] and not tick['parent']
        # Observer is inside the wrapper. Never hide its extra cost as product work.
        assert tick['wall_ns']+2000>=observed['work_us']*1000,'work correlation'
        if not i:continue
        first,last=ticks[i-1]['end_ns'],tick['start_ns'];assert first<=last
        intersections=[v for v in rows if v['tid']==tick['tid'] and v['start_ns']<last and v['end_ns']>first]
        covered=union_ns([(max(first,v['start_ns']),min(last,v['end_ns'])) for v in intersections])
        # Wrapper exit follows previous_tick and entry precedes observed_tick.
        # Exact equality is not expected; retain both and their difference.
        gap=last-first
        result.append(dict(ordinal=tick['ordinal'],gap_ns=gap,covered_ns=covered,uncovered_ns=gap-covered,
                           observed_delay_us=observed['delay_us'],observed_work_us=observed['work_us'],
                           wrapper_delay_difference_ns=observed['delay_us']*1000-max(0,gap-20000000),
                           rows=[v['id'] for v in intersections]))
    return result
