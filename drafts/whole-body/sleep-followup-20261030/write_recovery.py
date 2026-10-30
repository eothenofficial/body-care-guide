"""Authored recovery and overlooked sleep-symptom entries, with reading limits."""
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
DATE='2026-10-30'
sources=[]

def source(sid,citation,url,support,limitations,reading_depth,funding,doi=None,updated=None):
    value=dict(id=sid,citation=citation,url=url,type='原始临床研究或正式指南' if doi else '机构指导',support=support,limitations=limitations,reading_depth=reading_depth,funding_disclosure=funding,content_checked_at=DATE)
    if doi:value.update(doi=doi,doi_url='https://doi.org/'+doi)
    if updated:value['reviewed_at']=updated
    sources.append(value)

source('SLR-S01','National Heart, Lung, and Blood Institute. Sleep deprivation and deficiency: healthy sleep habits [Internet]. 2022 Mar 24 [cited 2026 Oct 30]. Available from: https://www.nhlbi.nih.gov/health/sleep-deprivation/healthy-sleep-habits',
 'https://www.nhlbi.nih.gov/health/sleep-deprivation/healthy-sleep-habits',
 '规律睡眠框架、较早的短小睡及夜里难入睡者限制午睡；保护主睡眠并避免临睡强刺激。',
 '一般睡眠习惯，不是通宵之后固定补几小时即可恢复的试验；轮班安排需另核。',
 '直接阅读全部习惯及轮班正文，核实际更新日2022-03-24；没有把另一失眠页的5–6小时前运动规则与本页混用。',
 '美国公共卫生机构患者指导，未列本页专项资助。',updated='2022-03-24')
source('SLR-S02','Food and Drug Administration. Spilling the beans: how much caffeine is too much? [Internet]. [cited 2026 Oct 30]. Available from: https://www.fda.gov/consumers/consumer-updates/spilling-beans-how-much-caffeine-too-much',
 'https://www.fda.gov/consumers/consumer-updates/spilling-beans-how-much-caffeine-too-much',
 '核全天各来源与标签总咖啡因，个体反应、孕哺/用药限制，高剂量和高浓缩产品的风险。',
 '多数成人400mg参考不是缺觉后必须加到的目标，也不是个体安全保证；未给缺觉者专用加量方案。',
 '实读每日参考、各来源与份量、能量饮料、纯粉高浓缩、过量症状等相关全部正文；未发现可可靠采用的实际更新日，故不填。',
 '美国监管机构消费者安全指导，未列本页专项研究资助。')
source('SLR-S03','National Highway Traffic Safety Administration. Drowsy driving [Internet]. [cited 2026 Oct 30]. Available from: https://www.nhtsa.gov/risky-driving/drowsy-driving',
 'https://www.nhtsa.gov/risky-driving/drowsy-driving',
 '睡眠不足时先处理驾驶风险；咖啡或能量饮料仍可能掩盖微睡眠，短小睡作用暂时。',
 '不据杯数换算人人安全剂量，也不能凭自觉清醒批准驾驶；美国事故数字与急救地点不移植中国。',
 '实读安全驾驶与短期干预段及相关背景，未以事故率给个体风险；网页未明确实际更新日，不把统计年份当更新。',
 '美国道路安全监管机构指导，无产品资助在本页列示。')
source('SLR-S04','Yamazaki EM, Antler CA, Lasek CR, Goel N. Residual, differential neurobehavioral deficits linger after multiple recovery nights following chronic sleep restriction or acute total sleep deprivation. Sleep. 2021;44(4):zsaa224. doi:10.1093/sleep/zsaa224.',
 'https://academic.oup.com/sleep/article/44/4/zsaa224/5959861',
 '83名21–50岁健康成人在连续5晚限制睡眠或一次36h清醒后，给予4晚长睡眠机会，各测试恢复轨迹不同；慢性限制后的持续注意未完全恢复。',
 '不是一次普通晚睡的全部后果；没有持续正常睡眠对照，排除睡眠及情绪疾病、轮班等；不能据测试结果算需要补几小时、开车是否安全或宣称永久损伤。',
 '实读原刊完整摘要、方法的样本/随机安排/测试、主要结果概述、讨论限制及资助与利益声明；未重算个体数据。正式卷期2021，在线发表2020，未拼接年份。',
 'ONR为主要资助，另有NASA、NIH与临床转化中心资助；作者声明资助方未参与设计/分析/写作，未声明利益冲突。',doi='10.1093/sleep/zsaa224')
