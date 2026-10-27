#!/usr/bin/env python3
import json, re, html
from datetime import datetime, timezone

TODAY = datetime(2026,7,1,tzinfo=timezone.utc)
props = json.load(open('deal_props.json'))
eng = json.load(open('smb_engagements.json'))
smb_ids = json.load(open('smb_ids.json'))

OWNERS = {'900000113':'AE_13','900000115':'AE_27','900000080':'SDR_Q'}
STAGE = {
 'appointmentscheduled':'1-Prospect','9000000003':'2-Need Analysis','presentationscheduled':'3-Opportunity',
 'decisionmakerboughtin':'4-Proposal','contractsent':'5-Negotiation',
 '90000040':'1-Prospect','9000000004':'2-Need Analysis','90000042':'3-Opportunity','90000043':'4-Proposal','90000044':'5-Negotiation',
}
STAGE_ORDER = {'5-Negotiation':5,'4-Proposal':4,'3-Opportunity':3,'2-Need Analysis':2,'1-Prospect':1}
CONNECTED='f240bbac-87c9-4f6e-bf70-924b57d47db7'
# approx USD->INR for a normalized value column
USD_INR=83.0

def clean(t):
    if not t: return ''
    t=re.sub(r'<[^>]+>',' ',t)
    t=html.unescape(t)
    t=t.replace('​','').replace('\xa0',' ')
    t=re.sub(r'\s+',' ',t).strip()
    return t

def parse(ts):
    if not ts: return None
    try: return datetime.fromisoformat(ts.replace('Z','+00:00'))
    except: return None

def days_since(dt):
    if not dt: return None
    return (TODAY-dt).days

SUMMARY_KW=['summary','poc','decision','quote','quoted','budget','commercial','pupm','requirement','employee','headcount','emp','pricing','proposal','demo','pilot','contract','renewal','setup']

rows=[]
for did in smb_ids:
    p=props[did]
    o=eng.get(did,{'notes':[],'emails':[],'calls':[]})
    owner=OWNERS.get(p.get('hubspot_owner_id'),p.get('hubspot_owner_id'))
    stage=STAGE.get(p.get('dealstage'),p.get('dealstage'))
    amt=float(p.get('amount') or 0)
    cur=p.get('deal_currency_code') or 'INR'
    amt_inr=amt*USD_INR if cur=='USD' else amt
    # emails
    emails=o['emails']; calls=o['calls']; notes=o['notes']
    ein=[e for e in emails if e['metadata'].get('direction')=='INCOMING_EMAIL']
    eout=[e for e in emails if e['metadata'].get('direction')!='INCOMING_EMAIL']
    cconn=[c for c in calls if c['metadata'].get('disposition')==CONNECTED]
    catt=[c for c in calls if c['metadata'].get('disposition')!=CONNECTED]
    def maxts(lst):
        ds=[parse(x['timestamp']) for x in lst]; ds=[d for d in ds if d]
        return max(ds) if ds else None
    last_email=maxts(emails); last_email_in=maxts(ein)
    last_call=maxts(calls); last_call_conn=maxts(cconn)
    allts=[parse(x['timestamp']) for x in emails+calls+notes]; allts=[d for d in allts if d]
    last_act=max(allts) if allts else None
    idle=days_since(last_act)
    # activity status
    def within(dt,days):
        d=days_since(dt); return d is not None and d<=days
    if within(last_call_conn,30) or within(last_email_in,30):
        act='Active'
    elif within(last_email,30) or within(last_call,30):
        act='One-way'
    elif last_act and idle is not None and idle<=60:
        act='Silent'
    else:
        act='Dead'
    # AE summary: choose most informative note (keyword score then length)
    best=''; best_score=-1
    for n in notes:
        txt=clean(n['body'])
        if not txt: continue
        low=txt.lower()
        score=sum(low.count(k) for k in SUMMARY_KW)*50+len(txt)
        if score>best_score:
            best_score=score; best=txt
    # if no useful note, fall back to latest connected call note
    if len(best)<40:
        for c in sorted(cconn,key=lambda x:x['timestamp'] or '',reverse=True):
            ct=clean(c['body'])
            if len(ct)>=40: best=ct; break
    ae_sum=best[:700]
    if len(best)>=200: ae_status='Yes'
    elif len(best)>=40: ae_status='Partial'
    else: ae_status='No'
    # next action (rule-based)
    so=STAGE_ORDER.get(stage,0)
    if ae_status=='No':
        na='Log deal context in HubSpot (POC, current setup, requirement, commercials, timeline) — no usable summary on record.'
    elif act in ('Silent','Dead'):
        na=f'Re-engage POC with a value refresh / trigger event; confirm the deal is still live before {("closing" if so>=4 else "advancing")}.'
    elif act=='One-way':
        na='Customer non-responsive to outbound — switch channel or escalate to a senior contact; confirm interest.'
    elif so>=5:
        na='Chase signature/PO; lock final commercials and go-live date this week.'
    elif so==4:
        na='Push for verbal agreement and send/confirm proposal; align on pricing and decision timeline.'
    elif so==3:
        na='Run solution demo / align on requirement; identify economic buyer and next milestone.'
    elif so==2:
        na='Complete needs analysis; map decision-makers and confirm budget/timeline.'
    else:
        na='Qualify: confirm need, headcount, budget owner and set the next meeting.'
    rows.append({
        'deal_id':did,'dealname':(p.get('dealname') or '').strip(),'owner':owner,'stage':stage,
        'amount':amt,'currency':cur,'amount_inr':round(amt_inr),
        'createdate':(p.get('createdate') or '')[:10],'closedate':(p.get('closedate') or '')[:10],
        'last_activity':last_act.strftime('%Y-%m-%d') if last_act else '',
        'days_idle':idle if idle is not None else '',
        'emails_in':len(ein),'emails_out':len(eout),'last_email':last_email.strftime('%Y-%m-%d') if last_email else '',
        'calls_connected':len(cconn),'calls_attempted':len(catt),'last_call':last_call.strftime('%Y-%m-%d') if last_call else '',
        'notes':len(notes),'ae_status':ae_status,'activity':act,'ae_summary':ae_sum,'next_action':na,
        'url':f'https://app.hubspot.com/contacts/1234567/record/0-3/{did}',
        'stage_order':so,
    })
json.dump(rows,open('smb_deal_rows.json','w'),ensure_ascii=False,indent=2)
# summary stats
from collections import Counter, defaultdict
print('rows',len(rows))
print('AE status',dict(Counter(r['ae_status'] for r in rows)))
print('Activity',dict(Counter(r['activity'] for r in rows)))
byown=defaultdict(lambda:[0,0])
for r in rows:
    byown[r['owner']][0]+=1; byown[r['owner']][1]+=r['amount_inr']
for k,v in byown.items(): print(k,'deals',v[0],'pipeline INR',v[1])
print('no cached engagements:',[r['deal_id'] for r in rows if r['notes']==0 and r['emails_in']==0 and r['emails_out']==0 and r['calls_connected']==0 and r['calls_attempted']==0])
