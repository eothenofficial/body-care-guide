"""Record the actual 100-entry original-versus-final independent editorial review."""
import hashlib,json,re
from collections import Counter
from pathlib import Path
P=Path(__file__).resolve().parent
load=lambda f:json.loads((P/f).read_text(encoding='utf-8'))
sha=lambda f:hashlib.sha256((P/f).read_bytes()).hexdigest()
orig={e['id']:e for e in load('intimate-input.json')['entries']}
final={e['id']:e for e in load('intimate-rewrites.json')}
merges={e['target']:e for e in load('intimate-merges.json')}
patches=load('intimate-review-patches.json')
notes_text='''chest-001|保留急性胸痛先急救、不自行驾车与120的行动；不将所有胸痛自诊为心脏病。
chest-002|保留年轻、无痛也不能忽略新乳房改变；去掉没有分母的“多数”表述。
chest-003|区分周期性乳痛与新固定痛、红热肿痛；不把疼痛与否当肿瘤排除工具。
chest-004|保留男性乳房发育、青春期与成年用药病因差别；衣物不承诺消除腺体。
chest-005|文胸按实际合身、受压和摩擦选择，术后另评估；不制造杯型与健康的统一排名。
chest-006|保留2016年21名中国女性的小样本、短期及跑步场景，未外推永久防下垂。
chest-007|保留55–74岁绝经后病例对照适用范围，未把未发现关联写成所有人零风险；丰胸补充剂不承诺有效。
chest-008|保留褶皱红疹多病因与强激素变薄风险，修正间擦疹定义的直译；发热红肿痛仍需及时就医。
chest-012|化脓性汗腺炎有中文概念解释，反复深部结节需诊断；不归咎卫生，也不自行挤引流。
chest-009|剃腋毛可选，破皮刺激时停；持续异常肿块不靠脱毛解决。
chest-010|止汗与除臭用途区分，保留铝盐证据边界及干燥皮肤按标签使用；不将癌症关联讨论当零风险保证。
chest-011|保留多汗的病因检查、口服抗胆碱风险、能量治疗不可逆及手术代偿出汗；离子导入部位不随意外推。
abdomen-001|保留急腹痛、消化道出血与全身危险表现的急诊路径，非用保养品等待。
abdomen-004|成人与儿童疝的处理仍分开；修复“更肿且周围变色”被改为“或”的条件变化。
abdomen-005|保留胀气记录、按病因限制食物及红旗；不统一禁奶果，不按菌种数给益生菌排疗效。
abdomen-006|保留反流饮食时点3–4小时的来源范围、不同胃药用途与警示；不把缓解等同查清病因。
abdomen-007|商业排毒与正规医疗肠道准备区分；清断食错词已改，不要求自行停处方准备。
abdomen-002|肚脐温和清洁和干燥，非无菌化；持续渗液异味等需查因。
abdomen-003|保留摩擦、感染及皮炎鉴别；修复否定歧义，不允许见红就自行上混合药膏。
private-001|突发或静息持续睾丸痛急诊，1小时不是等待门槛；无痛新块也检查，儿童不延误。
private-002|保留可能妊娠即使未测阳性也按腹痛、出血及肩尖痛分流，重症不等症状齐全。
private-009|中毒性休克综合征有解释，移除用品不延误急救；不要求等所有症状齐全。
private-036|保留持续勃起3–4小时与镰状细胞病1小时的特殊阈值、严重疼痛可更早求助；不冰敷或靠性活动处理。
private-019|HIV暴露后预防保留尽早且72小时内启动，不等检测阳性、不用剩药拼方案，也不覆盖所有感染。
private-003|区分外阴与阴道，外部轻洗而不灌洗；清凉香味不证明治疗作用。
private-004|成人包皮可轻松回缩才清洁且必须复位；嵌顿盖不回急诊，不硬翻消毒。
private-005|儿童包皮不设统一回缩年龄，不强行翻开；生理性现象与痛肿排尿问题仍分开。
private-006|阴囊皮肤瘙痒不等于全部真菌，亦不混同深部急性睾丸痛；不用长期强激素掩盖。
private-007|内裤按清洁干爽与耐受，不把银离子、石墨烯等材料标签当零感染保证。
private-008|经期用品按置入意愿、清洁条件和使用负担选择，入口链接由主项目别名兼容处理。
private-020|卫生巾按流量和湿闷及时更换，少量也非无限留置；洗护按标签，不以草本负离子证明疗效。
private-021|棉条4–8小时、更不可超过8小时及最低足够吸收量均保留；不非经期使用，取不出或全身不适按相应路径求助。
private-022|杯和碟的结构位置、解除密封与托前缘取法均保留；修复“不仅抓柄”歧义，不能互套取法或用作避孕。
private-023|保留Mooncup4–8小时与Flex至少每12小时仅限对应型号；一次性不复用，无法取出或全身不适仍求助。
private-024|保留杯与IUD脱落关联研究非随机用杯、型号差异，不外推激素型；碟资料不足不等于零风险，尾丝异常需检查和补避孕。
private-025|经血颜色不确诊贫血炎症也不排除怀孕；非经期、性交后或绝经后出血及妊娠腹痛分流仍保留。
private-026|保留1–2小时浸透、超过7天及影响生活即可评估的线索；急性失血分流、青少年凝血线索和按病史检查均未丢。
private-027|保留18岁以上止痛药范围、胃肾心肝/哮喘/过敏/抗凝及孕哺备孕限制，不叠同类；继发痛经与妊娠急症分开。
private-010|白带外观只是线索，pH与镜检阴性不能包办排除；儿童和伴侣忠诚推断限制保留。
private-011|无症状念珠菌带菌不自动治疗，复发不足2个月需检查；孕期局部唑类7天及不自行口服氟康唑保留。
private-028|BV与滴虫区分，滴虫伴侣管理保留；2025开放试验仅特定稳定男女伴侣和12周复发，未泛化所有阴道炎。
private-012|强处方激素、瘢痕与低但需监测癌变风险保留；重新读NHS确认不是感染且不性传播，修正“不必然”的歧义。
private-013|龟头包皮炎不是病原诊断，温和清洁复位及按因选药保留；嵌顿和睾丸痛急诊。
private-029|尿道流液尿痛需按接触选择检测，采样准备依机构，伴侣与恢复接触时机保留；发热或睾丸痛另分流。
private-030|正常阴茎变异不等于湿疣，睾丸新块无痛也查；不自行腐蚀处理，突发痛急诊。
private-031|血精多数不严重但颜色不确诊，仍预约查因；睾丸痛或发热腰侧痛加急路径保留。
private-014|妊娠、男性、儿童、年长、免疫/糖尿病/导尿人群不套普通成人；48小时不是高风险等待期，意识改变急救。
private-017|盆底训练证据的人群限制及收缩放松均保留；疼痛或过紧先评估，不以中断尿流练习或直接买设备替代。
private-015|无症状不能排除性传播感染，按部位/时间选检测；乳胶润滑剂兼容、未覆盖皮肤风险和HIV紧急预防仍保留。
private-035|疫苗预防而非清除已有感染，男性与不同型号年龄程序不通套；漏针补种和有宫颈者筛查保留。
private-016|润滑与阴道保湿的用途区分，痛先停止；出血、孕哺、激素相关肿瘤史和术后另评估，紧致不能替代查因。
private-032|PDE5药非营养品，硝酸酯、NO供体及尼可地尔禁同用；去掉“影响生活才评估”新增门槛并补中文缩写解释。
private-033|射精诊断不只分钟，持续性控制感与困扰保留；局麻延时药伴侣麻木、备孕谨慎及不能推成一用就不孕均保留。
private-034|自慰无统一健康次数，不必任务化或归为不孕视力受损；疼痛与失控求助、自由同意及用品卫生限制保留。
private-018|2026澳大利亚监管复核限相关用途，非中国或全球全部激光禁令；证据不足不写成全部技术已无效。
private-037|年度100人使用效果及典型/正确使用分母保留，全部表中数字未变；不作单次成功率或中国个体预测。
private-038|外置/内置不叠用，安全套位置和取出动作已补全；乳胶润滑兼容、失败当天补救与PEP尽早72小时保留。
private-045|体外法与日历App不等同规范生育力识别，不说绝对安全日；特别需避孕者优先比较少依赖预测的方法。
private-039|复方与单方、有效片/安慰片和各款漏服规则分清；21+7不可套全部，近5天风险需评估紧急避孕，中国供应限制保留。
private-040|贴、环、针的成分周期不通套，非口服未消除雌激素禁忌；部分针停后可约1年恢复及非永久不孕保留。
private-041|皮埋与宫内装置位置及铜/激素经量差别保留；放置前妊娠感染评估、镇痛与取放计划、海外延长期不通套。
private-046|永久选择不能以必可复通决定，男性术后8–16周精液分析并确认前继续避孕；非次数或三个月自动可靠。
private-042|保留LNG/UPA不同制剂72/120小时、CDC5天与第3–5天差异，铜宫内装置首次接触5天内及排卵判断例外。
private-043|LNG后立即常规、UPA至少5天第6天、额外7天、呕吐2或3小时制剂差异和最后接触21天验孕全部保留。
private-044|常见出血适应与警示分开，宫内器具首用有中文解释；新痛发热大出血尾丝异常当天查，胸痛气短晕厥急诊。
private-047|含雌激素方法禁忌与35岁以上吸烟、偏头痛先兆保留；哺乳闭经需全部条件及不足6个月，药物相互作用不概括全部抗生素。
private-048|双方孕前评估、用药疫苗与病史记录，潜在致畸药不能自行停，必要时调整完成前继续避孕。
private-049|400微克=0.4毫克、最好3个月至少1个月至孕12周保留；高风险个体化、不叠复合维生素、MTHFR不必昂贵活性叶酸。
private-050|备孕双方减少有害暴露，妊娠方从尝试起不饮酒；男性生活方式与精子指标关联不推成人人更快生下孩子。
private-051|自然阴道性交每2–3天，易孕前5天至当天共6天及每1–2天保留；体位抬腿不承诺促孕或选性别。
private-052|LH阳性只间接提示1–2天，40岁以下尝试不足12个月综述的可能收益、厂商资助和PCOS假阳性限制保留。
private-053|男性同步生育评估、精液指标不能单项定论；睾酮和合成代谢类固醇可能少精无精，处方治疗不自行停换。
private-054|小于35岁12个月、35岁以上6个月、超过40岁尽早，以及病因/症状提前评估例外保留；辅助生殖需求不套等待。
private-055|AMH是促排反应辅助不判自然生育力，补剂证据不足不等于所有营养无用；PRP侵入风险与缺乏可靠疗效证据均保留。
private-056|hCG、月经未到首日或最后接触至少21天检测、复测和检查保留；可能宫外孕不以阴性排除，重症不等复测。
anal-001|持续/大量便血或大块急诊，全身失血表现急诊；黑暗红便血泻当天、儿童检查及不自行停重要处方均保留。
anal-002|肛周脓肿深部可能外观不明显，需当天检查且多需引流；抗生素按感染范围与免疫情况，不用坐浴替代。
anal-003|有外阴者擦拭方向与污染转移解释，非一次反向必感染；厕后肥皂流水搓约20秒，男性也避免污染。
anal-004|干纸湿纸清水按舒适选择，不追求消毒；无香、过敏/破损标签、湿巾丢垃圾与医疗效果分开。
anal-005|外部低压不烫、洗后拍干，非灌肠或痔疮治疗；有限观察资料不算个人风险，感觉减退术后等需帮助。
anal-006|响应便意、少硬推久坐、不强迫每日任务，儿童不责怪；不将手机本身或蹲凳作确定病因/治疗。
anal-007|硬痛费力排不净而非只看频次，逐步纤维水分活动与心肾/限水/吞咽限制保留；出血消瘦及梗阻样症状仍分流。
anal-008|纤维/渗透/刺激药分类及PEG成人特发性范围保留；纠正无表称此表、特殊人群不照搬，反复救援或软仍难排需再评估。
anal-009|肛裂概念、硬便稀便均刺激、外用处方与低血压头痛风险保留；不能自行调心血管药，发热跳痛当天查脓肿。
anal-010|正常痔组织不因看到就治疗，既往痔不能诊断新便血；短期局部缓解与病因检查/结扎手术分层保留。
anal-011|肛痒不等于不洁或真菌，夜痒不确诊蛲虫；早晨清洁如厕前取样及家人/衣物安排、孕哺婴幼儿药物单独确认。
anal-012|粪渍可能渗漏，便秘嵌塞也可漏稀便；不直接止泻手掏强冲，温和皮肤护理与按因训练保留。
bodyskin-009|体毛无必须清除的卫生要求，个人外观可选；修剪减少贴皮损伤为实用取舍而非疗效排名。
bodyskin-010|剃/膏/蜡不同机制和操作限制保留，局测不保证不过敏；异维A酸等用药、破皮黏膜/孕哺年龄限制仍在。
bodyskin-011|IPL/激光概念和黑色素光热机制保留，有限型号不泛化；眼周黏膜禁用、肤色药物评估及异常痛水疱视力急停。
bodyskin-013|普通/肥厚/越界瘢痕疙瘩与凹陷挛缩分开；照片不确诊，无外伤硬块需排除肿物。
bodyskin-014|瘢痕体质非通用测试，病史家族与部位影响风险；小耳洞测试也留伤，必要手术不因怕疤延误。
bodyskin-015|硅酮待闭合无痂，既有瘢痕疙瘩贴片确定性很低；凝胶/贴片及预防/治疗不互借，证据不足非全部无效。
bodyskin-016|压力装置为医疗辅助非普通耳夹或瘦身衣，部位依从与痛麻破损停压联系团队保留。
bodyskin-017|局部激素与5-FU机制有解释，方案异质而非网络通用剂量；多次评估疗效损伤及孕哺备孕儿童药物限制保留。
bodyskin-018|冷冻与激光的目标、深肤色持久浅斑及联合治疗保留；表面变淡不能推增长复发已控制。
bodyskin-019|切除即时去除不等于长期控制，闭合减张及注射压力放疗须术前衔接；不套网络复发率。
bodyskin-020|核素锶90/磷32、X线、电子线技术不同，2021小薄病灶联合试验与2026综述不外推；孕未成年及长期肿瘤风险保留。
bodyskin-021|创面促愈合与既有增生消退终点不同，EGF和寡肽不互借，康复新缺可靠直接证据而非证明全创面无用。
bodyskin-022|普通稳定疤可观察，增长痒痛功能或异常破溃无伤史需评估；围绕实际目标而非完全无痕。'''
judgments=dict(line.split('|',1) for line in notes_text.splitlines())
assert set(judgments)==set(orig)==set(final), (set(orig)-set(judgments),set(judgments)-set(orig))
assert len(orig)==100 and len(merges)==3 and len(patches)==88
for patch in patches:
    e=(merges if patch['document']=='merges' else final)[patch['id']]
    text=e[patch['field']] if patch['field'] in ['title','summary'] else e['fields'][patch['field']]
    assert patch['after'] in text,(patch['id'],patch['field'],'patch not present')