source('SLR-S05','Watson NF, Badr MS, Belenky G, Bliwise DL, Buxton OM, Buysse D, et al. Recommended amount of sleep for a healthy adult: a joint consensus statement of the American Academy of Sleep Medicine and Sleep Research Society. J Clin Sleep Med. 2015;11(6):591–592. doi:10.5664/jcsm.4758.',
 'https://www.aasm.org/resources/pdf/adultsleepdurationconsensus.pdf',
 '成人常规睡眠机会与恢复睡债时可能需要更长睡眠，不能把超过8小时一概当有害。',
 '主要针对18–60岁健康成人；不是缺觉一晚之后给每个人规定睡满多少小时，不能直接据此制定儿童或老年睡眠量。',
 '实读学会官网原始两页PDF的声明、方法、范围与全部资助/利益披露；题名、前六作者、卷期页和DOI逐项对照原PDF。',
 'AASM、SRS与CDC协作项目支持；若干成员有药企、航空、设备或其他咨询/研究支持，详见原PDF披露，未当作无产业关系。',doi='10.5664/jcsm.4758')
source('SLR-S06','National Health Service. Insomnia [Internet]. 2024 Mar 19 [cited 2026 Oct 30]. Available from: https://www.nhs.uk/conditions/insomnia/',
 'https://www.nhs.uk/conditions/insomnia/',
 '失眠自护维持规律起床、困倦不驾驶及持续影响日常就诊的入口。',
 '针对失眠的常规自护，不代表严重缺觉后必须为守钟硬撑高风险工作；其全面禁午睡或4小时内运动的简化条款不能推广所有人。',
 '实读症状、自护、药房及就诊全部正文；核2024-03-19复核与2027计划日期，不以计划当更新。',
 '英国公共医疗机构患者指导，未列本页产品资助。',updated='2024-03-19')
source('SLR-S07','Department of Veterans Affairs, Department of Defense. VA/DoD clinical practice guideline for the management of chronic insomnia disorder and obstructive sleep apnea. Version 3.0 [Internet]. 2025 Jan [cited 2026 Oct 30]. Available from: https://healthquality.va.gov/HEALTHQUALITY/guidelines/CD/insomnia/I-OSA-CPG_2025-Guideline_final_20250915.pdf',
 'https://healthquality.va.gov/HEALTHQUALITY/guidelines/CD/insomnia/I-OSA-CPG_2025-Guideline_final_20250915.pdf',
 '第10项建议不将苯海拉明用于成人慢性失眠常规药疗；相关段说明长期资料不足、镇静耐受及老年抗胆碱副作用。',
 '弱反对建议不等于苯海拉明在所有短期或过敏适应证均无效；美国军人/退伍军人相关成人临床指南不能作为中国产品准入或个人处方。',
 '实际读取182页PDF的范围、建议10和印刷页57–60相关讨论、CBT-I安全相关段；未声称通读182页。检索截至2024-03-31，PDF标明January2025，未把文件名日期当新证据年。',
 '政府临床实践指南，声明以系统证据审查和专家过程制定；未逐个审核所有纳入试验资助，未称完全无利益关系。')
source('SLR-S08','National Health Service. About diphenhydramine [Internet]. 2025 May 13 [cited 2026 Oct 30]. Available from: https://www.nhs.uk/medicines/diphenhydramine/about-diphenhydramine/',
 'https://www.nhs.uk/medicines/diphenhydramine/about-diphenhydramine/',
 '苯海拉明是可致困的抗组胺药；可能与感冒复方混合，嗜睡、头晕、驾驶与饮酒限制，久用可能失效或依赖。',
 '英国药物页面提及短期用法，不是任意中国复方感冒药或海外助眠片的适用标签；不复制其服药时间和儿童许可为中国用药方案。',
 '实读完整药物介绍与关键事实，核复核日2025-05-13，未以2028计划更新。',
 '英国公共医疗药品教育页面，未列本页产品资助。',updated='2025-05-13')
