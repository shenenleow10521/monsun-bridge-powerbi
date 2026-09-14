"""Build a separate, offline PBIP from validated official snapshots.

Preserves the original research project. Empty exposure/AI estimates are never
converted to zero or disguised as observed workforce statistics.
"""
import argparse
import csv
import hashlib
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'MonsunOfficial'
MODEL = OUT / 'MonsunOfficial.SemanticModel'
REPORT = OUT / 'MonsunOfficial.Report'
VC = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json'
PAGES = ['a1000000000000000001','a2000000000000000002','a3000000000000000003','a4000000000000000004']
NAVY, TEAL, PAPER, MUTED = '#102A3A', '#087F82', '#F4F7F7', '#536A77'

def save_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding='utf-8')

def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def mstr(value):
    return '"' + str(value).replace('"','""').replace('\r','#(cr)').replace('\n','#(lf)') + '"'

def table(name, columns, rows):
    s = f'table {name}\n'
    for col, dtype, fmt in columns:
        s += f'\n\tcolumn {col}\n\t\tdataType: {dtype}\n\t\tsourceColumn: {col}\n\t\tsummarizeBy: none\n'
        if fmt:
            s += f'\t\tformatString: {fmt}\n'
        if col == 'source_url':
            s += '\t\tdataCategory: WebUrl\n'
    types={'string':'text','double':'number','int64':'Int64.Type','dateTime':'date'}
    schema=', '.join(f'{c} = {types[t]}' for c,t,_ in columns)
    records=[]
    for row in rows:
        vals=[]
        for c,t,_ in columns:
            v=row[c]
            if v is None:
                vals.append('null')
            elif t=='string':
                vals.append(mstr(v))
            elif t=='dateTime':
                y,m,d=map(int,str(v).split('-')); vals.append(f'#date({y}, {m}, {d})')
            else:
                vals.append(str(float(v)) if t=='double' else str(int(v)))
        records.append('{' + ', '.join(vals) + '}')
    s += f'\n\tpartition {name} = m\n\t\tmode: import\n\t\tsource =\n\t\t\t\t#table(type table [{schema}], {{\n'
    s += ',\n'.join('\t\t\t\t    '+r for r in records)
    s += '\n\t\t\t\t})\n'
    dest=MODEL/'definition'/'tables'/f'{name}.tmdl'
    dest.parent.mkdir(parents=True,exist_ok=True); dest.write_text(s,encoding='utf-8')

def lit(value): return {'expr':{'Literal':{'Value':str(value)}}}
def string(value): return lit("'" + value.replace("'","''") + "'")
def color(value): return {'solid':{'color':string(value)}}
def field(t,c): return {'Column':{'Expression':{'SourceRef':{'Entity':t}},'Property':c}}
def measure(c): return {'Measure':{'Expression':{'SourceRef':{'Entity':'Metrics'}},'Property':c}}
def projection(f,ref,label): return {'field':f,'queryRef':ref,'nativeQueryRef':label,'displayName':label}

visuals={p:[] for p in PAGES}
def visual(page, name, kind, xywh):
    x,y,w,h=xywh
    o={'$schema':VC,'name':name,'position':{'x':x,'y':y,'width':w,'height':h,'z':len(visuals[page])+1,'tabOrder':len(visuals[page])+1},'visual':{'visualType':kind,'drillFilterOtherVisuals':True}}
    visuals[page].append(o); return o

def title(o, text):
    o['visual'].setdefault('visualContainerObjects',{})['title']=[{'properties':{'show':lit('true'),'text':string(text)}}]

def text(page,name,xywh,lines,bg=None,fg=NAVY,size=13):
    o=visual(page,name,'textbox',xywh)
    o['visual']['objects']={'general':[{'properties':{'paragraphs':[{'textRuns':[{'value':v,'textStyle':{'fontFamily':'Segoe UI','fontSize':f'{size if i==0 else size-1}pt','fontWeight':'bold' if i==0 else 'normal','color':fg}}]} for i,v in enumerate(lines)]}}]}
    o['visual']['visualContainerObjects']={'title':[{'properties':{'show':lit('false')}}],'background':[{'properties':{'show':lit('true'),'color':color(bg or PAPER),'transparency':lit('0D')}}]}
    return o

def card(page,name,xywh,metric,label):
    o=visual(page,name,'cardVisual',xywh)
    o['visual']['query']={'queryState':{'Data':{'projections':[projection(measure(metric),'Metrics.'+metric,label)]}}}
    o['visual']['objects']={'label':[{'properties':{'show':lit('false')},'selector':{'id':'default'}}]}
    title(o,label);return o

