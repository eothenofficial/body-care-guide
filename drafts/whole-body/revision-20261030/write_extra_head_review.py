"""Save the editor's actual second pass through cost/evidence/sources."""
import hashlib
import json
from head_extra_reader import HERE, prepared

ROOT = HERE.parents[2]
ORDER = ['hair','eyes','nose','ears','oral','lips','skin']
chapters={key:prepared(key) for key in ORDER}
patches=[]

def revise(chapter,eid,old,new,reason='将作者怎样写、没做什么的过程陈述改为资料能支持什么的证据边界；不改变评级、临床建议和引用。'):
    e=next(x for x in chapters[chapter]['entries'] if x['id']==eid)
    text=e['fields']['evidence']
    if text.count(old)!=1:
        raise ValueError((eid,old,text))
    patches.append(dict(file='drafts/whole-body/baseline/chapters/'+chapter+'.json',
        target='entry',id=eid,field='fields.evidence',old=old,new=new,reason=reason))
    e['fields']['evidence']=text.replace(old,new)

revise('hair','hair-001','未以固定频率保证不脱发。','不能据此确定一种适合所有人、还能预防脱发的固定洗发频率。')
revise('hair','hair-002','没有据此给所有去屑品牌作头对头疗效排名。','这些指导不足以判断所有去屑品牌之间的疗效高低。')
revise('hair','hair-005','没有为胶囊或深海营销词补造临床证据。','胶囊剂型和“深海”名称本身不能证明人体生发效果。')
revise('hair','hair-006','离体发束实验支持物性线索，尚不能作为本项目B级人体疗效证据；','离体发束实验支持物性变化线索，不能直接证明使用者长期护理的效果；')
revise('hair','hair-009','没有将某次品牌召回或个案扩成所有干洗产品必然有害。','这些指导不能证明所有干洗产品必然有害，也不能用于全品类安全排名。')
revise('hair','hair-011','本文未完成所有乌发产品的系统综述，不将缺少证据写成每种产品均已被证伪。','这些护理资料不能证明所有乌发产品有效或无效。')
revise('hair','hair-013','具体产品比较未有直接研究支持。','所引资料未直接比较具体产品。')
revise('hair','hair-019','共识全文未读，不提供具体剂量与完整禁忌表。','具体剂量、禁忌和监测仍须按完整用药指导及个人情况评估。',
    '读取深度继续留在对应来源账本，删除公共证据栏的作者未读全文声明；不补写任何剂量或禁忌。')
revise('hair','hair-023','未独立审读不同植发术式的头对头试验，不给统一成活率。','这些指导不能用于比较不同植发术式的成活率。')

revise('eyes','eyes-014','此处给药物类别，不做具体品牌或浓度的疗效排名。','药物类别指导不能直接证明某个品牌或浓度更好。')
revise('eyes','eyes-006','没有把它写成高确定性量化疗效。','不能据此给出高确定性的改善幅度。')
revise('eyes','eyes-022','不提供自行改处方的算法。','处方参数说明不能替代验光。')
revise('eyes','eyes-031','户外与风险的关联不在此换算成个人获益，','人群层面的户外活动与风险关联不能直接换算成个人获益，')
revise('eyes','eyes-025','不提供个人发病概率或统一复查套餐。','不能由这些指导计算个人发病概率或确定适合所有人的复查套餐。')
revise('eyes','eyes-030','不声称已检验市场上每款商品或证明它们全部无效。','所引资料未逐款验证市场商品，不能据此断定它们全部无效。')
revise('eyes','eyes-002','没有把固定休息间隔写成保证疗效的处方。','固定休息间隔不是保证疗效的统一处方。')
revise('eyes','eyes-010','未据色素名称给全部成品作毒理判断。','色素名称本身不足以判断所有成品的毒理安全性。')
revise('eyes','eyes-027','本文不作术式疗效排行榜。','这些资料不足以按术式名称给出适合所有人的疗效排名。')
revise('eyes','eyes-028','未做具体ICL型号之间的直接疗效比较。','这些指导未直接比较具体ICL型号的疗效。')
revise('eyes','eyes-012','不据此排护理液品牌优劣。','这些规范不能用于比较护理液品牌的疗效高低。')
revise('eyes','eyes-017','不声称已证明健康泳客预防性用药无效，也不冒充随机试验。','这不是健康泳客预防性抗生素的随机试验证据，也不能据此判定该用法已被证明无效。')

revise('nose','nose-008','本条不根据症状自诊肿瘤，也不提供远程病因概率。','这些表现不能确定个体病因或计算肿瘤概率。')
revise('nose','nose-003','不作鼻贴或吸力仪全品牌疗效排名。','不能据此判断具体鼻贴或吸力仪的效果优劣。')
revise('ears','ears-006','未用该页排名所有新器械。','上述资料不能证明某种新器械优于其他方案。')
revise('ears','ears-007','航空机构健康指导及听损分流；不提供潜水平压教程或鼻喷药统一剂量。','航空机构的气压不适护理与听力下降分流指导。')
revise('ears','ears-008','未验证所有合金、涂层和低敏营销标签。','这些指导不能仅凭“低敏”标签判断具体合金或涂层一定适合。')