sources=lambda e:set(re.findall(r'@src-[a-z0-9]+',json.dumps(e['fields'],ensure_ascii=False)))
def numbers(s):
    s=re.sub(r'\[@src-[a-z0-9]+\]|#/entry/[a-z]+-\d+','',s)
    return Counter(re.findall(r'\d+(?:\.\d+)?',s))
rows=[]
for eid,e in orig.items():
    n=final[eid]
    assert sources(e)==sources(n),eid
    assert 60<=len(n['summary'])<=140,eid
    issues=[p for p in patches if p['id']==eid and p['document']=='rewrites']
    rows.append(dict(id=eid,all_original_and_final_fields_compared=True,
      original_fields_sha256=hashlib.sha256(json.dumps(e['fields'],ensure_ascii=False,sort_keys=True).encode()).hexdigest(),
      final_fields_sha256=hashlib.sha256(json.dumps(n['fields'],ensure_ascii=False,sort_keys=True).encode()).hexdigest(),
      clinical_scope_review=judgments[eid],source_ids_preserved=sorted(sources(e)),
      source_placement_reviewed=True,age_sex_and_special_population_limits_reviewed=True,
      concept_evidence_action_and_normal_sentences_reviewed=True,
      patch_count=len(issues),patch_reasons=[i['reason'] for i in issues],status='reviewed_after_patches'))
