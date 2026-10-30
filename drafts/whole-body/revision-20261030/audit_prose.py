"""Record explicit editorial replacements, without mutating the source chapters."""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BODY = ROOT / 'drafts/whole-body'
paths = sorted((BODY / 'baseline/chapters').glob('*.json')) + sorted((BODY / 'chapters').glob('*.json'))
books = {p.stem: (p, json.loads(p.read_text(encoding='utf-8'))) for p in paths}
entries = {e['id']: (p, e) for p, ch in books.values() for e in ch['entries']}
patches = []

def add(eid, field, old, new, reason='把写作过程说明改为读者可以使用的信息，保留医学条件与引文。'):
    p, obj = entries[eid]
    if field.startswith('fields.'):
        value = obj['fields'][field.split('.')[1]]
    else:
        value = obj[field]
    assert value.count(old) == 1, (eid, field, old)
    assert old != new
    patches.append(dict(file=p.relative_to(ROOT).as_posix(), target='entry', id=eid,
                        field=field, old=old, new=new, reason=reason))

def whole(eid, field, new, reason='删除内部写作口径，保留对读者有用的适用范围或操作限制。'):
    p, obj = entries[eid]
    old = obj['fields'][field.split('.')[1]] if field.startswith('fields.') else obj[field]
    add(eid, field, old, new, reason)

def unit(cid, uid, old, new):
    p, ch = books[cid]
    obj = next(u for u in ch['units'] if u['id'] == uid)
    assert obj['intro'].count(old) == 1
    patches.append(dict(file=p.relative_to(ROOT).as_posix(), target='unit', id=uid, field='intro',
                        old=old, new=new, reason='目录导语只介绍选读路径，不叙述筛选实现或内部编辑过程。'))

def chapter(cid, old, new):
    p, ch = books[cid]
    assert ch['intro'].count(old) == 1
    patches.append(dict(file=p.relative_to(ROOT).as_posix(), target='chapter', id=cid, field='intro',
                        old=old, new=new, reason='面向读者说明内容用途，删去内部稿件状态；不伪称经过临床签审。'))

# The site contains no step-by-step pictures. Product-specific operation belongs to
# the identified manufacturer's instructions, never to an imaginary local figure.
add('private-021', 'fields.plain', '都要按本款图示操作，把取出绳留在外面。',
    '第一次使用前，先阅读所购型号随包装附带的说明书；导管款和指入款的放入步骤不同，不互相套用。放好后把取出绳留在外面。',
    '删去并不存在的本站图示；明确实际可获得的说明书及型号差异。')
add('private-022', 'fields.plain', '按本款图示折叠后放入，确认展开并处在舒适位置。',
    '杯通常先把杯口折小再置入，碟通常先把盘缘捏窄、向后送入，再让前缘支在耻骨后方。初次使用前，到品牌官网查看所购型号的说明书或使用演示，学清它的折叠、放入和取出步骤；找不到完整说明就先选体外巾垫。放入应舒适，不靠忍痛把它推到位。',
    '以制造商可核实的型号操作补足文字说明，不宣称页面有图或给所有杯碟一套通用折法。')
add('private-023', 'fields.plain', '本次核到的Mooncup网页要求4–8小时排空，Flex可复用碟网页要求至少每12小时取出排空清洗。',
    '例如，Mooncup该款杯的官方说明要求每4–8小时排空，Flex该款可复用碟则要求至少每12小时取出排空清洗。')

# Remove implementation commentary and claims that contradict strict matching.
unit('ears', 'ears-u1', '先处理不能等的听力变化；年龄筛选不隐藏这条急症入口。', '突然听不清先安排当天评估，不要等清耳垢或买滴耳液后再说。')
chapter('private', '遇到紧急症状先看第一单元，不因年龄、性别或验孕结果自行排除风险。',
        '遇到剧痛、晕厥、明显出血或持续异常，先找对应的紧急处理建议；不要用一次阴性验孕结果排除妊娠相关急症。')
add('ears-009', 'fields.plain', '本稿不把年龄筛选结果当穿孔许可。', '未成年人穿孔还需满足当地规定，并与监护人、操作方确认是否适合。')
add('abdomen-001', 'fields.notes', '本条保留在人群筛选中；不提供跨年龄通用止痛或通便处方。', '急性重痛时先查明原因，不把成人止痛或通便用法直接套给儿童。')
add('hands-001', 'fields.notes', '这条在人群筛选中保留为危险信号入口，不提供跨年龄通用药物剂量。', '抗感染治疗取决于病因、严重程度、年龄与用药情况，不自行套用他人的药物剂量。')
add('neck-011', 'fields.notes', '本条危险信号在人群筛选中保留；儿童外伤不照抄成人训练或用药。', '儿童外伤需要针对年龄和受伤情况检查，不照抄成人训练或用药。')
add('neck-014', 'fields.notes', '女性与男性都可阅读；孕哺和长期基础病会改变方案，不由筛选标签自动推定。', '孕哺、糖尿病等基础病和正在使用的药物会影响检查与治疗选择，就诊时主动说明。')
add('private-002', 'fields.notes', '性别筛选不判断是否存在子宫或妊娠可能；绝经后、术后或其他器官状态应主动告知。', '就诊时主动说明妊娠可能、绝经情况、既往手术及实际保留的生殖器官；这些信息会改变检查方向。')
add('eyes-031', 'fields.notes', '本条给家长和学生安排日常活动使用；儿童视力筛查、验光和近视控制的复查节点另按诊疗方案，不由读书时长或本页年龄筛选替代。', '户外和间歇用眼不能代替视力筛查、验光与近视控制复查；复查时间按孩子的检查结果和治疗方案安排。')
add('eyes-032', 'fields.notes', '本条的儿童入口不包含一张通用药物处方，也不以筛选中的0–11岁或12–17岁替代具体产品批准年龄、禁忌或监护能力。', '近视控制产品的批准年龄、禁忌和护理要求各不相同，不能只按“儿童”或“青少年”标签决定使用。')
add('feet-011', 'fields.notes', '年龄筛选不排除年轻人出现甲部肿瘤；本条面向成人读者，异常变化需要实际检查。', '年轻人也可能出现甲部肿瘤；新生、变宽或不断变化的色带需要实际检查。')

