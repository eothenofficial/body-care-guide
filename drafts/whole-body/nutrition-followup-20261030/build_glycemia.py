"""Build the two independently researched glycaemia drafts; no shared files changed."""
import json
import re
from pathlib import Path

OUT = Path(__file__).resolve().parent
CHECKED = '2026-10-30'

def source(sid, citation, url, kind, support, limitations, reading, funding, **dates):
    return dict(id=sid, citation=citation, url=url, type=kind, support=support,
                limitations=limitations, reading_depth=reading,
                content_checked_at=CHECKED, funding_disclosure=funding, **dates)

SOURCES = [
    source('NFG-S01',
        'World Health Organization. Healthy diet [Internet]. 2026 Jan 26 [cited 2026 Oct 30]. Available from: https://www.who.int/news-room/fact-sheets/detail/healthy-diet',
        'https://www.who.int/news-room/fact-sheets/detail/healthy-diet',
        '世界卫生组织膳食指导',
        '碳水来源优先全谷物、蔬菜、水果和豆类；限制游离糖，果汁即使未加糖仍含游离糖；健康膳食强调营养充足、多样和适量。',
        '机构建议并非每一种食品组合均经过长期随机试验；不能把游离糖限制理解成禁止完整水果或所有主食。',
        '已读取2026-01-26页面的健康膳食原则、碳水、果蔬、游离糖相关正文及日期；未通读其链接的2023碳水指南全文。',
        '此事实表未单列专项资金及作者利益关系；未逐项审计底层指南证据。', published_at='2026-01-26'),
    source('NFG-S02',
        '中国疾病预防控制中心. 患有糖尿病 这样来食养 [Internet]. 2023 Nov 16 [cited 2026 Oct 30]. Available from: https://www.chinacdc.cn/jkkp/yyjk/jbyy/202408/t20240825_295602.html',
        'https://www.chinacdc.cn/jkkp/yyjk/jbyy/202408/t20240825_295602.html',
        '中国疾控中心官方食养科普',
        '糖尿病饮食需兼顾主食定量、全谷杂豆、食物多样、规律进餐和活动；低GI并不替代份量与整体营养。',
        '主要面向已患糖尿病者；不将其中主食比例、运动时长或食药物质建议照抄为所有健康人的个人处方。',
        '已实读网页八项食养原则中与主食、能量、规律进餐和活动有关的正文；网页标注日期为2023-11-16，URL中的202408不是医学更新日期。国家卫健委原指南PDF未成功读取，不声称通读。',
        '官方科普页未单列专项资助与商业利益；未据此评估文中所有食药物质功效。', published_at='2023-11-16'),
    source('NFG-S03',
        'Buffey AJ, Herring MP, Langley CK, Donnelly AE, Carson BP. The acute effects of interrupting prolonged sitting time in adults with standing and light-intensity walking on biomarkers of cardiometabolic health in adults: a systematic review and meta-analysis. Sports Med. 2022;52(8):1765-1787. doi:10.1007/s40279-022-01649-4.',
        'https://link.springer.com/article/10.1007/s40279-022-01649-4',
        '系统综述与荟萃分析',
        '七项成人单日交叉试验提示，用短暂轻走打断久坐可改善急性餐后葡萄糖和胰岛素指标；轻走通常优于仅站立。',
        '研究多为超重/肥胖成人、模拟久坐环境、短时指标；方案不一，不能据此规定人人餐后走固定分钟数，或推导长期减少糖尿病、心血管事件。',
        '已取得出版商开放全文，核读摘要、纳入设计、相关结果、实践意义、局限及资助/利益披露；未重算模型或逐读七项底层试验。核五作者、卷期页和DOI。',
        '研究资助为University of Limerick Health Research Institute Studentship；开放获取由IReL Consortium支持。作者声明无相关利益冲突；不因此排除方法偏倚。',
        published_at='2022-02-11', doi='10.1007/s40279-022-01649-4'),
    source('NFG-S04',
        'Okami Y, Tsunoda H, Watanabe J, Kataoka Y. Efficacy of a meal sequence in patients with type 2 diabetes: a systematic review and meta-analysis. BMJ Open Diabetes Res Care. 2022;10(1):e002534. doi:10.1136/bmjdrc-2021-002534.',
        'https://pmc.ncbi.nlm.nih.gov/articles/PMC8883221/',
        '随机试验系统综述与荟萃分析',
        '八项随机试验230名2型糖尿病患者的合并结果，未确立碳水后吃相较标准饮食建议的额外长期获益；HbA1c差异置信区间跨过零。',
        '总体证据低或很低确定性，样本小，检索截至2020年；不能断言所有进食顺序都无效，更不能直接代表健康人。短时曲线变化不同于长期并发症获益。',
        '已读取PMC开放全文的完整摘要、方法、结果及局限和资助披露，核四作者、期刊题录和DOI；未重算原始数据。',
        '作者声明未获得特定项目资助、无竞争性利益；仍保留小样本及偏倚局限。',
        published_at='2022-02-24', doi='10.1136/bmjdrc-2021-002534'),
    source('NFG-S05',
        'National Institute of Diabetes and Digestive and Kidney Diseases. Low blood glucose (hypoglycemia) [Internet]. 2021 Jul [cited 2026 Oct 30]. Available from: https://www.niddk.nih.gov/health-information/diabetes/overview/preventing-problems/low-blood-glucose-hypoglycemia',
        'https://www.niddk.nih.gov/health-information/diabetes/overview/preventing-problems/low-blood-glucose-hypoglycemia',
        'NIH所属研究机构患者指导',
        '胰岛素、磺脲类和格列奈类使用者，少吃碳水、漏餐以及增加活动可能低血糖；活动后仍可发生，需预先安排监测、食物和用药。',
        '2021审阅页用于稳定的药物安全原则；不按此页给个人设统一治疗阈值或改药剂量，也不把一般心慌确诊为低血糖。',
        '已直接读取症状、病因、活动风险、预防及处理相关正文，核页尾Last Reviewed July 2021；未将访问年份写成更新。',
        '机构患者页未单列专项资助和商业利益。', published_at='2021-07'),
    source('NFG-S06',
        '国家卫生健康委等. 关于印发健康中国行动——糖尿病防治行动实施方案（2024—2030年）的通知：国卫医急发〔2024〕23号 [Internet]. 2024 Jul 15 [cited 2026 Oct 30]. 新疆维吾尔自治区卫生健康委官网转载，2024 Sep 6. Available from: https://wjw.xinjiang.gov.cn/hfpc/wsyj1/202409/8d142ff4718a4884a136b549dd1a99cf.shtml',
        'https://wjw.xinjiang.gov.cn/hfpc/wsyj1/202409/8d142ff4718a4884a136b549dd1a99cf.shtml',
        '中国国家政策原文的省级卫健委正式转载',
        '第（九）项：提倡40岁及以上者每年至少一次空腹血糖；高危者每年至少一次；糖尿病前期每半年检测一次空腹或餐后2小时血糖，并每年做风险评估。',
        '为人群筛查政策，不是所有人的确诊标准或个体用药目标；高危与已确诊者还需结合风险和症状安排。原发文日和转载日分别记录。',
        '已直接读取新疆卫健委正式转载正文、14部门落款、2024-07-15发文日和第四部分第（八）至（十）项。国家卫健委原HTML访问未成功，未假称该地址全文可读。',
        '政策文件，不涉及一项产品试验的资助判断；未据其机构权威推断任何商业产品有效。',
        published_at='2024-07-15', reposted_at='2024-09-06'),
    source('NFG-S07',
        'National Institute of Diabetes and Digestive and Kidney Diseases. Diabetes tests & diagnosis [Internet]. 2022 Jul [cited 2026 Oct 30]. Available from: https://www.niddk.nih.gov/health-information/diabetes/overview/tests-diagnosis',
        'https://www.niddk.nih.gov/health-information/diabetes/overview/tests-diagnosis',
        'NIH所属研究机构诊断科普',
        '糖尿病和糖尿病前期用规范血液检查诊断；不能靠购买的血糖仪自诊。空腹血糖反映检测时点，HbA1c反映约三个月平均水平，贫血、血红蛋白变异等可影响解释。',
        '美国页面的35岁筛查年龄、复查周期和诊断阈值未搬作中国规则；本条中国筛查频次单独以NFG-S06支持。',
        '已实读诊断用途、空腹血糖、A1C、结果解释与审阅日期相关段；未引用美国筛查资格、医保或孕期安排。',
        '官方患者教育页未单列专项资助；内容有研究者审阅说明，不等于本项目经过医生签审。', published_at='2022-07'),
    source('NFG-S08',
        'National Institute of Diabetes and Digestive and Kidney Diseases. Continuous glucose monitoring [Internet]. 2023 Jun [cited 2026 Oct 30]. Available from: https://www.niddk.nih.gov/health-information/diabetes/overview/managing-diabetes/continuous-glucose-monitoring',
        'https://www.niddk.nih.gov/health-information/diabetes/overview/managing-diabetes/continuous-glucose-monitoring',
        'NIH所属研究机构医疗器械使用科普',
        'CGM通过皮下传感器估计组织间液葡萄糖，提供趋势并辅助治疗计划；与单次指尖血测量不同，部分情境需按装置和治疗方案确认读数。',
        '不把2023页面型号寿命或使用细节当当前所有产品通则，不声称每个用户每次均必须指尖复核；无各品牌或中国准入结论。',
        '已实读CGM定义、组成、用途、局限和Last Reviewed June 2023；未逐一评测设备或宣称其长期临床结局。',
        '机构科普页未单列专项资助和商业利益。', published_at='2023-06'),
    source('NFG-S09',
        'Johansson M, Dower JA, Lipska KJ. Continuous glucose monitoring for persons with and without diabetes. JAMA Intern Med. 2026;186(9):1182. doi:10.1001/jamainternmed.2026.2769.',
        'https://jamanetwork.com/journals/jamainternalmedicine/fullarticle/2851942',
        '医学期刊患者教育专页',
        '无糖尿病者使用CGM尚无充分证据证明改善健康或预防糖尿病；追逐曲线可导致不必要地限制健康食物、焦虑及皮肤刺激。',
        '这是患者教育专页，不是新随机试验或系统综述；仅用于无糖尿病消费者的证据缺口，不借其表述否定已确诊糖尿病者的所有CGM用途。',
        '已实读期刊原页完整患者教育正文、出版日期、作者、题录、DOI及利益披露；明确其文类与证据范围。',
        'Johansson披露Swedish Research Council和Kamprad Foundation资助；Lipska披露NIH资助、Forman Watkins & Krutz LLP个人报酬、UpToDate版税及CMS/VA等文外关系。未简写为无利益冲突。',
        published_at='2026-08-03', doi='10.1001/jamainternmed.2026.2769'),
    source('NFG-S10',
        'US Food and Drug Administration. Do not use smartwatches or smart rings to measure blood glucose levels: FDA safety communication [Internet]. 2024 Feb 21 [cited 2026 Oct 30]. Available from: https://www.fda.gov/medical-devices/safety-communications/do-not-use-smartwatches-or-smart-rings-measure-blood-glucose-levels-fda-safety-communication',
        'https://www.fda.gov/medical-devices/safety-communications/do-not-use-smartwatches-or-smart-rings-measure-blood-glucose-levels-fda-safety-communication',
        '监管机构医疗器械安全通告',
        '警惕宣称不穿透皮肤即可独立测血糖的手表/戒指；错误读数若被用于降糖药决定可能危险。与显示外部CGM传来数据的手表不同。',
        '美国2024安全通告不能证明截至2026全球所有装置的批准状态；不把FDA监管范围外推为中国准入结论。',
        '已实读官方通告全文的适用范围、消费者建议、背景、日期和与CGM显示端的区别；未查遍全球器械注册。',
        '监管安全通告未单列专项资助或商业利益。', published_at='2024-02-21'),
    source('NFG-S11',
        'National Institute of Diabetes and Digestive and Kidney Diseases. Symptoms & causes of diabetes [Internet]. 2024 Oct [cited 2026 Oct 30]. Available from: https://www.niddk.nih.gov/health-information/diabetes/overview/symptoms-causes',
        'https://www.niddk.nih.gov/health-information/diabetes/overview/symptoms-causes',
        'NIH所属研究机构症状及风险科普',
        '口渴、多尿、视物模糊及不明原因体重下降需评估；2型糖尿病也可长期无症状。超重/肥胖、家族史和妊娠糖尿病史是相关风险线索。',
        '症状与风险线索不等于确诊；美国年龄、种族或BMI界值未移植为中国筛查条件，不把所有上述症状归因于糖尿病。',
        '已直接读取常见症状、1/2型表现、妊娠糖尿病史、2型危险因素与页尾October 2024审阅日；未把营养性生酮与DKA混同。',
        '机构科普页未单列本页专项资助和商业利益。', published_at='2024-10'),
]

