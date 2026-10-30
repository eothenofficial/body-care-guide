"""Authored evidence-linked nutrition additions; not a medical decision engine."""
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
DATE='2026-10-30'
sources=[]
def src(n,citation,url,support,limitations,depth,funding='机构资料未单列专项资金或作者商业利益；不把机构名称当作每项效果均有强试验证据。',**extra):
    s=dict(id=f'NUT-S{n:02d}',citation=citation,url=url,type='原始研究、专业机构或监管一手资料',
        support=support,limitations=limitations,reading_depth=depth,content_checked_at=DATE,funding_disclosure=funding,**extra)
    sources.append(s)

src(1,'National Health Service. Low blood sugar (hypoglycaemia) [Internet]. 2023 Aug 3. [cited 2026 Oct 30]. Available from: https://www.nhs.uk/conditions/low-blood-sugar-hypoglycaemia/',
    'https://www.nhs.uk/conditions/low-blood-sugar-hypoglycaemia/',
    '糖尿病用药者漏餐/少吃碳水更易低血糖；清醒可安全吞咽时快速糖与复测，意识异常不喂食并急救；无糖尿病而反复类似症状也要查因。',
    '没有糖尿病时真正低血糖较少见，不能凭饿、抖或心慌自行诊断；不复制英国急救号码、驾车规定及统一糖果数量；2026为计划复审日而非已完成更新。',
    '已直接打开完整短页，逐项读症状、家庭处理、严重低血糖与漏餐风险，核真实2023-08-03审阅日。',published_at='2023-08-03')
src(2,'National Health Service. Diabetic ketoacidosis [Internet]. 2023 Jun 8. [cited 2026 Oct 30]. Available from: https://www.nhs.uk/conditions/diabetic-ketoacidosis/',
    'https://www.nhs.uk/conditions/diabetic-ketoacidosis/',
    '酮症酸中毒的口渴多尿、恶心腹痛呕吐、深呼吸和嗜睡/意识混乱等危险表现，尚未诊断糖尿病也可能首发；不吃饭仍不能自行停胰岛素。',
    '不把普通营养性生酮等同酮症酸中毒；不提供胰岛素自调剂量，未把预计2026复审写成实际更新。',
    '已直接打开完整短页，核症状、紧急分流、就医返程与不跳胰岛素提醒。',published_at='2023-06-08')
src(3,'Cambridge University Hospitals NHS Foundation Trust. Sodium-glucose cotransporter-2 (SGLT-2) inhibitors in type 2 diabetes [Internet]. 2023 Feb 5. [cited 2026 Oct 30]. Available from: https://www.cuh.nhs.uk/patient-information/sodium-glucose-cotransporter-2-sglt-2-inhibitors-in-type-2-diabetes/',
    'https://www.cuh.nhs.uk/patient-information/sodium-glucose-cotransporter-2-sglt-2-inhibitors-in-type-2-diabetes/',
    '格列净类SGLT2抑制剂的作用、正常血糖仍可酮症酸中毒、长期禁食/极低碳水/脱水风险，开始改变饮食前须核用药。',
    '仅借稳定药物安全事实，不照搬旧页手术前停药一天的时间，也不让读者自行更改处方；批准日是资料审批日，打印日不是医学更新。',
    '直接核读药物定义、低血糖、脱水、DKA表现及风险段，并核2023-02-05 Approved与动态打印时间的区别。',published_at='2023-02-05')
src(4,'Naude CE, Brand A, Schoonees A, Nguyen KA, Chaplin M, Volmink J. Low-carbohydrate versus balanced-carbohydrate diets for reducing weight and cardiovascular risk. Cochrane Database Syst Rev. 2022;1(1):CD013334. doi:10.1002/14651858.CD013334.pub2.',
    'https://pubmed.ncbi.nlm.nih.gov/35088407/',
    '61项随机试验6925名超重或肥胖成年人；低碳与均衡碳水减重饮食至两年体重及部分心血管风险指标差异很小，长期不良反应报告不足。',
    '检索截至2021-06；低碳范围宽，不能把全部干预称严格生酮或宣布所有人疗效等同；不外推儿童和孕哺。',
    '已直接读取Cochrane官网完整通俗及结构式摘要，另核PubMed六作者、正式题录和DOI；未逐读所有原试验。',
    funding='未逐项重新核61项试验资金来源；不以系统综述名义排除底层研究的偏倚与利益影响。')
src(5,'Gardner CD, Landry MJ, Perelman D, Petlura C, Durand LR, Aronica L, et al. Effect of a ketogenic diet versus Mediterranean diet on glycated hemoglobin in individuals with prediabetes and type 2 diabetes mellitus: the interventional Keto-Med randomized crossover trial. Am J Clin Nutr. 2022;116(3):640-652. doi:10.1093/ajcn/nqac154.',
    'https://pubmed.ncbi.nlm.nih.gov/35641199/',
    '40名糖尿病前期或2型糖尿病成人，两种饮食各12周；主要分析33人，糖化血红蛋白无组间差异，生酮阶段甘油三酯更低但LDL更高、部分营养摄入更低。',
    '小型单中心短期交叉试验，不能当所有健康年轻人的长期结局；不复制体重百分比作个人预期。原文有2022勘误，未凭原图自行重算。',
    '已直接核PubMed前六作者、正式卷期页、DOI和完整摘要，查看列出的勘误记录；未将摘要称全文审读。',
    funding='资金详情未从完整正文逐项重核，因此不声称无产业关联；主要判断与更广Cochrane证据及机构安全资料并用。')
