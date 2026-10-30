"""Reviewed-source sleep expansion; JSON is the editable output, not generated advice."""
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
DATE='2026-10-30'
sources=[]

def website(number,org,title,url,date,support,limits,depth):
    s=dict(id=f'LIFE-SLP-S{number:02d}',citation=f'{org}. {title} [Internet]. '+(date+'. ' if date else '')+f'[cited 2026 Oct 30]. Available from: {url}',url=url,
        type='专业机构或监管原始指导',support=support,limitations=limits,reading_depth=depth,
        content_checked_at=DATE,funding_disclosure='机构官方教育或监管材料；未见该页单独专项资助声明，不据此推成独立临床试验。')
    sources.append(s)

def paper(number,citation,url,support,limits,depth,funding):
    sources.append(dict(id=f'LIFE-SLP-S{number:02d}',citation=citation,url=url,type='原始研究或专业指南',support=support,limitations=limits,reading_depth=depth,content_checked_at=DATE,funding_disclosure=funding))

website(1,'National Highway Traffic Safety Administration','Drowsy driving','https://www.nhtsa.gov/risky-driving/drowsy-driving','',
    '困倦驾驶应停止驾驶；咖啡和短小睡只有短期作用，不能补足睡眠或保证安全。',
    '交通安全指导，不把美国事故数字或驾驶法律移植中国；不把喝咖啡/睡20分钟当重新开车许可。',
    '已读Tips to Drive Alert及Short-term interventions完整正文，核缺觉、药物和安全停车分支；未使用事故发生率。')
paper(2,'Edinger JD, Arnedt JT, Bertisch SM, Carney CE, Harrington JJ, Lichstein KL, et al. Behavioral and psychological treatments for chronic insomnia disorder in adults: an American Academy of Sleep Medicine clinical practice guideline. J Clin Sleep Med. 2021;17(2):255-262. doi:10.5664/jcsm.8986.',
    'https://pubmed.ncbi.nlm.nih.gov/33164742/',
    '多组分CBT-I为成人慢性失眠的强推荐；单独睡眠卫生不能替代完整治疗。',
    '成人慢性失眠指南；不从推荐强度机械换算本指南ABC，也不把诊断和睡眠限制疗法改成无监督家庭处方。',
    '已核PubMed完整题录、六作者、年卷期页、DOI、完整摘要与利益披露；未重读所有所引试验。',
    'AASM资助；部分作者有Merck研究/顾问、Philips设备等关系，PubMed披露已读。')
website(3,'National Heart, Lung, and Blood Institute','Insomnia: treatment','https://www.nhlbi.nih.gov/health/insomnia/treatment','2022 Mar 24',
    'CBT-I的认知、放松、刺激控制与睡眠安排组成，可面对面、电话或线上进行；药物按具体类型选择。',
    '机构患者教育，药品名单与美国批准不能套成中国用药许可；褪黑素结论与2023欧洲指南的剂型/年龄差异分层使用。',
    '已读睡眠习惯、CBT-I、处方/非处方与其他治疗全文，核实际2022-03-24更新日；未采用全部药物列表。')
website(4,'National Center for Complementary and Integrative Health','Melatonin: what you need to know','https://www.nccih.nih.gov/health/melatonin-what-you-need-to-know','2024 May',
    '褪黑素是黑暗信号相关激素；用途、长期安全资料不足、老年日间困倦及癫痫/抗凝药/孕哺等限制。',
    '未采用该页慢性失眠持续一个月的旧概括，也不沿用2014轮班综述为2026现行结论；国外软糖检测不能推断所有国内备案产品含量失实。',
    '已读定义、时差/睡眠相位、慢性失眠、轮班、安全与老年/孕哺/药物互动各段，核2024年5月更新；不将所引研究视作均已阅读全文。')
website(5,'北京市市场监督管理局','你知道褪黑素有新吃法了吗？','https://scjgj.beijing.gov.cn/zwxx/scjgdt/202602/t20260202_4485364.html','2026 Feb 2',
    '中国褪黑素保健食品查询、每日用量1–3mg、操作前/操作中不食用；新增口服液剂型不等于药效升级。',
    '监管消费教育只用于国内标签/选择和安全范围，不用其广义改善睡眠表述替代失眠疗效指南，不推断所有商品处方属性。',
    '已读官方完整短页，核2026-02-02日期、1–3mg、蓝帽查询与驾驶警示；不引用宣传性的疗效概括。')