# Head and face: remove manuscript wording and needless meta-disclaimers.
add('hair-007', 'fields.plain', '本稿没有直接研究支持只凭“负离子”“胶原风”等标签就保证修复或生发。', '“负离子”“胶原风”等标签本身不能证明修复或生发效果；购买时先看温度控制、风量和实际使用感受。')
add('hair-014', 'fields.plain', '每天梳一百下、越用力按摩越能生发，不是本稿能从这些护理资料推出的任务。', '不要把每天梳一百下、用力按摩当作生发任务；梳理的目标是理顺头发、减少拉扯。')
add('hair-013', 'summary', '专用游泳洗发水可以比较，但本稿没有证据证明所有人都必须另买一瓶。', '常规洗护已经能洗净、发丝也不明显粗涩时，不必仅为“游泳专用”再加一瓶。')
add('hair-013', 'fields.plain', '本稿没有直接头对头资料证明每个偶尔游泳的人都要额外买一瓶，先看常规方案能否完成清洁、发丝是否仍明显粗涩。', '是否需要专用产品，先看常规洗护能否洗净、发丝是否仍明显粗涩；现有资料不足以证明偶尔游泳的人都必须额外购买。')
whole('hair-001', 'fields.evidence', entries['hair-001'][1]['fields']['evidence'].replace('专业学会实践指导与按头皮、发丝需求作出的编辑选择', '专业学会实践指导；洗护选择取决于头皮和发丝需求'))
add('hair-003', 'fields.evidence', '本轮资料不足以给全部表活或含硅/无硅成品统一排名。', '现有资料不足以给全部表活或含硅/无硅成品统一排名。')
add('hair-004', 'fields.evidence', '学会护理指导与按需求逐步加品的编辑建议；未给所有发膜作头对头疗效排名。', '学会护理指导；逐步增加用品依据实际需求，不代表不同发膜已作直接疗效比较。')
add('hair-006', 'fields.evidence', '购买顺序属于编辑取舍。', '购买优先级按受损程度、需求和维护负担判断，不代表全部成品已有直接比较。')
add('hair-008', 'fields.evidence', '专业使用指导与减少摩擦热负担的编辑建议；未找到直接试验来排列剪裁或蓬松产品胜负。', '专业使用指导；减少摩擦和热负担有护理依据，但不同剪裁和蓬松产品缺少可直接比较的试验。')
add('hair-021', 'fields.evidence', '购买优先级是C类编辑取舍，不是药物与设备的疗效排名。', '购买优先级按证据、维护与风险判断，不能理解为药物和设备已作直接疗效排名。')
add('lips-002', 'fields.evidence', '不叠加同目标产品是基于需求与耐受的编辑选择。', '是否增加同用途产品，应看干裂是否改善及皮肤能否耐受。')
add('skin-004', 'fields.plain', '喷雾可以按个人舒适需要使用，但本章未找到足以证明它比正常保湿更值得优先购买的直接证据。', '喷雾可以为即时舒适使用，但现有依据不足以支持把它排在正常保湿之前。')
add('skin-011', 'summary', '按摩也没有被本章证据证明能消掉眼袋', '按摩也没有可靠证据证明能消掉眼袋')
add('skin-011', 'fields.plain', '本章没有足够直接证据推荐按摩消除眼袋。', '不要指望按摩消除眼袋：现有依据不足以支持这种效果。')
add('skin-014', 'fields.evidence', '专业学会患者指导间接总结红光潜在效果，本稿未直接审读具体设备疗效试验，不作B级直接研究或全品类有效率判断；', '红光部分依据专业学会患者指导的间接总结，不能据此保证某款设备的效果或整个品类的有效率；')
add('skin-015', 'fields.evidence', '本条是咨询、资质核验和并发症分流指导，未据此给不同医美项目作疗效排行榜；', '咨询、资质核验和并发症分流指导，不能据此给不同医美项目作疗效排名；')
chapter('skin', '好看、舒服和节省时间都可以是正当收益。我们给出具体选择，也标明哪些来自人体研究、哪些是临床建议、哪些仍有争议；没有可靠当前价格的项目不编成本。本文面向年轻成人，不代替个体诊断，尚未经过皮肤科医生临床审阅；遇到不明斑痣变化、持续恶化或严重反应时，先按对应条目处理。',
        '好看、舒服和节省时间都可以是正当收益。选择产品时，把实际效果、刺激风险和维护负担一起比较；人体研究、临床建议与仍有争议的判断，会在证据栏说明。遇到不明斑痣变化、持续恶化或严重反应时，先按对应条目处理，不用美容护理代替检查。')