source('SLR-S09','National Health Service. Who can and cannot take diphenhydramine [Internet]. 2025 May 13 [cited 2026 Oct 30]. Available from: https://www.nhs.uk/medicines/diphenhydramine/who-can-and-cannot-take-diphenhydramine/',
 'https://www.nhs.uk/medicines/diphenhydramine/who-can-and-cannot-take-diphenhydramine/',
 '儿童不得自行用于催眠，闭角型青光眼、排尿困难、部分呼吸及肝肾问题、老年混乱等需核适用性。',
 '列举的是苯海拉明具体药物注意，并不表示所有抗过敏药有完全相同风险；不据外国年龄阈值批准中国儿童助眠。',
 '实读全页who can/cannot和儿童警示并核真实复核日期。',
 '英国公共医疗机构药品指导，未列本页专项资助。',updated='2025-05-13')
source('SLR-S10','National Health Service. Restless legs syndrome [Internet]. 2025 Sep 22 [cited 2026 Oct 30]. Available from: https://www.nhs.uk/conditions/restless-legs-syndrome/',
 'https://www.nhs.uk/conditions/restless-legs-syndrome/',
 '夜间休息时强烈移动双腿冲动及不适的识别、可类似于抽筋或神经病；影响睡眠需评估，轻走/伸展等可暂缓，需查药物及相关病因。',
 '症状线索不能确诊；该页多种药物列举不等于推荐读者自购，也不能把夜间腿不舒服都当缺钙或缺铁。',
 '实读症状、自护、就诊、病因与治疗段，核真实复核2025-09-22；不采用其所有药物列举做自用方案。',
 '英国公共医疗机构患者指导，无专项产品资助在本页列示。',updated='2025-09-22')
source('SLR-S11','Winkelman JW, Berkowski JA, DelRosso LM, Koo BB, Scharf MT, Sharon D, et al. Treatment of restless legs syndrome and periodic limb movement disorder: an American Academy of Sleep Medicine clinical practice guideline. J Clin Sleep Med. 2025;21(1):137–152. doi:10.5664/jcsm.11390.',
 'https://link.springer.com/article/10.5664/jcsm.11390',
 'Good practice statements支持临床显著RLS检查铁蛋白和转铁蛋白饱和度、先处理咖啡因/酒精、加重药物及未治睡眠呼吸暂停。',
 '良好实践声明含专家共识，不能当所有腿不舒服者补铁的试验证据；补铁阈值及药物方案由临床判断，本书不据该阈值自开药。',
 '实读原刊可公开预览的完整摘要、good practice statements、推荐列表及作者/卷期页/DOI；订阅全文未获，不声称全文已读。利益信息另核同学会官方发布页。',
 '同学会官方发布页披露Winkelman等与药企/设备企业咨询、研究或委员会关系，Falck-Ytter为AASM付费顾问；原刊全文利益段未完整读到。',doi='10.5664/jcsm.11390')
source('SLR-S12','American Academy of Sleep Medicine. New guideline provides treatment recommendations for restless legs syndrome [Internet]. 2024 Nov 13 [cited 2026 Oct 30]. Available from: https://aasm.org/new-guideline-provides-treatment-recommendations-for-restless-legs-syndrome/',
 'https://aasm.org/new-guideline-provides-treatment-recommendations-for-restless-legs-syndrome/',
 '学会对自身RLS指南的正式发布，说明症状线索、铁评估、加重因素及资金/利益关系。',
 '学会发布说明不是单独临床试验；临床建议另对照原刊公开推荐，不只凭新闻稿给治疗剂量。',
 '实读文章全部主体、利益披露与发布日期；2024年发布对应2025正式卷期，站点技术修改时间不冒称医学更新。',
 '原页披露Winkelman有Luitpold委员会及多家企业咨询/研究关系、Walters研究资助，Falck-Ytter为AASM付费顾问。',updated='2024-11-13')
source('SLR-S13','National Health Service. Taking or using diphenhydramine with other medicines and herbal supplements [Internet]. 2025 May 13 [cited 2026 Oct 30]. Available from: https://www.nhs.uk/medicines/diphenhydramine/taking-or-using-diphenhydramine-with-other-medicines-and-herbal-supplements/',
 'https://www.nhs.uk/medicines/diphenhydramine/taking-or-using-diphenhydramine-with-other-medicines-and-herbal-supplements/',
 '核对复方药是否已含止痛成分，避免重复；其他抗组胺药、镇静催眠或可致困药物及部分草药补剂可能叠加风险。',
 '苯海拉明特定交互指导不是所有成分的完整配伍表，不能由此断言所有复方药或同服药都被禁用。',
 '直接阅读全页药物交互、复方止痛成分、草药补剂及药物安全段，核真实复核日。',
 '英国公共医疗药品教育网页，未列本页产品资助。',updated='2025-05-13')

