"""Dinner and sleep: scoped primary evidence, no universal fasting cutoff."""
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
HERE.mkdir(parents=True,exist_ok=True)

entry={
 'id':'sleep-010','chapter_id':'sleep','unit_id':'sleep-u2','ordinal':10,
 'title':'夜宵后睡不踏实，先把大餐前移；饿了可少量加餐，反酸者另留间隔',
 'summary':'睡前吃撑与饿着睡都不必硬扛。若夜宵后总睡不好，先把大份正餐前移，记录吃什么、几点吃及夜间反酸；临睡只是饿了，可选少量自己能耐受的食物。反酸烧心者更要拉开吃饭与躺下的间隔，不能把两三小时当人人统一的禁食线；正在按降糖方案加餐的人也别自行删餐。',
 'fields':{
  'cost':'',
  'plain':'**如果夜宵后总睡不踏实，先改临睡前的大餐，而不是一口不吃、饿着等天亮。** 把大份正餐提前，给睡觉留出几小时；若只是饥饿，少量自己吃后不反酸的普通食物可以考虑，不必额外买“助眠零食”。连续记录晚餐和夜宵的分量、时点、反酸与夜醒，观察调整后是否好转。这里没有人人通用的“晚上八点后禁食”。[@SLM-S01]\n\n如果躺下后胸口烧灼、酸水上涌，要同时考虑胃内容物回到食管的反流。ACG对反流人群建议避免睡前2–3小时内进餐，属于低确定性、有条件的建议；一般睡眠指导则侧重大餐，不等于要求每个健康人禁掉所有小点心。优先减少过饱和确实诱发自己的食物，油辣食品不必照别人的忌口单全禁。反复发作或吞咽卡住，按[反酸烧心的处理与检查](#/entry/abdomen-006)进一步评估；新发明显胸痛不能只当胃病。[@SLM-S02]\n\n夜宵影响不能全归给“消化慢”：进食量、距入睡的间隔、反流与个人反应需要一起看。小型试验结果并不一致，既不能由一次吃完困了认定睡得更好，也不能说所有夜宵都会破坏整夜睡眠。先调整最有可能触发自己的大餐和时间，持续失眠仍走[失眠评估](#/entry/sleep-002)。[@SLM-S03][@SLM-S04]\n\n用胰岛素或会引起低血糖的降糖药时，不为遵守“睡前禁食”自行删掉原计划中的加餐、改药或长时间挨饿；夜里出汗、噩梦、醒后异常不适可核血糖并按既定低血糖方案处理，见[节食不适与低血糖](#/entry/nutrition-001)。[@SLM-S05]',
  'benefit':'减少可能由过饱、临睡进餐及反流带来的夜间不适，同时避免把必要加餐误删成一条养生禁令。',
  'evidence':'B，睡前进餐的直接睡眠试验规模小、结局不一致：2026年13名健康年轻女性、4日交叉试验中，睡前1小时正餐相比5小时更影响睡眠连续性；2021年20名健康成人的单晚交叉试验事后分析，整夜常规分期未见明显不利差异。不能推出统一最佳间隔，也不将后一结果当作严格等效。[@SLM-S03][@SLM-S04] 大餐/小点心的日常安排与低血糖安全为C；ACG反流2–3小时建议为低确定性、有条件，不能直接换算成强推荐。[@SLM-S01][@SLM-S02][@SLM-S05]',
  'sources':'NHLBI睡眠习惯；ACG反流指南；2026与2021晚餐时点交叉研究；NIDDK低血糖；NHS孕期反酸。[@SLM-S01][@SLM-S02][@SLM-S03][@SLM-S04][@SLM-S05][@SLM-S06]',
  'notes':'孕期反酸可先调整为少量多餐、避免吃完就躺；生活调整无效时联系产科或全科。需要药物时说明已孕，部分抗酸药并不适用，不直接照搬非孕期方案。[@SLM-S06]'
 },
 'audience':{'age_groups':['adult','older'],'sexes':['all'],'scope_note':'成年人和老年人的晚餐、夜宵与睡眠选择；孕期反酸及糖尿病用药按正文分支，非个人饮食或用药处方。','safety_pin':False},
 'clinical_review_status':'not_clinically_reviewed','content_checked_at':'2026-10-30'
}

def source(id,citation,url,type,support,limitations,reading_depth,funding,**extra):
 return dict(id=id,citation=citation,url=url,type=type,support=support,limitations=limitations,reading_depth=reading_depth,funding_disclosure=funding,content_checked_at='2026-10-30',**extra)