def chart(page,name,xywh,kind,table_name,category,metrics,label,series=None):
    o=visual(page,name,kind,xywh)
    cat=projection(field(table_name,category),table_name+'.'+category,category);cat['active']=True
    q={'Category':{'projections':[cat]},'Y':{'projections':[projection(measure(m),'Metrics.'+m,m) for m in metrics]}}
    if series: q['Series']={'projections':[projection(field(table_name,series),table_name+'.'+series,series)]}
    o['visual']['query']={'queryState':q,'sortDefinition':{'sort':[{'field':field(table_name,category),'direction':'Ascending'}]}}
    title(o,label); return o

def grid(page,name,xywh,t,cols,label):
    o=visual(page,name,'tableEx',xywh)
    o['visual']['query']={'queryState':{'Values':{'projections':[projection(field(t,c),t+'.'+c,l) for c,l in cols]}}}
    o['visual']['objects']={'total':[{'properties':{'totals':lit('false')}}]}
    title(o,label); return o

def slicer(page,name,xywh,t,c,label):
    o=visual(page,name,'slicer',xywh)
    o['visual']['query']={'queryState':{'Values':{'projections':[projection(field(t,c),t+'.'+c,label)]}}}
    o['visual']['objects']={'data':[{'properties':{'mode':string('Dropdown')}}],'selection':[{'properties':{'singleSelect':lit('true')}}]}
    title(o,label);return o