entries=[]
def entry(eid,title,summary,plain,benefit,evidence,refs,scope,notes=''):
    assert 100<=len(summary)<=180,(eid,len(summary))
    entries.append(dict(id=eid,title=title,summary=summary,
        fields=dict(cost='',plain=plain,benefit=benefit,evidence=evidence,sources='；'.join('[@'+r+']' for r in refs),notes=notes),
        audience=dict(age_groups=['adult','older'],sexes=['all'],scope_note=scope,safety_pin=False),
        clinical_review_status='not_clinically_reviewed',content_checked_at=DATE))

entry('sleep-012','前晚没睡好，次日先减危险任务，再安排短休息，别用浓咖啡硬顶整天',
 '少睡一晚后，先看是否困得打盹、反应迟钝，再决定通勤和工作安排；不要用咖啡后的清醒感证明可以安全开车。白天可按需要早些短睡，避免睡到傍晚，晚上留足睡眠机会。咖啡因不能还睡眠债，别叠加浓缩饮料和训练前补剂；训练降级与持续失眠另有对应条目。',
 '**先取消或改派需要持续警觉的危险任务。** 明显打盹、反应慢时，改乘公共交通、请清醒的人驾驶，别靠开窗、音乐或高浓度咖啡因证明自己还能开。通宵后先找安全休息地点，而不是为守作息强撑驾驶或操作机器，见[困倦驾驶](#/entry/sleep-001)。[@SLR-S03]\n\n白天可按需要安排较早的短小睡，例如先试约20分钟；醒后等迟钝过去再做事。若本就反复难入睡，长时间或临近晚间补觉可能让下一夜更难睡，宜缩短、提前或与治疗人员调整。尽量保留平日的起床与主睡眠框架，今晚留足机会，不靠从下午睡到傍晚补偿，也不机械限制恢复睡眠只能8小时。年轻成人或恢复睡债者可能需要更长睡眠，但没有人人相同的补觉小时数。[@SLR-S01][@SLR-S05][@SLR-S06]\n\n习惯喝咖啡的成人，不必因为昨晚少睡就自动禁掉平常用量；想提神先核每份毫克数、全天总量和个人反应，别把浓缩能量饮料、咖啡和训练前补剂叠起来。400mg是多数成人的每日参考，不是缺觉后的加量目标；心悸、手抖或更焦虑就别继续补。靠近今晚睡觉的咖啡因要提前收尾，见[全天咖啡因](#/entry/energy-001)与[睡前咖啡酒精](#/entry/sleep-005)。[@SLR-S02]\n\n恢复睡眠有用，但“感觉好些”与注意力完全恢复不是同一件事；一次补觉不能保证抹平反复缺觉的影响。健身是否降级见[少睡后的训练选择](#/entry/sleep-013)；反复发生或影响生活就记录并[评估失眠](#/entry/sleep-002)，不等满三个月才求助。[@SLR-S04][@SLR-S06]',
 '减少缺觉后继续高风险作业，以及白天刺激、晚上更难睡的循环；保留恢复睡眠的机会。',
 'C，安全与作息安排以机构指导、成人共识为主；恢复并非各项功能同步的判断有B级实验资料，不据此规定个人恢复时长。',
 ['SLR-S03','SLR-S01','SLR-S05','SLR-S06','SLR-S02','SLR-S04'],
 '主要供规律夜睡的成人与老年读者；18–60岁共识不充当老年固定睡眠量，轮班、孕哺、疾病及用药另核个人限制。')
