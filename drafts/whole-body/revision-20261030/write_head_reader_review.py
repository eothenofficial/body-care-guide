"""Record the editor's completed, sentence-by-sentence head review."""
import hashlib
import json
from pathlib import Path
from head_reader import HERE, ROOT, read_prepared

ORDER = ['hair', 'eyes', 'nose', 'ears', 'oral', 'lips', 'skin']
chapters = {k: read_prepared(k) for k in ORDER}
patches = []

def obj(chapter, target, identifier):
    c = chapters[chapter]
    if target == 'chapter':
        return c
    return next(x for x in c['entries' if target == 'entry' else 'units'] if x['id'] == identifier)

def add(chapter, identifier, field, old, new, reason, target='entry'):
    x = obj(chapter, target, identifier)
    for bit in field.split('.')[:-1]:
        x = x[bit]
    key = field.split('.')[-1]
    if x[key].count(old) != 1:
        raise ValueError((identifier, field, old))
    patches.append(dict(file='drafts/whole-body/baseline/chapters/'+chapter+'.json',
        target=target, id=identifier, field=field, old=old, new=new, reason=reason))
    x[key] = x[key].replace(old, new)

def replace(chapter, identifier, field, new, reason, target='entry'):
    x = obj(chapter, target, identifier)
    for bit in field.split('.')[:-1]:
        x = x[bit]
    add(chapter, identifier, field, x[field.split('.')[-1]], new, reason, target)

add('hair','hair-007','fields.plain','；购买时先看温度控制、风量和实际使用感受。','。',
    '删除同一段中温控、风量与使用体验的重复购买建议。')
add('hair','hair-008','fields.plain','轻配方选择来自发质与使用负担的讨论，不是承诺看见某个成分就蓬松。',
    '不要只凭某个成分名判断蓬松效果，试用后看是否洗净、是否压塌再调整。',
    '把编辑论证过程改成读者可实际采用的判断，保持原有成分不能保证成品效果的边界。')
add('hair','hair-013','fields.plain',
    'AAD泳季指导提到游泳专用洗发水和后续调理，这是可比较的品类建议；是否需要专用产品，先看常规洗护能否洗净、发丝是否仍明显粗涩；现有资料不足以证明偶尔游泳的人都必须额外购买。需要新增产品时，按实际问题试，不把泳后固定叠加一整套当必须。',
    '常规洗护已经能洗净、发丝也不明显粗涩，就不必仅因偶尔游泳再买一瓶专用洗发水。洗后仍有残留或粗涩时，再按实际问题比较游泳专用洗发水和调理品。AAD泳季指导提供了这些品类选择，但不能据此认定每个人都必须额外购买一整套。',
    '按读者是否需要买专用品的判断重排，保留AAD出处与证据边界，不叙述作者如何归类材料。')
replace('hair','hair-021','fields.notes','',
    '此栏只有作者读取深度及不提供品牌/价格的说明；读取深度已在来源账本保留，正文已说明型号与流程不能互借证据。')
replace('hair','hair-023','fields.notes','毛囊数、头发根数和疗程数是不同计价单位，比较报价前先确认清楚。',
    '保留有用的报价单位提醒，删去作者没有当前价格/不做排名的工作说明。')

chemical = obj('eyes','entry','eyes-005')['fields']['notes']
old = obj('eyes','entry','eyes-005')['fields']['plain']
replace('eyes','eyes-005','fields.plain',old+'\n\n'+chemical,
    '将已有化学伤/穿刺伤和返程安全动作从备注移入正文；原数值、条件、措辞和引用全部保留。')
replace('eyes','eyes-005','fields.notes','',
    '关键急救动作已原样移到正文，避免重复。')
add('eyes','eyes-023','fields.notes','本文不沿用英国111、999等号码或驾驶申报制度；中国就医按当地急救与医疗服务安排。','',
    '正文未提供英国号码或申报要求，删去无实际读者动作的来源改编说明，保留遮眼改善也需检查的提醒。')
add('eyes','eyes-020','fields.notes','标准2011年发布、2017年转为推荐性，当前国家标准平台仍列现行。','',
    '标准书目与状态可在来源查看；此处只保留测视力条件不可直接混比的实用提醒。')
add('eyes','eyes-026','fields.notes','本文未提供自行训练处方、器材参数或疗程承诺。','',
    '删去作者未提供什么的声明；保留新发复视先分流的具体动作。')
add('eyes','eyes-022','fields.plain','英国专业规范的处方形式不直接当中国法律要求。','',
    '该段仅解释测量和配装，没有提出中国法律要求；删去让读者中断理解的改编说明，来源地区限制仍留账本。')
add('eyes','eyes-009','fields.plain','先假设两种都验配合适，不能为省钱跳过适配。',
    '无论选哪一种，都应先完成验配，不能为省钱跳过适配。',
    '把作者的假设论证改成读者的实际操作顺序，不改变验配要求。')