src(6,'Semnani-Azad Z, Khan TA, Chiavaroli L, Chen V, Bhatt HA, Chen A, et al. Intermittent fasting strategies and their effects on body weight and other cardiometabolic risk factors: systematic review and network meta-analysis of randomised clinical trials. BMJ. 2025;389:e082007. doi:10.1136/bmj-2024-082007.',
    'https://pmc.ncbi.nlm.nih.gov/articles/PMC12175170/',
    '99项随机试验6582名成人；间歇禁食与持续能量限制均可改善体重，隔日禁食相较持续限制的平均额外减重较小，较长期直接比较不足。',
    '不是所有16:8或5:2方案一致有效的证明；中间代谢指标不等于寿命或重大疾病结局；2025勘误主要修作者单位，不能假称另有新试验。',
    '已取得PMC全文，核读完整摘要、随访分层与利益披露相关段；未重算网络模型和逐项复核99试验。',
    funding='多位作者披露食品、营养、制药等商业或专业组织关系；利益关系不等于研究自动无效，但应保留并结合方法和其他证据判断。')
src(7,'National Institute for Health and Care Excellence. Overweight and obesity management (NG246): physical activity and diet [Internet]. 2026 Jan 8. [cited 2026 Oct 30]. Available from: https://www.nice.org.uk/guidance/ng246/chapter/Physical-activity-and-diet',
    'https://www.nice.org.uk/guidance/ng246/chapter/Physical-activity-and-diet',
    '1.16.8–1.16.12：低能量800–1200千卡及低于800千卡极低能量方案的专科支持、营养完整性、最长12周和恢复普通饮食/长期支持条件。',
    '本次直接网页/PDF未能完整读取，只用于官方原页索引可核见的具体建议，并与NHS成人治疗说明交核；英国服务资格和界值不能当中国个体处方。',
    '读取官方原页检索返回的1.16.8–1.16.12相关建议文本，核营养完整和不超过12周；未声称通读指南全文。',published_at='2025-01-14',updated_at='2026-01-08')
src(8,'National Health Service. Overweight and obesity in adults [Internet]. [cited 2026 Oct 30]. Available from: https://www.nhs.uk/conditions/overweight-and-obesity/',
    'https://www.nhs.uk/conditions/overweight-and-obesity/',
    '持续的饮食活动与专业体重服务；极低热量方案并非人人适合；GLP-1/GIP食欲调节与奥利司他减少脂肪吸收的区别。',
    '未把英国BMI种族界值或服务获得方式照抄为中国标准，不采用原页把800或1200都笼统称极低热量的分类，数值定义另以NICE明确分层。',
    '原旧treatment地址重定向至现行成人页，已读评估、体重服务、低热量与用药段；视频审阅日不当正文更新日。')
src(9,'National Institutes of Health, Office of Dietary Supplements. Dietary supplements for exercise and athletic performance: health professional fact sheet [Internet]. 2024 Apr 1. [cited 2026 Oct 30]. Available from: https://ods.od.nih.gov/factsheets/ExerciseAndAthleticPerformance-HealthProfessional/',
    'https://ods.od.nih.gov/factsheets/ExerciseAndAthleticPerformance-HealthProfessional/',
    '蛋白、BCAA和肌酸分别有不同证据；健康成人重复短时高强度训练可从肌酸获益，一水肌酸研究最多，非加载用法与水重增加；吃够完整蛋白后BCAA额外增肌证据不一致。',
    '原机构综述而非特定品牌RCT；主要为成年人和运动人群，不能把旧页全部给药表、青少年或患肾病人群一并套用，也不借用完整蛋白组成的简化说法判断所有植物蛋白。',
    '已直接读蛋白、肌酸及BCAA的机制、疗效、安全与实际使用段，核2024-04-01更新；未重读全部引用原试验。',updated_at='2024-04-01')
src(10,'Morton RW, Murphy KT, McKellar SR, Schoenfeld BJ, Henselmans M, Helms E, et al. A systematic review, meta-analysis and meta-regression of the effect of protein supplementation on resistance training-induced gains in muscle mass and strength in healthy adults. Br J Sports Med. 2018;52(6):376-384. doi:10.1136/bjsports-2017-097608.',
    'https://pubmed.ncbi.nlm.nih.gov/28698222/',
    '健康成人进行较长期抗阻训练时，补充蛋白可小幅增加平均肌肉量和力量收益；总蛋白摄入已较足时边际收益有限。',
    '旧综述、49研究1863人，不能用约1.6克/公斤回归转折点当个人最优阈值或肾病处方；未宣称所有蛋白品牌优于食物。',
    '已直接读PubMed完整摘要、题录与利益披露并核DOI；未全文重评49研究和2020更正的全部数据。',
    funding='作者SMP披露美国乳品委员会的研究、差旅和讲课支持，部分所评试验受其支持。')
src(11,'National Institute of Diabetes and Digestive and Kidney Diseases. Prescription medications to treat overweight and obesity [Internet]. 2024 Jun. [cited 2026 Oct 30]. Available from: https://www.niddk.nih.gov/health-information/weight-management/prescription-medications-treat-overweight-obesity',
    'https://www.niddk.nih.gov/health-information/weight-management/prescription-medications-treat-overweight-obesity',
    '减重药结合生活方案按健康风险选择，药物作用不同，疗程、持续获益与停药体重回升需计划；妊娠/备孕需专门核对。',
    '2024患者指导不是2026所有药物上市清单；不复制美国批准年龄、BMI、医保或儿童药物表。',
    '已直接读用途、选择、疗程、停药后变化和患者安全说明，核Last Reviewed June 2024。',updated_at='2024-06')