add('nose-003', 'fields.notes', '本条只处理鼻表面的皮肤入口；[黑头与皮脂丝的完整护理](#/entry/skin-018)放在面部皮肤章，避免在鼻子章复制一套用药。', '需要进一步处理黑头或皮脂丝时，继续读[黑头与皮脂丝的完整护理](#/entry/skin-018)；鼻腔清洁用品不用于治疗鼻表面的粉刺。')
add('ears-001', 'fields.notes', '本条不是把皮肤清洁剂灌进耳道的教程。', '皮肤清洁剂不要灌进耳道。')
add('ears-007', 'fields.notes', '本条不是教人在潜水时硬撑耳痛。', '潜水时出现耳痛也不要硬撑继续下潜。')
add('ears-009', 'fields.notes', '本条不教自行穿刺。', '不要在家自行穿刺。')
add('ears-010', 'fields.evidence', '不同机构对部分护理细节存在差异，本条不混用互相冲突的高频消毒或转动方案。', '不同机构对部分护理细节存在差异；不要自行把高频消毒、反复转动和其他护理方案混在一起。')
add('ears-010', 'fields.notes', '本条不把任何油膏列为人人必买。', '油膏并非人人必需。')
add('ears-011', 'fields.notes', '本条不推荐给婴幼儿选耳夹。', '不要给婴幼儿佩戴容易脱落的小耳夹。')
add('oral-001', 'fields.notes', '本条面向成人，不套用儿童牙膏用量；不吞咽牙膏。', '成人与儿童的牙膏用量不同，不把成人用量照搬给孩子；不要吞咽牙膏。')
add('oral-022', 'fields.notes', '本条以成人与老年缺牙为主；', '成人缺牙与青少年发育期缺牙的处理不同；')
add('oral-023', 'fields.notes', '本条讨论可自行取下的义齿；', '活动义齿可自行取下清洁；')
add('skin-002', 'fields.notes', '本条不把睡前偶尔没卸妆直接写成必然长痘或加速衰老；', '偶尔一次睡前没卸妆，不代表必然长痘或加速衰老；')
add('skin-019', 'fields.notes', '本条也未要求每个年轻人按同一周期做全身筛查。', '年轻人也不需要不分风险地按同一周期做全身筛查。')
add('skin-018', 'fields.evidence', '粉刺药物的疗效依据见痤疮指南，但本条不提供自行诊断后的处方。', '粉刺药物的疗效依据见痤疮指南；是否需要用药仍取决于实际皮损和禁忌。')
add('skin-016', 'fields.notes', '本条列药物类别用于理解治疗方向，未给处方、剂量或疗程，也未将美国药品可得性搬到中国。', '这些药物类别用于理解治疗方向；具体处方、用法和能否在当地购买，需要按实际诊断及中文药品说明核对。')
add('skin-009', 'fields.evidence', '本条没有把单项研究当成所有配方的通用保证，也不据此评出浓度冠军。', '单项研究不能保证所有配方都有相同效果，也不足以选出一个通用的最佳浓度。')
add('skin-010', 'fields.notes', '本条不提供处方浓度、每日次数或加量表；不同国家非处方权限也不能互相套用。', '具体浓度、频次和调整方式需按产品及治疗方案确定；不同国家的非处方权限不能互相套用。')