replace('eyes','eyes-028','fields.notes','具体成品的适用年龄、度数等，应核对国内许可和说明书，不能直接套用美国标签。',
    '保留地区许可差异的实际核查动作，删去作者如何不沿用旧网页的过程。')

add('nose','nose-001','fields.benefit','没有可靠数字能预测拔一次会怎样。','',
    '收益栏保留外观与减少牵拉的实际收益；偶尔拔过不等于严重感染的边界已在备注清楚说明。')
add('nose','nose-004','fields.notes','这里的煮沸步骤按CDC现行页写，不混用不同机构的时间。','',
    '正文已给具体煮沸动作和CDC来源，备注不再重复作者取舍；保留器具不与接触镜混用等提醒。')

add('ears','ears-009','fields.plain','海外的“持证”称谓不直接当成中国资质判定。','',
    '本段已具体列无菌针具、手套、灭菌和书面护理等要核事项，未用海外执照作中国资质承诺；删去编辑改编声明。')
if '[下一条](#/entry/ears-010)' in obj('ears','entry','ears-009')['fields']['notes']:
    add('ears','ears-009','fields.notes','[下一条](#/entry/ears-010)', '[新耳洞护理](#/entry/ears-010)',
        '用目标内容命名链接，不依赖可能被筛选或重新排序的“下一条”。')
add('ears','ears-011','fields.plain',
    '对普通时尚耳夹，没有可靠医学研究给出所有人统一的安全夹力或每天佩戴小时数；不能因此编出一个“戴满几小时就安全”的指标。耳扣过紧可损伤皮肤、嵌入耳垂，压力风险值得同样留意；这不等于已经有耳夹与耳钉直接比较的试验证据。',
    '耳夹没有统一适合所有人的安全夹力或佩戴时长，不能只靠计时判断是否适合；出现不适就取下。耳扣过紧也可损伤皮肤、嵌入耳垂。',
    '将重复的方法学自辩压缩成有用的压力和时长边界；未新增时限或比较优势，来源仍接原位。')

add('lips','lips','intro','；这里只保留各条的主要归属，跨章仍用原链接连接。','。',
    '删去条目归属及旧链接维护说明，保留牙齿与黏膜的选读分流。',target='chapter')
add('lips','oral-008','fields.plain','也不追求舌头完全没有正常颜色和纹理。',
    '舌面本来有正常颜色和纹理，不要为了看起来“更干净”反复刮刷。',
    '把别扭的否定表述改成清楚的正常结构解释，保持轻柔清洁而非刮净的含义。')

add('oral','oral','intro','；原条目链接仍保留。','。',
    '旧链接是否保留属于维护说明，不进入读者的章导语。',target='chapter')
add('oral','oral-002','fields.notes','没有当前同口径报价，不列价格或机型榜；','',
    '删去价格/机型榜的工作说明，保留更换刷头后重新确认操作的方法。')
add('oral','oral-006','fields.plain','不能把国外网页的某个毫升数或四周例子当作所有国内制剂的通用处方。',
    '不同制剂的浓度、用法和疗程可能不同，不把别人的用量直接套在自己身上。',
    '把引用加工过程转成与读者直接相关的制剂差异和不可照抄用量提醒。')

add('skin','skin-021','fields.notes','2026共识检索至2024年，仅核题录和摘要；发表新不等于包含所有新研究。美国氢醌处方属性不能直接当作中国规定；',
    '用药前核对国内药品说明书，不能直接套用美国处方分类；',
    '检索截止和实际读取深度保留在来源账本；备注改成有用的本地药品核查动作。')
add('skin','skin-007','fields.notes','；旧机构网页中的泛化安全表述不覆盖FDA2025新通报。','。',
    '保留射频微针独立风险条目的链接，删除作者怎样取舍旧网页的说明。')
add('skin','skin-011','fields.plain','不要为了消肿强力揉按眼球或拉扯眼皮；不要指望按摩消除眼袋：现有依据不足以支持这种效果。',
    '不要为了消肿强力揉按眼球或拉扯眼皮；现有依据也不足以证明按摩能消除眼袋。',
    '合并连续否定的同义提醒，不改变安全和证据判断。')
replace('skin','skin-012','fields.notes',
    '2026年综述中的生活质量改善多来自关节炎患者，不能据此推断健康年轻人的美容收益。[@src-10394308cc83][@src-5b0c281fb291]',
    '读取深度留在来源账本；保留真实研究人群不能外推的读者判断，删去作者是否重做统计的过程。')
replace('skin','skin-023','fields.notes',
    '不必为了“提前抗老”开始注射；咨询时应说明全部用药、妊娠哺乳情况和既往反应。',
    '删去“不提供品牌、剂量、时间表”等作者任务声明，保留非必需及咨询时需说明的信息。')