sources=[
source('SLM-S01',
 'National Heart, Lung, and Blood Institute. Sleep deprivation and deficiency: healthy sleep habits [Internet]. 2022 Mar 24 [cited 2026 Oct 30]. Available from: https://www.nhlbi.nih.gov/health/sleep-deprivation/healthy-sleep-habits',
 'https://www.nhlbi.nih.gov/health/sleep-deprivation/healthy-sleep-habits','政府机构患者教育',
 '睡前几小时避免大份或油腻大餐；轻点心可以；与睡眠机会和规律安排一起考虑。',
 '常规健康行为指导，不是确定最佳禁食间隔的随机试验；不能证明某一种助眠零食有效，也不把几小时写成人人相同钟点。',
 '直接读取healthy sleep habits与shift workers全部相关正文，核实际更新2022-03-24；并与最新小型原始研究和反流指南交核，不把年份旧视作自动失效。',
 '官方公共教育页；未见单页研究资助声明，不视为独立临床试验。',reviewed_at='2022-03-24'),
source('SLM-S02',
 'Katz PO, Dunbar KB, Schnoll-Sussman FH, Greer KB, Yadlapati R, Spechler SJ. ACG Clinical Guideline for the Diagnosis and Management of Gastroesophageal Reflux Disease. Am J Gastroenterol. 2022;117(1):27-56. doi:10.14309/ajg.0000000000001538.',
 'https://pmc.ncbi.nlm.nih.gov/articles/PMC8754510/','专业学会临床指南',
 '反流人群避免睡前2–3小时进餐为低确定性、有条件建议；按自身触发食物调整，吞咽困难及其他警示症状进一步检查。',
 '针对GERD而非所有健康人的睡眠；饮食与生活方式研究有限、异质，不能由反流建议推每个健康人的统一禁食线或所有油辣食物都须戒；不提供抑酸药个体处方。',
 '直接核PubMed正式题名、六位作者、卷期页和DOI；PMC实读推荐表、Medical Management建议、Diet and Lifestyle Changes及Footnotes利益披露，不声称通读全部药物/手术章节。',
 'Footnotes列多作者与Phathom、Medtronic、Ironwood、Diversatek、Takeda等顾问/研究或权益关系；未将学会名头当作零利益冲突保证。',doi='10.14309/ajg.0000000000001538',doi_url='https://doi.org/10.14309/ajg.0000000000001538'),
source('SLM-S03',
 'Enomoto M, Kitamura S, Kunieda T, Eto T. Effects of later dinner timing on subsequent metabolic function and nocturnal sleep in healthy young women. J Physiol Anthropol. 2026;45(1):12. doi:10.1186/s40101-026-00430-0.',
 'https://pmc.ncbi.nlm.nih.gov/articles/PMC13196191/','小样本随机交叉原始研究',
 '13名健康年轻女性，睡前1小时与5小时约700千卡正餐、各4日干预；家庭脑电显示晚餐较近时睡眠连续性指标较差，而入睡潜伏期未显著改变。',
 '样本小、仅健康年轻女性、短期且未控制月经周期；不能外推全部男性、老年、孕妇、病人或小点心；未直接测机制，不能由血糖变化证明消化过程导致失眠，也不将4日观察写成长期疾病风险。摘要与表格睡眠效率p值稍有出入，不用该精确数值承载建议。',
 'PubMed核完整四位作者、年卷期文章号与DOI；PMC实读摘要、Participants/Protocol/Dietary control、睡眠指标与表2、Discussion限制、Funding/Competing interests；未重析原始个体数据或读取补充DOCX。',
 '资助来自Yazuya Co., Ltd.旗下Institute for Food and Health Science；作者申报无竞争性利益，两项分别保留。',doi='10.1186/s40101-026-00430-0',doi_url='https://doi.org/10.1186/s40101-026-00430-0'),
source('SLM-S04',
 'Duan D, Gu C, Polotsky VY, Jun JC, Pham LV. Effects of Dinner Timing on Sleep Stage Distribution and EEG Power Spectrum in Healthy Volunteers. Nat Sci Sleep. 2021;13:601-612. doi:10.2147/NSS.S301113.',
 'https://pmc.ncbi.nlm.nih.gov/articles/PMC8131073/','随机交叉试验的事后睡眠分析',
 '20名18–30岁健康非肥胖成人，实验室固定睡眠机会；18:00正餐、22:00小点心与相反时序作交叉比较，正餐和点心约占全天能量35%及10%。两组均在睡前1小时进食；整夜常规分期相近，脑电频谱有前后半夜不同变化。',
 '单晚、事后分析、样本小且排除睡眠及代谢疾病；是正餐与小点心交换时点，不是睡前吃东西与完全禁食的比较。未见显著整体不利差异不等于证明严格等效、临睡大餐人人安全或可以治疗失眠；不能把论文对潜在治疗的推测变推荐。',
 '直接核PubMed题录五作者、年卷页与DOI；PMC读完整摘要、Participants and Study Protocol、主要睡眠结果、Discussion结论和Funding/Disclosure；未重算频谱模型。',
 'NIH、AHA博士后奖、American Thoracic Society unrestricted grant等资助，原文声明本工作无利益冲突；这不是全品类商业安全保证。',doi='10.2147/NSS.S301113',doi_url='https://doi.org/10.2147/NSS.S301113'),
source('SLM-S05',
 'National Institute of Diabetes and Digestive and Kidney Diseases. Low blood glucose (hypoglycemia) [Internet]. 2021 Jul [cited 2026 Oct 30]. Available from: https://www.niddk.nih.gov/health-information/diabetes/overview/preventing-problems/low-blood-glucose-hypoglycemia',
 'https://www.niddk.nih.gov/health-information/diabetes/overview/preventing-problems/low-blood-glucose-hypoglycemia','政府机构患者教育',
 '胰岛素及部分促胰岛素分泌药与低血糖风险；漏餐、延迟进餐和禁食可增加风险；夜间低血糖线索与按预定监测/饮食/治疗计划处理。',
 '未把普通饥饿或所有夜醒诊断为低血糖，也不将旧网页中的固定阈值、克数等改成统一个人处方；此条不新增夜间加餐和药物调整方案。',
 '实读夜间低血糖、药物/漏餐/禁食原因、预防及处理相关完整段，核实际Last Reviewed July 2021；未声称所引全部试验均读全文。',
 '机构官方教育；未见此网页独立专项研究资助声明。',reviewed_at='2021-07'),
source('SLM-S06',
 'National Health Service. Indigestion and heartburn in pregnancy [Internet]. 2023 Nov 14 [cited 2026 Oct 30]. Available from: https://www.nhs.uk/pregnancy/common-symptoms/indigestion-and-heartburn/',
 'https://www.nhs.uk/pregnancy/common-symptoms/indigestion-and-heartburn/','公共医疗机构患者教育',
 '孕期反酸可少量多餐、调整晚餐与躺下间隔；调整无效或出现吞咽异常等需联系产科/全科，药师须知已孕，部分抗酸药不适用。',
 '只支持孕期反酸分支，不证明所有孕妇需要睡前禁食；不将英国供药方式或完整药单移植中国，也不建议自行停处方。',
 '读取症状、生活调整、when to get help、用药和原因相关全文，核真实复核日2023-11-14；2026-11-14仅预定复审日。',
 'NHS公共患者教育，非产品赞助试验；未见单页独立专项资助声明。',reviewed_at='2023-11-14')
]