# Body: convert editorial caveats into useful boundaries rather than reciting
# instructions that were meant for the author.
add('chest-009', 'fields.plain', '本稿不把剃光列作人人必须完成的卫生动作，也不承诺留毛一定更有味。', '剃光不是人人必须完成的卫生动作；留毛也不等于一定更有味。')
add('legs-008', 'fields.plain', '没有关节病或明确需要时，本稿不推荐为日常健康一次配齐护膝、矫形鞋垫和矫腿器，也不把辅助用品代替力量训练。', '没有关节病或明确需要，不必为了日常保养一次配齐护膝、矫形鞋垫和矫腿器；辅助用品也不能代替力量训练。')
add('legs-009', 'fields.plain', '对髋膝骨关节炎，本稿不建议把氨糖、软骨素或其组合当作日常核心治疗：', '对髋膝骨关节炎，不建议把氨糖、软骨素或其组合当作日常核心治疗：')
add('neck-009', 'fields.notes', '本稿不提供穴位、进针深度或孕期针刺处方，也不把某地医保可报销当有效性证明。', '针灸由具备相应资质的医疗人员操作；孕期等特殊情况先说明。医保能否报销，不代表某种疗法已经证明有效。')
add('neck-012', 'fields.notes', '本条不替读者安排注射次数或强度；注射与训练应围绕具体诊断。', '注射次数、强度与训练安排需要围绕具体诊断和恢复情况调整，不照搬他人的疗程。')
add('neck-003', 'fields.notes', '学生可借鉴任务分段与舒适支撑原则；本条未逐项评估儿童课桌尺寸或脊柱发育方案。', '学生可借鉴任务分段与舒适支撑原则；儿童课桌尺寸与支撑要按实际身高、发育和使用任务调整，不能照搬成人尺寸。')
add('neck-005', 'fields.notes', '本条不提供儿童敷用时长；皮损和新近重外伤先按相关诊疗路径。', '儿童敷用的时间和保护措施要单独确认；有皮损或新近重外伤时先检查，不按普通酸痛反复热敷。')
add('neck-010', 'fields.notes', '不编通用安全转速、力度和每日时长；设备广告的冲击深度不是临床疗效大小。', '不同设备的转速、力度和接触时间不能直接互换；广告里的冲击深度也不代表疗效更强。')
add('abdomen-003', 'fields.notes', '原有处方药不要自行因本条停用；', '不要自行停用原有处方药；')
add('abdomen-004', 'fields.notes', '本条以成人腹壁鼓包为主；', '成人腹壁鼓包与儿童脐疝的评估不同；')
add('abdomen-005', 'fields.notes', '本条不提供益生菌或消化酶的通用处方；拟试用时说清希望改善的症状和复评点。', '益生菌或消化酶并非所有腹胀都适用；拟试用时先说清希望改善的症状，以及多久无效就停止或复查。')
add('anal-005', 'fields.notes', '不编统一水温、压力数值或必需冲洗时长；不同设备档位不能直接互换。', '不同冲洗器的档位不能直接互换；以不烫、不刺痛、能温和冲净外部为准，不追求更高水压或更长时间。')
add('anal-007', 'fields.notes', '本条主要供成人生活调整与记录。', '成人的生活调整和记录方法不能直接当作儿童或孕哺期的药物方案。')
whole('basics-001', 'fields.notes', '睡眠受作息、压力、环境、疾病和药物等共同影响，不要把所有失眠都归咎于蓝光，也不必把“运动必须离睡前四小时”当作人人适用的硬规定。')
add('basics-005', 'fields.notes', '本条不判定任何碱水、矿泉水或电解质品牌的全部疗效。', '不能只凭“碱性”“矿物质”或“电解质”标签判断一种饮料的实际用途。')
whole('basics-006', 'fields.notes', '上述时长是一般健康活动的最低参考，不是伤病康复或孕期运动处方；有相关情况时另订计划。')
add('basics-007', 'fields.notes', '儿童与孕哺安全未被本篇成人标签自动保证。', '成人能用的补剂，不代表儿童或孕哺期也适用。')
whole('basics-008', 'fields.notes', '', '仅为作者避免照搬海外热线的指令，不是读者需要反复看到的正文；原有正文求助与急症信息保留。')
whole('basics-010', 'fields.notes', '体重管理需结合年龄、健康风险与当地适用标准；不要照搬海外BMI门槛、手术条件或他人的热量和用药方案。')
add('bodyskin-004', 'fields.notes', '孕哺期、儿童或既往药物过敏，需另核具体药物；本条未给维A酸类用药方案。', '孕哺期、儿童或既往有药物过敏时，要先核对具体药物；不要自行加入维A酸类治疗。')
add('bodyskin-010', 'fields.notes', '本条限成人身体外部皮肤；', '这里的脱毛方法用于成人身体外部皮肤，不用于黏膜；')
whole('bodyskin-011', 'fields.notes', '设备的能量和操作间隔要按实际型号与适用部位确定，不能照搬别人的档位。孕哺期与未成年人不套用成人方案。')
add('bodyskin-014', 'fields.notes', '是否需要任何医学检查取决于具体皮损；本条不提供所谓疤痕体质检测包。', '是否需要医学检查取决于实际皮损；不要仅凭“疤痕体质”宣传购买检测套餐。')
whole('bodyskin-020', 'fields.notes', '放疗剂量、适用年龄和生育安排应由熟悉瘢痕治疗的团队按实际部位与方案评估；妊娠或备孕情况要提前说明，不能照搬肿瘤放疗的安排。')
add('bodyskin-021', 'fields.evidence', '未找到可靠直接资料支持本条所述既有瘢痕购买目的，不等于已证明无效。', '现有可靠直接资料不足以支持把这些药物用于消退既有瘢痕疙瘩；这不等于它们在所有创面情境都无效。')
whole('bodyskin-021', 'fields.notes', '药品、化妆品和伤口护理用品的用途不同；买前核对当前批准用途和实际标签。2019年的药监问答可用于理解概念，不能代替当前产品的合规查询。')
add('chest-002', 'fields.notes', '本条不发布人人同一年龄、同一频率的超声或钼靶体检套餐。', '超声或钼靶筛查的起始年龄与频率要按个人风险和适用规范决定，不必购买人人一套的套餐。')
add('chest-004', 'fields.notes', '本条不提供抗雌激素剂量或自行停药建议；', '抗雌激素用药及原有药物调整需要评估，不自行配药或停药；')
add('chest-007', 'fields.notes', '本条不据补剂无效就推荐手术。', '补剂缺少效果证据，也不意味着应改做手术。')
add('chest-011', 'fields.notes', '此处不提供自行口服的剂量，不按国外商品清单直接下单。', '不按国外商品清单自行下单或照搬口服剂量。')
add('feet-001', 'fields.notes', '本条紧急信号对没有确诊糖尿病的人也有提醒价值；', '没有确诊糖尿病，也需要重视这些紧急变化；')
add('feet-004', 'fields.notes', '本条适用于青少年日常运动、宿舍和泳池场景；', '运动、宿舍和泳池场景都需要留意擦干和换湿袜；')
add('feet-007', 'fields.notes', '本条指明确摩擦造成的普通水疱，不覆盖烫伤、过敏或不明原因多发水疱。', '上述方法适用于明确摩擦造成的普通水疱；烫伤、过敏或不明原因的多发水疱，需要按病因处理。')
add('feet-009', 'fields.notes', '本条未把普通嵌甲的温水浸泡建议泛给糖尿病足；已有感觉或循环问题先检查。', '糖尿病、感觉下降或循环异常者，不照普通嵌甲的方法自行泡脚和修剪；先检查。')
add('feet-010', 'fields.notes', '本条不提供其剂量。', '儿童的具体药物与剂量要按年龄及批准用法另定。')
add('hands-002', 'fields.evidence', '不把去菌比例或个人感染概率作本条疗效承诺。', '实验去菌比例不等于个人感染风险会同比下降。')
add('hands-009', 'fields.evidence', '疗效比较为指导概括，不在本条提供统一治愈率或品牌排名。', '疗效比较为指导概括，不能保证个人治愈率，也不足以给所有品牌排名。')
add('hands-009', 'fields.notes', '本条不把英国OTC分类或美国批准自动套到中国。', '英国非处方分类或美国批准情况，不代表中国市场的处方权限与批准用途相同。')
add('hands-010', 'fields.notes', '本条是尽快安排检查，不是所有色带都要急诊；', '不断变化的色带要尽快安排检查，但不代表所有色带都需要急诊；')
add('hands-011', 'fields.notes', '本条不把减少暴露解释为证明频繁美甲安全；', '减少暴露不能保证频繁美甲没有风险；')
add('legs-002', 'fields.notes', '本条没有提供抗凝药物选择或剂量。', '不要自行购买抗凝药试治或照搬他人的剂量。')
add('legs-004', 'fields.plain', '不能用本条省去必要影像。', '不能因已有一张旧影像报告就省去本次必要检查。')
add('legs-005', 'fields.plain', '不能因为本条自行停用。', '不要自行停用已经因骨折、术后等原因安排的支具。')
add('legs-006', 'fields.notes', '本条不替代伤后返场评估。', '伤后恢复运动还需要按实际损伤与功能评估，不能只凭疼痛减轻就返场。')

