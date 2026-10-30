"""Frozen exercise and sleep additions, including resolved editorial safety refinements."""
import hashlib
import json
import re
from pathlib import Path
HERE=Path(__file__).resolve().parent

ENTRIES=[{'id': 'sleep-009',
  'chapter_id': 'sleep',
  'unit_id': 'sleep-u2',
  'ordinal': 9,
  'title': '晚间运动先看强度和离睡觉多久，别按晚上几点一刀切停练',
  'summary': '晚间锻炼不用统一按八点或九点叫停，先看离预计睡觉还有多久，以及练得多猛、多长。临睡前改做轻松活动；若晚练后总是发热、心跳迟迟平复不了或难入睡，先把较重训练提前到约睡前四小时结束。这个间隔是调整起点，不是四小时内任何活动都有害的分界线。',
  'fields': {'cost': '',
             'plain': '**没有人人适用的“晚上过几点就不能练”。** '
                      '先从自己的预计睡觉时间倒推，给训练、回程和放松留位置，不为凑一场运动继续缩短睡眠。临睡前剩下的时间适合轻松步行、温和活动；高强度间歇、长时间高负荷训练尽量往前排。负荷既看多猛，也看练多久，不能把十分钟轻活动和一整场激烈训练看成一回事。[@SLX-S01][@SLX-S03]\n'
                      '\n'
                      '若晚练后常觉得身体很热、心跳迟迟平复不了或更难入睡，先把较重训练移到预计入睡前约4小时结束，并记录结束时间、强度和当夜睡眠；只能较晚练时，先缩短、降低强度。4小时来自大型可穿戴观察研究的参考，不是过线就有害的生理开关。它发现相关性，不能证明晚练一定导致失眠，也没有证明每个运动方式都同样受影响。[@SLX-S01]\n'
                      '\n'
                      '如果同时出现胸痛、晕厥或明显气短，先停止运动并按[运动急症](#/entry/activity-001)求助，不能只把它当作晚练兴奋、等待改时间后观察。\n'
                      '\n'
                      '健康且原本睡得好的人，不必仅因晚上练就全部取消：较小的实验综述中，睡前2–4小时结束高强度运动，总体未见明显睡眠恶化；结果不能直接保证老年人或失眠患者。失眠护理网页有更保守的“睡前4小时不运动”，而NHLBI的一般睡眠习惯页强调睡前一小时安静并避免剧烈运动；这些并不是同一人群的统一禁令。已有失眠、每次晚练后都难睡时，优先提前较重训练；持续影响白天则按[失眠评估](#/entry/sleep-002)处理。[@SLX-S02][@SLX-S04][@SLX-S03]',
             'benefit': '保留可坚持的运动机会，同时减少临睡前高负荷和挤占睡眠带来的困扰。',
             'evidence': 'B，健康良好睡眠者的小型实验综述与2025年大型观察研究方向并不完全相同，不能合成人人适用的硬截止线；根据症状提前或减量的起步安排为C。',
             'sources': '晚练时间与负荷观察研究。[@SLX-S01]；健康成人实验综述。[@SLX-S02]；一般睡眠习惯与失眠护理指导。[@SLX-S03][@SLX-S04]',
             'notes': ''},
  'audience': {'age_groups': ['adult', 'older'],
               'sexes': ['all'],
               'scope_note': '成年与老年读者按作息和反应调整的入口；2–4小时实验主要来自18–50岁良好睡眠者，不直接保证老年人、失眠者或心血管病患者。',
               'safety_pin': False},
  'clinical_review_status': 'not_clinically_reviewed',
  'content_checked_at': '2026-10-30'},
 {'id': 'sleep-013',
  'chapter_id': 'sleep',
  'unit_id': 'sleep-u5',
  'ordinal': 13,
  'title': '少睡后先看清醒程度，困得打盹就休息，别用咖啡硬顶大强度训练',
  'summary': '偶尔少睡一晚，不等于第二天必须完全躺着，也不适合照常挑战极限。通宵后、接连打盹或动作控制变差时，先休息并取消高风险训练；只是稍少睡且仍清醒、没有不适，可先换成熟悉的轻活动并减量。咖啡不能证明反应和协调已恢复，也别为了晨练再次挤掉睡眠。',
  'fields': {'cost': '',
             'plain': '**先改当天计划，不用完成原训练表来证明自己撑得住。** '
                      '一夜没睡、接连打盹或明显难集中注意时，先休息，取消冲极限、大重量测试及一旦失误后果严重的项目；不要困着开车赶去健身房，见[困倦驾驶](#/entry/sleep-001)。睡少会影响反应、判断和动作表现，主观觉得能撑并不可靠。[@SLX-S06][@SLX-S05][@SLX-S07]\n'
                      '\n'
                      '若只是偶尔少睡、仍清醒且没有不适，可以把当天换成熟悉、轻松、短一些的活动，例如平地步行或温和活动，不必为了“把自己累垮好睡觉”去补做高强度训练。开始后更困、动作控制变差或明显不舒服就停。这是根据警觉和表现资料作的保守取舍，不是某种轻训练已被证明对所有缺觉者绝对安全。[@SLX-S05][@SLX-S06]\n'
                      '\n'
                      '别靠浓咖啡、能量饮料或训练前补剂把计划强度顶回去；更清醒的感觉不等于缺的睡眠已经补上，全天摄入另见[咖啡因总量](#/entry/energy-001)。研究中晨间表现有时比下午受影响小，也不意味着要闹钟提前叫醒自己去练；先留够睡眠机会。[@SLX-S07][@SLX-S05]\n'
                      '\n'
                      '胸痛、晕厥或明显气短不能一概解释为昨晚没睡，按[运动急症](#/entry/activity-001)处理。连续多晚睡少、白天功能持续受影响时，先处理作息或睡眠问题，不把每天减量当长期解决办法。[@SLX-S06]',
             'benefit': '把短期表现波动和安全风险放进训练安排，避免用提神产品或硬补课进一步挤占恢复。',
             'evidence': 'B，急性缺觉控制试验的系统综述支持次日表现总体受影响，但任务、缺觉模式和个体差异很大；停止高风险项目、改轻活动与通勤安排为C，不是按睡眠小时数开统一运动处方。',
             'sources': '急性缺觉与运动表现综述。[@SLX-S05]；缺觉的警觉与安全影响。[@SLX-S06]；咖啡及困倦驾驶指导。[@SLX-S07]',
             'notes': ''},
  'audience': {'age_groups': ['adult', 'older'],
               'sexes': ['all'],
               'scope_note': '供成年与老年读者调整偶发缺觉次日活动；研究以较年轻、健康男性为主，不能据此为有病者开训练量，也不套儿童方案。',
               'safety_pin': False},
  'clinical_review_status': 'not_clinically_reviewed',
  'content_checked_at': '2026-10-30'}]