src(12,'US Food and Drug Administration. FDA’s concerns with unapproved GLP-1 drugs used for weight loss [Internet]. [cited 2026 Oct 30]. Available from: https://www.fda.gov/drugs/drug-alerts-and-statements/fdas-concerns-unapproved-glp-1-drugs-used-weight-loss',
    'https://www.fda.gov/drugs/drug-alerts-and-statements/fdas-concerns-unapproved-glp-1-drugs-used-weight-loss',
    '不明或未批准复配药有质量、冷链、假货、剂量测量和过快加量风险，研究试剂不可自注射。',
    '美国监管信息不等于全球每款药违法或同风险；报告不能算发生率，不用其中多剂量28天规则给所有中国注射笔规定统一期限。',
    '已直接核读假货、无处方销售、运输冷链与配制/加量错误段；未以报告统计截止日期冒充整页更新日。')
src(13,'National Center for Complementary and Integrative Health. Detoxes and cleanses: what you need to know [Internet]. [cited 2026 Oct 30]. Available from: https://www.nccih.nih.gov/health/detoxes-and-cleanses-what-you-need-to-know',
    'https://www.nccih.nih.gov/health/detoxes-and-cleanses-what-you-need-to-know',
    '排毒产品的长期减重/去毒证据不足，泻药腹泻和多日不吃仅灌茶水可造成脱水、电解质危险。',
    '生活营销排毒与有指征医疗中毒治疗不同；不把间歇性禁食研究一概当假排毒，也不声称所有成分都已被逐一证明无效。',
    '已直接读定义、研究、安全和禁食区别段；未将其引用综述视为逐篇已读。')
src(14,'National Institutes of Health, Office of Dietary Supplements. Dietary supplements for weight loss: health professional fact sheet [Internet]. [cited 2026 Oct 30]. Available from: https://ods.od.nih.gov/factsheets/WeightLoss-HealthProfessional/',
    'https://ods.od.nih.gov/factsheets/WeightLoss-HealthProfessional/',
    '减重补充剂很多复配成品缺乏直接试验，部分刺激类成分有心血管/肝脏等安全风险，不能把体重变化都当脂肪下降。',
    '未逐项重审全部配方，不替所有成分作同等无效判定；只用于产品核证原则和明显风险，不据此给育亨宾等自用剂量。',
    '已直接读总论、部分刺激成分和安全考虑相关段；未声称对市场全部燃脂产品评测。')
src(15,'World Health Organization. WHO advises not to use non-sugar sweeteners for weight control in newly released guideline [Internet]. 2023 May 15. [cited 2026 Oct 30]. Available from: https://www.who.int/news/item/15-05-2023-who-advises-not-to-use-non-sugar-sweeteners-for-weight-control-in-newly-released-guideline',
    'https://www.who.int/news/item/15-05-2023-who-advises-not-to-use-non-sugar-sweeteners-for-weight-control-in-newly-released-guideline',
    '不把非糖甜味剂作为长期控制体重的主要方法的条件性建议，排除既有糖尿病管理；不属于毒理安全评定。',
    '不是糖醇全部包含、所有无糖饮料有毒或致癌的结论；长期观察可能混杂，不能由关联证明因果。',
    '已直接完整读官方建议、适用/排除人群、条件性与毒理边界，并核2023-05-15日期。',published_at='2023-05-15')
src(16,'McGlynn ND, Khan TA, Wang L, Zhang R, Chiavaroli L, Au-Yeung F, et al. Association of low- and no-calorie sweetened beverages as a replacement for sugar-sweetened beverages with body weight and cardiometabolic risk: a systematic review and meta-analysis. JAMA Netw Open. 2022;5(3):e222092. doi:10.1001/jamanetworkopen.2022.2092.',
    'https://pubmed.ncbi.nlm.nih.gov/35285920/',
    '17项RCT1733名超重/肥胖成人，低无热量甜味饮料替代含糖饮料可有小幅体重收益；比较对象与替代而非追加很重要。',
    '中期替换试验并非长期疾病或寿命证明；女性居多，多为糖尿病或其风险人群，不据此声称胜过清水或无限喝。',
    '已直接读PubMed完整结构摘要、作者、年卷文号、DOI和商业利益披露；未声称逐读全部试验。',
    funding='多位作者披露食品、糖/甜味剂、营养组织资助或顾问关系，资助来源不能单独决定研究对错。')
src(17,'Kreider RB, Kalman DS, Antonio J, Ziegenfuss TN, Wildman R, Collins R, et al. International Society of Sports Nutrition position stand: safety and efficacy of creatine supplementation in exercise, sport, and medicine. J Int Soc Sports Nutr. 2017;14:18. doi:10.1186/s12970-017-0173-z.',
    'https://link.springer.com/article/10.1186/s12970-017-0173-z',
    '正式学会立场支持力量/重复高强度运动用途、一水肌酸研究基础、渐进增加储量的非加载方案及所研究健康运动者的长期安全数据。',
    '叙述性立场而非全新系统综述；长期资料的人群、剂量和监测条件有限，不把其中较宽泛的全龄安全或疾病治疗推断写成大众自行使用建议。',
    '已取得出版商开放全文，核读补充方案、生物利用度/不同形式、运动用途、安全及利益披露段；未逐读269条引用。',
    funding='稿件获Council for Responsible Nutrition支持；多位作者有肌酸/补充剂产业资助、顾问、销售或知识产权关系，已核原文披露。')
src(18,'Hultman E, Söderlund K, Timmons JA, Cederblad G, Greenhaff PL. Muscle creatine loading in men. J Appl Physiol (1985). 1996;81(1):232-237. doi:10.1152/jappl.1996.81.1.232.',
    'https://pubmed.ncbi.nlm.nih.gov/8828669/',
    '31名男性的肌肉储量研究：较小日量持续28天可逐渐增加肌肉总肌酸，支持不必以大剂量加载作为唯一进入方式。',
    '旧、小型男性生理研究，主要测肌肉储量及排泄，不直接证明各种运动成绩、女性/疾病人群效果或长期肾安全；不把研究日量当个人处方。',
    '直接核PubMed完整摘要、五名作者、卷期页与DOI；未获得原论文全部正文，因此不声称全文评审。',
    funding='摘要未提供资助与利益披露，未核实，不写成无利益冲突。')