# Private care notes had several audit-only source/date explanations. Retain them
# in the source ledger/audit, while the reader receives their practical meaning.
add('private-001', 'fields.notes', '本文不提供自行复位或跨年龄药物剂量。', '不要自行扳转睾丸试图复位，也不照搬其他年龄的药物剂量。')
whole('private-006', 'fields.notes', '阴囊皮肤瘙痒与睾丸内部疼痛不是同一问题；出现突然疼痛、持续不退或静息仍痛，按[睾丸急症](#/entry/private-001)处理。', '把资料日期与研究边界留在来源记录，正文备注突出相关急症区别。')
add('private-012', 'fields.notes', '不提供成人激素强度、频率、疗程供跨年龄套用。', '不要把成人激素的强度、频率和疗程照搬给孩子。')
whole('private-013', 'fields.notes', '儿童的包皮发育与用药要求不同，不照搬成人药膏或强行翻开；日常护理另见[儿童包皮](#/entry/private-005)。')
add('private-014', 'fields.notes', '这里只评价既有感染治疗，不由此断言蔓越莓对复发预防全无效；不照搬英国药房服务权限。', '治疗已经发生的感染，与预防以后复发是两个问题；不能用蔓越莓代替当前感染的检查和治疗，也不能据此断言它对所有复发预防都无效。')
add('private-016', 'fields.notes', '孕哺、激素相关肿瘤史及术后另核对，不提供阴道激素统一购买或用量。', '孕哺、激素相关肿瘤史及术后需要单独评估；阴道激素不是所有干涩者都能直接按同一用量购买的用品。')
add('private-020', 'fields.evidence', '不提供未经逐产品核查的材质优劣或疗效排名。', '不能据此给所有材质或品牌作疗效排名。')
add('private-027', 'fields.evidence', '本条依据NHS症状/药物指导；成人药物信息明确限18岁以上，未提供未成年人或孕哺剂量。', 'NHS症状与药物指导；其中成人药物信息限18岁以上，不能直接套给未成年人或孕哺期。')
add('private-035', 'fields.notes', '本条不意味着所有年龄、男女都在任一疫苗批准范围。', '不同疫苗批准的年龄和性别范围不同，不是任一型号都适合所有人。')
add('private-039', 'fields.notes', '本轮未逐一核中国所有单方制剂的注册供应，不推荐照海外品牌网购；', '中国大陆具体单方制剂的注册和供应需向正规药师或医疗机构确认，不按海外品牌清单代购；')
add('private-042', 'fields.notes', '未核得UPA在中国大陆当前批准与现场供应，不推荐代购，也不称其一定未获批。国内其他处方方案需当地评估，本篇不列自行用法。', 'UPA在中国大陆的批准与现场供应，应向正规药师或计划生育门诊确认；不要为代购某种海外药延误已有的正规紧急避孕服务。其他处方方案也需当地评估。')
add('private-043', 'fields.notes', '本条7天屏障采用CDC紧急避孕后的建议，不把它混为所有普通起始或漏服场景的统一规则。', '这里的7天屏障保护针对紧急避孕后的衔接，不是所有常规起始或漏服情形的统一规则。')
whole('private-047', 'fields.notes', '产后与哺乳期能选什么方法，取决于距分娩的时间、是否哺乳、血栓风险及具体方法。就诊时说明这些情况，不按统一的停乳天数或某个产后日期自行启停。')
add('bodyskin-021', 'summary', '本轮核到的资料不足以支持这个购买目的；', '现有可靠证据不足以支持这个购买目的；')
add('bodyskin-021', 'fields.plain', '针对康复新液，本轮检索没有核到足以推荐它使既有瘢痕疙瘩消退的可靠直接人体证据，因而不把它列为这一用途的优先购买项。', '目前缺少足以推荐康复新液使既有瘢痕疙瘩消退的可靠直接人体证据，因此不把它列为这一用途的优先购买项。')
add('private-040', 'fields.plain', '国内注射服务与具体成分有差异；本轮未核实全部贴片、阴道环的中国批准及供应，只作方法比较，不给海外购买入口。', '国内可获得的注射服务与具体成分有差异；贴片、阴道环的批准和供应也需向当地正规医疗机构或药师确认，不按国外商品清单代购。')
unit('private', 'private-u1', '睾丸痛、严重下腹症状、置入用品后的全身异常、持续勃起与近期暴露，都有单独的紧急入口。', '先判断症状是否需要立即急诊或当天评估，不用清洗、试药或等待检查结果拖延。')
unit('private', 'private-u2', '外阴、阴道、包皮和阴囊不采用同一套清洁动作；衣物先看合身干爽。', '不同部位需要不同的清洁动作；避免强行拉扯、过度冲洗和消毒，衣物先看合身干爽。')
unit('private', 'private-u6', '把感染预防、干涩疼痛、勃起射精和自我照护分开，不靠紧致、壮阳和延时营销包治。', '按感染预防、疼痛、舒适度或性功能困扰找对应建议，不靠一种“改善性能力”的产品包治。')