website(6,'European Medicines Agency','Circadin: EPAR product information','https://www.ema.europa.eu/en/documents/product-information/circadin-epar-product-information_en.pdf','2025 Jul 7',
    '该欧洲2mg缓释处方制剂仅在55岁及以上原发失眠的特定适应证，餐后睡前1–2小时、最多13周；整片吞服、困倦与酒精/镇静药/孕哺等限制。',
    '单一受监管药品说明，不是中国所有保健食品或普通速释剂的统一剂量，也不证明每个55岁以上失眠者均适合；非中国批准证明。',
    '已打开28页PDF，实际审读物理第2–4页适应证、剂量、特殊人群、互动与驾驶警示；版本上传更新日由EMA产品入口2025-07-07核对，未将PDF日期占位符当已填写日期。')
paper(7,'Riemann D, Espie CA, Altena E, Arnardottir ES, Baglioni C, Bassetti CLA, et al. The European Insomnia Guideline: an update on the diagnosis and treatment of insomnia 2023. J Sleep Res. 2023;32(6):e14035. doi:10.1111/jsr.14035.',
    'https://pubmed.ncbi.nlm.nih.gov/38016484/',
    '成人慢性失眠先考虑CBT-I；一般速释褪黑素与55岁以上特定缓释方案的推荐有区别。',
    '适用于成人慢性失眠，不把欧洲药物可得性当中国许可；该文自定推荐字母不等于本指南ABC；未依据完整药物表给个人处方。',
    '核PubMed完整题录与摘要、原刊题录及出版方索引返回4.2.6 Melatonin相关文字；没有声称通读36页全文或全部引文。',
    '本次未完整核读全文资金与利益声明，不声称无商业关系；仅采摘要及已见相关段落支持的区别。')
website(8,'Centers for Disease Control and Prevention','Jet lag disorder. CDC Yellow Book 2026','https://www.cdc.gov/yellow-book/hcp/travel-air-sea/jet-lag-disorder.html','2025 Apr 23',
    '时差需要按时区/方向安排睡眠、见光与褪黑素；0.5–1mg通常足以移相，错误时点可加重错位，不推荐高于5mg；短小睡不代替正常睡眠。',
    '2026版章节实际网页日期2025-04-23；临床时差指引不是中国保健食品标签，不能把0.5–1mg、时区计算或美国药品清单通用给儿童、孕哺及慢性失眠。',
    '已读时差定义、方向、旅行前后安排、战略睡眠、褪黑素与刺激/镇静药相关正文；未照搬图内固定示例行程和药物剂量表。')
website(9,'National Heart, Lung, and Blood Institute','Sleep deprivation and deficiency: healthy sleep habits','https://www.nhlbi.nih.gov/health/sleep-deprivation/healthy-sleep-habits','2022 Mar 24',
    '咖啡因可作用至8小时、睡前避免酒精与强光；成人短小睡约20分钟、夜间入睡困难时限制/提前午睡；轮班保护日间睡眠机会。',
    '实践指导中的8小时和20分钟是起步参考，不是人人代谢或午睡的硬性安全线；成人午睡参数不套婴幼儿，也不作减肥饮食处方。',
    '已读全部习惯、小睡和轮班段，核2022-03-24实际更新；未把全部旧实践节拍写成RCT最优阈值。')
paper(10,'Wright KP Jr, Abbott SM, Ashbrook L, Drake CL, Flynn-Evans E, Framnes-DeBoer S, et al. Management of shift work disorder: an American Academy of Sleep Medicine clinical practice guideline. J Clin Sleep Med. 2026;22(1):202. doi:10.1007/s44470-026-00084-w.',
    'https://pmc.ncbi.nlm.nih.gov/articles/PMC13695634/',
    '成人轮班障碍的计划小睡、咖啡因与亮光为条件性建议；相应失眠情境可讨论褪黑素，醒后惯性及服药困倦影响通勤安全。',
    '推荐均有条件，大部分非药物/褪黑素证据低或很低；适用于成人SWD，不是每位熬夜者的完整移相处方；频繁轮转者未必适合追求夜班完全适应。',
    'PMC原始全文已打开；实际审读推荐5、8–12、16–18及相应解释、Table2、资助与利益声明；PubMed核2026-10-24、22(1):202和DOI，未重做系统综述。',
    'AASM资助；部分作者有睡眠药企顾问、研究支持、学会雇佣等关系，文末披露已读。')