src(19,'Wolfe RR. Branched-chain amino acids and muscle protein synthesis in humans: myth or reality? J Int Soc Sports Nutr. 2017;14:30. doi:10.1186/s12970-017-0184-9.',
    'https://link.springer.com/article/10.1186/s12970-017-0184-9',
    '解释BCAA仅为三种必需氨基酸、蛋白合成需要其他原料，以及不能由信号通路或动物实验直接推成人长期增肌。',
    '机制性叙述评论，所述当时缺口不能作2026年现状；不采用其“没有口服人体研究”或一概不刺激合成的断言，须结合同期口服随机试验。',
    '已取得出版商开放全文，核读背景、理论/人体输注研究、信号与合成区别及利益披露；用于推理边界而非疗效最高等级。',
    funding='作者披露牛肉行业、Abbott Nutrition、Danone、PepsiCo研究/酬金，Essential Blends持股及Axcella顾问关系；原文专项Funding为不适用。')
src(20,'Jackman SR, Witard OC, Philp A, Wallis GA, Baar K, Tipton KD. Branched-chain amino acid ingestion stimulates muscle myofibrillar protein synthesis following resistance exercise in humans. Front Physiol. 2017;8:390. doi:10.3389/fphys.2017.00390.',
    'https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2017.00390/full',
    '10名训练年轻男性的随机交叉试验：BCAA较安慰剂提高运动后4小时的肌原纤维蛋白合成，表明并非完全没有生理作用。',
    '没有完整蛋白同场对照，不证明吃够完整蛋白后额外获益、长期肌肉量或力量；论文与旧乳清试验的跨研究数值比较不能当直接头对头试验。',
    '已读取出版商完整摘要及方法、主要合成结局、讨论/局限和资金披露；核10名完成者及4小时测量，不重算示踪模型。',
    funding='GlaxoSmithKline Healthcare向KDT提供研究资助并提供试验饮品；作者另声明无可被视为潜在冲突的商业关系，两项原文均保留。')
src(21,'Antonio J, Candow DG, Forbes SC, Gualano B, Jagim AR, Kreider RB, et al. Common questions and misconceptions about creatine supplementation: what does the scientific evidence really show? J Int Soc Sports Nutr. 2021;18:13. doi:10.1186/s12970-021-00412-w.',
    'https://link.springer.com/article/10.1186/s12970-021-00412-w',
    '肌酸与肌酐的代谢区别，补充背景影响肌酐及以肌酐估算肾功能的解读；健康人研究不能仅凭一项化验等同肾损伤。',
    '专家叙述综述，非独立肾病使用指南；不能由肌酐有混杂就忽略真实异常，也不能把健康研究推成肾病、孕哺和未成年自行使用的安全证明。',
    '已取得出版商开放全文，核读水重、类固醇区别、肾功能/肌酐完整相关段及利益披露；未声称逐条复核全部原试验。',
    funding='多位作者披露Alzchem及补充剂公司的顾问、经费、产品捐赠或讲课关系，ISSN也接受相关企业支持；不隐去产业关系。')

entries=[]
def entry(n,title,summary,plain,benefit,evidence,refs,notes='',ages=('adult','older'),urgent=False,unit=None):
    unit=unit or ('nutrition-u1' if n==1 else 'nutrition-u2' if n<=4 else 'nutrition-u3' if n<=7 else 'nutrition-u4')
    token=''.join(f'[@NUT-S{i:02d}]' for i in refs)
    e=dict(id=f'nutrition-{n:03d}',chapter_id='nutrition',unit_id=unit,ordinal=n,title=title,summary=summary,
        fields=dict(cost='',plain=plain,benefit=benefit,evidence=evidence,sources=token,notes=notes),
        audience=dict(age_groups=list(ages),sexes=['all'],scope_note='面向成年读者的饮食与消费判断；孕哺、低体重、慢病和用药限制按正文分支核对。',safety_pin=urgent),
        clinical_review_status='not_clinically_reviewed',content_checked_at=DATE)
    entries.append(e)

entry(1,'节食时发抖先停下来处理，晕厥、意识异常或深快呼吸直接急救',
    '减脂不该靠忍住明显不适继续饿。发抖、出汗、心慌或头晕先停止禁食和训练，糖尿病用药者及时测血糖并按低血糖方案处理。意识异常、晕厥不能喂糖水；持续呕吐、腹痛、深快呼吸或嗜睡也要急诊，尤其正在用格列净类药物时，血糖正常不能排除危险。',
    '**出现发抖、冷汗、心慌或头晕，先停止禁食和运动，坐下或躺到安全处；不要开车硬撑。** 这些表现并不自动等于低血糖，但用胰岛素或部分降糖药时，漏餐和少吃碳水会增加风险。已知糖尿病者尽快测血糖，低于自己的处理阈值或出现熟悉的低血糖症状时，清醒且能安全吞咽才按既定方案用快速糖，之后复测；不靠无糖饮料补糖。[@NUT-S01]\n\n意识不正常、抽搐或昏迷，立即呼叫120，不把食物、糖水或凝胶塞进嘴里。若有预先处方的胰高血糖素且施救者受过使用指导，按既定急救方案处理。没有糖尿病却反复这样不适，也需要查原因，不能一直用吃糖掩盖。[@NUT-S01]\n\n**持续呕吐、腹痛、深快呼吸、异常嗜睡或意识混乱，要立即急诊，不当作生酮适应期。** 酮症酸中毒是血液中酸性物质危险积累的急症，和普通营养性生酮不同。服达格列净、恩格列净等SGLT2抑制剂时，长期禁食、极低碳水及脱水会增加风险，血糖不高也不能排除；就诊时带上用药信息。不因没吃饭自行停胰岛素。[@NUT-S02][@NUT-S03]',
    '把可及时处理的不适与必须抢时间的代谢急症分开，避免为掉秤拖延救治。',
    'C，官方急症及药物安全指导；症状用于分流，不作低血糖或酸中毒的远程确诊。',[1,2,3],
    notes='不能把普通饥饿等同低血糖，也不能凭呼气味道或一张尿酮试纸自行排除急症。',urgent=True,unit='nutrition-u1')