# Follow-up: every body entry (174 records) was actually read in full for title,
# summary, plain, benefit and notes. These issues were found by reading, not by
# treating a keyword hit as a substitute for editorial understanding.
add('anal-011', 'fields.plain', '医生可能指导晨起清洗和如厕前用胶带取样，再决定用药与家庭同时处理的安排。',
    '医生可能指导在早晨起床后、清洗和如厕之前，用胶带取样检查虫卵，再决定用药与家庭同时处理的安排。',
    '原句缺少停顿可能被理解为先洗再采样；重新核CDC原页，明确采样在清洗、如厕之前。')
add('abdomen-002', 'fields.plain', '已有疼痛、破损或流液，走下一条的检查路径。', '已有疼痛、破损或流液，按[肚脐持续异常](#/entry/abdomen-003)安排检查。', '筛选、重排或独立分享后，“下一条”未必仍可见，改为稳定条目链接。')
add('ears-009', 'fields.notes', '穿孔后护理见[下一条](#/entry/ears-010)。', '穿孔后护理见[新耳洞护理](#/entry/ears-010)。', '链接名称应说明目的，避免筛选后“下一条”改变。')
add('abdomen-003', 'fields.plain', '按本篇急症入口处理', '按[腹痛急症](#/entry/abdomen-001)处理')
add('abdomen-004', 'fields.plain', '完全不能排便排气或其他本篇急症信号同样不等。', '完全不能排便排气，或出现[腹痛急症](#/entry/abdomen-001)所列的其他严重变化，也不要等待。')
add('abdomen-005', 'fields.plain', '突然剧痛、呕吐或排不出便气走急症路径。', '突然剧痛、呕吐或排不出便气，按[腹痛急症](#/entry/abdomen-001)处理。')
add('abdomen-006', 'fields.plain', 'PPI则减少产酸', '质子泵抑制剂（PPI）则通过抑制胃酸分泌起作用', '在独立条目中先解释新缩写与用途，不要求先读其他条目。')
add('abdomen-007', 'fields.plain', '若已在医生指导下用药，不因本条自行停药。', '已经因便秘或检查准备按医嘱用药时，继续按原方案，不要把商业排毒疗程的问题误用为停药理由。')
add('anal-006', 'fields.plain', '手机若让你停留更久，就先放在外面；这里的重点是减少无意义停留，不是已经证明某个手机动作一定致痔。', '手机若让你停留更久，就先放在外面；要减少的是久坐和用力，并不是说一拿手机就会长痔。')
add('basics-004', 'fields.plain', 'WHO2026对10岁以上给出每天至少400克蔬果、25克食物中天然膳食纤维的参考，本条仅供成人阅读。', '世界卫生组织（WHO）2026年对10岁以上人群给出每天至少400克蔬果、25克食物中天然膳食纤维的参考；这里用于成人日常饮食，不代替儿童或特殊疾病的营养方案。')
add('basics-009', 'fields.plain', '突然整夜停掉可能有危险；', '已有酒精依赖时，自行骤停可能有危险；', '“突然整夜停掉”是不自然的转述，改为明确的行为与适用条件。')
add('chest-001', 'fields.plain', '这里是危险信号入口，不提供凭疼痛位置自行排除心肺疾病的口诀。', '疼痛位置和是否年轻，都不足以在家排除心肺急症。')
add('chest-001', 'fields.notes', '不照搬英国的急救号码或自行套用其药物剂量；是否用药听从当地急救人员与既定处方指导。', '等待急救时，是否用药听从当地急救人员与既定处方指导，不自行照海外科普中的剂量服药。')
add('chest-004', 'fields.plain', '男性仍要按前面的共同警示留意异常变化。', '发现新肿块、乳头流液或皮肤改变，按[乳房异常变化](#/entry/chest-002)安排检查。')
add('chest-008', 'fields.notes', '无完整儿童用药核对；', '儿童不套用成人药膏和疗程；')
add('chest-009', 'fields.plain', '先按本章皮损路径检查；', '先查[反复腋下痛包](#/entry/chest-012)等原因；')
whole('chest-009', 'fields.notes', '想比较脱毛膏、专业激光或家用光脱毛时，继续读[脱毛方法](#/entry/bodyskin-010)和[光脱毛选择](#/entry/bodyskin-011)。')
add('hands-001', 'title', '伴寒战、快呼吸或意识异常', '伴寒战、呼吸急促或意识异常')
add('hands-001', 'fields.plain', '若伴寒战、快呼吸、眩晕', '若伴寒战、呼吸急促、眩晕')
add('hands-002', 'title', '如厕、做饭前后把手洗到位；没水皂时再用合格手消毒剂', '如厕后、做饭前后把手洗到位；不方便水洗时再用合格手消毒剂')
add('hands-002', 'fields.plain', '先抓住如厕后、准备或进食食物、处理伤口前后等关键时刻', '先抓住如厕后、准备和进食食物前、处理生食后、处理伤口前后等关键时刻')
add('hands-002', 'fields.plain', '水皂不便取得时', '不方便用流动水和肥皂洗手时')
add('hands-005', 'fields.notes', '优先走本篇急症分流', '按[手部感染警示](#/entry/hands-001)及时处理')
add('hands-008', 'fields.plain', '成簇疼疱按水疱条目尽早求医。', '成簇疼疱按[手指水疱](#/entry/hands-006)尽早求医。')
add('hands-009', 'fields.plain', '治疗杀灭真菌与旧甲全部长出是两件事', '真菌受到控制，与受损旧甲被新甲替换是两件事', '旧甲并不是重新长好的部分，改清楚感染控制和新甲生长的不同。')
add('hands-010', 'fields.notes', '按本篇相应急症处理。', '按[手部感染警示](#/entry/hands-001)处理。')
add('feet-003', 'fields.notes', '这里列成分用于识别，不列口服剂量。', '口服用药需按诊断及风险评估开具，不自行加用。')
add('feet-008', 'fields.plain', '先换宽、合脚、低跟且不磨的位置', '先换成鞋头较宽、合脚、低跟且不磨患处的鞋', '修复“换……位置”的语病，明确读者需要更换的是鞋。')
whole('feet-008', 'fields.notes', '', '原备注只解释人群标签实现，风险分支已明确写在正文，不重复向读者说明内部标签。')
add('neck-011', 'fields.plain', '变形严重肿胀', '变形、严重肿胀', '补清并列关系，避免把两种独立警示黏成一个条件。')
add('neck-008', 'fields.plain', '动脉夹层报告', '动脉夹层的报告，即动脉壁层间发生异常分离', '第一次出现专业风险名词时简要解释，不增加个人发生率判断。')
add('legs-004', 'fields.notes', '2015综述只实读题录与摘要，未重新核算各年龄百分比，因此正文不列精确患病率。', '无症状人群也可能出现影像改变，但不能据此估算你个人的患病概率，也不能否定持续疼痛。')
add('bodyskin-005', 'fields.notes', '按本篇急症入口处理。', '按[皮肤感染警示](#/entry/bodyskin-001)处理。')
add('bodyskin-008', 'fields.plain', '准备点痣、激光或IPL时', '准备点痣、激光或强脉冲光（IPL）治疗时', '缩写不能依赖另一条目首次定义，独立分享时也应读懂。')
add('bodyskin-021', 'title', '别把生长因子和康复新液的创面证据，当成既有瘢痕疙瘩能消退', '别凭创面愈合的研究，就买生长因子或康复新液消瘢痕疙瘩')
add('bodyskin-021', 'fields.plain', '药监问答也区分EGF与名称相近的寡肽-1', '药监问答也区分表皮生长因子（EGF）与名称相近的寡肽-1')
whole('bodyskin-021', 'fields.benefit', '避免把促进新伤口愈合的药物，误当成能让既有增生组织消退的治疗。')
add('bodyskin-023', 'summary', '面口咽肿', '面部、口唇或咽喉肿胀')
add('bodyskin-023', 'fields.plain', '风团伴面口咽肿、呼吸吞咽困难、明显眩晕或将要晕倒', '风团伴面部、口唇或咽喉肿胀，或呼吸、吞咽困难、明显眩晕或将要晕倒')
add('private-001', 'fields.plain', 'NHS另列超过1小时仍痛为急诊入口，但突发剧痛或静息仍痛不需要等够1小时才行动。', '疼痛持续超过1小时仍在，也需要急诊评估；突发剧痛或静息仍痛时，更不需要等够1小时才行动。')
add('private-007', 'title', '内裤先选干爽不磨、洗净干透，别为抑菌率直接加上防病想象', '内裤选干爽合身、洗净干透，别把抑菌率当成预防感染的保证')
add('private-007', 'fields.plain', '不编造所有人必须煮多久、晒几小时或每几个月整批丢弃的医学数字。', '没有适用于所有人的煮洗、日晒或整批丢弃时限；按衣物标签、污染和磨损情况安排清洗与更换。')
add('private-011', 'fields.notes', '不等同典型STI', '不等同典型性传播感染')
add('private-013', 'fields.plain', '刺激、念珠菌、STI及包皮因素', '刺激、念珠菌、性传播感染及包皮因素')
add('private-014', 'fields.plain', '尿痛也可能来自外阴刺激或STI。', '尿痛也可能来自外阴刺激或性传播感染。')
add('private-019', 'fields.plain', '暴露后预防简称PEP，是接触后降低感染风险的紧急用药方案', 'HIV是可引起艾滋病的人类免疫缺陷病毒；暴露后预防简称PEP，是接触后降低感染风险的紧急用药方案')
add('private-019', 'fields.plain', 'PEP不处理所有STI', 'PEP不能预防所有性传播感染')
add('private-032', 'fields.plain', 'NO供体如poppers', '一氧化氮（NO）供体，如俗称poppers的助兴吸入剂')
add('private-032', 'fields.plain', '持续勃起不退按急症入口处理。', '持续勃起不退按[异常勃起急症](#/entry/private-036)处理。')
add('private-039', 'summary', '不照另一种药的补服图机械操作。', '不照另一种药的漏服处理规则机械操作。')
add('private-043', 'title', '紧急避孕后先核成分再接常规方法：UPA后等5天，验孕按最后一次无保护时间算', '紧急避孕后先核药名再接常规方法，验孕从最后一次无保护接触算')
add('private-043', 'fields.plain', '拿药时就确认是LNG还是UPA，并写下下一步开始日期。', '拿药时就确认是左炔诺孕酮（LNG）还是醋酸乌利司他（UPA），并写下下一步开始日期。')
add('private-047', 'title', '先说清偏头痛先兆、血压血栓、产后哺乳和全部用药，再决定能否用某类激素', '先说清偏头痛先兆、高血压、血栓史、产后哺乳和全部用药，再选激素避孕')
add('private-049', 'fields.plain', '不同指南的高剂量安排并不完全相同，这里不提供自行服用的高剂量处方；', '不同指南的高剂量安排并不完全相同，高风险者应按具体病史获得方案，不自行照海外剂量加量；')

