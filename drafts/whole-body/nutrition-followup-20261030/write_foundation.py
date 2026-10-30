import json, re, hashlib
from pathlib import Path

OUT = Path(__file__).resolve().parent
DAY = '2026-10-30'

def source(i, citation, url, typ, support, limitations, reading, funding, doi=None, reviewed=None):
    d = dict(id=f'NFB-S{i:02}', citation=citation, url=url, type=typ, support=support,
             limitations=limitations, reading_depth=reading, funding_disclosure=funding,
             content_checked_at=DAY)
    if doi:
        d.update(doi=doi, doi_url='https://doi.org/'+doi)
    if reviewed:
        d['reviewed_at'] = reviewed
    return d

sources = [
source(1, 'World Health Organization. Use of lower-sodium salt substitutes: WHO guideline. Scope [Internet]. Geneva: World Health Organization; 2025 [cited 2026 Oct 30]. Available from: https://www.ncbi.nlm.nih.gov/sites/books/NBK612027/',
 'https://www.ncbi.nlm.nih.gov/sites/books/NBK612027/', 'WHO指南的官方托管章节',
 '针对成年人烹调/餐桌盐中的含钾低钠替代盐；不覆盖儿童、孕妇及排钾受限者，后者包括肾功能损害、保钾利尿剂或补钾者；不是将食品工业、餐馆及调味酱中的盐全部替换的推荐。',
 'Scope章节解释对象和边界，不能单独证明疗效或最优配方；未以82页整本已读为前提，也未把未纳入孕妇儿童等同已证明有害。',
 '直接读完整Scope章节和WHO出版页概述，核2025年出版；整本PDF403，Recommendations章节验证码页未继续尝试，正式conditional措辞另核WHO发布会材料。',
 'WHO指南，公共卫生机构文件；Scope章节不含完整利益申报，未声称所有作者无利益关系。'),
source(2, 'Kumanyika S. The road to finalizing the LSSS guideline [Internet]. Geneva: World Health Organization; 2025 Jan 27 [cited 2026 Oct 30]. Available from: https://cdn.who.int/media/docs/default-source/nutrition-and-food-safety/events/2025/launch-of-lsss-guideline-presentation-2-road-to-finalization.pdf?sfvrsn=e08be11_3',
 'https://cdn.who.int/media/docs/default-source/nutrition-and-food-safety/events/2025/launch-of-lsss-guideline-presentation-2-road-to-finalization.pdf?sfvrsn=e08be11_3',
 'WHO指南发布会正式说明',
 '最终2025建议：若使用餐桌盐，建议用含钾低钠替代盐替代普通盐，为有条件推荐；减钠本身为强推荐，并保留成人及排钾限制。',
 '发布会幻灯片用于核最终推荐措辞和适用范围，不代替完整证据表；2023年草案与2025年最终稿分开读取，不把conditional翻译成所有人必须换盐。',
 '实读16页文本，重点核第6、8–10及14页的草案/最终推荐、范围和食品工业外推限制；与官方Scope章节及WHO出版页交核。',
 'WHO正式发布会材料；未获得整份指南完整利益申报，不称无利益冲突。', reviewed='2025-01-27'),
source(3, 'World Health Organization. Sodium reduction [Internet]. 2026 May 11 [cited 2026 Oct 30]. Available from: https://www.who.int/news-room/fact-sheets/detail/sodium-reduction',
 'https://www.who.int/news-room/fact-sheets/detail/sodium-reduction', '国际公共卫生机构事实表',
 '成人每天钠少于2000毫克，约相当于5克盐；1克盐约含400毫克钠；计入全部食物和调味品；一般人群用盐应加碘，减少高钠食品。',
 '总量换算用于追踪钠，不等于每人另外再加5克盐；不提供某位年轻人的心血管绝对风险或个体治疗方案。',
 '直接读事实表主要建议、食物来源、换算与碘盐段，核页面实际2026-05-11日期。',
 'WHO公共卫生教育；没有将网页作为单独随机试验或品牌测评。', reviewed='2026-05-11'),
source(4, 'Neal B, Wu Y, Feng X, Zhang R, Zhang Y, Shi J, et al. Effect of Salt Substitution on Cardiovascular Events and Death. N Engl J Med. 2021;385(12):1067-1077. doi:10.1056/NEJMoa2105675.',
 'https://pubmed.ncbi.nlm.nih.gov/34459569/', '整群随机原始试验',
 'SSaSS在中国600个村庄、20995名有卒中史或至少60岁且高血压者中比较75%氯化钠/25%氯化钾盐和普通盐，支持在相应高风险人群降低卒中等事件。',
 '平均年龄约65岁、随访约4.7年，不能把相对效果直接套给健康青年；未见严重临床高钾事件显著增加也不能证明肾病或高钾者安全，试验人群与排除范围重要。',
 '直接读完整PubMed摘要、作者题录和资助索引，核人群、配方、设计、随访与DOI；NEJM全文403，未称读完全文或补充方案。正文不采用个人绝对获益或价格。',
 'PubMed列NHMRC与MRC等研究资助；原刊完整资助及捐盐披露未直接完整读取，未称无商业支持。', doi='10.1056/NEJMoa2105675'),
source(5, 'National Health Service. Common questions about ramipril [Internet]. 2026 Mar 18 [cited 2026 Oct 30]. Available from: https://www.nhs.uk/medicines/ramipril/common-questions-about-ramipril/',
 'https://www.nhs.uk/medicines/ramipril/common-questions-about-ramipril/', '公共医疗机构用药教育',
 '雷米普利为ACE抑制剂；使用时含钾盐替代品可升高血钾，不能自行合用；不为改变饮食自行停用降压药。',
 '针对雷米普利的用药安全，不把其英国膳食6克盐建议移植中国，也不将所有降压药都视为同样风险。',
 '实读药物类别、停药与饮食/钾盐问题全文，页面实际last reviewed为2026-03-18；同日next review显示异常，未用作新更新证据。',
 'NHS患者教育页；未见此页面独立商业资助声明。', reviewed='2026-03-18'),
source(6, 'National Health Service. Candesartan [Internet]. 2026 Mar 18 [cited 2026 Oct 30]. Available from: https://www.nhs.uk/medicines/candesartan/',
 'https://www.nhs.uk/medicines/candesartan/', '公共医疗机构用药教育',
 '坎地沙坦为ARB，含钾补充剂或盐替代品可能与其不合；需要核全部用药、肾功能与监测，不自行停处方。',
 '具体药物相互作用说明，不把存在风险写成所有ARB使用者必然高钾或按本文自行改药。',
 '原common-questions地址重定向到该现行页；直接读分类、监测、停药与Taking with other medicines相关完整段，核实际复核日期。',
 'NHS公共用药教育，未见该单页专项商业资助声明。', reviewed='2026-03-18'),
source(7, '国家疾病预防控制局. 对十四届全国人大二次会议第2249号建议的答复 [Internet]. 2024年6月26日 [引用日期2026年10月30日]. Available from: https://www.ndcpa.gov.cn/jbkzzx/c100033/common/content/content_1863898536274939904.html',
 'https://www.ndcpa.gov.cn/jbkzzx/c100033/common/content/content_1863898536274939904.html', '国家卫生公共政策原文',
 '我国继续实施普遍食盐加碘，碘缺乏与过量均需关注；应按地区水碘、人群监测及特殊情况调整，不笼统追求无碘盐。',
 '政策与监测解释，不是某品牌钾盐成分检测或每个甲状腺疾病的个体食谱；高水碘等例外不能忽略。',
 '直接读取答复全文；正文落款2024-06-26，网页发布时间2024-12-03，两者已区分，未把检索日当更新时间。',
 '国家疾病预防控制局正式答复，不是企业产品研究。', reviewed='2024-06-26'),
source(8, '国家食物与营养咨询委员会. 《中国居民膳食指南（2022）》一图读懂 [Internet]. 2022年5月20日 [引用日期2026年10月30日]. Available from: https://sfncc.caas.cn/xyyw/79c86454ef84437eb3e0df055deffd56.htm',
 'https://sfncc.caas.cn/xyyw/79c86454ef84437eb3e0df055deffd56.htm', '国家食物营养咨询机构刊载的膳食指南核心推荐',
 '2022核心推荐正文：成人每日蔬菜不少于300克、深色占一半，新鲜水果200–350克且果汁不替代，奶制品相当于至少300毫升液态奶；食物多样，常吃全谷大豆，适量鱼禽蛋瘦肉。',
 '机构官网呈现核心推荐，不等同已通读膳食指南全书或中国DRI；谷物、肉类总克数原页未细述生熟称量，本文不用这些数值配餐。',
 '直接读该官方站点刊载的2022八条核心推荐完整正文；中国营养学会原页超时、卫健委部分原页412，未用商业文章冒充已读一手指南。',
 '公共机构对国家膳食指南核心内容的呈现，未见此网页独立商业资助。', reviewed='2022-05-20'),
source(9, 'World Health Organization. Healthy diet [Internet]. 2026 Jan 26 [cited 2026 Oct 30]. Available from: https://www.who.int/news-room/fact-sheets/detail/healthy-diet',
 'https://www.who.int/news-room/fact-sheets/detail/healthy-diet', '国际公共卫生机构事实表',
 '膳食足量、均衡、适度、多样；全谷、果蔬和豆类为重要来源；果汁含游离糖，冷冻或罐装蔬果在无加糖、不过量盐时也可用，不按包装判健康。',
 '一般膳食原则，不是证明一种食物能保证寿命或减脂的试验；特殊治疗膳食需另行个体化。',
 '直接读取基本原则、碳水/纤维、果蔬/果汁及冷冻罐装相关完整段，核实际2026-01-26日期；基线basics-004已有400克和25克目标，此处不重复当作新发现。',
 'WHO公共健康教育；未视作品牌或某一种食品的独立临床试验。', reviewed='2026-01-26'),
source(10, 'National Institute of Diabetes and Digestive and Kidney Diseases. Eating, diet, & nutrition for constipation [Internet]. 2018 May [cited 2026 Oct 30]. Available from: https://www.niddk.nih.gov/health-information/digestive-diseases/constipation/eating-diet-nutrition',
 'https://www.niddk.nih.gov/health-information/digestive-diseases/constipation/eating-diet-nutrition', '政府消化疾病患者教育',
 '增加纤维应少量逐渐，结合适量液体与个体健康需求；全谷、豆类、蔬果等为食物来源。',
 '便秘人群教育，不据其美国分龄纤维克数给中国所有人下处方，也不由纤维有效推出所有腹胀都该强加粗粮。',
 '直接读饮食、逐渐加纤维及饮水相关全文；实际last reviewed为May 2018，未虚构2021或2026更新日；与WHO2026原则交核使用。',
 'NIDDK公共教育页，未见该页独立产品资助声明。', reviewed='2018-05'),
source(11, 'National Health Service. Processed foods [Internet]. 2023 Jun 12 [cited 2026 Oct 30]. Available from: https://www.nhs.uk/live-well/eat-well/how-to-eat-a-balanced-diet/what-are-processed-foods/',
 'https://www.nhs.uk/live-well/eat-well/how-to-eat-a-balanced-diet/what-are-processed-foods/', '公共医疗机构营养教育',
 '加工不自动不健康；巴氏杀菌、冷冻与罐装有食品安全及保存价值；部分全麦面包、高纤维早餐谷物或罐装豆类虽高度加工仍可纳入健康膳食。优先识别高糖盐饱和脂肪、结合标签和食用量。',
 '未按NOVA对每个中国在售品牌定类；有关慢病风险的观察关联并不确定是加工本身还是营养及其他因素所致，不宣称所有添加剂安全或有毒。',
 '实读正文全部主要段，核实际复核2023-06-12；2026-06-12为预定复审日，未假称已2026更新。',
 'NHS公共营养教育，无单页专项产品试验资助说明。', reviewed='2023-06-12'),
source(12, 'Monteiro CA, Cannon G, Levy RB, Moubarac JC, Louzada MLC, Rauber F, et al. Ultra-processed foods: what they are and how to identify them. Public Health Nutr. 2019;22(5):936-941. doi:10.1017/S1368980018003762.',
 'https://pubmed.ncbi.nlm.nih.gov/30744710/', 'NOVA分类定义原作者评论',
 'NOVA按工业加工的程度和目的分类；超加工定义涉及食品组分重组及工业配方，与精制谷物的去麸皮/胚芽不是同一层面的定义。',
 '这是分类说明评论而非随机临床试验；分类不能单独判断每一种食品或添加剂危害，更不能由有某一种添加剂推定致病。',
 '直接读完整PubMed摘要、分类定义与题录，核正式卷期页和DOI；未称读取全文、资助或全部引文。',
 '摘要页未完整列本文资助或作者利益申报，未写作无利益冲突；定义作者对该分类有学术立场。', doi='10.1017/S1368980018003762'),
source(13, 'Hall KD, Ayuketah A, Brychta R, Cai H, Cassimatis T, Chen KY, et al. Ultra-Processed Diets Cause Excess Calorie Intake and Weight Gain: An Inpatient Randomized Controlled Trial of Ad Libitum Food Intake. Cell Metab. 2019;30(1):67-77.e3. doi:10.1016/j.cmet.2019.05.008.',
 'https://pubmed.ncbi.nlm.nih.gov/31105044/', '住院随机交叉喂养原始试验',
 '20名成人住院随机交叉、两种菜单各两周；在可自由进食条件下，超加工菜单阶段平均摄入更多、体重变化不同；为整套菜单短期因果效应提供证据。',
 '小样本、短期、整套菜单比较，不能定位某种添加剂、单一食品或长期心血管因果；题录列两项勘误，未直接完整核勘误文本，正文因此不采用精确热量差或体重差。',
 '直接读完整PubMed摘要、题录、图注和利益声明；PMC全文遇验证码不再尝试替代路径，未称全文或原始数据已重审。检出2019和2020勘误，不隐去但也不擅称推翻结果。',
 '摘要页列Forde与食品营养公司演讲/差旅、顾问及联合项目资助关系；其余作者申报无利益冲突；本文全文完整Funding未读，不笼统称零商业关系。', doi='10.1016/j.cmet.2019.05.008'),
source(14, 'Dicken SJ, Jassil FC, Brown A, Kalis M, Stanley C, Ranson C, et al. Ultraprocessed or minimally processed diets following healthy dietary guidelines on weight and cardiometabolic health: a randomized, crossover trial. Nat Med. 2025;31(10):3297-3308. doi:10.1038/s41591-025-03842-0.',
 'https://pubmed.ncbi.nlm.nih.gov/40760353/', '社区随机交叉供餐原始试验',
 '英国55名习惯高比例超加工饮食、BMI至少25且小于40成人，两套符合UK Eatwell建议的供餐各8周；两组均平均减重，较少加工菜单下降更多，不能说营养改善后的超加工菜单必然增重。',
 '50人进入意向治疗分析，特定招募人群、短期供餐；原刊有2026年Matters Arising，不能将其当作所有营养差异或顺序效应已排除、加工本身为唯一原因的证明。不把英国试验移植成中国个人减重承诺。',
 '直接读PubMed完整摘要、Extended Data相关图注、正式卷期页及利益声明；原刊首访见2026评论链接和updated提示，后访问身份/cookie gate未继续尝试。未完整读全文、补充材料或评论，因此正文不引精确减重数字、不声称争议已解决。',
 'PubMed披露Dicken及van Tulleken有超加工主题书籍版税，部分作者有Novo Nordisk、Lilly等顾问/研究关系，Batterham自2023年起Lilly雇员和持股；全文完整资助未完整读取，未称无商业或学术利益关系。', doi='10.1038/s41591-025-03842-0'),
source(15, '淮南市市场监督管理局食品生产安全监管科. 食品生产企业请注意！新版食品标签国标明年3月施行，这些变化与您息息相关 [Internet]. 2026年8月25日 [引用日期2026年10月30日]. Available from: https://scjgj.huainan.gov.cn/public/118319860/1261095742.html',
 'https://scjgj.huainan.gov.cn/public/118319860/1261095742.html', '中国市场监管部门标准实施说明',
 'GB 7718-2025与GB 28050-2025于2027-03-16实施；营养标签从1+4增加糖和饱和脂肪为1+6。允许提前执行，实施前产品可按规定销售至保质期结束。',
 '监管部门的实施说明，不等同已完整审核两部标准全部正文；这里只核时间和新增强制营养项，不推断2026所有食品已经必须列糖/饱和脂肪，也不用它给单个标签作法律判定。',
 '直接读该监管科正式说明全文，核网页发布时间2026-08-25、文内落款2026-08-24；卫健委标准问答原页412，未冒称原标准全文全部读过。',
 '食品生产安全监管部门发布，不是企业营养宣传。', reviewed='2026-08-25')
]