website(11,'Cleveland Clinic','Is it OK to sleep with earbuds in?','https://health.clevelandclinic.org/sleeping-with-headphones','2026 Apr 8',
    '睡眠耳机的侧睡压迫、湿气/耳垢、音量和报警感知风险；短时低音量与定时停播，外放可减少机械压迫。',
    '听力师临床患者教育而非长期头对头试验；不采绝对最安全或特定耳机形态必然改善睡眠的背书，不用设备百分比当声压阈值。',
    '已读2026-04-08正文全部益处、风险、安全与外放段；未采用相关商品导流或全部白噪音助眠概括。')
website(12,'World Health Organization','Deafness and hearing loss: safe listening','https://www.who.int/news-room/questions-and-answers/item/deafness-and-hearing-loss-safe-listening','2026 Mar 6',
    '音量、时间和频率共同决定听觉暴露；降低音量、减少时长并核监测、留意耳鸣和听力变化。',
    '周暴露框架不是保证个人无损伤的睡眠音量线；滑块百分比不能等同全部设备固定声压，不以降噪或骨传导保证安全。',
    '已读音量/时间、监测及听力警示全部相关问答，核2026-03-06日期；未把所有场景耳机建议机械套到夜间报警安全。')
paper(13,'Basner M, Smith MG, Cordoza M, Kayser MS, Carlin M, Ecker AJ, et al. Efficacy of pink noise and earplugs for mitigating the effects of intermittent environmental noise exposure on sleep. Sleep. 2026;49(5):zsag001. doi:10.1093/sleep/zsag001.',
    'https://pubmed.ncbi.nlm.nih.gov/41627391/',
    '25名健康成人七夜实验室交叉比较，特定粉红噪音条件减少快速眼动（REM）睡眠；耳塞较能减轻环境噪声扰眠。',
    '小型短期实验室研究，测试40/50dBA特定噪声；不能推所有白噪音/雨声/音量均有害或耳塞长期人人更佳；没有证明耳机一晚必损听力。',
    '已核PubMed六作者、正式49(5)文号、DOI和完整摘要的设计/结果；全文未能完整读取，未声称重新分析表格。',
    '未完整核读全文资助/利益声明，不声称独立无资助；研究规模与条件已作为主要限制公开。')
website(14,'National Institute for Occupational Safety and Health','Effects of light on circadian rhythms','https://www.cdc.gov/niosh/work-hour-training-for-nurses/longhours/mod2/19.html','2020 Mar 31',
    '通常夜睡者的晨间亮光有助时相提前、晚间亮光可使时相推后；见光时机依睡眠节律而异。',
    '职业健康培训只支持稳定光暗机制和行为安排，不据此给所有人统一照射分钟、光强或轮班治疗，也不承诺晒太阳治疗抑郁。',
    '已读完整短页定义、规律夜睡者晨晚相反效应与特殊时段，核Last Reviewed 2020-03-31；未用旧培训代替2026SWD指南。')
website(15,'National Institute of Mental Health','Seasonal affective disorder','https://www.nimh.nih.gov/health/publications/seasonal-affective-disorder','2023',
    '持续随季节出现的情绪与功能异常需评估；临床光疗使用滤紫外线灯箱，眼病和光敏药者需额外监督。',
    '季节性抑郁治疗不能外推为普通心情不好晒太阳即可治愈；不把灯箱当晒黑/紫外线灯，不给读者照搬临床光疗参数。',
    '已读定义、症状、日光与节律解释、治疗及光疗安全段，核Revised2023；未采用维生素D或心理药物自行治疗方案。')
website(16,'National Heart, Lung, and Blood Institute','Insomnia: diagnosis','https://www.nhlbi.nih.gov/health/insomnia/diagnosis','2022 Mar 24',
    '就诊前记1–2周作息、午睡、白天困倦、咖啡因酒精和活动；病史与检查区分药物、节律或其他睡眠疾病。',
    '日记帮助评估而非自诊；不要求所有人自行做全部睡眠监测或抽血，不把3个月慢性定义当此前症状无需处理。',
    '已打开短页并实际审读日记、病史、体检和检查路径，核2022-03-24更新及慢性失眠3个月/每周3夜表述；正文未让读者以阈值替代就诊。')