# Verify all target literals still exist, and preserve the complete citation graph
# for each edited field unless the replacement explicitly relocates an audit note.
applied = {}
for patch in patches:
    key = (patch['file'], patch['target'], patch['id'], patch['field'])
    if key not in applied:
        _, ch = books[Path(patch['file']).stem]
        obj = ch if patch['target'] == 'chapter' else next(x for x in ch['units' if patch['target'] == 'unit' else 'entries'] if x['id'] == patch['id'])
        field = patch['field']
        applied[key] = obj['fields'][field.split('.')[1]] if field.startswith('fields.') else obj[field]
    assert applied[key].count(patch['old']) == 1, patch
    applied[key] = applied[key].replace(patch['old'], patch['new'])
for key, new in applied.items():
    if key[-1] == 'summary':
        assert 100 <= len(new) <= 180, (key, len(new))

warnings = []
rules = {
    'imaginary_illustration': r'本款图示|见下图|如下图|上图所示|如图所示|配图可见',
    'internal_copy': r'本稿|本轮|校对稿|交付稿|出片|本地稿|初稿研究|待用户',
    'filter_implementation': r'筛选.*(?:保留|隐藏)|(?:保留|隐藏).*筛选',
}
review = []
for p, ch in books.values():
    for e in ch['entries']:
        texts = {'title': e['title'], 'summary': e['summary'], **{'fields.'+k:v for k,v in e['fields'].items()}}
        for field in list(texts):
            key = (p.relative_to(ROOT).as_posix(), 'entry', e['id'], field)
            if key in applied: texts[field] = applied[key]
        hits = []
        for rule, regex in rules.items():
            for field, value in texts.items():
                if re.search(regex, value): hits.append(dict(rule=rule, field=field))
        if hits: warnings.append(dict(id=e['id'], hits=hits))
        review.append(dict(id=e['id'], source_file=p.relative_to(ROOT).as_posix(),
            original_text_sha256=hashlib.sha256(json.dumps({'title':e['title'],'summary':e['summary'],'fields':e['fields']},ensure_ascii=False,sort_keys=True).encode()).hexdigest(),
            fields_screened=list(texts), rule_screen='complete',
            changed=any(x['target']=='entry' and x['id']==e['id'] for x in patches),
            manual_scope=('标题、摘要、plain、benefit、notes逐条实际阅读完成；cost/evidence/sources全量规则扫描，不冒充重新临床核证。' if 'baseline/' not in p.relative_to(ROOT).as_posix() else '头面126由独立编辑sop_complete逐字段通读，另见其审校记录；本文件记录规则扫描与已有命中项修改。'),
            manual_fields=(['title','summary','fields.plain','fields.benefit','fields.notes'] if 'baseline/' not in p.relative_to(ROOT).as_posix() else [])))
