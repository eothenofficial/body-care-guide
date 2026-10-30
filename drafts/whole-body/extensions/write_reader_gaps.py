"""Author the source-traced reader gaps; integration keeps existing stable IDs."""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATE = '2026-10-29'


def save(name, obj):
    (HERE/name).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def web(identifier, author, title, url, date, support, limits, depth):
    return dict(id=identifier, citation=f'{author}. {title} [Internet]. '+(date+'. ' if date else '')+
        '[cited 2026 Oct 29]. Available from: '+url, url=url, type='监管、公共卫生或专业学会原始指导',
        support=support, limitations=limits, reading_depth=depth, content_checked_at=DATE,
        funding_disclosure='机构指导；本轮未对其引用的全部试验另作资助审查，机构名称不替代证据质量。')


def entry(identifier, group, title, summary, plain, benefit, sources, evidence='C，机构临床与患者指导；不以症状自诊或替个体开处方。',
          notes='', sexes=('all',), ages=('adult','older'), safety=False):
    fields=dict(cost='', plain=plain, benefit=benefit, evidence=evidence, sources=sources, notes=notes)
    return dict(id=identifier, chapter_id='private', unit_id=group, ordinal=int(identifier.rsplit('-',1)[1]),
        title=title, summary=summary, fields=fields, evidence_labels=list(dict.fromkeys(re.findall(r'\b[ABC]\b',evidence))),
        tags=[], source_ids=list(dict.fromkeys(re.findall(r'\[@([^\]]+)\]', '\n'.join(fields.values())))),
        audience=dict(age_groups=list(ages), sexes=list(sexes), safety_pin=safety,
            scope_note='按实际器官、症状和生活场景阅读；成人用药和检查不直接套给儿童、孕哺或有特殊疾病者。'),
        content_checked_at=DATE, clinical_review_status='not_clinically_reviewed')