def entry(eid, title, summary, plain, benefit, evidence, refs, notes=''):
    return dict(id=eid, chapter_id='nutrition', unit_id='nutrition-u6',
                ordinal=int(eid.rsplit('-', 1)[1]), title=title, summary=summary,
                fields=dict(cost='', plain=plain, benefit=benefit, evidence=evidence,
                            sources=''.join(f'[@{s}]' for s in refs), notes=notes),
                audience=dict(age_groups=['adult', 'older'], sexes=['all'],
                              scope_note='面向成年及年长读者；糖尿病用药、妊娠和个体筛查安排按正文分支处理。',
                              safety_pin=False),
                clinical_review_status='not_clinically_reviewed', content_checked_at=CHECKED)

ENTRIES = [
    entry('nutrition-015',
        '想让餐后血糖更平稳，先改主食份量和饮料，再用轻走打断久坐',
        '餐后血糖会上升，健康目标不是把曲线压成直线。先把含糖饮料换成水，让主食有份量、用部分全谷杂豆替换精白主食，并保留蔬菜和蛋白质食物。饭后或久坐中安排短暂轻走；先吃菜可以自选，不必严格计时。用胰岛素或会低血糖的药时，大改饮食和活动前先配好监测方案。',
        '**先改一顿饭的组成，不用从戒掉全部主食开始。** 血糖就是血液中的葡萄糖；餐后有所上升本身不是疾病。给自己盛好合适份量的主食，别一边吃菜一边无限续饭；将一部分精白米面换成全谷物、杂豆，搭配蔬菜和鱼、蛋、豆制品等蛋白质食物。少喝含糖饮料，用水或不加糖的茶替代；果汁不能代替完整水果。低GI表示食物升糖特点的一种比较，不意味着可以无限吃，也不代表营养一定更好。[@NFG-S01][@NFG-S02]\n\n**饭后别一坐就是几个小时，能走动就安排短暂轻走。** 比如收拾餐桌后走一小段，工作中也起身走动。成人短时试验支持用轻走打断久坐，改善当日餐后血糖和胰岛素指标；仅站起来的效果通常不如轻走。但这还不能证明某个固定分钟数能长期预防糖尿病，不必为“消掉这顿饭”立刻高强度训练。[@NFG-S03]\n\n**喜欢先吃菜、蛋白质再吃主食，可以保留；不需要把进食顺序变成计时任务。** 它若帮助你吃得更均衡、控制份量，就有实际价值；不能据此放心多吃。针对2型糖尿病的小型试验综述，尚未确立这种顺序在标准饮食建议之外的额外长期控糖收益，证据确定性也较低。不能把某次餐后峰值变小，直接翻译成已证明防病或抗衰。[@NFG-S04]\n\n**正在用胰岛素、磺脲类或格列奈类药，不要突然大减主食、漏餐或猛加运动。** 先和处方团队约定饮食变化时怎样监测、何时补充食物及何时联系调整方案；不要自行减停药。运动后的低血糖也可能延后出现。发抖、冷汗、头晕或心慌时先停止运动和禁食，按[节食不适与低血糖处理](#/entry/nutrition-001)分流，不把不适当成“控糖成功”。[@NFG-S05]',
        '把注意力放在能持续的餐食与活动上，减少餐后负担，同时保留主食、水果和必要营养。',
        'B/C。轻走打断久坐有急性试验综述支持；进食顺序的长期增量收益证据低或很低确定性。总体膳食与用药安全依据权威机构指导，不能由短时曲线推导长期防病。',
        ['NFG-S01','NFG-S02','NFG-S03','NFG-S04','NFG-S05']),
    entry('nutrition-016',
        '担心血糖先做正规筛查，别靠手表或一条动态曲线自诊',
        '担心血糖，先核对年龄、家族史、体重和既往检查，而不是先买传感器。中国现行行动方案提倡40岁及以上每年至少查一次空腹血糖；高危者和糖尿病前期另有更密的安排。口渴多尿、无故变瘦不等下次体检。动态血糖仪可辅助特定患者治疗，健康人靠它抗老或防糖尿病尚缺充分证据。',
        '**先把该做的筛查排进日历。** 中国《糖尿病防治行动实施方案（2024—2030年）》提倡40岁及以上人群每年至少查一次空腹血糖；高危者每年至少一次；已经确认糖尿病前期者，每半年查一次空腹或餐后2小时血糖，并每年做一次糖尿病风险评估。糖尿病前期指血糖高于正常、但尚未达到糖尿病诊断范围。没到40岁但有超重/肥胖、糖尿病家族史或妊娠糖尿病史，先把这些信息带到社区或内分泌门诊做风险评估，不把年龄当成免查凭证。[@NFG-S06][@NFG-S11]\n\n**持续口渴、多尿、视物模糊或无故变瘦，要尽快就诊检查，不等年度体检。** 这些症状不一定都是糖尿病；反过来，没有明显不适也不能排除。若伴持续呕吐、深快呼吸、嗜睡或意识异常，按[代谢急症信号](#/entry/nutrition-001)立即处理。[@NFG-S11]\n\n**检查报告异常，带报告复核，不靠几天不吃饭“把数值压回去”。** 空腹血糖反映检测时点的情况；糖化血红蛋白（HbA1c）反映约三个月平均血糖，两者不是同一项。贫血、某些血红蛋白变异等会影响HbA1c解释。规范诊断需要结合血液化验、症状及必要的复查；不要拿消费级设备的某个数值给自己确诊。[@NFG-S07]\n\n**动态血糖仪先看用途，再决定是否购买。** 持续葡萄糖监测（CGM）通常把细小传感器置于皮下，估计组织间液中的葡萄糖并显示趋势，并非直接连续抽血。已用胰岛素等需要细致监测的人，可和治疗团队讨论是否用它识别规律、配合既定治疗；读数与身体感觉不符时，按设备说明及既定方案核实，不自行追着曲线加药。没有糖尿病者，目前缺乏充分证据证明佩戴它改善健康或预防糖尿病；不必为了“抗老”频繁扎指、买传感器，或因为一次峰值就戒掉完整水果。[@NFG-S08][@NFG-S09]\n\n**别用宣称无创独立测糖的手表、戒指决定吃药或诊断。** 它和显示正规CGM传来数据的手表是两回事。FDA曾专门警告这类宣称的误测风险；那份美国通告不等于当前全球器械准入清单，但足以提醒你：先核产品真实用途与注册信息，不拿健康功能广告代替医学检测。[@NFG-S10]',
        '把筛查、确诊与日常治疗监测分开，让真正有风险的人及时检查，也避免健康人花钱追逐一条没有明确临床意义的曲线。',
        'C。中国筛查频次来自2024国家行动方案；化验与器械用途依据官方患者指导。健康人CGM的局限参考2026医学期刊患者教育页，证据不足不等于已证明所有人使用都无效。',
        ['NFG-S06','NFG-S11','NFG-S07','NFG-S08','NFG-S09','NFG-S10']),
]