result = dict(version='2026-10-30', scope='300 entries; original 17 chapters; no direct chapter writes',
    method='全量字段规则扫描；新增身体174条标题、摘要、plain、benefit、notes及十章导语/单元导语逐条实际阅读；头面126由独立编辑另记通读。医学内容以原已附证据为基线，操作歧义另核官方说明。',
    patches=patches, coverage=review, remaining_rule_warnings=warnings,
    external_checks=[dict(url='https://wearemooncup.com/pages/mooncup-instructions', supported='折叠、低位置入、先解除密封后取出，4–8小时排空；只作为该型号操作说明。'),
                     dict(url='https://flexfits.com/a/faq', supported='该碟捏窄、向后置入与前缘支撑、取出方法；不采用营销疗效宣称。'),
                     dict(url='https://www.fda.gov/consumers/consumer-updates/facts-tampons-and-tampon-safety', supported='棉条两类置入辅助、按包装说明、仅经期与4–8小时上限8小时。'),
                     dict(url='https://www.cdc.gov/pinworm/diagnosing/index.html', supported='早晨起床后，清洗、如厕和更衣之前取样；纠正原句标点导致的先洗再采样歧义。')])
(HERE/'prose-patches.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(patches=len(patches),changed_entries=sum(x['changed'] for x in review),coverage=len(review),warnings=warnings),ensure_ascii=False))