add('skin','skin-001','fields.plain',
    '转到本章的敏感反应、玫瑰痤疮或脂溢性皮炎条目辨别下一步',
    '参看[新产品反应](#/entry/skin-005)、[玫瑰痤疮](#/entry/skin-016)或[脂溢性皮炎](#/entry/skin-017)，辨别下一步',
    '把笼统的本章指代改成已存在的具体条目链接，原临床分支不变。')
replace('skin','skin-001','fields.notes','',
    '备注原本重复正文最后一段的减刺激与继续处理；相关链接已移入正文，不重复提醒。')

reviewed_fields = ['title', 'summary', 'fields.plain', 'fields.benefit', 'fields.notes']
per_entry = []
for key in ORDER:
    for e in chapters[key]['entries']:
        changed = [p['field'] for p in patches if p['target']=='entry' and p['id']==e['id']]
        per_entry.append(dict(id=e['id'], chapter=key, title=e['title'],
            actual_read_fields=reviewed_fields, method='分批展开全部字段后逐句阅读，非关键词命中代替通读',
            result='editorial_patch' if changed else 'read_no_additional_patch',
            changed_fields=sorted(set(changed)), medical_claim_changed=False))

payload = dict(version='2026-10-30', scope='7 head chapters, 126 entries',
    input_status='raw baseline chapters with prose-patches.json sequentially applied',
    apply_after=['prose-patches.json'],
    method='实际逐条通读标题、独立摘要、plain/benefit/notes，且通读全部章/单元导语；仅措辞、链接命名和现有安全信息位置调整。未重做医学检索或把原有证据复核声称为本轮完成。',
    limitations='本次不以审读代替完整临床复核；未通读每条cost/evidence/sources栏，来源深度记录保持真实。',
    patches=patches,
    coverage=dict(entry_count=len(per_entry), entries=per_entry,
        chapters=[dict(id=k, chapter_fields_read=['title','subtitle','intro'],
            units_read=[dict(id=u['id'], fields=['title','intro']) for u in chapters[k]['units']]) for k in ORDER]),
    input_files_sha256={str((ROOT/'drafts/whole-body/baseline/chapters'/f'{k}.json').relative_to(ROOT)):
        hashlib.sha256((ROOT/'drafts/whole-body/baseline/chapters'/f'{k}.json').read_bytes()).hexdigest() for k in ORDER},
    prose_input_sha256=hashlib.sha256((HERE/'prose-patches.json').read_bytes()).hexdigest())
(HERE/'head-reader-patches.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')

lines = ['# 头面126条逐句阅读记录：2026-10-30', '',
    '供维护者审计。本次在原始头面JSON上依次应用prose-patches.json后阅读，不直接修改原章节；整合顺序必须为prose补丁在前、本补丁在后。', '',
    '实际读取范围：七章全部title/subtitle/intro、全部单元title/intro；126条全部title、summary、fields.plain、fields.benefit、fields.notes。通过分批完整展开逐条阅读，不以关键词扫描代替。未重新全面核验每条临床证据，未把未读的cost/evidence/sources栏算入这次逐句通读。', '',
    f'共输出{len(patches)}处额外编辑补丁，涉及{len({p["id"] for p in patches if p["target"]=="entry"})}条及2章导语；其余条目也已逐条读取。修改不增医疗处方、时限或适用人群，原有来源与医学判断保留。', '',
    '## 本次发现与处理', '',
    '- 将吹风机选择、眼袋按摩等句子中的同义反复合并。',
    '- 把假设论证、作者怎样核读/删价格/改写国外资料等过程，改成读者需要的动作或从公共备注移除；实际来源读取深度不从账本删除。',
    '- 原样将化学伤/穿刺伤等关键安全动作从眼急症备注移入正文，防止必要动作只藏在备注；没有改变20分钟等原值。',
    '- 以目标名称代替“下一条”，为面部反复红痒补现存条目的明确内链。',
    '- 删去章导语中原链接/条目归属等维护说明，修正舌面清洁的别扭表述。', '',
    '## 逐条记录', '',
    '| 条目ID | 实际读取 | 处理 |', '| --- | --- | --- |']
for e in per_entry:
    status='已读；额外修改'+ '、'.join(e['changed_fields']) if e['changed_fields'] else '已读；无额外修改'
    lines.append('| '+e['id']+' | 标题、摘要、说人话、收益、备注 | '+status+' |')
lines += ['', '## 章与单元导语', '',
    *[f'- {k}：章标题、副标题、导语及{len(chapters[k]["units"])}个单元的标题与导语均已完整读取。' for k in ORDER], '',
    '精确旧新文本、理由、输入哈希及逐条coverage见drafts/whole-body/revision-20261030/head-reader-patches.json。本记录不声称所有句子无瑕疵或完成持证临床签审。']
(ROOT/'docs/审校_20261030_头面逐条阅读.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps(dict(entries=len(per_entry), patches=len(patches), changed_entries=len({p['id'] for p in patches if p['target']=='entry'})),ensure_ascii=False))