SOURCES=[{'id': 'SLX-S01',
  'citation': 'Leota J, Presby DM, Le F, Czeisler MÉ, Mascaro L, Capodilupo ER, et al. Dose-response relationship '
              'between evening exercise and sleep. Nat Commun. 2025;16(1):3297. doi:10.1038/s41467-025-58271-x.',
  'url': 'https://www.nature.com/articles/s41467-025-58271-x',
  'type': '原始观察性队列研究',
  'support': '14,689名有规律活动成人、约408万人夜可穿戴资料中，运动更晚及综合负荷更高与较晚入睡和较差睡眠指标相关；约4小时是相对入睡时点的参考。',
  'limitations': '回顾性观察，不证明因果或人人存在同一4小时生理阈值；设备估计睡眠，不是全部多导睡眠监测。样本以男性及活跃用户为主，不直接外推儿童、失眠患者或所有运动方式。',
  'reading_depth': '实读原刊摘要、引言、人口及相对习惯入睡时点的主要结果；方法中个体习惯入睡与实际入睡定义另核PMC官方索引返回正文；PubMed核完整题录、摘要和利益声明。未通读所有补充表或重分析数据。',
  'funding_disclosure': 'PubMed披露E.R.C.和D.M.P.在WHOOP任职并受薪，公司按声明不另参与设计、分析或发表；其余作者声明无竞争利益。未完整核读全部致谢，不声称已穷尽全部资助关系。',
  'content_checked_at': '2026-10-30',
  'doi': '10.1038/s41467-025-58271-x',
  'doi_url': 'https://doi.org/10.1038/s41467-025-58271-x'},
 {'id': 'SLX-S02',
  'citation': 'Frimpong E, Mograss M, Zvionow T, Dang-Vu TT. The effects of evening high-intensity exercise on sleep '
              'in healthy adults: a systematic review and meta-analysis. Sleep Med Rev. 2021;60:101535. '
              'doi:10.1016/j.smrv.2021.101535.',
  'url': 'https://pubmed.ncbi.nlm.nih.gov/34416428/',
  'type': '系统综述与荟萃分析',
  'support': '15项急性晚间高强度实验、194名18–50岁良好睡眠成人；距睡前2–4小时的训练总体未见睡眠恶化，0.5–4小时合并分析REM比例略低。',
  'limitations': '试验小、人群与运动方案有限；未显著不同不等于证明等效或对所有人无影响。不能直接指导老年失眠者或以REM小差异推疾病损害。',
  'reading_depth': '实读PubMed完整摘要、四位作者、年卷文章号、DOI与利益声明；未取得全文或逐读15项原始试验。',
  'funding_disclosure': 'PubMed声明作者无需披露的利益冲突；全文资助未完整核读，不能宣称无任何资助。',
  'content_checked_at': '2026-10-30',
  'doi': '10.1016/j.smrv.2021.101535',
  'doi_url': 'https://doi.org/10.1016/j.smrv.2021.101535'},
 {'id': 'SLX-S03',
  'citation': 'National Heart, Lung, and Blood Institute. Sleep deprivation and deficiency: healthy sleep habits '
              '[Internet]. 2022 Mar 24 [cited 2026 Oct 30]. Available from: '
              'https://www.nhlbi.nih.gov/health/sleep-deprivation/healthy-sleep-habits',
  'url': 'https://www.nhlbi.nih.gov/health/sleep-deprivation/healthy-sleep-habits',
  'type': '政府医学机构护理指导',
  'support': '睡前一小时安静放松、避免剧烈运动；保持日常活动并为睡眠留够时间，睡眠时点按个人作息而非统一钟点。',
  'limitations': '实践指导，不证明一小时为全人群最优临界点；运动治疗失眠、低强度活动效果及缺觉后训练安全不能由此单独确立。同机构失眠治疗页另给上床前5–6小时活动的保守说法，因此本页一小时不能代表全部NHLBI页面统一截止线。',
  'reading_depth': '实读健康睡眠习惯全部条目、小睡与轮班段；核原页实际2022-03-24更新日，未将当前页脚或未来复审当更新。另实际核https://www.nhlbi.nih.gov/health/insomnia/treatment的Healthy '
                   'sleep habits段，5–6小时的对象是失眠护理建议，不采用为人人硬线。',
  'funding_disclosure': '美国政府机构患者教育；页面未见独立专项资助声明，不作随机试验。',
  'content_checked_at': '2026-10-30',
  'reviewed_at': '2022-03-24'},
 {'id': 'SLX-S04',
  'citation': 'National Health Service. Insomnia [Internet]. 2024 Mar 19 [cited 2026 Oct 30]. Available from: '
              'https://www.nhs.uk/conditions/insomnia/',
  'url': 'https://www.nhs.uk/conditions/insomnia/',
  'type': '公共医疗机构失眠患者指导',
  'support': '失眠页面建议白天规律运动、睡前4小时不运动；用于展示较保守的失眠护理建议及其与健康人群实验的适用区别。',
  'limitations': '该页未区分运动强度，不能拿它宣布所有健康人4小时内轻活动有害；不把此页禁止午睡条目套给困倦驾驶、轮班或全部缺觉情况。',
  'reading_depth': '实读症状、原因、Do/Do not、药师与就医段，核2024-03-19实际复核日和2027计划复核日区别。',
  'funding_disclosure': '公共医疗机构患者教育，页面未见独立研究资助声明。',
  'content_checked_at': '2026-10-30',
  'reviewed_at': '2024-03-19'},
 {'id': 'SLX-S05',
  'citation': 'Craven J, McCartney D, Desbrow B, Sabapathy S, Bellinger P, Roberts L, et al. Effects of acute sleep '
              'loss on physical performance: a systematic and meta-analytical review. Sports Med. '
              '2022;52(11):2669-2690. doi:10.1007/s40279-022-01706-y.',
  'url': 'https://link.springer.com/article/10.1007/s40279-022-01706-y',
  'type': '系统综述与荟萃分析',
  'support': '成人短期缺觉控制试验合并显示次日多类运动表现降低；影响依缺觉模式、任务及时间不同。技能任务敏感，晨间和傍晚结果不能一概而论。',
  'limitations': '约89%参与者为男性，异质性很高；不是受伤率研究，不能把平均百分比换成个人风险或判断某强度绝对安全。≤6小时是研究纳入界定，不是运动禁令或健康睡眠最低线。',
  'reading_depth': '实读原刊全文相关方法2.1–2.2、结果3.2/3.6–3.9、讨论4.1–4.4、结论及资助/利益声明；核PubMed题录。没有重读所有原试验或原始数据。',
  'funding_disclosure': '原文声明文章准备未获专项经费，开放获取由CAUL及成员机构支持；作者声明无与本文直接相关的利益冲突。',
  'content_checked_at': '2026-10-30',
  'doi': '10.1007/s40279-022-01706-y',
  'doi_url': 'https://doi.org/10.1007/s40279-022-01706-y'},
 {'id': 'SLX-S06',
  'citation': 'National Heart, Lung, and Blood Institute. Sleep deprivation and deficiency: how sleep affects your '
              'health [Internet]. 2022 Jun 15 [cited 2026 Oct 30]. Available from: '
              'https://www.nhlbi.nih.gov/health/sleep-deprivation/health-effects',
  'url': 'https://www.nhlbi.nih.gov/health/sleep-deprivation/health-effects',
  'type': '政府医学机构安全指导',
  'support': '缺觉可降低注意、反应和决策能力，可能出现未觉察的微睡眠，自觉能撑不等于功能正常。',
  'limitations': '机构概括不能计算个人运动伤害率、判断哪项力量训练负荷安全或诊断胸痛病因；没有用其长期关联宣称一晚失眠永久伤害。',
  'reading_depth': '实读缺觉线索、日间功能及安全全文相关段，并核原页实际2022-06-15更新日；未采用事故统计或长期疾病风险数字。',
  'funding_disclosure': '美国政府机构患者教育，页面未见独立专项资助声明。',
  'content_checked_at': '2026-10-30',
  'reviewed_at': '2022-06-15'},
 {'id': 'SLX-S07',
  'citation': 'National Highway Traffic Safety Administration. Drowsy driving [Internet]. [cited 2026 Oct 30]. '
              'Available from: https://www.nhtsa.gov/risky-driving/drowsy-driving',
  'url': 'https://www.nhtsa.gov/risky-driving/drowsy-driving',
  'type': '交通安全政府原始指导',
  'support': '咖啡或能量饮料不能补足睡眠，严重缺觉者自觉提神后仍可能微睡眠；困倦不驾车。',
  'limitations': '交通指导用于通勤安全，不将短时提神结论套成训练后恢复疗效，也不搬美国事故数字和法律。',
  'reading_depth': '实读Tips to Drive Alert和Short-term interventions全部段；未采用主页死亡数或美国车速示例。',
  'funding_disclosure': '政府机构安全教育，页面未见独立专项资助声明。',
  'content_checked_at': '2026-10-30'}]