entries=[]
def add(n,title,summary,plain,benefit,evidence,source_numbers,scope,pin=False,notes='',ages=None,unit='sleep-u2'):
    refs='；'.join(f'[@LIFE-SLP-S{i:02d}]' for i in source_numbers)
    entry=dict(id=f'sleep-{n:03d}',chapter_id='sleep',unit_id=unit,ordinal=n,title=title,summary=summary,
        fields=dict(cost='',plain=plain,benefit=benefit,evidence=evidence,sources=refs,notes=notes),
        audience=dict(age_groups=ages or ['adult','older'],sexes=['all'],scope_note=scope,safety_pin=pin),
        clinical_review_status='not_clinically_reviewed',content_checked_at=DATE)
    assert 100<=len(summary)<=180,(n,len(summary));entries.append(entry)

add(1,'开车犯困就安全停车，别靠咖啡、开窗或音乐硬撑',
    '频繁打哈欠、压线或记不起刚驶过的路段，就该安全停车并换人或改乘其他交通工具。咖啡和短小睡只能短暂提神，醒后仍困不能继续开；睡够仍反复突然打瞌睡，也需要评估睡眠疾病、药物或其他原因。把通勤安全排在赶时间前面，不等真正睡着才处理。',
    '出现眼皮撑不住、反复压线或漏看路标时，尽快在合法安全地点停车，交给清醒驾驶者或改用其他交通方式。开窗、拍脸、音乐和能量饮料都不能代替睡眠。咖啡配合约20分钟短小睡有时只能暂时提高警觉，不能据此保证已经恢复驾驶能力；醒后仍困就不继续开。夜班下班前先安排返程，含嗜睡警示的药物也要核对。[@LIFE-SLP-S01]\n\n已经留够睡眠却仍反复不受控地打瞌睡、发生险情，带上作息和用药记录去睡眠门诊或相应专科；打鼾憋醒另查睡眠呼吸暂停。[@LIFE-SLP-S16]',
    '减少困倦驾驶和高风险操作造成的伤害，避免把短暂清醒误当成睡眠已经补足。',
    'C，交通安全与睡眠医学实践建议；没有给个人估算事故率，短时提神效果不等于恢复全部能力。',[1,16],
    '供成年驾驶者、夜班及高风险作业者阅读；疲劳或服药后不能由阅读筛选判断是否可以开车。',True,unit='sleep-u1')

add(2,'失眠反复影响白天，就做睡眠评估并优先了解CBT-I',
    '有时间睡却长期难入睡、易醒或早醒，还影响白天，就该记录作息并安排评估。失眠认知行为治疗简称CBT-I，有结构化的睡眠安排、刺激控制和认知调整，并不只是听放松音乐；它是成人慢性失眠的一线选择。习惯调整仍有用，但别靠反复换枕头、助眠香薰或保健品拖着。',
    '先用一到两周记录上床、入睡大概时间、夜醒、起床、午睡、咖啡酒精及白天困倦，带去评估。睡眠日记帮助区分睡眠机会不够、生物钟错位和失眠，也会提示是否需要查打鼾、疼痛或药物因素。[@LIFE-SLP-S16]\n\nCBT-I是“失眠认知行为治疗”：由受训人员把睡眠安排、床与睡眠的联系、放松和对睡不着的担忧一起调整。成人慢性失眠优先考虑这种完整治疗，可面对面或通过合适的线上服务进行；只给一张早睡清单或播放音频的App，不自动等于完整CBT-I。不要照网帖自行大幅压缩睡眠时间，有明显白天困倦或需要开车时尤其要先讨论安全。[@LIFE-SLP-S02][@LIFE-SLP-S03]',
    '获得针对失眠本身的可执行治疗路径，减少长期试用品而没有处理原因的负担。',
    'A，多组分CBT-I有成人慢性失眠临床依据并获指南强推荐；日记与就诊准备为C。推荐强度与本指南ABC分开理解。',[2,3,16],
    '以成人及老年慢性或反复失眠为主；儿童、躁狂发作或其他复杂睡眠病的方案另行评估。',unit='sleep-u3')