def entry(n, title, summary, plain, benefit, evidence, refs, notes, scope):
    return dict(id=f'nutrition-{n:03}', chapter_id='nutrition', unit_id='nutrition-u5', ordinal=n,
                title=title, summary=summary,
                fields=dict(cost='', plain=plain, benefit=benefit, evidence=evidence, sources=refs, notes=notes),
                audience=dict(age_groups=['adult','older'], sexes=['all'], scope_note=scope, safety_pin=False),
                clinical_review_status='not_clinically_reviewed', content_checked_at=DAY)

entries = [
entry(12, '换低钠钾盐先排除禁忌，酱料和零食里的钠也要一起减',
 '减盐要计算一天所有食物里的钠，不能只盯炒菜放了几勺。没有排钾障碍的成年人，可以考虑用正规含钾低钠盐替代家中烹调盐，但仍要少放；有肾病、高血钾、正在补钾或用相关药物，先核方案。选盐还要兼顾加碘，家里有儿童或孕妇时，不把成人建议直接推广给全家。',
 '**如果想从厨房开始减钠，没有排钾障碍的成年人可以考虑把普通烹调盐换成正规生产的含钾低钠盐，同时减少使用量。** 这种盐通常用氯化钾替代一部分氯化钠；它仍然是盐，吃多了也不能抵消其他食物里的钠。WHO在2025年给的是“有条件推荐”，不是人人必须换，更不适用于儿童、孕妇或排钾受限者。不要自己买氯化钾粉配盐。[@NFB-S01][@NFB-S02]\n\n**先核身体情况和药单，再决定能不能换。** 有肾功能损害、已知高血钾、正在补钾或用保钾利尿剂时，不自行尝试。雷米普利这类“普利”及坎地沙坦这类“沙坦”也可能与含钾盐产生风险，把药单交给医生或药师，结合肾功能与血钾决定；不是每种降压药都一样，也不要为换盐停药。家庭共餐有孕妇、儿童或上述高风险成员时，不直接给整锅菜都换钾盐。[@NFB-S01][@NFB-S05][@NFB-S06]\n\n成人减钠目标是**全天钠少于2000毫克，约相当于5克盐**，包含食物本身、酱油、蚝油、腌菜、零食和外卖，不是另外还可以撒5克盐。营养表可先看“钠”和实际吃掉多少：一份食品含400毫克钠，约占用1克盐的额度；每100克的数据要乘上吃掉的份数。调味改用少量盐和酱料，再以葱姜、醋等增加风味；不能换钾盐的人仍可减少这些钠来源。[@NFB-S03]\n\n选低钠盐时看清配料、钠/钾含量及是否加碘，**“低钠”与“无碘”不是同一个卖点**。我国通常仍需使用碘盐，别因追求天然或低钠顺手改成无碘盐；高水碘地区或已获特别限碘方案者按当地指导与个人方案执行。低钠盐的获益证据也不是“健康年轻人从此少多少死亡风险”：SSaSS研究主要是有卒中史或老年高血压的农村高风险人群，不能把其平均结果当你的个人承诺。[@NFB-S07][@NFB-S04]',
 '减少可避免的钠摄入，并在适合的人群中利用含钾替代盐；把药物、排钾能力与碘营养一并考虑。',
 'B，含钾替代盐有随机试验支持，但SSaSS主要为中国老年或既往卒中的高风险人群，健康青年绝对获益不能照搬。WHO对合适成年人换盐为有条件推荐；特殊人群排除、用药核对、总钠换算和碘盐选择为指南/安全指导，不由机构权威自动升级成所有人确定获益。[@NFB-S01][@NFB-S02][@NFB-S03][@NFB-S04]',
 'WHO2025替代盐指南范围与正式推荐、2026减钠事实表；SSaSS；NHS相关用药安全；国家疾控局碘盐政策。[@NFB-S01][@NFB-S02][@NFB-S03][@NFB-S04][@NFB-S05][@NFB-S06][@NFB-S07]',
 '不为此推荐普遍抽血筛查，也不提供自配盐比例。没有病史并不意味着能忽略正在吃的处方药、补钾剂或共餐者情况；不确定时先带药单核对，肾功能和血钾检查按临床需要安排。',
 '适用于考虑减少钠摄入的成年人及老年人；钾盐分支不扩展给儿童、孕妇、排钾障碍或相关用药者，后者须另行核定。'),
entry(13, '把部分白米白面换成全谷杂豆，餐餐给蔬菜留位置',
 '改善吃法不用一夜间把白饭全换成粗粮。先从一餐少量混入燕麦、糙米或杂豆开始，餐餐安排蔬菜，每天留出完整水果和奶制品的位置，再轮换鱼、蛋、豆制品及瘦肉。蔬果汁和青汁不能代替这些食物；纤维加得太快会不舒服，按耐受逐渐加，治疗性饮食者另按方案。',
 '**先改一顿常吃的饭：白米里加少量糙米或杂豆，早餐白粥的一部分换成原味燕麦，再为这顿饭安排一份蔬菜。** 不是把白米白面全部禁掉，也不是在原有饭量外再加一碗粗粮。全谷物保留谷粒的麸皮、胚芽和胚乳，相较精白谷物能保留更多纤维等成分；选燕麦、全麦食品要看配料，不能只看面包颜色深不深。变化从自己能接受的一餐开始，下一步再扩大。[@NFB-S08][@NFB-S09]\n\n接着看一天是否确实吃到了以下食物，而不是只数“今天吃了几种营养素”。中国2022膳食指南核心推荐，成人每天新鲜蔬菜不少于300克、深色蔬菜约占一半，水果200–350克，奶制品相当于至少300毫升液态奶。用这些量检查自己漏在哪里，不必精确到每一口：蔬菜可分到午晚餐，水果选完整可吃的水果，奶或酸奶等看实际乳含量和自己耐受。**果汁、果蔬汁、青汁不能据包装宣传替掉蔬菜和完整水果，喝奶茶也不等于喝了同量的奶。**[@NFB-S08][@NFB-S09]\n\n鱼、蛋、豆制品、禽肉和瘦肉轮换安排，不让一整天只剩主食加咸菜，也不把补足营养理解成顿顿加大肉量。忙时可利用无过量盐糖的冷冻蔬菜、罐装豆类或普通奶制品；方便不意味着差，反而比为了“纯天然”直接省掉这一类食物更容易落实。蛋白粉与代餐是否需要，另看[蛋白粉补缺口](#/entry/nutrition-005)和[基础膳食与补剂](#/entry/basics-004)。[@NFB-S08][@NFB-S09]\n\n如果原来很少吃全谷、豆类和蔬菜，**逐渐增加，不要一天猛吃大量麸皮、纤维粉或粗粮**；结合自己需要补足液体，观察腹胀、排便与耐受。不是所有腹胀便秘都能靠继续加纤维解决。已有医生要求的限钾、低渣或其他治疗性营养方案，先按该方案调整食材与分量；饮水量也不为吃纤维而硬套“人人八杯”，见[日常补水](#/entry/basics-005)。[@NFB-S10]',
 '把宽泛的均衡饮食落实为每天能购买、能安排的一餐，减少只删主食或只买补剂带来的食物缺口。',
 'C，主要依据中国膳食指南核心推荐及WHO膳食原则，纤维递增来自消化病患者教育；文中的一餐起步、分到午晚餐是便于执行的示例，不是临床验证的唯一餐盘比例。不能保证按某个克数进食就减脂、降血糖或延长寿命。[@NFB-S08][@NFB-S09][@NFB-S10]',
 '中国2022膳食指南核心推荐的官方刊载；WHO2026健康膳食；NIDDK增加纤维与饮水。[@NFB-S08][@NFB-S09][@NFB-S10]',
 '以上成人食物目标用于查漏补缺，不是儿童、孕哺、运动员或疾病营养处方。未采用原页未说明生熟重的谷物/肉类总克数，不将“全谷物+杂豆”与“全谷物”两种统计口径混用。',
 '一般成年人与老年人的日常食材安排；有治疗性膳食、吞咽问题或明显进食不足者按个体方案，不用此表覆盖医疗营养需求。'),
entry(14, '少买高糖高盐、容易吃过量的食品，别按“有包装”一律拉黑',
 '白米白面属于精制谷物，超加工食品则是另一种按工业配方和加工目的划分的概念，两者不能画等号。买东西先比较同类食品的钠、糖、饱和脂肪、纤维与实际吃量；冷冻蔬菜、普通奶、合适的罐装食品不必因加工而排除。研究支持警惕整套饮食容易让人多吃，不能据此断言所有添加剂有毒。',
 '**买食品先比较同类产品实际吃进去的糖、盐、脂肪和分量，再看“天然”“零添加”等宣传。** 少把含糖饮料、咸味零食、甜点和加工肉当日常主力；有包装不是拉黑理由。巴氏杀菌奶、原味燕麦、无过量盐糖的冷冻蔬菜和合适的罐装食品，仍能帮助把饭吃齐；全麦面包等即使属于较高加工类别，也要结合营养与吃量判断。[@NFB-S09][@NFB-S11]\n\n先分清两个词：**精制谷物**是谷粒去掉较多麸皮、胚芽后制成的白米白面等；**超加工食品**常指NOVA分类里由工业食品成分和配方加工制成的一类产品。这是两种不同的分类角度，一碗普通白米饭不能只因“精制”就判为超加工；加工也不等于不安全。不要从“某产品含乳化剂/防腐剂”直接跳到“它会致病”，更不必为避开所有添加剂放弃能负担、能保存的基本食物。[@NFB-S09][@NFB-S11][@NFB-S12]\n\n对超加工的担心并非全无根据，但要看研究究竟比较了什么。2019年20名成人住院交叉试验中，超加工菜单阶段平均吃得更多；2025年英国8周交叉供餐试验里，两套都符合当地健康膳食建议的菜单都平均减了重，较少加工的一套下降更多。它们比较的是**整套菜单、短期自由进食的结果**，不是把某种添加剂单独拿出来试验，更不能保证你停买某一包食品就能瘦。较长期慢病研究里的风险关联也不自动等于加工本身的单独因果。[@NFB-S13][@NFB-S14][@NFB-S11]\n\n在中国读营养表，先按同样每100克或每100毫升横向比较，再乘上自己实际吃掉的量；一袋若有多份，别只算一份。钠换算与盐的总量见[减钠与钾盐](#/entry/nutrition-012)。**截至2026年10月，不能把“没标糖”理解成“无糖”**：新增糖、饱和脂肪等强制标示要求的新国标将于2027年3月16日实施，部分企业可提前执行，过渡期内会见到不同版本。配料表可帮助了解原料组成，但仅看一个成分名字或营销词，仍不能代替营养与食用量的判断。[@NFB-S15]',
 '优先减少真正容易挤占正餐、带来过量糖盐或能量的选择，同时保留方便、价格可承受的健康食材。',
 'B，两项随机喂养/供餐试验支持特定菜单影响短期摄入与体重，但样本、时长和人群有限，2025试验也有后续方法学讨论，不能归因为单一添加剂或推广所有产品。选购原则与标签过渡期为C；没有给任何具体品牌出具安全或减肥认证。[@NFB-S13][@NFB-S14][@NFB-S11][@NFB-S15]',
 'WHO膳食原则；NHS加工食品；NOVA定义；Hall2019与Dicken2025随机试验；中国市场监管部门新标签实施说明。[@NFB-S09][@NFB-S11][@NFB-S12][@NFB-S13][@NFB-S14][@NFB-S15]',
 '“不因添加剂名称恐慌”不等于所有配方、剂量、储存条件都安全。具体食物过敏、医疗营养、保质期与储存要求仍需分别核对；本条不以国外分类代替中国食品安全标准。',
 '成年与老年读者的食品选择和标签识读；不进行儿童食品、疾病配方或单个品牌的安全认证。')
]