merge_rows=[]
for eid,m in merges.items():
    members=[eid]+m['retired']
    expected=set().union(*(sources(orig[i]) for i in members))
    assert sources(m)==expected,eid
    a=[orig[i]['audience'] for i in members]
    assert all(x['age_groups']==a[0]['age_groups'] and x['sexes']==a[0]['sexes'] for x in a),eid
    expected_pin=any(x['safety_pin'] for x in a)
    assert m['age_sex_check']['safety_pin']==expected_pin,eid
    merge_rows.append(dict(target=eid,retired=m['retired'],all_original_members_compared=True,
      source_union_preserved=sorted(expected),age_groups_and_sexes_equal=True,
      original_safety_pins=[x['safety_pin'] for x in a],merged_safety_pin=expected_pin,
      review_note={'private-022':'已重写合并正文为自然句，全部操作与两型号时限、清洗/遗留/急症限制保留。','anal-007':'已重写生活—用药—检查路径；类型、成人适用、医用标签与特殊人群和急症限制保留。','private-042':'已重写当日处理—方法—后续—验孕路径；全部时间、药理区别、中国供应、妊娠急症保留；安全置顶沿用target true，未扩年龄性别。'}[eid],
      status='reviewed_after_patches'))
numerical=[]
for eid,e in orig.items():
    old=numbers(e['fields']['plain']);new=numbers(final[eid]['fields']['plain'])
    if old!=new:numerical.append(dict(id=eid,removed_tokens=dict(old-new),added_tokens=dict(new-old)))