add(3,'先分清褪黑素用途和每份毫克数，别靠不断加量解决失眠',
    '褪黑素主要帮助传递夜晚和生物钟信号，不能把所有睡不好都当成缺这种激素。购买时看每份毫克数、剂型和实际标签，不把一粒软糖当固定剂量，也不叠加多款。中国相关保健食品用量范围为每日1至3毫克；这不是人人需要补的量，更不是长期失眠的统一处方。',
    '褪黑素是身体在黑暗中分泌、参与睡眠时序的激素。持续失眠先查作息与病因；一般速释保健品不是成人慢性失眠的一线治疗，晚睡晚起的节律问题、时差和某些特定缓释药物方案要分开。欧洲对55岁及以上部分原发失眠者有特定缓释处方制剂选择，不能据此推所有助眠软糖有效。[@LIFE-SLP-S04][@LIFE-SLP-S07]\n\n决定尝试前，先查国内保健食品注册或备案信息，算清“一次几份×每份多少mg”的每日总量。国内相关原料目录的每日用量范围为1–3mg，按所购产品标示及专业建议使用，不把进口10mg、大瓶口服液或多款叠吃当升级；用后头晕、白天困或反而影响生活，应停止自行加量并复评。超量、混酒和长期替代检查属于不合理使用，不能简单用是否成瘾判断安全。[@LIFE-SLP-S05][@LIFE-SLP-S04]\n\n速释与缓释的服用时点、进食要求和适用人群不同。例如EMA的Circadin 2mg缓释处方制剂，对符合适应证的55岁及以上患者规定餐后、睡前1–2小时服用、最长13周，且整片吞服；这套方案只属于该药，不能移给任意中国保健食品。未成年人、孕哺及备孕者不自行照成人方案；服抗凝药、抗癫痫或镇静药、患自身免疫/肝肾疾病者先核相互作用与限制。服后困倦不驾驶。[@LIFE-SLP-S06][@LIFE-SLP-S04]',
    '把剂量、剂型与真正目标对上，减少叠加、错误服用和用助眠产品掩盖持续疾病。',
    'B，剂型与人群不同，褪黑素收益和长期安全存在限制；国内标示与特定药品操作为C，不能由标签推整个品类疗效。',[4,7,5,6],
    '供成人和老年人比较产品与用法；保健食品剂量范围不构成个人用药处方，孕哺与具体疾病需另核。',unit='sleep-u3')

add(4,'跨时区先安排睡觉与见光时间，再决定是否用褪黑素',
    '倒时差是身体时钟与目的地时间没对上，先根据出发地、目的地和停留天数安排睡眠与见光。褪黑素吃在错误时点可能越调越乱，不能按北京时间每晚固定补，更不能用大剂量弥补缺觉。方向和跨越时区越复杂，越需要把行程带给专业人员确认时机。',
    '跨多个时区后白天困、晚上醒，往往是内部时钟还留在原地。出发前几天可逐步把作息往目的地靠近；到达后按当地安排进餐、睡眠和适当见光，避免靠长时间白天补觉把夜间睡意冲掉。短停留是否调整要看行程。[@LIFE-SLP-S08]\n\n确有需要再讨论褪黑素。CDC时差章节指出，约0.5–1mg常已足以推动时相变化，不推荐高于5mg；这里是成人时差的临床参考，不是中国保健食品标签，也不是“越低必然适合所有人”。吃在内部生物钟的错误时段可加重错位，所以让医生或药师按跨越方向、时区、到达时刻与原作息确定时间，并核对实际剂型和服后活动。不要因一晚未睡着就凌晨补几次，更不在准备开车前用。[@LIFE-SLP-S08][@LIFE-SLP-S05]',
    '在需要时用较清楚的节律策略缩短适应过程，减少错误用药时点造成的额外困倦。',
    'B，褪黑素对部分成人时差有帮助，方向、时机和个体条件影响效果；旅行安排与用法安全为C。',[8,5],
    '供成年旅行者使用；不把时差方案套到轮班、儿童、孕哺或一般慢性失眠。',unit='sleep-u3')