AUDIT={'checked_at': '2026-10-30',
 'entries': 2,
 'sources': 7,
 'clinical_review_status': 'not_clinically_reviewed',
 'read_style_sop': True,
 'read_project_sop': True,
 'coverage': {'sleep-009': '睡前运动：钟点/相对入睡时点、负荷×时长、普通好睡者与失眠、指南分歧、症状记录调整。',
              'sleep-013': '缺觉后运动：偶发少睡/通宵/明显困倦分流，安全通勤，训练减量与高风险推迟，咖啡不是恢复许可。'},
 'important_limits': ['2025观察研究与2021实验综述不假装完全一致。4小时作为较重训练调整起点而非普遍禁动阈值；2025约408万夜不当408万人。',
                      'NHS失眠网页的睡前4h禁运动与NHLBI一般睡眠习惯的睡前1h避免intense明确并列，未假称指南一致；良好睡眠成人试验不保证老年失眠患者。',
                      '2022睡少SR的≤6h为研究纳入界定，不写成健身禁线；合并平均−7.56%与每醒1h降0.4%未用于个人预测。',
                      '运动表现下降不等于受伤风险已量化；改轻活动和推迟极限项目明确为基于证据的保守编辑建议，未声称干预安全RCT。',
                      '未建议为晨练再次早起缩短睡眠，也未认定一晚失眠必有长期器官损伤。',
                      '引用的NHLBI认知/安全与NHTSA驾驶资料不冒充运动伤害试验；胸痛晕厥入口稳定链接已有急症。',
                      'sleep-009新增胸痛/晕厥/明显气短时转activity-001，急症依据由该已核条目的NHS来源提供，不把NHLBI一般缺觉安全页冒充胸痛分流来源。',
                      'SLX-S03记录同机构失眠treatment页5–6h口径，正文称一般睡眠习惯页1h，避免把NIH所有页面等同一线。',
                      'sleep-013收益中的兴奋剂改提神产品，便于理解且不改变原临床结论。'],
 'reading_limits': ['Nature原刊初次能读摘要/引言/主要结果；后续部分获取受身份跳转限制。PMC直接页为校验页面，未绕过；方法相关定义来自PMC官方搜索索引所返回正文，资金用PubMed实际完整利益声明，均在source阅读深度如实标记。',
                    '2021 Frimpong只核PubMed完整摘要和题录及利益声明，不称全读或全读原试验。',
                    '2022 Craven原刊全文相关方法/结果/讨论限制/资金实际读取；没声称独立重分析。'],
 'not_added': ['具体损伤概率或人人同一安全睡眠小时线', '全品类训练前补剂成分评测', '把运动当慢性失眠一线治疗替代CBT-I'],
 'summaries': {'sleep-009': 117, 'sleep-013': 117},
 'blocking_unresolved': [],
 'disposition': 'updated_after_independent_ai_editorial_review_ready_for_reread'}

def main():
    for entry in ENTRIES:
        assert 100<=len(entry['summary'])<=180
        assert not re.search(r'[\r\n|]|\[@|\]\(',entry['summary'])
    for name,value in [('exercise-entries',ENTRIES),('exercise-sources',SOURCES)]:
        (HERE/(name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    AUDIT['input_sha256']={name:hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in ['exercise-entries.json','exercise-sources.json']}
    (HERE/'exercise-audit.json').write_text(json.dumps(AUDIT,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(AUDIT['input_sha256']))

if __name__=='__main__':main()