def main():
    sources = [
        web('READER-S01','Centers for Disease Control and Prevention','About bacterial vaginosis (BV)',
            'https://www.cdc.gov/bacterial-vaginosis/about/','2023 Dec 11',
            'BV为菌群失衡，症状、处方抗菌治疗和不灌洗。',
            '旧公众页不承担2025年后伴侣治疗推荐；该问题单独采用新试验并保留边界。',
            '实际读CDC原页定义、症状及治疗；没有借旧页覆盖后续新研究。'),
        dict(id='READER-S02', citation='Vodstrcil LA, Plummer EL, Fairley CK, Hocking JS, Law MG, Petoumenos K, et al. Male-partner treatment to prevent recurrence of bacterial vaginosis. N Engl J Med. 2025;392(10):947–957. doi:10.1056/NEJMoa2405404.',
            doi='10.1056/NEJMoa2405404', url='https://pubmed.ncbi.nlm.nih.gov/40043236/', type='原始人体随机试验',
            support='特定稳定异性伴侣中，女性治疗加男伴口服与局部联合治疗，12周BV复发低于只治女性。',
            limitations='开放试验、提前终止、特定伴侣与联合方案、短随访；未推广到所有阴道炎/所有伴侣或自行分药。',
            reading_depth='实际核PubMed完整结构化摘要、前六作者与正式题录；未取得NEJM付费全文，也未完成所有后续研究系统综述。',
            funding_disclosure='摘要列澳大利亚NHMRC资助及StepUp注册；未逐条核作者全部利益申报。',content_checked_at=DATE),
        web('READER-S03','Centers for Disease Control and Prevention','Trichomoniasis: STI treatment guidelines',
            'https://www.cdc.gov/std/treatment-guidelines/trichomoniasis.htm','2021 Jul 22',
            '滴虫感染检测、有效抗微生物药类别、同步伴侣治疗、疗程后症状消退前避免性接触及复查。',
            '美国2021指导，不搬处方剂量与伴侣代处方法规；并未逐篇重读所有引用试验。',
            '实际读原页诊断、治疗、复查及Management of Sex Partners相关段。'),
        web('READER-S04','National Health Service','Urethritis',
            'https://www.nhs.uk/conditions/urethritis/','2023 May 10',
            '尿道灼痛与异常分泌物需评估，尿液/拭子检测、按因用药、伴侣与暂停性接触。',
            '超过计划复审日；仅采用稳定症状与就诊原则，与CDC现有评估资料并读，不采用英国服务号码和供药状态。',
            '实际读原页症状、就诊检测、治疗和伴侣段及页脚日期。'),
        web('READER-S05','National Health Service','Penis lumps and spots',
            'https://www.nhs.uk/symptoms/penis-lumps-and-spots/','2024 Jun 25',
            '阴茎新皮损可有正常变异、皮肤病或STI；需检查而非图片自诊。',
            '不声称所有丘疹是病，也不凭良性外观排除所有疾病。',
            '实际读原页何时检查、可能原因和检查方式。'),
        web('READER-S06','National Health Service','Testicle lumps and swellings',
            'https://www.nhs.uk/symptoms/testicle-lumps-and-swellings/','2023 Jul 18',
            '睾丸新肿块形态变化安排检查；持续静息痛与突发剧痛急诊；可需超声。',
            '超过预计复审日，用于稳定分流并与现有2026睾丸痛入口核对；不推荐所有无症状者做影像筛查。',
            '实际读原页全部相关症状、急诊与检查段。'),
        web('READER-S07','National Health Service','Blood in semen',
            'https://www.nhs.uk/symptoms/blood-in-semen/','2025 Sep 23',
            '新鲜/陈旧血精可红或褐色；通常非严重但应检查，治疗按原因。',
            '不能凭颜色确诊前列腺炎或肿瘤，不建议普遍自行用抗生素。',
            '实际读原页外观、伴随症状、病因及处理。'),
        web('READER-S08','European Association of Urology','EAU guidelines on sexual and reproductive health: Management of erectile dysfunction',
            'https://uroweb.org/guidelines/sexual-and-reproductive-health/chapter/management-of-erectile-dysfunction','2026',
            'ED病史和代谢/激素等评估、生活/心理支持、PDE5抑制剂适应选择；硝酸酯/NO供体/尼可地尔禁忌。',
            '2026有限更新；仅核相关正文与推荐，不是重审全部试验、器械或具体中国药品说明。',
            '实际读5.4评估、5.5推荐、5.6治疗及5.6.3.f.2禁忌段；版本状态在介绍页另核。'),
        web('READER-S09','European Association of Urology','EAU guidelines on sexual and reproductive health: Disorders of ejaculation',
            'https://uroweb.org/guidelines/sexual-and-reproductive-health/chapter/disorders-of-ejaculation','2026',
            '早泄多维判断，时间不足以单独诊断；先天后天分型、药物与心理行为方案、局麻药向伴侣转移及备孕警示。',
            '成人男性指南；不输出通用剂量、以秒数诊断或将延时商品等同受试制剂。',
            '实际读6.2定义/诊断及6.2.6局麻药与相应治疗段；未声称全文所有射精病种审读。'),
        web('READER-S10','National Health Service','Priapism (painful erections)',
            'https://www.nhs.uk/symptoms/priapism-painful-erections/','2023 Dec 5',
            '持续3至4小时勃起需急诊，镰状细胞病疼痛超过1小时更早；不冰敷/继续性活动拖延。',
            '警示时间不是必须等满；痛程度不用于家庭鉴别不同血流型。',
            '实际读原页急诊阈值、错误处理和病因。'),
        web('READER-S11','Department of Health, Victoria','Masturbation',
            'https://www.betterhealth.vic.gov.au/health/HealthyLiving/masturbation','2026 Apr 23',
            '各性别可选择自慰，无统一正常次数；影响生活才需评估，不能把自慰当不孕/失明原因。',
            '只用频率、选择、同意和误区段；未将其广泛好处叙述当随机试验证实的治病用途。',
            '实际读2026复核日期、定义、频率、同意及myths段，未核所有外链。'),
        web('READER-S12','中国疾病预防控制中心','HPV感染：常见问答',
            'https://www.chinacdc.cn/jkyj/mygh02/ymkyfjb/hpvgr/202606/t20260622_1837244.html','2026 Jun 22',
            '男女HPV预防、国内不同疫苗/人群程序差异、疫苗不清已有感染、接种后仍应按规范筛查。',
            '公众问答将男性年龄概括为9–26，不当作每款产品同一适应证；本篇不替具体品牌现行标签。',
            '实际读全部11问，重点男性适用、国家免疫规划、针次差异及接种后筛查，核页面日期。'),
        web('READER-S13','European Association of Urology','EAU guidelines on sexual and reproductive health: Priapism',
            'https://uroweb.org/guidelines/sexual-and-reproductive-health/chapter/priapism','2026',
            '缺血性异常勃起属急症，疼痛程度/病史不能代替血气或超声鉴别，保守措施证据有限。',
            '成人专科指南，未复制穿刺、注射或手术方案供家庭操作。',
            '实际读10.1急症/时间、10.1.2鉴别血流与血气超声、10.1.3保守处理局限；未声称审完所有后续手术。'),
    ]
    entries=[
        entry('reader-001','symptoms','确诊菌群失衡或滴虫后按病因治疗，反复发作时把伴侣问题一起问清',
            '鱼腥味、稀薄或黄绿分泌物可以提示方向，却不能决定药方。细菌性阴道病是菌群失衡，滴虫则是可性传播的寄生虫感染，不能都拿抗真菌药处理。确诊后有对应药物，反复发作要复核病因和伴侣管理；滴虫需同步处理伴侣，菌群失衡是否同步治疗则要按具体情境讨论，不能自行互分药。',
            '**先确认是细菌性阴道病、滴虫还是其他原因，再选药。** 细菌性阴道病简称BV，是阴道菌群失衡；滴虫是寄生虫感染。它们都可能有异味或分泌物变化，但不是念珠菌，抗真菌药不能包治。有症状且确诊BV时，可使用针对它的抗菌药物，不靠冲洗、香氛或普通益生菌“洗回正常”。[@READER-S01][@READER-S03]\n\n确诊滴虫后，应让当前性伴侣一同接受评估和治疗；双方完成治疗且症状消退前避免性接触，并约好复查。不能只治有症状的一人，也不直接借对方处方。[@READER-S03]\n\n**反复BV则可以具体问：这次是否确诊、是否需要调整疗程，以及伴侣同步治疗是否适合。** 一项2025开放随机试验，在女性有BV并有稳定男性伴侣的特定人群中，伴侣口服加局部联合治疗降低了12周复发；这不是所有阴道炎、所有伴侣都该吃药的证明。不要用旧的“一律不用治伴侣”或新的一律同治替代个体讨论。[@READER-S02]',
            '减少抗菌药与抗真菌药用错，以及只处理症状却反复复发的情况。',
            'CDC病因与滴虫管理；2025年StepUp原始试验。[@READER-S01][@READER-S03][@READER-S02]',
            evidence='B，特定伴侣与12周复发的开放随机试验；C，病因治疗和伴侣管理指导。',
            notes='BV和念珠菌感染都不能单凭症状判断伴侣忠诚或个人卫生。孕期、反复感染与免疫状态另核，不照试验剂量自行分药。',sexes=('female','male')),
        entry('reader-002','male','尿道口流液或排尿灼痛就检查，别只当上火或自己吃剩抗生素',
            '阴茎尿道口新出现白浊分泌物、尿痛或灼热，应到泌尿或皮肤性病门诊查原因。尿道炎常与性传播感染有关，也可能有其他原因；只有普通尿常规，未必排除了需要特定检测的病原。带上接触时间和用药记录，按结果治疗及安排伴侣评估；不要反复挤液、灌消毒剂或先吃剩药。',
            '**尿道口新流液、尿痛或灼热，安排泌尿外科或皮肤性病科评估。** 尿道是排尿通道，发炎叫尿道炎；衣物上的新白浊液和疼痛不能只解释为“上火”。医生可按接触方式和症状选择尿样或拭子及病原检测。[@READER-S04]\n\n说明哪天开始、是否尿频/睾丸痛、近期接触及已用过什么药。采样前是否暂停排尿等准备，按接诊机构要求，不自己往尿道灌水或消毒。若与性传播感染相关，伴侣也可能需检测治疗；完成治疗、症状消退及接诊者确认的恢复时点前，避免包括口交在内的性接触。[@READER-S04]\n\n单凭好转不自行停改疗程。睾丸突发或持续静息痛走急诊；发热寒战或明显全身不适也要及时求助，不等待自行消炎。[@PRIVATE-S01][@PRIVATE-S15]',
            '把新分泌物接上正确的检测和治疗，而不是用反复清洗掩盖问题。',
            'NHS尿道炎；本篇睾丸和尿路急症来源。[@READER-S04][@PRIVATE-S01][@PRIVATE-S15]',sexes=('male',),ages=('teen','adult','older')),
        entry('reader-003','male','阴茎新疙瘩或睾丸新硬块先检查，别照图片点疣或自行挤掉',
            '阴茎上的小丘疹可能是正常变异，也可能是皮肤病或性传播感染，单靠网络图片分不清。睾丸出现新硬块、形态或大小变化，即使不痛也应检查，不能等变疼再去。就诊会根据位置安排观察、采样或超声；普通祛疣酸液、腐蚀点痣产品和挤压，都不适合作为尚未确诊的私处处理。',
            '**新出现、改变或自己分不清的私处疙瘩，先让医生检查位置和性质。** 阴茎丘疹不自动等于尖锐湿疣，有些属于正常变异；但溃疡、持续皮疹或外观变化不能凭图片排除感染等疾病。先检查再谈是否需要治疗，不自行用腐蚀剂点掉。[@READER-S05]\n\n睾丸本体的新肿块、肿大或形态改变，即使不疼也应尽快预约检查。医生可体检，必要时做超声，区分积液、囊肿、静脉问题与其他病变；不是查出一个包都要手术，也不是年轻人就不用查。[@READER-S06]\n\n若同时突然明显痛、恶心，或疼痛持续不退、静息仍痛，改走急诊，不按普通无痛肿块等待。[@PRIVATE-S01]',
            '避免把正常结构当病处理，也避免漏掉不痛但需要检查的新变化。',
            'NHS阴茎皮损、睾丸肿块和本篇睾丸急症。[@READER-S05][@READER-S06][@PRIVATE-S01]',sexes=('male',),ages=('teen','adult','older')),
        entry('reader-004','male','精液出现红色或褐色血迹就预约检查，别凭颜色诊断前列腺炎',
            '精液中出现红色或褐色可能是血精，褐色可以来自较陈旧的出血；它通常并非严重疾病，但仍应检查原因。先记录出现次数、尿血、排尿或射精痛、近期操作和用药，交给接诊者判断是否需要检查或治疗。别因一次颜色变化就认定前列腺炎、癌症或自行买抗生素，也别因变褐而忽略持续症状。',
            '**看到精液中的红色或褐色血迹，安排全科或泌尿外科检查。** 血精是精液里混有血，颜色可能随出血新旧改变；多数情况并不严重，但颜色不能告诉你来自哪里，也不能直接确诊前列腺炎。[@READER-S07]\n\n记录出现多久、是否反复，是否有尿血、尿痛或射精痛，以及近期检查、手术与用药。确有病因才针对处理，不默认所有人都需抗生素；有时检查后可观察。[@READER-S07]\n\n若合并突然或持续不退、静息仍有的睾丸痛，直接急诊；发热寒战、腰背侧痛等也应当天评估，不按普通血精慢慢预约。[@PRIVATE-S01][@PRIVATE-S16]',
            '既不因颜色惊慌买药，也不漏掉应当描述给医生的伴随线索。',
            'NHS血精；本篇睾丸及上尿路感染分流。[@READER-S07][@PRIVATE-S01][@PRIVATE-S16]',sexes=('male',)),
        entry('reader-005','male','勃起困难反复发生就查原因，别把网购壮阳产品当作正规治疗',
            '偶尔因疲劳或紧张勃起不理想，不等于身体报废；反复发生并影响生活时，值得评估药物、血压血糖、激素和心理关系因素。正规治疗可包括生活与心理支持、合适的处方药和其他方法。西地那非等不是补肾保健品，使用前要核药物相互作用；尤其不能与硝酸酯类或某些助兴吸入剂同用。',
            '**反复难以获得或维持勃起，先查可改变的原因，再选治疗。** 这类表现称勃起功能障碍，评估包括病史、用药、身体检查，以及按情况检查血糖、血脂和晨间睾酮等，不靠网购测评给自己下结论。[@READER-S08]\n\n生活调整、心理性支持和正规药物各有适用场景。PDE5抑制剂，如西地那非，是帮助勃起反应的药物，不能当作提升所有性能力的营养品；是否适用要结合心血管状况和正在使用的药。**不能与任何形式的有机硝酸酯、NO供体如poppers，或尼可地尔同用**，可能造成危险低血压。[@READER-S08]\n\n不把“天然壮阳”当安全保证，也不为追求更强自行叠药。持续勃起不退按急症入口处理。[@READER-S10]',
            '找到可以治疗或调整的原因，同时减少混药和自我补激素的风险。',
            'EAU2026勃起功能障碍指南；持续勃起急症。[@READER-S08][@READER-S10]',sexes=('male',)),
        entry('reader-006','male','射精过快或困难持续困扰就评估，别用秒数或延时喷雾独自解决',
            '射精问题要看是否一直如此、能否控制、是否新近改变和造成多少困扰，而不是只拿一个分钟数当标准。早泄、勃起后太快疲软和迟迟不能射精，处理并不相同。可以讨论心理行为与正规药物方案；延时喷剂若含局麻药，会有过敏、伴侣麻木和备孕方面的限制，不能因名字普通就随意叠用。',
            '**持续困扰的射精过快、延迟或不能射精，可以去正规男科或泌尿外科评估。** 说明一直如此还是后来改变、是否每次发生、控制感、用药及伴随疼痛；诊断不只取决于插入后多久射精。偶尔变化与持续疾病要分开，射精后的正常疲软也不等于勃起障碍。[@READER-S09]\n\n处理可能包括沟通、心理行为支持和适合的药物，先解决合并的勃起问题或其他病因。延时喷剂/乳膏若含利多卡因、丙胺卡因等局麻药，是降低局部感觉的药物，不是无风险的护理香水；可能过敏或转移到伴侣造成麻木，应核成分、用法及屏障兼容性。备孕时应先避免这类含利多卡因或丙胺卡因的局麻延时制剂，并讨论替代方案；这是指南的谨慎建议，不等于已经证明一用就会不孕。[@READER-S09]\n\n射精痛、血精或新分泌物，则把检查病因放在延时之前；不要自行用镇痛药或抗抑郁药拼方案。[@READER-S07][@READER-S04]',
            '把困扰、功能与病因说清，减少为一个营销时长标准反复买产品。',
            'EAU2026射精障碍指南；血精和尿道症状。[@READER-S09][@READER-S07][@READER-S04]',sexes=('male',)),
        entry('reader-007','sexual','自慰不按次数判断亏损，疼痛、破皮或影响生活时再调整和求助',
            '自慰与否都可以，不存在人人适用的每周健康次数，也不能把它当作不孕、失明或身体亏空的原因。更实际的判断是有没有疼痛破损、是否干扰睡眠学习和关系、能否自主选择。清洁双手与用品，避免强摩擦，涉及他人先有同意；共用器具还要考虑清洁和屏障，而不是以为没有插入就绝无感染风险。',
            '**不需要为了“养精”强行按统一次数戒断，也不用把自慰当成必须完成的健康任务。** 自慰是自我性刺激；各性别都可选择，频率差异很大。更值得关注的是身体不适、是否影响学习工作生活，以及本人是否因此困扰，而不是一周某个数字。不能把自慰直接归为不孕或视力受损原因。[@READER-S11]\n\n疼痛、破皮就停下，减少摩擦并找原因；涉及他人的活动需要自由同意。性用品要按本品说明清洁，不与别人直接共用；换人或换接触部位时需要清洁并更换合适屏障，不能把“没有阴道性交”当作一切感染风险归零。[@READER-S11][@READER-S04]\n\n若行为难以控制、持续影响作息或引发明显痛苦，可以寻求心理或性健康支持，目的在恢复自主与生活，不是证明你道德有问题。[@READER-S11]',
            '用身体感受和生活影响取代羞耻或固定次数的健康焦虑。',
            '维多利亚州卫生部门2026自慰指导；NHS用品接触预防。[@READER-S11][@READER-S04]',ages=('teen','adult','older')),
        entry('reader-008','prevention','男女都可咨询适龄HPV接种，有宫颈者接种后仍按规范筛查',
            'HPV疫苗预防相关型别感染和病变，不能清除已经存在的感染；接种与筛查各有任务。男性也有适用疫苗，但不同产品的年龄、性别和程序要分别核对，不能把某款范围抄给全部品牌。带接种记录到正规接种点咨询；有宫颈者仍需按年龄与病史安排筛查，异常出血则直接查原因，别等下次体检。',
            '**想预防HPV相关疾病，带年龄、既往接种和健康记录到正规接种点选适合的疫苗。** HPV是人乳头瘤病毒，可涉及宫颈、肛门等部位。中国疾控2026问答明确男性也有适用疫苗；但不同产品的年龄和程序并不完全一致，不能把“9到26岁男性”理解成每一款都可如此接种。[@READER-S12]\n\n疫苗是预防，不能拿来清除已存在感染或代替治疗。漏过针次通常不是从头重打，先带接种记录补核计划；不要因恐慌重复买全套。国家免费人群与其他自费人群的资格也分开核对。[@READER-S12]\n\n有宫颈者接种后仍需按相应年龄、病史和临床规范筛查，不能以打过疫苗免筛。有性交后、月经间或绝经后出血等症状，应先查原因，不等待常规筛查档期。[@READER-S12][@PRIVATE-S20]',
            '同时抓住疫苗与适龄筛查的预防作用，避免重复接种或遗漏症状检查。',
            '中国疾控2026 HPV问答及本篇异常出血指导。[@READER-S12][@PRIVATE-S20]',ages=('child','teen','adult','older'),
            notes='儿童/青少年供本人及照护者理解；老年读者主要看筛查与症状分流。本条不意味着所有年龄、男女都在任一疫苗批准范围。'),
        entry('reader-009','urgent','勃起持续3至4小时不消退就急诊，别靠冷敷或继续性交拖延',
            '没有继续性刺激却长时间勃起不退，可能是需要抢时间的异常勃起，不能把它当成性能力特别好。持续接近或超过3至4小时就立即急诊，明显疼痛或有镰状细胞病等情况更早求助。别靠冰敷、饮酒、继续性交或再吃药尝试解决；带上近期用药，说明何时开始，不等待第二天自己消退。',
            '**勃起持续接近或超过3至4小时仍不消退，立即急诊，不继续等到第二天。** 异常勃起可能损害组织，是否缺血不能在家凭疼不疼准确判断；明显疼痛或不适可以更早求助。镰状细胞病患者疼痛性勃起超过1小时就需急诊。[@READER-S10]\n\n不要冰敷或泡冷水，也别试图通过继续性活动、喝酒或自行加药解除。就诊说明何时开始、是否持续不退、疼痛和近期所有药物/助兴用品。它与反复不能勃起是不同问题，不按壮阳或补肾思路处理。[@READER-S10]',
            '减少把异常勃起误当好状态而拖延，及时保护组织和功能。',
            'NHS异常勃起急诊指导。[@READER-S10]',sexes=('male',),ages=('child','teen','adult','older'),safety=True,
            notes='时间是紧急识别线索，不是必须忍到满时长才求助，也不用于家庭鉴别血流类型。'),
    ]
    urgent = next(e for e in entries if e['id']=='reader-009')
    urgent['fields']['plain'] = urgent['fields']['plain'].replace('[@READER-S10]', '[@READER-S10][@READER-S13]', 1)
    urgent['fields']['sources'] += ' EAU2026鉴别与缺血急症。[@READER-S13]'
    urgent['source_ids'].append('READER-S13')
    # Kept as an explicit edit so the existing private-010 ID is preserved.
    edits={'private-010':dict(
        title='先认正常白带的周期变化，新异味、瘙痒、疼痛或出血再查原因',
        summary='透明或白色、无明显异味也没有不舒服的白带，随周期变稀或变多可以正常，不必追求每天无分泌物。新鱼腥味、结块、黄绿泡沫或疼痒、异常出血，是检查线索而非颜色诊断书。记录变化并查原因；家庭酸碱试纸不能分清全部阴道炎，止味洗液也不能替代针对病因的治疗。',
        plain='**先和自己平常的状态比，再看气味、疼痒和出血，不要求白带每天一样。** 白带是阴道分泌物；透明或白色、无强烈异味、无不适，黏稠或湿滑都可以正常，排卵前后常更清透湿润。[@PRIVATE-S05]\n\n| 看到的变化 | 怎么理解和行动 |\n| --- | --- |\n| 新鱼腥味，或变得稀薄灰白 | 可见于菌群失衡等，检查而不直接买抗真菌药 |\n| 白色结块并明显痒、红痛 | 可以提示念珠菌，但不能单凭外观确诊 |\n| 黄绿、泡沫，或伴尿痛 | 需排查滴虫等感染，不用灌洗掩盖 |\n| 伴盆腔痛、性交后或月经间出血 | 查因；剧痛、晕厥或可能怀孕时按急症分流 |\n\n这些是可能性线索，并不是一种颜色对应一种药。[@PRIVATE-S05][@PRIVATE-S06][@PRIVATE-S02]\n\n就诊带上开始时间、与月经/性接触的关系、妊娠可能、新用品和已用药。检查可结合外观、镜检、pH和病原检测；pH只是酸碱指标，家庭试纸不能包办诊断，镜检阴性也不排除全部感染。持续有症状而检测未解释时，还要查刺激、摩擦、过敏等原因，不无限叠加抗菌药。[@PRIVATE-S06]')}
    for e in entries:
        if not 110 <= len(e['summary']) <=170:raise ValueError((e['id'],len(e['summary'])))
    save('reader-entries.json',entries);save('reader-sources.json',sources);save('reader-edits.json',edits)
    save('reader-audit.json',dict(status='author_checked_pending_independent_review', clinical_review_status='not_clinically_reviewed',
        entries=len(entries),source_records=len(sources), existing_entry_edits=['private-010'],
        actual_reading='逐项记录原页相关段与题录；EAU2026限相关临床分支；StepUp为摘要，不声称全文或穷尽后续Meta分析。',
        excluded=[dict(source='ACOG2025伴侣治疗新闻与更新、ISSVD2026原页/正式PDF',reason='原站403或PubMed验证码；仅作检索线索，未引用搜索摘要承担临床建议。')],
        conflicts=[dict(topic='BV伴侣治疗',resolution='不以CDC2021普遍不推荐覆盖2025新联合试验；写为特定人群可讨论，不一律同治，也不自行分药。')],
        limits='旧NHS页只承担稳定分流并如实注明过计划复审；成人性功能方案不外推儿童；男女按器官范围看。'))


if __name__=='__main__':main()
