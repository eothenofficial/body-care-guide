"""Three deliberate same-decision merges; no audience expansion or concatenation."""
import copy,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
original={e['id']:e for e in json.loads((HERE/'body-input.json').read_text(encoding='utf-8'))['entries']}
merges=[]
def merge(target,retired,title,summary,plain,benefit,notes):
    ids=[target,*retired];members=[original[i] for i in ids]
    refs=list(dict.fromkeys(s for e in members for s in e['source_ids']))
    def expand(v):return re.sub(r'\[@(\d+)\]',lambda m:'[@'+refs[int(m[1])]+']',v)
    assert all(members[0]['audience']==e['audience'] for e in members[1:]) or all(members[0]['audience'][k]==e['audience'][k] for e in members[1:] for k in ['age_groups','sexes'])
    fields=dict(cost='',plain=expand(plain),benefit=benefit,evidence='\n\n'.join(dict.fromkeys(e['fields']['evidence'] for e in members)),sources='\n\n'.join(dict.fromkeys(e['fields']['sources'] for e in members)),notes=notes)
    allrefs=set(re.findall(r'\[@([^\]]+)\]','\n'.join(fields.values())))
    assert allrefs==set(refs),(target,allrefs^set(refs))
    assert 60<=len(summary)<=140,(target,len(summary))
    merges.append(dict(target=target,retired=retired,title=title,summary=summary,fields=fields,reason='两条帮助读者作同一个决定；重写为一个解释与行动顺序，保留双方依据、条件与旧链接。',age_sex_check=dict(age_groups=members[0]['audience']['age_groups'],sexes=members[0]['audience']['sexes'],all_members_same_filter_tags=True,scope_notes=[e['audience']['scope_note'] for e in members]),clinical_boundaries_preserved=True))

merge('nutrition-013',['basics-004'],'一餐配齐主食、蔬菜和蛋白，再考虑补剂代餐',
'不用一夜戒白饭：从一餐用部分全谷杂豆替精白主食，配蔬菜和鱼蛋豆肉，再安排完整水果、合适奶制品。蛋白粉只补真实缺口，青汁奶昔不自动是一餐。纤维逐步加，体重、训练或疾病需要另定，不照推荐量给自己强加补剂。',
'全谷保留麸皮、胚芽、胚乳，较精白谷物保留更多纤维；纤维是不能完全消化的食物成分，可来自全谷、豆、蔬果。蛋白质参与肌肉等结构，蛋白粉可方便补不足，吃够后加粉不自动更健康，单个超级食物也不能包办营养。[@0][@1][@3]\n\n中国2022核心推荐成人每天新鲜蔬菜至少300克、深色约半，水果200–350克，奶制品相当于至少300毫升液态奶。WHO2026另给10岁以上至少400克蔬果、25克天然食物纤维参考；这里用于成人查漏补缺，不是再加25克纤维粉或给所有年龄统一处方。[@0][@1]\n\n**从一顿常吃的饭改起：部分白米白粥换糙米、原味燕麦或杂豆，同时加蔬菜、轮换鱼蛋豆肉。** 不额外加一碗粗粮，也不全戒白饭。蔬菜可分午晚餐，水果选完整食物；奶看实际乳含量和耐受，果汁、青汁、奶茶不自动替代。冷冻蔬菜、合适罐装豆和普通奶能让忙时也吃齐。[@0][@1]\n\n原来纤维少就逐步加，按需要补液、观察腹胀排便，不猛吃麸皮粉。限钾、低渣、肾病、吞咽或吸收问题先按营养方案。想买粉或代餐，先查全天总量、训练和缺口；普通蛋白粉、青汁、维生素糖不算营养完整一餐，低热量全代餐需专业支持。[@2][@3][@4]',
'把能买、能安排的餐食吃完整，让补充产品只填实际缺口。',
'食物目标不是儿童、孕哺、运动员或疾病的个人处方；称重先分生重、熟重和可食部分。25克纤维不是要求额外补同量纤维粉；正常健康蛋白摄入不能直接解释为会损肾。')