AUDIT = {
    'checked_at': CHECKED,
    'entries': len(ENTRIES), 'sources': len(SOURCES),
    'entry_ids': [e['id'] for e in ENTRIES],
    'clinical_review_status': 'not_clinically_reviewed',
    'scope': 'nutrition-015/016：日常餐后血糖实践，以及中国成人筛查、用药低血糖与CGM消费判断。',
    'proposed_unit': {'id': 'nutrition-u6', 'title': '让血糖管理回到餐食、活动和正规检查', 'entry_ids': ['nutrition-015','nutrition-016']},
    'claim_checks': [
        {'entry': 'nutrition-015', 'claim': '主食份量、质量、食物组合与限制含糖饮料', 'sources': ['NFG-S01','NFG-S02'], 'boundary': '不提供个人碳水克数，不要求健康人禁止主食、完整水果或全部餐后上升；低GI不等于无限量。'},
        {'entry': 'nutrition-015', 'claim': '用短暂轻走打断餐后/工作久坐', 'sources': ['NFG-S03'], 'boundary': '只把单日实验结果写成急性餐后指标；没有最优固定分钟数、长期防病或抗老结论。'},
        {'entry': 'nutrition-015', 'claim': '先菜后饭可自选，但长期增量收益未确立', 'sources': ['NFG-S04'], 'boundary': '综述样本为2型糖尿病；未宣称健康人一定有效或所有进食顺序绝对无效。'},
        {'entry': 'nutrition-015', 'claim': '减少碳水和增加活动需核胰岛素/促泌剂低血糖风险', 'sources': ['NFG-S05'], 'boundary': '不用简单心慌确诊反应性低血糖，不自行改药；急症与具体处理链接既有001。'},
        {'entry': 'nutrition-016', 'claim': '40岁以上年度空腹筛查、高危至少年度、糖前每半年和年度评估', 'sources': ['NFG-S06'], 'boundary': '中国2024发文，省级卫健委正式全文转载；不移植美国35岁和三年周期。'},
        {'entry': 'nutrition-016', 'claim': '风险线索与症状需正规评估，空腹血糖与HbA1c不同', 'sources': ['NFG-S07','NFG-S11'], 'boundary': '不给健康人设个人波动阈值；无症状不排除，有症状不自诊。不搬外国BMI界值或妊娠筛查安排。'},
        {'entry': 'nutrition-016', 'claim': 'CGM用途与无糖尿病消费者证据边界', 'sources': ['NFG-S08','NFG-S09'], 'boundary': '组织间液与血液区分；没有否定医疗CGM。JAMA患者页并非新RCT，不用其表述概括所有糖尿病长期结局。'},
        {'entry': 'nutrition-016', 'claim': '不以无创独立测糖手表/戒指指导诊疗', 'sources': ['NFG-S10'], 'boundary': '区分外部CGM数据显示端；2024美国通告未冒充2026中国或全球审批清单。'},
    ],
    'exclusions': [
        '不把餐后波动小等同延寿、防糖尿病或皮肤抗老；不为健康人要求常规CGM、频繁指尖测试。',
        '未列诊断阈值表：不能将ADA与中国的糖前空腹界值混用；筛查入口不需要个人自诊表。',
        '不编控糖产品价格；成本为空，没有品牌、实时采购或中国注册清单结论。',
        '未新增糖前预防独立条目；相关饮食、活动与体重分支可由整合者交叉链接，不超出指定ID。',
        '没有临床医生签审；未声称来源或推导百分之百无误。',
    ],
    'screened_but_not_used': [
        {'source': 'American Diabetes Association Professional Practice Committee for Diabetes. Diagnosis and Classification of Diabetes: Standards of Care in Diabetes—2026. Diabetes Care. 2026;49(Suppl 1):S27-S49. doi:10.2337/dc26-S002.', 'reason': '核到PubMed题录；原刊和PDF返回403，PMC呈校验页。只见官方索引中的CGM诊断相关片段，未据片段承载正文关键结论，也未假称全文审阅。'},
        {'source': 'NHC成人糖尿病食养指南2023原PDF', 'reason': 'PDF读取失败；改用已实读中国疾控中心相关官方科普，并明确其2023日期和范围。'},
        {'source': 'NIDDK Risk Factors for Type 2 Diabetes（2022审阅）', 'reason': '实读风险相关段，但为避免重复来源，最终用已读2024 Symptoms & Causes中的共同风险线索；美国年龄与BMI界值未采用。'},
    ],
    'metadata_checks': [
        '三篇期刊资料逐项核对作者、题名、卷期页/文章号和DOI；不把在线日期与正式卷期混为新证据。',
        '2023疾控网页URL含202408，未当作更新时间；中国行动方案分别标发文日和转载日。',
        '所有实际阅读范围与访问失败均按事实保留；系统综述未声称逐读全部底层试验或复算。',
        '摘要为100–180字符纯文，六字段齐全；adult/older与sexes all不因题内40岁条件误设互斥过滤。',
        '每段重要医学主张有来源映射，急性症状只做安全分流并链接既有nutrition-001。',
    ],
}

if __name__ == '__main__':
    ids = {s['id'] for s in SOURCES}
    for e in ENTRIES:
        assert 100 <= len(e['summary']) <= 180, (e['id'], len(e['summary']))
        assert e['fields']['cost'] == ''
        assert set(e['fields']) == {'cost','plain','benefit','evidence','sources','notes'}
        refs = set(re.findall(r'\[@([^\]]+)\]', json.dumps(e, ensure_ascii=False)))
        assert refs <= ids, (e['id'], refs - ids)
        assert set(re.findall(r'\[@([^\]]+)\]', e['fields']['plain'])) == set(re.findall(r'\[@([^\]]+)\]', e['fields']['sources']))
    for name, value in [('entries',ENTRIES),('sources',SOURCES),('audit',AUDIT)]:
        (OUT / f'glycemia-{name}.json').write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'entries':len(ENTRIES),'sources':len(SOURCES),'summary_lengths':{e['id']:len(e['summary']) for e in ENTRIES}}, ensure_ascii=False))