revise('oral','oral-006','本文不提供个体处方或品牌比较。','具体处方需要结合个人情况，来源并未直接比较品牌。')
revise('oral','oral-019','未宣称所有孩子按同一天换牙。','换牙时间存在个体差异，不能只按同学进度判断异常。')
revise('oral','oral-017','未将牙垫保护作用写成治愈磨牙。','牙垫保护作用不等于治愈磨牙。')
revise('oral','oral-022','不建立“所有缺牙者最佳材料”排名。','这些资料支持分条件选择，不能证明一种方式适合所有缺牙者。')

revise('skin','skin-001','没有据此给所有洁面或面霜排效果名次。','这些建议不足以比较所有洁面或面霜的效果高低。')
revise('skin','skin-004','没有据此量化不同品牌、喷雾或膜布的长期效果。','不能据此估算不同品牌、喷雾或膜布的长期效果。')
revise('skin','skin-019','没有把ABCDE作为自行排除或确诊的工具。','ABCDE用于提醒检查，不能自行排除或确诊病变。')
revise('skin','skin-021','未重做药物试验，不据此比较所有美白成品。','这些治疗路径不能直接比较市售美白成品的效果。')
revise('skin','skin-005','未声称所有轻微短暂感觉都代表过敏。','并非所有轻微短暂感觉都意味着过敏。')
revise('skin','skin-006','未独立重评所有药物试验或作品牌排序；','不能据此给所有成品作品牌排名；')
revise('skin','skin-017','没有据此比较全部去屑或抗真菌品牌，也不把抗真菌等同所有病例的唯一治疗。','这些指导不足以确定某一品牌优于其他品牌，抗真菌也不是所有病例的唯一治疗。')
revise('skin','skin-007','未给不同医美项目统一有效率，不承诺完全复原。','这类分流指导不能确定不同医美项目的统一有效率，也不能承诺完全复原。')
revise('skin','skin-008','未把观察性食物关联、糖化机制或个人记录写成治疗因果证据。','观察性食物关联、糖化机制或个人记录不能确立治疗因果关系。')
revise('skin','skin-011','没有引用直接比较各类眼霜或按摩的高质量试验。','所引机构资料未直接比较各类眼霜或按摩的效果。')
revise('skin','skin-013','本文未提供头对头器械试验结论。','所引护理资料未直接比较不同器械的效果。')

coverage=[]
for key in ORDER:
    for e in chapters[key]['entries']:
        coverage.append(dict(id=e['id'],chapter=key,actual_read_fields=['fields.cost','fields.evidence','fields.sources'],
            method='完整展开三栏后逐句阅读，非关键词扫描替代',
            result='editorial_patch' if any(p['id']==e['id'] for p in patches) else 'read_no_additional_patch',
            medical_claim_changed=False,grading_changed=False))
out=dict(version='2026-10-30',scope='126 head entries, remaining cost/evidence/sources fields',
    input_status='raw baseline chapters with prose-patches.json then frozen head-reader-patches.json applied',
    apply_after=['prose-patches.json','head-reader-patches.json'],
    method='实际通读每条cost/evidence/sources三栏；删除或重写作者未做何事的过程用语，保留证据类型、等级和不确定性，不新增医学推荐。',
    limitations='此轮通读不是重新完成126条的系统临床核证。来源栏为简短引用说明与稳定来源引用，未据此宣称已重新逐篇核读来源账本中全部完整文献。',
    patches=patches,coverage=dict(entry_count=len(coverage),entries=coverage),
    input_sha256={name:hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in ['prose-patches.json','head-reader-patches.json']})
(HERE/'extra-fields-patches-head.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

report=['# 头面三栏逐句阅读补充：2026-10-30','','维护者记录；接续已完成的126条摘要、正文、收益、备注审读。',
    '本次在prose-patches.json及冻结head-reader-patches.json应用后，对七章126条的cost、evidence、sources三栏再次完整展开并逐句阅读。由此本轮两遍合计覆盖全部六字段、标题和摘要，以及全部章/单元导语。', '',
    f'输出{len(patches)}处额外补丁，均为证据栏表述：把“本文未完成/没有写成/不冒充/没重做”等作者过程改为具体来源的支持与外推边界。没有改A/B/C评级、药物剂量、时限或其他临床结论。来源实际读取深度仍在来源账本，未伪称阅读全文。', '',
    '成本栏核读结果：只有eyes-015（包装/弃置浪费）、eyes-012（复用维护）、oral-010（修补更换）存在实际内容，其余为空；这三处无虚构金额或“价格待核”占位，本轮无需改动。', '',
    '来源栏核读结果：均为稳定引用或简短来源说明，未发现需要在该栏新改的明显格式错误；不能因此推称已经重新逐篇核验全部期刊原文/DOI元数据。完整书目的统一校验仍由整站构建与引用审计承担。', '',
    '## 逐条记录','','| ID | 实读字段 | 结果 |','| --- | --- | --- |']
for e in coverage:
    report.append(f'| {e["id"]} | 成本、证据等级、来源 | '+('证据措辞修改' if e['result']=='editorial_patch' else '已读，无新增修改')+' |')
report += ['', '精确替换及输入哈希见drafts/whole-body/revision-20261030/extra-fields-patches-head.json。应用顺序为prose → head-reader → extra-head；不修改冻结的head-reader补丁。', '',
    '限度：这是文本与推理表达审校，不是持证临床签审，也未重新系统检索126条的全部医学问题。']
(ROOT/'docs/审校_20261030_头面三栏补充.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
print(json.dumps(dict(entries=len(coverage),patches=len(patches),changed_entries=len({p['id'] for p in patches})),ensure_ascii=False))