add(5,'把咖啡因截止时间往前移，别用睡前酒精换入睡',
    '下午或晚上的咖啡、浓茶和能量饮料，可能让你到了该睡时仍清醒；总量和喝的时间要一起看。先试把最后一次咖啡因提前，再记录睡眠是否改善。酒精虽然可能让人更快困，后半夜却更容易睡碎，不能当助眠药，也别和镇静药或褪黑素叠用。',
    '咖啡因存在于咖啡、茶、可乐、能量饮料和部分巧克力，别只算咖啡杯数。它的影响可持续到8小时，个体差异也大；若晚上难睡，可以先把最后一次咖啡因放到计划睡觉前约8小时或更早，连续记录是否改善。这个间隔是调整起点，不是过了8小时就一定没有作用。[@LIFE-SLP-S09]\n\n睡前酒精可能让入睡更快，却让后续睡眠较浅、更易醒；不把晚安酒或含酒助眠饮品当保养。需要夜班提神时，尽量把咖啡因放在班次前半段，给下班后的睡眠留出空间。已经用镇静助眠药或褪黑素时，也不要自行混酒。[@LIFE-SLP-S03][@LIFE-SLP-S09][@LIFE-SLP-S06]',
    '减少可避免的入睡困难与夜醒，保留咖啡因真正需要的提神用途而不侵占下一段睡眠。',
    'C，机构睡眠与用药安全指导；8小时是实用参考，不能替代个体代谢或药物相互作用判断。',[9,3,6],
    '以成人及老年规律作息者为主；轮班按实际计划睡眠调整，不能将咖啡因当疲劳驾驶许可。')

add(6,'午睡先试短而靠前，轮夜班另做睡眠和通勤安排',
    '白天犯困可先试较早、约20分钟的短小睡，夜里本就难入睡时更要留意是否被午睡影响。夜班者需要保护完整的白天睡眠，不能只靠咖啡和零碎打盹。睡醒后会有短暂迟钝，彻底清醒前别立即开车或做危险操作；持续适应不了班次就评估轮班睡眠问题。',
    '普通日间小睡可以从较早下午、约20分钟开始，设好结束提醒。醒后感觉好、晚上也睡得着才算适合；若越睡越晚、夜间更难入睡，就提前或减少午睡，别把这个成人起点当所有年龄的硬性时限。[@LIFE-SLP-S09]\n\n夜班另看：先保住下班后的主睡眠，卧室遮光、降噪，咖啡因尽量限在班次前半段。上首个夜班前的计划小睡可讨论，但醒后睡眠惯性会暂时影响反应，给清醒留时间再开车或上机操作。持续班上过度困、白天睡不着而影响生活，应带班表和睡眠记录评估是否轮班工作障碍。[@LIFE-SLP-S09][@LIFE-SLP-S10]\n\n2026年AASM指南对确诊成人轮班障碍的部分情境给出褪黑素等条件性选择，证据多为低或很低确定性。频繁轮转者未必能把生物钟完全调成夜班模式；别自己把大剂量褪黑素、强光和提神药叠成一套通用方案。[@LIFE-SLP-S10]',
    '以更少干扰夜间睡眠的方式缓解短时困倦，并为夜班者保留主睡眠及安全返程。',
    'B，成人轮班障碍的小睡/褪黑素等有条件性、低或很低确定性证据；普通午睡安排与醒后安全为C。',[9,10],
    '供成人及老年人比较小睡与轮班安排；不将成人20分钟建议套到婴幼儿，具体药物不能由班次筛选自动生成。')

add(7,'睡前听声音先设低音量和定时，别把入耳耳机戴整夜当必需',
    '睡前听音乐可以按舒适偏好选择，但整夜播放会增加声音暴露，入耳设备还可能带来压迫、耳垢和潮湿问题。先处理房间噪声，想听时从低音量、定时停播或合适外放开始；被环境声吵醒也可试合适耳塞。白噪音、粉红噪音和睡眠耳机都没有人人适合的保证。',
    '没有耳机就睡不踏实，先问你要的是放松还是隔绝噪声。房间能安静就不必额外播声；想听一段音乐，可用低音量并定时停播。外放能减少耳道机械压迫，但也要照顾同住者与总音量。侧睡时耳塞式耳机压痛、刚洗澡耳内潮湿、有痒痛流液时都不宜继续硬戴；出现耳痛、耳鸣或听力改变应停用并检查。[@LIFE-SLP-S11]\n\n听觉风险取决于音量和时间，不能把手机60%的滑块、降噪或骨传导标签当零损伤保证；还要确保能听见重要警报。需要隔绝环境噪声可试合适、清洁的耳塞，出现刺激就调整。[@LIFE-SLP-S12][@LIFE-SLP-S11]\n\n对白噪音机或睡眠音频，先短试实际是否更好睡，不追求整夜大声覆盖。2026年一项25名成人、七夜实验室研究中，特定粉红噪音条件减少快速眼动（REM）睡眠，耳塞较能缓解环境噪声影响；这提示助眠声并不必然改善睡眠，不能推成所有雨声或所有音量都有害，也不能据此证明某款耳塞长期最佳。[@LIFE-SLP-S13]',
    '保留喜欢的睡前放松方式，同时减少不必要的持续声暴露、耳道刺激和对产品宣传的误判。',
    'B，特定粉红噪音与耳塞有小型短期实验室比较；耳机压迫、音量与定时安全为C，没有长期品牌排名。',[11,12,13],
    '供青少年、成人和老年人选择夜间音频用品；婴幼儿、耳病或特殊听觉设备另行评估。',ages=['teen','adult','older'],unit='sleep-u4')