entry('sleep-015','别拿感冒药或抗过敏药长期催眠，先核成分和第二天的嗜睡风险',
 '有些感冒药、抗过敏药和海外助眠片会让人犯困，因为含有可致镇静的抗组胺成分；犯困不代表适合长期治疗失眠。不要为了睡觉叠吃复方药或配酒，也别因前晚没睡好就自行加量。老年人、有青光眼或排尿困难者更要核风险；用药后仍困，次日不要开车。',
 '**先看有效成分，别只看包装上的“夜用”或“助眠”。** 苯海拉明等镇静性抗组胺药原本可用于某些过敏症状，也可能出现在复方感冒药、夜间止痛药或助眠片里。不能为获得困意顺带吃入不需要的退热、止痛或其他复方成分，也不要叠多款含相同成分的产品。[@SLR-S08][@SLR-S13]\n\n这类药可能让人想睡，却不等于适合长期处理失眠；久用可能镇静作用变弱。成人慢性失眠指南对苯海拉明作出不建议常规使用的弱推荐，不能把它说成所有短期使用都无效，也不能据此自行停掉正在治疗其他疾病的药。反复睡不好先走[失眠评估与CBT-I](#/entry/sleep-002)。[@SLR-S07][@SLR-S08]\n\n别配酒，别自行和其他镇静药叠加；服后头晕、站不稳或次日仍困，就不驾驶。老年人，以及闭角型青光眼、排尿困难、肝肾或呼吸问题者，带药名和全部用药清单让医生或药师核是否合适。儿童不以成人催眠方案处理；这里也不给孕哺或任何人的自购剂量。[@SLR-S08][@SLR-S09][@SLR-S13]',
 '避免为追困意重复摄药、增加不需要的成分，以及忽略次日警觉与跌倒风险。',
 'C，药品安全与处置建议；苯海拉明用于慢性失眠的收益资料有限且长期资料不足，弱反对不等于已证明所有短期用途均无效。',
 ['SLR-S08','SLR-S07','SLR-S09','SLR-S13'],
 '成人及老年用药选择；外国页面的销售属性、年龄和用法不能当作中国产品说明。')
entry('sleep-016','夜里一躺下就想动腿、动了暂缓，别只补钙，记录后评估不宁腿',
 '如果晚间坐着或躺下时，腿里发痒、蚁走般不舒服，忍不住想动，起来走走又暂时缓解，要考虑不宁腿这类睡眠相关问题。它不等于普通抽筋，也不能直接判断缺钙或缺铁。记录时段、诱因和用药，影响睡眠就评估；补铁、按摩仪或助眠片都不能代替查原因。',
 '**把“休息时更明显、夜间更重、动后暂缓”的规律记下来，影响睡眠就到全科、神经或睡眠门诊评估。** 不宁腿综合征（RLS）是一种常在静止时出现强烈动腿冲动、伴不适的睡眠相关运动问题；普通抽筋、周围神经病等也可能相似，不能凭一次腿痒确诊。[@SLR-S10][@SLR-S12]\n\n发作时可轻走、轻柔伸展或按摩，看看能否暂缓；这不证明病因已经解决。就诊带上咖啡因、酒精及药物清单，特别是感冒、过敏或精神科用药；某些成分可能加重症状，不能未经评估就自行停处方。[@SLR-S10][@SLR-S11]\n\n医生会按情况检查铁储备，包括铁蛋白及转铁蛋白饱和度，而不是凭“缺钙”印象买补剂。即使考虑铁治疗，也需结合结果、基础病和孕哺状态选方案；不自行按网帖化验阈值吃铁或打铁针，不用镁片、钙片或腿部按摩仪替代评估。检查是否有相关疾病和加重药物，会改变后续选择。[@SLR-S11]',
 '为一种常被误当抽筋、焦虑或单纯缺营养的困扰提供检查入口，避免长期只换助眠用品。',
 'C，症状识别与良好实践指导；检查铁状态不等于人人需要补铁，具体药物疗效没有据此泛化。',
 ['SLR-S10','SLR-S12','SLR-S11'],
 '成人及老年症状入口；孕期可见但治疗需单独核安全性，儿童不直接套成人补铁或用药方案。')

HERE.mkdir(parents=True,exist_ok=True)
for name,value in [('recovery-entries',entries),('recovery-sources',sources),('recovery-audit',dict(date=DATE,entry_ids=[e['id'] for e in entries],scope='缺觉次日安排、镇静抗组胺药与不宁腿线索',clinical_review_status='not_clinically_reviewed',limitations=['未逐个核国内现售药品标签，不提供个人剂量。','原刊RLS完整摘要及推荐可读、全文订阅部分未读；未规避访问限制。','恢复睡眠实验健康成人21–50岁，既不保证一次补觉全恢复，也不宣称普通晚睡留下永久伤害。']))]:
    (HERE/(name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print({e['id']:len(e['summary']) for e in entries})