claims = [
 dict(entry='nutrition-012', claim='WHO2025 conditional成人适用，儿童/孕妇/排钾障碍不覆盖；家庭共餐与药物分支', sources=['NFB-S01','NFB-S02','NFB-S05','NFB-S06']),
 dict(entry='nutrition-012', claim='全天钠<2000毫克/约5克盐，1克盐=400毫克钠，全部来源合计', sources=['NFB-S03']),
 dict(entry='nutrition-012', claim='低钠不等于无碘，我国普遍盐碘政策与特殊例外', sources=['NFB-S07']),
 dict(entry='nutrition-012', claim='SSaSS老年/卒中高风险人群，不能外推健康青年个人收益', sources=['NFB-S04']),
 dict(entry='nutrition-013', claim='蔬菜≥300克/深色约半，水果200–350克/非果汁，奶等量≥300毫升及多样食物', sources=['NFB-S08','NFB-S09']),
 dict(entry='nutrition-013', claim='纤维逐渐加，饮水个体化；一餐替换为编辑性执行示例', sources=['NFB-S10']),
 dict(entry='nutrition-014', claim='加工不等于有害，部分包装食品可属健康膳食；NOVA定义不是安全判定', sources=['NFB-S09','NFB-S11','NFB-S12']),
 dict(entry='nutrition-014', claim='2019/2025短期菜单随机试验不是单一添加剂或长期慢病因果', sources=['NFB-S13','NFB-S14','NFB-S11']),
 dict(entry='nutrition-014', claim='新GB28050强制糖/饱和脂肪2027-03-16实施，2026不假定全面已强制', sources=['NFB-S15'])
]
audit = dict(
 checked_at=DAY, entry_ids=[e['id'] for e in entries], sources=len(sources), clinical_review_status='not_clinically_reviewed',
 proposed_unit=dict(id='nutrition-u5', title='把日常吃法和购物选择落到实处', entry_ids=[e['id'] for e in entries]),
 nonduplication='basics-004保留整体食物/补剂框架，basics-005保留个体化饮水；013专门提供中国食物目标及一餐替换示例，不重复蛋白粉/代餐评估；血糖管理nutrition-015另写，不在此扩展控糖产品。',
 claim_source_map=claims,
 rejected_inferences=[
 '低钠钾盐人人必用或可以多吃；WHO未覆盖的儿童孕妇等于已被证明有害。',
 'SSaSS老年高风险人的相对风险数字就是健康青年个人可获得的降幅。',
 '不显著高钾事件等于慢性肾病或用药者已证安全；换盐可以停降压药。',
 '钾盐等于无碘盐，或钾盐可以自己买氯化钾粉按网传比例调配。',
 '5克盐是烹调用盐额外额度、不含酱料零食外卖；把英国6克套成中国目标。',
 '所有人必须禁白米白面、猛加纤维；果汁青汁可以代替完整蔬果。',
 '全谷物+杂豆50–150克与全谷物50–100克是相同口径，或未核原页就统一称干生重。',
 '加工、精制、NOVA超加工、食品安全是同一个分类；包装冷冻罐装等于有害。',
 '20人短期整套菜单试验能单独证明乳化剂致胖，或观察性慢病关联已证明因果。',
 '2025英国供餐研究可忽略2026评论并保证中国所有人的个人减重效果。',
 '2027实施的新标签项目在2026已全面强制；2026没标糖就说明没有糖。',
 '机构权威自动等于A级临床疗效；已读摘要等于已审全文、补充材料与原始数据。'
 ],
 reading_limitations=[
 'WHO指南出版概述、Scope章节及官方发布会slides已直接读；82页全文PDF403、Recommendations章节验证码，未绕过或假称全文已读。',
 '中国营养学会原页超时、部分卫健委页412，食物目标使用国家食物与营养咨询委员会官方站点刊载2022核心推荐完整正文；未声称读中国DRI或指南全书。',
 'NHC2025健康膳食核心信息的全谷50–100克与2022全谷+杂豆口径不同，因原页访问受限且无需该数值，本次不采用两者谷物总克数。',
 'SSaSS、NOVA、Hall、Dicken均核完整摘要与正式题录；Hall与Dicken另外读了页面可见图注/利益申报，未称全部全文。',
 'Hall原刊2019/2020两项勘误已检出但未完整读取内容，正文不采用精确能量差/体重差；Dicken原刊存在2026 Matters Arising且updated，未审全部争论，正文不用精确减重数字或单一加工因果。',
 'GB标签实施日期和新增强制项目读中国市场监管部门原始实施说明，未声称完整标准逐条法律审读；不采用未来标准推2026标签均已符合。',
 'NIDDK2018和NHS2023实际复核日如实保留，未把预定复审或检索日冒充更新；与WHO2026交核原则。'
 ],
 excluded=['未经可靠核实的商品价格或个体成本数字','具体品牌疗效和单一添加剂致病认定','个人每日热量/营养处方','自配钾盐配方','对儿童/孕妇推广钾盐','未经临床签审却标注专家审核'],
 checks={}
)

refs = set()
for e in entries:
    assert 100 <= len(e['summary']) <= 180, (e['id'],len(e['summary']))
    assert not re.search(r'\[@|\||https?://',e['summary'])
    assert list(e['fields']) == ['cost','plain','benefit','evidence','sources','notes']
    assert e['fields']['cost'] == ''
    refs.update(re.findall(r'\[@(NFB-S\d+)\]',json.dumps(e,ensure_ascii=False)))
assert refs == {s['id'] for s in sources}, (refs, {s['id'] for s in sources})
audit['checks'] = dict(summary_lengths={e['id']:len(e['summary']) for e in entries}, six_fields=True, all_costs_empty=True,
                       refs_resolved=True, source_count=len(sources), male_female_shared=True,
                       age_groups=['adult','older'], external_clinical_review=False,
                       frozen_for_independent_review=True)
for filename, obj in [('foundation-entries.json',entries),('foundation-sources.json',sources),('foundation-audit.json',audit)]:
    p=OUT/filename
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(filename, hashlib.sha256(p.read_bytes()).hexdigest())
print(audit['checks'])
