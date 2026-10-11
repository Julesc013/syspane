"""Strict complete tick attribution; nested timings are never added twice."""
import re
FIELDS=('index','stage','generation_before','generation_after','points','work_us','delay_us','receiver_us','delivery_us','lookup_us','publication_us','admission_us','adoption_us','presentation_us','phase_mask')
PARTS=('receiver_us','delivery_us','lookup_us','publication_us')
LIMIT=6*1024*1024

def decode(raw,timings):
    if len(raw)>LIMIT or not raw.endswith(b'\n'):raise ValueError('phase size/completion')
    lines=raw.splitlines()
    begin=re.fullmatch(rb'history-phases-begin ([12]) ([0-9]{1,5})',lines[0]) if lines else None
    if not begin:raise ValueError('phase begin/version')
    version=int(begin[1]);count=int(begin[2])
    fields=FIELDS if version==1 else tuple('handoff_us' if key=='publication_us' else key for key in FIELDS)
    parts=PARTS if version==1 else tuple('handoff_us' if key=='publication_us' else key for key in PARTS)
    if not 0<count<=32768 or len(lines)!=count+2 or lines[-1]!=b'history-phases-end '+str(count).encode() or count!=len(timings):raise ValueError('phase count/end/timing coverage')
    result=[]
    for index,line in enumerate(lines[1:-1]):
        if not re.fullmatch(rb'history-phase(?: [0-9]{1,20}){15}',line):raise ValueError('phase row')
        values=list(map(int,line.split()[1:]))
        if any(v>=2**64 for v in values):raise ValueError('phase integer overflow')
        row=dict(zip(fields,values))
        if version==2:row['journal_version']=2
        if row['index']!=index or row['stage']>5 or max(row['generation_before'],row['generation_after'])>4099 or row['points']>4096 or row['phase_mask'] not in (0,3,7):raise ValueError('phase identity/state')
        if any(row[k]!=timings[index][k] for k in ('work_us','delay_us')):raise ValueError('phase original timing mismatch')
        if sum(row[k] for k in parts)>row['work_us'] or row['admission_us']+row['adoption_us']>row['delivery_us'] or row['presentation_us']>row['adoption_us']:raise ValueError('phase nested/disjoint accounting')
        if row['phase_mask']==0 and any(row[k] for k in ('admission_us','adoption_us','presentation_us')):raise ValueError('unobserved phase duration')
        if row['phase_mask']==3 and row['presentation_us']:raise ValueError('unobserved presentation')
        if version==1 and row['publication_us'] and (row['stage']!=1 or row['generation_after']!=row['generation_before']+1):raise ValueError('fixture publication state')
        row['residual_us']=row['work_us']-sum(row[k] for k in parts)
        row['delivery_residual_us']=row['delivery_us']-row['admission_us']-row['adoption_us']
        row['adoption_other_us']=row['adoption_us']-row['presentation_us']
        result.append(row)
    return result

def summarize(rows,limit=100000):
    parts=PARTS if 'publication_us' in rows[0] else tuple('handoff_us' if key=='publication_us' else key for key in PARTS)
    if any(('publication_us' in row)!=('publication_us' in rows[0]) for row in rows):raise ValueError('mixed journal versions')
    names=('work_us','delay_us',*parts,'admission_us','adoption_us','presentation_us','residual_us','delivery_residual_us','adoption_other_us')
    return dict(records=len(rows),maxima={k:max(row[k] for row in rows) for k in names},slow=[row for row in rows if max(row['work_us'],row['delay_us'])>limit],nested_accounting='presentation within adoption within delivery; admission also within delivery',uncovered='Residual time is unattributed overhead; native accessibility requests outside ticks and scheduling are not measured')