for name,value in [('meals-entries',[entry]),('meals-sources',sources)]:
 (HERE/(name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

audit=dict(checked_at='2026-10-30',entry_ids=['sleep-010'],sources=len(sources),summary_length=len(entry['summary']),
 clinical_review_status='not_clinically_reviewed',
 coverage=['夜宵/晚餐分量与时点','大餐与小点心','反流的具体分支与2–3小时间隔的证据限制','小型试验矛盾和不外推','降糖用药的漏餐风险','孕期反酸及用药边界'],
 nonduplication='常规饮食/减脂留在nutrition；反流完整药物和检查留在abdomen-006。此条只回答晚餐、夜宵与睡眠的决定，不重复药物清单。',
 claim_source_map=[
  {'claim':'大餐前移而非人人禁止小点心','sources':['SLM-S01']},
  {'claim':'反流人群2–3小时为低确定性、有条件；按触发调整','sources':['SLM-S02']},
  {'claim':'直接睡眠试验不一致、不能由机制或血糖变化给统一禁食线','sources':['SLM-S03','SLM-S04']},
  {'claim':'用胰岛素/部分降糖药不自行删计划加餐','sources':['SLM-S05']},
  {'claim':'孕期反酸与药物选择另核','sources':['SLM-S06']}],
 rejected_inferences=['夜宵一律损害睡眠','八点后绝对禁食','肠道消化使脑缺血所以失眠','只有女性研究所以一般睡眠习惯标female-only','血糖短期变化证明慢病风险','统计不显著=已证严格等效','2026小试验覆盖旧研究且无需保留不一致'],
 actual_reading_limits=['SOP与用户原始style SOP已读取，未改写原文件。','两篇论文实际读取范围在source.reading_depth中逐项列出；未核原始个体数据或补充DOCX。','ACG读有关推荐/生活方式与披露，不称完整长篇全文每节皆已审。'],
 potential_extra_topic_not_added='夜间反复必须起床吃东西、无意识睡食可另作睡眠或进食障碍评估选题；当前没有完成相应专病研究，不先添加诊断结论。',
 blocking_unresolved=[],disposition='ready_for_independent_ai_editorial_review')
audit['file_sha256']={name:hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in ['meals-entries.json','meals-sources.json']}
(HERE/'meals-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'entries':1,'sources':len(sources),'summary_length':len(entry['summary']),'paths':['meals-entries.json','meals-sources.json','meals-audit.json']},ensure_ascii=False))