entry(2,'想低碳减脂可以比较，但别把严格生酮当人人更优的必选项',
    '生酮是把碳水压得很低、让身体更多利用脂肪和酮体供能的饮食，和少喝奶茶不是一回事。它可能帮助一些人减重，却没有可靠证据证明所有人长期都比均衡减能量更好。先看能否保留营养与长期坚持；糖尿病用药者先核低血糖和酸中毒风险，不自己减药。',
    '**先选择能持续吃、营养够且符合健康目标的方案，不必为了减脂强行进入生酮。** 低碳饮食有多种程度；严格生酮通常把碳水降得更低，使身体产生更多酮体，但不是吃越多油就能越瘦。Cochrane汇总成人随机试验，低碳与均衡碳水减重饮食在一至两年的平均体重差异很小；不能把开始快速掉秤都理解成多减了脂肪。[@NUT-S04]\n\n若选择低碳，别只删主食再用加工肉、黄油和奶油填满：记录实际餐食、蔬菜和纤维、饱腹感及能否坚持。已有血脂问题时，把饮食前后的血脂复查纳入计划。小型Keto-Med试验在糖尿病前期/2型糖尿病成人中发现，生酮相较地中海式方案并没有更好的主要血糖结局，同时出现更高LDL和更低部分营养摄入；这不是所有人的个人结果。[@NUT-S04][@NUT-S05]\n\n正在用降糖药，特别是胰岛素、磺脲类或格列净类，开始大幅改碳水前先让处方团队调整监测与用药方案，不自行减停药。孕哺、低体重、进食障碍史或复杂慢病者，不按网红模板自行开始严格生酮。针对癫痫等疾病的医疗生酮另有专业方案。[@NUT-S01][@NUT-S03][@NUT-S07]',
    '把能执行的饮食偏好与特殊代谢方案分开，不为追求酮体数值牺牲安全和营养。',
    'B，成人随机试验综述支持低碳与均衡方案长期差异有限；具体严格生酮的长期安全、依从性及个体反应仍有局限。',[4,5,1,3,7])
entry(3,'限时进食可当安排餐次的工具，别把越饿越久当成更会减脂',
    '16:8、5:2和隔日禁食是不同的间歇性进食安排，不是自动减脂公式。部分成人会因更容易少吃而受益，但长期并不稳定优于每天适度减少总能量。先看工作、训练和进食是否协调；若让你反复头晕、暴食或总量严重不足，就换更规律的吃法，不继续缩短窗口。',
    '**如果限时吃饭让你更容易安排餐次，可以试；若只是把正常饭量挤进更短时间，却反复饿到失控，就不值得坚持。** 16:8通常指一天在8小时内进食，5:2指一周部分天限制能量，隔日禁食又是另一种安排，不能互相借用效果。[@NUT-S06]\n\n2025年99项成人随机试验的综合分析显示，间歇禁食和持续能量限制相比随意吃都可减重；隔日禁食有小幅平均额外收益，但较长期比较并未显示一种禁食法稳定胜出。不把短期体重或血糖变化说成已证明延寿、排毒或防所有慢病。[@NUT-S06]\n\n先保留能吃够的正餐和蛋白质，观察精力、饥饿、训练恢复和能否长期执行，不用App连续打卡逼自己延长禁食。已经发抖、头晕或明显乏力就停止限制并查原因。用降糖药、孕哺、低体重、进食障碍史或年长体弱/进食不足者，先作个体评估，不自行照搬16:8；儿童青少年不使用这份成人减脂方案。[@NUT-S01][@NUT-S03][@NUT-S07]',
    '把进食时间作为可替换的安排，而不是必须完成的挨饿考核。',
    'B，成人网络荟萃分析主要评估体重和代谢中间结局；时长、方案与人群不同，不能外推为统一最佳禁食窗口。',[6,1,3,7])
entry(4,'别自行长期吃到每天不足800千卡，快速减重方案要把恢复进食也安排好',
    '每天只喝几瓶奶昔、只吃水果或干脆不吃饭，不等于医学减重。低到每天不足800千卡的方案需要特定指征、营养完整配方、用药核对和专业支持，也不能长期照做。便秘、疲劳、掉发和体重回升都应提前考虑；买产品前先问清监测、普通食物如何恢复和谁来随访。',
    '**不要把极低能量菜单当成人人都能自行坚持的减脂捷径。** NICE把每天低于800千卡列为极低能量饮食；800至1200千卡也属于需要特定支持的低能量方案，不是给所有成年人的日常推荐值。特定肥胖或相关疾病情境下，专业团队可能采用这些方案；单凭想快点瘦不是充分理由。[@NUT-S07][@NUT-S08]\n\n正式方案应营养完整、事先核对药物与进食障碍风险，并有临床支持。NICE这类方案要求不超过12周，之后逐步恢复多样食物，并接上长期维持支持；不能把这个上限理解成自行饿12周都安全。只喝蛋白粉、果蔬汁或排毒茶并不自动满足营养完整。[@NUT-S07][@NUT-S13]\n\n开始前问清适用目的、谁监测、哪些症状要停、多久复评以及恢复普通饮食的步骤。长期几乎不进食、明显消瘦或持续乏力者，先就医评估营养和代谢状况，不再自行加码限制。明显不适按急症入口处理，不把掉发、疲劳一概当意志训练的代价。[@NUT-S07][@NUT-S08]',
    '区分有医学支持的短期方案与营养不足的自行挨饿，并防止只买产品而没有后续维护。',
    'C，NICE具体实践建议与NHS成人治疗说明；不能把其能量分类或最长周期当个人处方或中国服务资格。',[7,8,13])