def build(snapshot):
    status=json.loads((snapshot/'BUILD_STATUS.json').read_text())
    if status['download_and_validation']!='PASSED':raise ValueError('Official build not validated')
    labour=read_csv(snapshot/'processed'/'official_lfs.csv')
    income=read_csv(snapshot/'processed'/'official_income.csv')
    fish=read_csv(snapshot/'processed'/'official_fish.csv')
    for item in status['sources']:
        raw=snapshot/'raw'/(item['dataset']+'.csv')
        if hashlib.sha256(raw.read_bytes()).hexdigest()!=item['sha256']:raise ValueError('Source hash mismatch')
    for d in [MODEL/'definition'/'tables',REPORT/'definition'/'pages',OUT/'Data']:d.mkdir(parents=True,exist_ok=True)
    for f in (snapshot/'processed').glob('*.csv'):shutil.copy2(f,OUT/'Data'/f.name)
    shutil.copy2(snapshot/'BUILD_STATUS.json',OUT/'Data'/'SOURCE_MANIFEST.json')
    shutil.copytree(snapshot/'raw', OUT/'Data'/'raw', dirs_exist_ok=True)
    src='https://www.dosm.gov.my/portal-main/release-content/'
    tourism=[]
    releases=[('2025-01-01','2025 Q1',69.7,29.4,'malaysias-domestic-tourism-survey-first-quarter-2025'),('2025-04-01','2025 Q2',73.8,29.2,'malaysias-domestic-tourism-survey-second-quarter-2025'),('2025-07-01','2025 Q3',72.6,29.8,'malaysias-domestic-tourism-survey-third-quarter-2025'),('2025-10-01','2025 Q4',74.0,32.6,'malaysias-domestic-tourism-survey-q42025')]
    for dt,q,v,e,url in releases:tourism.append(dict(date=dt,quarter=q,visitors_million=v,expenditure_billion=e,source_url=src+url))
    with (OUT/'Data'/'official_tourism.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(tourism[0]));w.writeheader();w.writerows(tourism)
    table('Tourism',[('date','dateTime','yyyy-MM-dd'),('quarter','string',''),('visitors_million','double','0.0'),('expenditure_billion','double','0.0'),('source_url','string','')],tourism)
    table('Labour',[('state','string',''),('district','string',''),('date','dateTime','yyyy'),('labour_force_thousands','double','0.0'),('employed_thousands','double','0.0'),('unemployment_rate_pct','double','0.0'),('source_url','string','')],labour)
    table('Income',[('state','string',''),('district','string',''),('date','dateTime','yyyy'),('income_mean_rm','double','#,0'),('income_median_rm','double','#,0'),('source_url','string','')],income)
    table('Fish',[('state','string',''),('date','dateTime','MMM yyyy'),('month','int64','0'),('landings_mt','double','#,0'),('source_url','string','')],fish)
    table('Participation',[('rate','double','0%')],[{'rate':i/100} for i in range(0,101,5)])
    table('Duration',[('months','int64','0')],[{'months':i} for i in range(1,7)])
    table('UnitCost',[('rm','int64','#,0')],[{'rm':i} for i in range(500,3001,100)])
    table('Metrics',[('placeholder','string','')],[])
    metrics={
     'Visitors (million)':('SUM(Tourism[visitors_million])','0.0'),
     'Expenditure (RM billion)':('SUM(Tourism[expenditure_billion])','0.0'),
     'Q4 visitors (million)':('CALCULATE([Visitors (million)], Tourism[quarter] = "2025 Q4")','0.0'),
     'Q4 expenditure (RM billion)':('CALCULATE([Expenditure (RM billion)], Tourism[quarter] = "2025 Q4")','0.0'),
     'Published quarters':('COUNTROWS(Tourism)','0'),
     'Employed persons':('SUM(Labour[employed_thousands]) * 1000','#,0'),
     'Labour force persons':('SUM(Labour[labour_force_thousands]) * 1000','#,0'),
     'District count':('DISTINCTCOUNT(Labour[district])','0'),
     'Marine landings (tonnes)':('SUM(Fish[landings_mt])','#,0'),
     'Monthly records':('COUNTROWS(Fish)','0'),
     'Scenario rate':('SELECTEDVALUE(Participation[rate], 0.05)','0%'),
     'Scenario duration':('SELECTEDVALUE(Duration[months], 1)','0'),
     'Scenario unit cost':('SELECTEDVALUE(UnitCost[rm], 1100)','#,0'),
     'Scenario participants':('ROUND([Employed persons] * [Scenario rate], 0)','#,0'),
     'Scenario training budget':('[Scenario participants] * [Scenario duration] * [Scenario unit cost]','"RM "#,0'),
     'Scenario admin budget':('[Scenario training budget] * 0.1','"RM "#,0'),
     'Scenario total budget':('[Scenario training budget] + [Scenario admin budget]','"RM "#,0'),
     'Scenario cost per participant':('DIVIDE([Scenario total budget], [Scenario participants])','"RM "#,0')}
    p=MODEL/'definition'/'tables'/'Metrics.tmdl';s=p.read_text()
    declarations=''
    for name,(dax,fmt) in metrics.items():declarations+=f"\n\tmeasure '{name}' = {dax}\n\t\tformatString: {fmt}\n"
    p.write_text(s.replace('table Metrics\n','table Metrics\n'+declarations),encoding='utf-8')
    (MODEL/'definition'/'model.tmdl').write_text('model Model\n\tculture: en-GB\n\tdefaultPowerBIDataSourceVersion: powerBI_V3\n\tsourceQueryCulture: en-GB\n\nannotation __PBI_TimeIntelligenceEnabled = 0\n\n'+'\n'.join('ref table '+n for n in ['Tourism','Labour','Income','Fish','Participation','Duration','UnitCost','Metrics'])+'\n',encoding='utf-8')
    shutil.copy2(ROOT/'codexversion.SemanticModel'/'definition'/'database.tmdl',MODEL/'definition'/'database.tmdl')
    shutil.copy2(ROOT/'codexversion.SemanticModel'/'definition.pbism',MODEL/'definition.pbism')
    save_json(OUT/'MonsunOfficial.pbip',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json','version':'1.0','artifacts':[{'report':{'path':'MonsunOfficial.Report'}}],'settings':{'enableAutoRecovery':True}})
    save_json(REPORT/'definition.pbir',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json','version':'4.0','datasetReference':{'byPath':{'path':'../MonsunOfficial.SemanticModel'}}})
    shutil.copy2(ROOT/'codexversion.Report'/'definition'/'version.json',REPORT/'definition'/'version.json')
    # Reuse registered resource names and a supported report structure.
    shutil.copytree(ROOT/'codexversion.Report'/'StaticResources',REPORT/'StaticResources',dirs_exist_ok=True)
    r=json.loads((ROOT/'codexversion.Report'/'definition'/'report.json').read_text());save_json(REPORT/'definition'/'report.json',r)
    theme_path=REPORT/'StaticResources'/'RegisteredResources'/'Monsun_Bridge3300894932160078.json'
    theme=json.loads(theme_path.read_text());theme['name']='Monsun Bridge — Official Evidence'
    theme['dataColors']=[TEAL,'#476E88','#87AFAE'];theme['background']=PAPER
    theme['visualStyles']['*']['*']['dropShadow']=[{'show':False}]
    theme['visualStyles']['page']['*']['background']=[{'color':{'solid':{'color':PAPER}},'transparency':0}]
    save_json(theme_path,theme)
    names=['P1 Tourism Clock','P2 Workforce Context','P3 Alternative Activity','P4 Programme Scenario']
    subtitles=['National tourism observations. No district forecast is implied.','Observed employment and household income. Tourism exposure is not identified.','Marine activity is observable. Vacancies and skill pathways require separate evidence.','Budget envelope from an observed workforce base and explicit assumptions.']
    for i,p in enumerate(PAGES):
        save_json(REPORT/'definition'/'pages'/p/'page.json',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json','name':p,'displayName':names[i],'displayOption':'FitToPage','width':1600,'height':900})
        text(p,f'header{i}',(32,24,1536,82),[f'MONSUN BRIDGE     {i+1:02d} / {names[i][3:]}',subtitles[i]],NAVY,'#FFFFFF',22)
        text(p,f'footer{i}',(32,856,1536,28),['Official-data edition • Source dates and units are retained • Desktop rendering remains to be verified'],None,MUTED,10)
    p=PAGES[0]
    card(p,'tourism1',(32,130,490,125),'Q4 visitors (million)','2025 Q4 domestic visitors · million')
    card(p,'tourism2',(554,130,490,125),'Q4 expenditure (RM billion)','2025 Q4 domestic expenditure · RM billion')
    card(p,'tourism3',(1076,130,492,125),'Published quarters','2025 quarterly observations')
    chart(p,'visitorchart',(32,282,752,330),'clusteredColumnChart','Tourism','quarter',['Visitors (million)'],'Domestic visitors · million · national')
    chart(p,'expenditurechart',(816,282,752,330),'lineChart','Tourism','quarter',['Expenditure (RM billion)'],'Domestic expenditure · RM billion · nominal')
    grid(p,'tourismledger',(32,640,1000,192),'Tourism',[('quarter','Quarter'),('visitors_million','Visitors (million)'),('expenditure_billion','Expenditure (RM billion)'),('source_url','DOSM publication')],'Published observations and source links')
    text(p,'tourismlimit',(1060,640,508,192),['What these figures support','Official national activity in 2025, at published rounding precision.','Four quarters cannot validate a seasonal forecast or explain island-level disruption.'], '#E7F1F0')
    p=PAGES[1]
    card(p,'labour1',(32,130,490,125),'Employed persons','Employed persons · selected districts · 2024')
    card(p,'labour2',(554,130,490,125),'Labour force persons','Labour force · selected districts · 2024')
    slicer(p,'labourselection',(1076,130,492,125),'Labour','district','District · employment views')
    chart(p,'employmentchart',(32,282,752,310),'clusteredBarChart','Labour','district',['Employed persons'],'Employment by district · persons · 2024')
    grid(p,'incometable',(816,282,752,310),'Income',[('district','District'),('date','Year'),('income_mean_rm','Mean (RM)'),('income_median_rm','Median (RM)')],'Monthly household income · all four districts · 2024')
    grid(p,'labourtable',(32,620,1000,212),'Labour',[('district','District'),('employed_thousands','Employed (thousands)'),('unemployment_rate_pct','Unemployment (%)'),('source_url','Source')],'Published employment statistics')
    text(p,'labourlimit',(1060,620,508,212),['Scope of the workforce base','Published employment is in thousands; headline cards convert to persons.','These totals include every industry. They are not tourism-worker counts.','Income table remains a four-district reference.'], '#E7F1F0')
    p=PAGES[2]
    card(p,'fish1',(32,130,490,125),'Marine landings (tonnes)','Marine fish landed · tonnes · 2023')
    card(p,'fish2',(554,130,490,125),'Monthly records','Observed state-month records · 2023')
    slicer(p,'fishstate',(1076,130,492,125),'Fish','state','Landing state')
    chart(p,'fishchart',(32,282,1000,360),'lineChart','Fish','date',['Marine landings (tonnes)'],'Monthly marine landings · tonnes · 2023',series='state')
    text(p,'skillstatus',(1060,282,508,360),['Skill Bridge · evidence needed','Occupational texts and training records are not loaded in this edition.','No similarity scores, vacancies or placement guarantees are shown.','Marine landings indicate activity, not aquaculture production or hiring demand.'], '#E7F1F0')
    grid(p,'fishledger',(32,670,1000,162),'Fish',[('state','State'),('date','Month'),('landings_mt','Tonnes'),('source_url','DOF source')],'Underlying monthly observations')
    text(p,'fishlimit',(1060,670,508,162),['Time alignment','Fish observations are from 2023; the tourism panel is 2025.','A contemporaneous CSI has not been calculated across these unmatched periods.'], '#FFF3DF')
    p=PAGES[3]
    for name,t,c,label,x in [('p_rate','Participation','rate','Planning share · defaults to 5%',32),('p_months','Duration','months','Training duration · defaults to 1 month',424),('p_cost','UnitCost','rm','RM per participant-month · default 1,100',816),('p_district','Labour','district','District · all sectors',1208)]:
        slicer(p,name,(x,130,360,115),t,c,label)
    for name,m,label,x in [('scenario1','Employed persons','Observed workforce base · persons',32),('scenario2','Scenario participants','Scenario participants · assumed share',424),('scenario3','Scenario total budget','Scenario budget · RM',816),('scenario4','Scenario cost per participant','Scenario cost per participant · RM',1208)]:
        card(p,name,(x,272,360,135),m,label)
    chart(p,'budgetchart',(32,435,1000,320),'clusteredColumnChart','Labour','district',['Scenario training budget','Scenario admin budget'],'Training and administration · modelled budget')
    text(p,'scenarioassumptions',(1060,435,508,320),['ASSUMPTIONS · NOT OFFICIAL BUDGETS','Participants = employed persons × chosen share.','Training = participants × months × monthly rate.','Administration = 10% of training cost.','This is a broad all-sector envelope, not verified tourism eligibility or avoided income loss.'], '#FFF3DF')
    text(p,'scenarioaction',(32,780,1536,52),['Before implementation: identify eligible tourism workers → verify employers and courses → confirm places → monitor outcomes'], '#E7F1F0',NAVY,13)
    save_json(REPORT/'definition'/'pages'/'pages.json',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json','pageOrder':PAGES,'activePageName':PAGES[0]})
    for page,items in visuals.items():
        for o in items:save_json(REPORT/'definition'/'pages'/page/'visuals'/o['name']/'visual.json',o)
    checks=[]
    for page,items in visuals.items():
        for i,a in enumerate(items):
            x=a['position'];assert 0<=x['x'] and 0<=x['y'] and x['x']+x['width']<=1600 and x['y']+x['height']<=900
            for b in items[i+1:]:
                y=b['position'];overlap=min(x['x']+x['width'],y['x']+y['width'])>max(x['x'],y['x']) and min(x['y']+x['height'],y['y']+y['height'])>max(x['y'],y['y'])
                assert not overlap,(a['name'],b['name'])
        checks.append({'page':page,'visuals':len(items),'bounds_and_overlap':'PASS'})
    observed_employed=sum(float(r['employed_thousands'])*1000 for r in labour)
    save_json(OUT/'BUILD_CHECKS.json',{'raw_hashes_verified':True,'official_script_executed':True,'embedded_rows':{'Labour':len(labour),'Income':len(income),'Fish':len(fish),'Tourism':len(tourism)},'employed_persons_total':observed_employed,'scenario_default_participants':round(observed_employed*.05),'scenario_default_budget_rm':round(observed_employed*.05)*1100*1.1,'checks':checks,'Power_BI_Desktop_tested':False})
    (OUT/'README.txt').write_text('MONSUN BRIDGE — OFFICIAL DATA EDITION\n\nOpen MonsunOfficial.pbip in a current Power BI Desktop supporting PBIP/PBIR.\nAll source rows are embedded in M tables; no CSV path, API, credentials or Python runtime is required to load this snapshot. Use Refresh if tables have not loaded.\n\nP1: 2025 national quarterly tourism observations, transcribed from cited DOSM release overviews at published precision. Not a forecast.\nP2: 2024 official district labour force and household income.\nP3: 2023 official monthly marine fish landings. Skills and capacities remain unavailable.\nP4: all-sector workforce budget scenario. Parameters and 10% admin coefficient are analytical assumptions.\n\nSlicers are page-specific. Income reference table always shows four districts.\nRaw-source hashes and download metadata: Data/SOURCE_MANIFEST.json.\nReproduction: scripts/build_official_data.py and scripts/build_embedded_official_project.py in the repository.\n\nThis is a separate factual-baseline edition; original research project is preserved. It is not the completed three-engine submission.\nPower BI Desktop cannot be executed here. Opening, visual rendering and offline interaction must be confirmed on Windows before Save As PBIX and PDF export. No final PBIX or PDF is claimed.\n',encoding='utf-8')
    print(json.dumps(json.loads((OUT/'BUILD_CHECKS.json').read_text()),indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('snapshot',type=Path)
    build(parser.parse_args().snapshot)