merge('nutrition-020',['basics-010'],'先看BMI、腰围和健康风险，再决定是否减重',
'体脂秤变红不等于需要继续瘦。先算BMI、量腰围，再结合血压血糖、病史、体力和营养确定目标；家用体脂率肌肉量是估算，不凭一天读数改吃练。儿童、孕期或虚弱老人需另定标准，药物、极低能量代餐也有特定条件，不照他人方案。',
'BMI是体重（千克）除以身高（米）的平方。中国普通成人18.5至不足24为正常、24至不足28为超重、28及以上为肥胖；它不能区分所有肌肉和脂肪，正常也不排除腹部代谢风险，肌肉发达者可被高估。[@0]\n\n家用体脂秤常用生物电阻抗（BIA），让弱电流通过身体，结合身高年龄推算成分，不是直接看见脂肪肌肉。2021三型号研究的体重表现优于成分估计，不能推广所有新品都差，也别因今天显示掉1kg肌肉就加餐停练。[@2]\n\n**用普通体重秤和软尺，相近条件看数周趋势、腰围和力量。** 腰围在肋骨下缘与髋骨上缘中点水平绕腹，自然呼气、贴合不勒。中国成人男≥90cm、女≥85cm达中心性肥胖界值，低于也非零风险；腹部变化或血压血糖异常，带记录和病史就诊。[@1][@0]\n\n确定有健康减重需要，再选能维持的饮食活动与支持；需要药物不等于意志差，但[用药门槛](#/entry/nutrition-017)不能由BMI诊断线直接代替。极低热量全代餐不适合自己长期照做。儿童看年龄性别生长评估，孕期、虚弱或偏瘦老人、吃不够者先顾营养功能；极端限制或失控进食按[进食问题](#/entry/nutrition-023)求助，不追同一数字。[@0][@3][@4]',
'分清健康、营养与活动目标，减少极端节食和无指征用药。',
'中国成人分类不是所有人的个人目标；不要直接照搬海外BMI、手术条件、他人的热量或用药方案。')

merge('sleep-012',['sleep-013'],'少睡次日先保安全，短休息、咖啡和训练都降风险',
'少睡后先看是否打盹、反应或动作变差：通勤和危险工作先改，极限大重量训练先取消。只是稍少睡但清醒无不适，可短而轻地活动。白天按需早些短睡，咖啡不叠浓缩产品，晚上留足睡眠；提神和一次补觉都不能保证所有能力完全恢复。',
'**明显打盹、反应慢或通宵后，先休息，取消或改派驾驶、机器及其他高风险任务。** 请清醒者驾驶或改公共交通，不为守作息或赶健身房硬撑，开窗音乐咖啡都不是安全证明。[@0]\n\n少睡可影响警觉、判断和动作表现，影响因任务与个人而异；恢复睡眠有用，但感觉好些不等于注意协调已完全恢复，一次补觉不保证抹平反复缺觉。没有按睡几小时规定人人训练强度或补觉时数的依据。[@5][@6][@7]\n\n**白天需要时可较早短睡约20分钟，醒后等迟钝过去。** 反复难睡者缩短、提前午睡，尽量留日常起床和主睡眠框架；今晚留足机会，不从下午补到傍晚，也不把恢复封顶8小时。年轻成人或还睡债可能需更久。惯常咖啡不必自动全禁，但算每份及全天量，400mg不是缺觉加量目标，不叠能量饮料、训练补剂；心悸手抖或更焦虑就别续，靠近今晚睡眠提前停。[@1][@2][@3][@4]\n\n通宵、接连打盹、难集中时，取消极限、大重量测试及失误后果大的训练。只是偶尔少睡、清醒且无不适，可改熟悉、轻松、短些的活动；更困、控制变差或不舒服就停，不为累垮催睡而猛练，也不为晨练再次提前闹钟。胸痛、晕厥、明显气短走[运动急症](#/entry/activity-001)。连续少睡或持续影响白天，记录并[评估睡眠](#/entry/sleep-002)，不等满三个月。[@6][@7][@0][@3]',
'给恢复留下机会，减少高风险作业、强训练和提神产品叠加。',
'轻活动是按警觉和表现作的保守选择，不是已证明对每位缺觉者绝对安全。恢复与失眠、轮班和疾病安排需个体调整。')

if __name__=='__main__':
    (HERE/'body-merges.json').write_text(json.dumps(merges,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print([(m['target'],m['retired'],len(m['summary'])) for m in merges])