entry(5,'先算一日蛋白缺口再买蛋白粉，别为练后半小时的倒计时加量',
    '蛋白粉是补充蛋白质的方便食品，不是打开增肌开关的药。先看全天餐食与力量训练，再决定有没有缺口；吃够后额外多灌不保证继续长肌肉。乳清、酪蛋白和合适的植物蛋白按耐受与配方选，不必为错过练后半小时焦虑；肾病或营养问题另定摄入方案。',
    '**先把一天从蛋、奶、豆、鱼肉等吃到的蛋白算进去，只补实际不足的部分。** 有规律抗阻训练、同时摄入不够时，蛋白补充可帮助提高平均肌肉和力量收益；不训练或已经吃够，单纯多买几勺不会按比例变强。健康成人抗阻训练研究中，总蛋白已较足后的额外收益有限，不能把研究回归点当所有人的精确上限。[@NUT-S09][@NUT-S10]\n\n选产品先看每份实际蛋白量、配料、过敏原和是否耐受，而不是桶有多大。乳清、酪蛋白和配得合适的植物来源都能帮助补充；若乳制品引起不适，核对乳糖和过敏问题，不必硬喝同款。增肌粉可能同时带来很多能量，和单纯蛋白粉不是同一任务。[@NUT-S09]\n\n不用为了“黄金半小时”慌忙加量。训练前后能正常吃饭时，把蛋白分散到日常餐食、确保总量与恢复更实用；确实不方便吃饭再用粉补。肾病、孕哺、进食困难或需要医学营养治疗时，不按健身博主克数自配；蛋白粉也不是营养完整代餐。[@NUT-S09][@NUT-S10]',
    '让蛋白粉解决方便与摄入缺口，减少为时机焦虑或大包装溢价付费。',
    'B，健康成人抗阻训练试验综述支持适当补充的平均收益；不证明所有品牌胜过普通食物，也不提供疾病人群统一剂量。',[9,10])
entry(6,'有力量训练目标再考虑一水肌酸，别把涨水重当长脂肪或追昂贵变体',
    '肌酸帮助肌肉在短时高强度活动中快速供能，和类固醇不是一回事。一水肌酸证据较多，可辅助反复冲刺或力量训练，但不是普通散步必须买的保养品。开始后体重可能因肌肉水分增加而上升；先看训练目标、耐受和健康条件，不为高级肌酸名称或强制冲击期多花钱。',
    '**规律做力量或重复短时高强度训练、饮食已基本到位时，可以把一水肌酸作为可选辅助。** 它参与肌肉快速能量周转，不是合成代谢类固醇，也不是减脂药；对长时间耐力项目的帮助和体重代价要另看。研究最多的是一水肌酸，其他更贵的盐类、缓冲或酯化形式没有被可靠证明普遍更好。[@NUT-S17][@NUT-S21]\n\n不要照搬先大量“冲击”的做法。成人研究也有不加载、每天约3至6克持续数周的方案；这说明不必先大剂量灌入，不是要求每人照这个克数用。较小日量使肌肉储量逐渐增加，开始起效可能较慢；早期试验测到储量相近，也不等于证明每个人短期运动成绩一样。选单一成分、量具清楚的产品，按标签与专业运动营养方案核对；明显胃肠不适时停止并复评。[@NUT-S09][@NUT-S17][@NUT-S18]\n\n早期体重增加可能含水分，不能直接当成新增脂肪。健康运动者的研究没有支持常规补充必然损害肾功能，但这不等于所有健康状态和产品都安全。抽血检查时主动说明在用肌酸，化验结果需结合背景解读，不自己凭单次肌酐判断肾损伤或宣布肾绝对没问题。已知肾病、孕哺或其他慢病者先核方案，儿童青少年不照这份成人运动补充指南自行用。[@NUT-S17][@NUT-S21]',
    '保留肌酸在合适训练中的实际价值，避免把它当人人必需或因短期体重变化误判减脂。',
    'B，成人运动研究、肌肉储量原试验和学会立场支持特定用途；不加载证据不等于即时运动效果相同，安全也不能外推所有年龄、疾病或复配产品。',[9,17,18,21],ages=('adult',))