add(8,'规律夜睡者白天多接触自然光，别把晒太阳当情绪治疗处方',
    '规律夜睡的人起床后安排适当户外自然光，晚上减少强光，有助把昼夜节律放回合适的位置。这里需要的是合适时机的见光，不是把皮肤晒伤，也不是盯着太阳看。若情绪与睡眠反复随季节明显变化、影响生活，应安排评估；普通晒太阳和临床灯箱治疗不能混同。',
    '对通常晚上睡、白天活动的人，可以把起床后的一段时间安排在户外，白天也适当走动，睡前减少强光。晨间和晚间的光对生物钟方向不同，所以不规定人人同一晒太阳时数；夜班或时差要按目标睡眠安排，不能照抄晨光方案。做好日常防晒，不直视太阳。[@LIFE-SLP-S14][@LIFE-SLP-S09]\n\n心情短时不好时，出门走动和见光可以是舒服的日常选择，不能保证解决情绪问题。若每到某一季节反复明显低落、睡眠食欲改变并影响生活，要评估是否存在季节性情感障碍等原因，即是否有随季节反复的抑郁发作。临床光疗使用滤除紫外线的特定灯箱，并有时机和剂量要求；眼病或服光敏药者尤其需要监督，不用晒黑灯、紫外线灯或暴晒替代。[@LIFE-SLP-S15]',
    '用环境光支持正常睡眠与白天清醒，把日常习惯和需要专业处理的持续异常分开。',
    'C，节律与机构生活指导；季节性疾病光疗有专门适应证，不能从其疗效推导一般日晒都可治疗抑郁。',[14,9,15],
    '供通常夜间睡眠的成人与老年人阅读；轮班、时差和特定眼病不自动适用同一见光方案。')

for name,value in [('sleep-entries',entries),('sleep-sources',sources)]:
    (HERE/(name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
audit=dict(date=DATE,entries=len(entries),sources=len(sources),clinical_review_status='not_clinically_reviewed',
    approach='成人/老年睡眠决策为主；机构与指南定位问题，原始人体研究核具体产品结论；无可靠费用则省略。',
    input_scope='新增8条，保留原basics001睡眠机会/起床及basics002睡眠呼吸暂停，不重复旧正文。',
    corrections_and_limits=[
        'NCCIH2024慢性失眠一个月定义未采用，未将其2014轮班综述作为2026最终结论。',
        '2026-10-24AASM轮班指南PubMed和PMC正文已核，条件性建议与ABC分开，未复制刺激药/强光个人处方。',
        '中国保健食品1–3mg每日范围、CDC成人时差0.5–1mg临床参考、EMA特定欧洲2mg缓释方案分别限定，不能彼此替代。',
        'NHS时差页与用药页的推荐差异不用于制造统一疗效结论；未采用NHS6mg加量和每年16疗程作为中国通用规则。',
        '2026粉红噪音试验只核完整摘要与题录，不能推所有白噪音有害；全文资助未完整核读，如实公开。',
        '欧洲2023指南仅核摘要、题录及出版方索引相关段，未称36页全读；具体缓释用法另外核EMA当前2025产品资料。',
        '耳机风险机构患者指导与原始睡眠研究分列，不根据感染机制给个人发生率，不按手机滑块百分比保证安全。',
        '情绪仅保留季节性异常识别与光疗/日晒边界，不写心理治疗百科或多说废话有医学疗效。',
    ],
    reviewed_fields=['title','summary','plain','benefit','evidence','sources','notes','audience'],
    summaries={e['id']:len(e['summary']) for e in entries},
    disposition='ready_for_independent_editorial_review')
(HERE/'sleep-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(entries=len(entries),sources=len(sources),summaries=audit['summaries']),ensure_ascii=False))