report=dict(reviewed_by='rewrite_body (independent of intimate author)',reviewed_at='2026-10-30',
 scope='100条全部原始字段与最终改写逐条对照，另审3个合并；逐句看临床含义、限制、警示、引用位置、首次概念和自然语法。',
 count=100,merged_count=3,applied_patch_count=88,
 input_sha256={f:sha(f) for f in ['intimate-rewrites.json','intimate-merges.json']},
 final_sha256={f:sha(f) for f in ['intimate-rewrites.json','intimate-merges.json']},
 original_input_sha256=sha('intimate-input.json'),patch_file_sha256=sha('intimate-review-patches.json'),
 patches_verified_applied=True,blocking_unresolved=[],covered_ids=list(orig),checks=rows,merge_checks=merge_rows,
 numeric_comparison=dict(scope='只比正文阿拉伯数字，剔除引用哈希与entry路由ID；不是所有题录数字，也不以数字集合证明临床等效。',
  differences=numerical,interpretation='private-023少一次12是删除重复而非改时限；private-032额外5为PDE5缩写重复出现；private-040额外3来自原备注的非每3个月统一规则；private-043正文2024年份省略但该指南年份仍在证据/来源及合并正文，均非临床数字丢失。'),
 additional_primary_source_check=[dict(url='https://www.nhs.uk/conditions/lichen-sclerosus/',purpose='核实非感染且不经性接触传播，以修正原稿易误导措辞。'),dict(url='https://www.nhs.uk/conditions/urethritis/',purpose='核对尿道症状、尿样/拭子及其他性传播感染检测，伴侣和恢复性接触条件。')],
 limitations=['本轮是全文编辑与医学含义对照，不是重新完成全部原始研究的系统综述，也未逐一重新查证所有来源页面。','已核保留旧来源ID和重要主张相邻引用；保留并非声称每个来源达到同一等级。','无临床医生签审；clinical_review_status仍为not_clinically_reviewed。'],
 clinical_review_status='not_clinically_reviewed')
(P/'intimate-independent-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'entries':len(rows),'merges':len(merge_rows),'patches_verified':88,'input_sha256':report['input_sha256'],'blocking_unresolved':[],'report_sha256':sha('intimate-independent-review.json')},ensure_ascii=False))