entry(7,'已经吃够完整蛋白时，先别为BCAA和亮氨酸再加一份增肌预算',
    'BCAA是亮氨酸、异亮氨酸和缬氨酸三种必需氨基酸，不是完整蛋白质的替代品。它们能参与肌肉代谢，不代表饮食蛋白已经足量时再补就一定多长肌肉。先补餐食、总蛋白与训练缺口；只有体感酸痛变轻，也不能直接推成长期增肌更好。',
    '**有预算时先保证训练、餐食和完整蛋白，不把BCAA列成蛋白粉之外的必买第二桶。** BCAA指三种支链必需氨基酸；人体合成肌肉蛋白需要的不只有这三种，完整蛋白食物本来就含它们。只拿“亮氨酸能触发合成信号”这样的机制，不足以证明该瓶产品让你长期多长肌肉。[@NUT-S09][@NUT-S19]\n\nBCAA并非完全没有生理作用：一项10名年轻训练男性的试验发现，相较安慰剂，练后4小时的肌肉蛋白合成更高。但它没有完整蛋白同场对照，也没有观察长期肌肉量，不能证明已经吃够优质蛋白后再补还有增量价值。长期肌肉量和训练表现的额外收益尚未稳定建立；酸痛或恢复指标变化也不能自动翻译成所有人更强、更不受伤。[@NUT-S20][@NUT-S09]\n\n如果日常总蛋白不足，先增加合适食物或确有需要的蛋白补充；如果已经足够，就把钱留给更有明确作用的训练条件。不要因为饮料标了BCAA，就把它当蛋白质正餐；也不按网上安全上限反推应该服用的剂量。疾病、孕哺或未成年情境另核。[@NUT-S09]',
    '把生理机制、短期恢复感受和真正增肌收益分开，减少没有明确增量价值的叠加购买。',
    'B，短期口服随机试验显示可有合成信号和生理作用，但不能证实完整蛋白已足时的长期额外增肌；机制评论不替代临床结局。',[9,19,20],ages=('adult',))
entry(8,'用代餐前先认清是否营养完整，别拿蛋白奶昔或青汁长期替一日三餐',
    '代餐只是一种把进食定量、方便携带的方式，效果要看它替代了什么以及整天怎么吃。普通蛋白粉、青汁、果汁和一根棒不能自动算完整的一餐；把全天都换成配方食品则是另一种需要支持的减重方案。买之前核对能量、蛋白、纤维与维矿，并提前安排恢复普通食物。',
    '**先分清“替一餐方便”与“全天配方饮食”。** 普通奶昔、青汁、蛋白粉或零食棒，只有一个产品名不能证明营养完整；全日替代更不能只靠把产品份数乘三。代餐的减重价值要看是否帮助形成可持续的总能量调整，而不是有独立燃脂成分。[@NUT-S07][@NUT-S08]\n\n偶尔需要方便进食时，核对每份能量、蛋白质、纤维、维生素矿物质及过敏原，连同当天其他餐食一起看；不是标签写高蛋白就可长期省掉蔬果和普通食物。若计划全天只用配方，必须确认是否营养完整、是否适合自己的疾病与药物，并接入有长期支持的专业方案。[@NUT-S07]\n\n购买前就问清能执行多久、出现不适找谁、普通食物怎么逐步恢复及体重回升时怎样调整。产品本身没有提供这些，不要把全代餐当成无人监督的长期日常饮食。低体重、孕哺、进食障碍史或年长进食不足者，优先作营养评估。[@NUT-S07][@NUT-S08]',
    '保留代餐的便利与定量价值，避免把营养不完整的节食包装成专业减重。',
    'C，营养完整性与专业低能量方案的实践规范；不能仅从“代餐”二字判断成品有效、完整或适合。',[7,8])
entry(9,'需要减重药就按长期治疗选方案，别买研究针剂或照别人的剂量加量',
    '正规减重药对合适人群可以有效，但它不是人人都该用的美容保养。先核是否有健康相关指征、现有疾病与药物，再比较效果、副作用、妊娠计划和长期维护。网购不明原料、自己分装或为快瘦提前加量，会额外带来质量和剂量风险；停药后的体重管理也应提前谈好。',
    '**需要药物帮助并不等于意志差，但要由正规诊疗把适用条件和随访定清。** GLP-1、GIP是参与进食和代谢调节的激素信号；相关药物可模拟这些信号，影响食欲、饱腹与血糖。奥利司他主要减少部分脂肪吸收，不能只按“都能瘦”互换。临床会结合体重相关健康风险、其他疾病、全部用药和妊娠计划，不照搬海外BMI门槛自购。[@NUT-S08][@NUT-S11]\n\n购买只走能核实处方、产品和药房来源的正规渠道。标研究用途、非人体用、不需要评估就售卖的针剂，或让你自己把粉末和液体配成剂量的产品，不拿来试。具体制剂的浓度、给药器和加量节奏不同，不能把别人的“几格、几滴、几个单位”照搬；冷链和包装异常先联系药师核实。[@NUT-S12]\n\n提前谈何时评估效果、哪些副作用要联系团队、能否长期使用以及停药后的维护；不要因为短期停滞自行叠加药或加快加量。持续严重腹痛、反复呕吐或明显脱水要及时求助。孕哺、准备怀孕或已有进食/营养问题时，方案须另核。[@NUT-S11][@NUT-S12]',
    '把确有证据的药物治疗与不明针剂消费分开，减少无指征使用、配错剂量和无人随访。',
    'C，本条是选择与安全路径，依据官方治疗和监管资料；药物具体疗效需分制剂、剂量及人群评估。',[8,11,12])
entry(10,'别用燃脂丸、排毒茶和泻药追掉秤，先核它减的是脂肪还是水分',
    '排便更多、出汗更多和几天体重下降，都不能证明脂肪减少。燃脂复配产品常缺乏成品的长期人体证据，排毒茶和泻药还可能带来腹泻、脱水或电解质问题。先看具体成分、直接研究和风险；来源不明、承诺不用改变吃动就快瘦的产品，不拿来长期保养。',
    '**不要用腹泻、利尿或出汗当作减脂成效。** 排毒茶、果汁清肠和泻药套餐没有因此获得长期去脂或“清毒”的证明；持续只喝茶水不吃饭，反而可能出现脱水和电解质紊乱。便秘需要按排便问题治疗，不能把泻药当美容减重用品。[@NUT-S13]\n\n燃脂丸、左旋肉碱复配、育亨宾、绿茶提取物或高咖啡因产品要逐个看成分和实际成品研究，不能凭“促进脂肪代谢”机制认定长期更瘦。很多试验样本小、时间短，单一成分信号也不能替多成分瓶装产品背书；刺激类或高浓缩成分还可能增加不适、相互作用或其他安全风险。[@NUT-S14]\n\n购买前若说不出研究对象、对照、多久、改善多少，以及成分总量，就先不买。出现明显心悸、胸痛、晕厥、持续呕吐或其他严重不适，停止可疑产品并及时就医，带上包装。不要为排毒自行停处方药；有明确中毒时的医学治疗与这类营销不是一回事。[@NUT-S13][@NUT-S14]',
    '减少以水分与排便变化冒充减脂、以模糊机制替代成品证据的消费。',
    'C，机构产品证据与风险梳理；未把所有成分一概判无效，也不能从短期掉秤推出长期脂肪改善。',[13,14])
entry(11,'想少喝糖可以用无糖饮料替换，别把它追加成长期减脂保健品',
    '无糖饮料是否帮忙，取决于它替代了含糖饮料还是额外加在原有饮食上。成人替换试验发现小幅体重收益，不能由此说比清水更养生或长期必瘦。日常优先水和不加糖饮品，暂时换成无糖款也不必恐慌；无糖也不表示整份食品没有能量，更不是可以无限吃的通行证。',
    '**如果原来经常喝含糖饮料，用低/无热量款替换可以是过渡选择；本来就喝水，不必为减脂额外加一瓶代糖饮料。** 成人随机试验综述发现，用低无热量甜味饮料替含糖饮料有小幅平均体重改善，但不证明它优于清水，也不是无限喝或补偿性多吃的理由。[@NUT-S16]\n\nWHO不建议把非糖甜味剂作为长期控制体重的主要方法，这是一项有条件建议：长期观察可能受混杂影响，既有糖尿病的管理不在该建议范围，糖醇也不是同一分类。不能把这句话改写成“每次喝代糖都致癌”，也不能把短期替换试验升级为长期防病保证。[@NUT-S15]\n\n实际选择时看它有没有替掉原来的糖与能量，核对整份食品的营养标签，别把甜味剂研究当所有无糖点心可以无限吃的依据。逐渐减少整体甜度、把清水和不加糖饮品作为常用选项，比追一种所谓零负担饮料更容易说明目标。[@NUT-S15][@NUT-S16]',
    '用正确的比较对象判断替换价值，避免无糖营销与无依据恐慌两个方向的误读。',
    'B，成人替换试验与条件性公共卫生建议回答不同问题；中期体重收益不能证明长期疾病结局。',[15,16])

for e in entries:
    assert 100<=len(e['summary'])<=180,(e['id'],len(e['summary']))
    assert list(e['fields'])==['cost','plain','benefit','evidence','sources','notes']
    assert e['fields']['sources']
for name,value in [('entries',entries),('sources',sources)]:
    (HERE/f'nutrition-{name}.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
audit=dict(checked_at=DATE,entries=11,sources=len(sources),clinical_review_status='not_clinically_reviewed',
    main_scope='成人减重饮食、运动营养产品与相关急症；运动中补水、空腹运动和完整心理健康另由整合者分工。',
    non_duplication='基线basics004/005/007/010保留；新增条目回答具体方案与产品分支，不复制基础餐盘、饮水和补剂清单。',
    exclusions=['不编个人热量、BMI用药门槛、统一药物剂量、外国批准等同中国准入。','不把营养性生酮等同DKA，不把单纯饥饿确诊低血糖。','不以新发表等同纳入新试验，也不以机构名称决定A级。','未针对每个现售品牌完成评测；未声称临床医生签审。'],
    reading_limitations=['NICE正文与PDF访问未成功，只有官方原页索引相关1.16.8–1.16.12建议，准确记录此范围并与NHS服务说明交核。','WHO已读取官方发布页与完整建议说明，90页全文未通读。','蛋白、低碳与甜味饮料论文核完整摘要与题录，不称全部全文或原始数据已审核。','ISSN2017立场、Wolfe2017评论、Jackman2017口服试验与Antonio2021综述已直接取得出版商开放全文并读相关段；Hultman1996只核完整摘要，不冒称全文。'],
    proposed_units=[dict(id='nutrition-u1',title='先处理节食中的危险信号',entry_ids=['nutrition-001']),dict(id='nutrition-u2',title='按长期可持续性比较低碳、禁食和低能量方案',entry_ids=['nutrition-002','nutrition-003','nutrition-004']),dict(id='nutrition-u3',title='按实际缺口选蛋白与训练补充品',entry_ids=['nutrition-005','nutrition-006','nutrition-007']),dict(id='nutrition-u4',title='分清便利、医疗治疗与营销产品',entry_ids=['nutrition-008','nutrition-009','nutrition-010','nutrition-011'])],
    fact_checks=['Vancouver前六作者+et al.，DOI没有重复url前缀或末尾乱码。','全部摘要100–180字，成本为空且不写价格待核占位。','成人研究不推儿童；肌酸/BCAA成人only，其他成年与年长范围保留正文慢病/营养限制。','006保留ODS支持的非加载3–6克研究范围，未新增固定个人剂量；Hultman只支持渐进储量，不升级为运动表现等效或长期肾安全。','007纳入BCAA相较安慰剂的急性合成阳性原试验，不把旧Wolfe评论的“无人类口服研究”或普遍无效断言当现状；急性合成与长期完整蛋白之外增量收益分开。','17/19/20/21均逐项记录补充剂、食品或药企资助关系，不因正式学会或开放全文而隐去产业影响。'])
(HERE/'nutrition-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('written',len(entries),'entries',len(sources),'sources')
