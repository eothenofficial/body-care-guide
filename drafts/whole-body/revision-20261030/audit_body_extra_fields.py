"""Reader wording for remaining body fields; input is original + prose164."""
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
base = json.loads((HERE/'prose-patches.json').read_text(encoding='utf-8'))['patches']
chapters = {}
for p in sorted((ROOT/'drafts/whole-body/chapters').glob('*.json')):
    ch = json.loads(p.read_text(encoding='utf-8'))
    for x in base:
        if x['file'] != p.relative_to(ROOT).as_posix(): continue
        obj = ch if x['target'] == 'chapter' else next(y for y in ch['entries' if x['target']=='entry' else 'units'] if y['id']==x['id'])
        target = obj['fields'] if x['field'].startswith('fields.') else obj
        key = x['field'].split('.')[-1]
        assert target[key].count(x['old']) == 1
        target[key] = target[key].replace(x['old'], x['new'])
    chapters[p.stem] = (p, ch)
entries = {e['id']:(p,e) for p,ch in chapters.values() for e in ch['entries']}
patches = []

def add(eid, field, old, new, reason='把作者过程说明改成读者可以理解的证据范围或选择条件。'):
    p,e = entries[eid]
    assert e['fields'][field].count(old) == 1, (eid,field,old)
    patches.append(dict(file=p.relative_to(ROOT).as_posix(),target='entry',id=eid,field='fields.'+field,
                        old=old,new=new,reason=reason))

labels = {
 'NECK-S01':'NHS颈痛自护', 'NECK-S02':'2025非特异性颈痛临床指南',
 'NECK-S03':'Northwestern Medicine颈部神经根与脊髓症状', 'NECK-S04':'NIOSH居家工位与职业健康指导',
 'NECK-S05':'剑桥大学医院颈部活动与护理', 'NECK-S06':'Sherwood Forest医院冷热敷指导',
 'NECK-S07':'NHS成人布洛芬说明', 'NECK-S08':'Cochrane颈痛按摩系统综述',
 'NECK-S09':'NCCIH脊柱手法安全资料', 'NECK-S10':'NCCIH针灸效果与安全资料',
 'NECK-S11':'筋膜枪表现与恢复系统综述', 'NECK-S12':'Nebraska Medicine颈部筋膜枪风险说明',
 'NECK-S13':'HSS筋膜枪使用指导', 'NECK-S14':'NHS肩痛分流', 'NECK-S15':'NHS冻结肩指导',
 'NECK-S16':'NHS网球肘指导', 'NECK-S17':'NHS腕管综合征指导', 'NECK-S18':'NHS重复性劳损指导',
 'NECK-S19':'NHS成人对乙酰氨基酚说明', 'NECK-S20':'NHS卒中症状与急救',
 'LEGS-S01':'NHS腰背痛分流', 'LEGS-S02':'剑桥大学医院腰背痛指导', 'LEGS-S03':'NHS深静脉血栓指导',
 'LEGS-S04':'NHS扭伤与拉伤指导', 'LEGS-S05':'NHS膝痛指导', 'LEGS-S06':'NHS成人髋痛指导',
 'LEGS-S07':'WHO慢性原发性腰痛指南发布摘要', 'LEGS-S08':'无症状人群脊柱退变影像系统综述',
 'LEGS-S09':'ACR2026骨关节炎推荐摘要', 'LEGS-S10':'NHS骨关节炎治疗与支持',
 'LEGS-S11':'跑步与膝骨关节炎系统综述', 'LEGS-S12':'Berkshire Healthcare返跑康复指导',
 'LEGS-S13':'NHS跑步相关膝痛与损伤指导', 'LEGS-S14':'NHS静脉曲张指导',
 'LEGS-S15':'Dorset County Hospital医用压力衣穿戴指导', 'LEGS-S16':'NHS非甾体抗炎药说明',
 'LEGS-S17':'NCCIH氨糖与软骨素资料',
 'FEET-S01':'CDC糖尿病足护理', 'FEET-S02':'Northamptonshire Healthcare高风险足护理',
 'FEET-S03':'NHS坏疽急症指导', 'FEET-S04':'DermNet足癣鉴别与检查', 'FEET-S05':'NHS足癣护理',
 'FEET-S06':'CDC癣病治疗指导', 'FEET-S07':'NHS脚臭护理', 'FEET-S08':'AAD多汗诊疗',
 'FEET-S09':'NHS多汗症指导', 'FEET-S10':'AAD干裂足跟护理', 'FEET-S11':'NHS水疱护理',
 'FEET-S12':'NHS鸡眼与足茧护理', 'FEET-S13':'Cleveland Clinic脱皮足膜说明',
 'FEET-S14':'NHS嵌甲指导', 'FEET-S15':'BAD甲真菌感染患者说明', 'FEET-S16':'BAD2026甲真菌病循证指南',
 'FEET-S17':'AAD甲部黑色素瘤警示', 'FEET-S18':'NHS疣与跖疣指导', 'FEET-S19':'AAD疣的自我护理',
 'FEET-S20':'NHS足底筋膜相关疼痛指导', 'FEET-S21':'Guy’s and St Thomas’拇外翻指导',
 'PERIOD-S01':'FDA棉条安全', 'PERIOD-S02':'CDC经期卫生', 'PERIOD-S03':'FDA卫生巾与护垫',
 'PERIOD-S04':'FDA月经杯安全', 'PERIOD-S05':'Mooncup该型号使用说明', 'PERIOD-S06':'Flex该型号杯碟使用说明',
 'PERIOD-S07':'FSRH宫内避孕指南', 'PERIOD-S08':'NHS中毒性休克指导', 'PERIOD-S09':'NHS月经基础说明',
 'PERIOD-S10':'NHS月经不规律', 'PERIOD-S11':'NHS经量过多', 'PERIOD-S12':'NHS绝经后出血',
 'PERIOD-S13':'NHS痛经指导', 'PERIOD-S14':'NHS成人布洛芬说明', 'PERIOD-S15':'NHS宫外孕症状',
 'PERIOD-S16':'NHS非经期与性交后出血', 'PERIOD-S17':'Healthdirect经量过多',
 'PERIOD-S18':'Healthdirect阴道遗留用品处理', 'PERIOD-S19':'墨尔本皇家儿童医院青少年经量过多',
 'PERIOD-S20':'2024月经杯与铜宫内节育器脱落研究',
}
for p,ch in chapters.values():
    for e in ch['entries']:
        source = e['fields']['sources']
        if '依据[@' in source:
            new = re.sub(r'依据\[@([^\]]+)\]', lambda m:labels[m.group(1)]+'[@'+m.group(1)+']',source)
            add(e['id'],'sources',source,new,'来源栏应说明机构与主题，不能只重复“依据”；引文ID和顺序保持。')
        elif e['id'] in ['private-009','private-020','private-021','private-022','private-023','private-024','private-025','private-026','private-027']:
            ids = re.findall(r'\[@([^\]]+)\]',source)
            new = '；'.join(labels[sid]+'[@'+sid+']' for sid in ids)+'。'
            add(e['id'],'sources',source,new,'只有编号的来源栏补上机构与主题；制造商材料仍只称型号说明。')

add('anal-008','evidence','健康成人慢性特发性便秘中PEG的直接试验综合','成人慢性特发性便秘中聚乙二醇（PEG）的直接试验综合','患慢性便秘的人不应被笼统称为健康成人，顺便解释缩写。')
add('anal-002','evidence','不提供自行引流或抗生素选择。','引流和抗生素选择需要实际检查，不能只靠疼痛位置判断。')
add('anal-003','evidence','不提供擦拭方向的个人感染概率。','不能据擦拭方向计算个人感染概率。')
add('anal-009','evidence','未以症状或自查确诊，未给处方剂量。','症状只提示检查方向，不能自行确诊或照搬药物剂量。')
add('basics-004','evidence','未指定通用高蛋白剂量或给品牌背书。','不能据此设定人人相同的高蛋白摄入量或给品牌背书。')
add('basics-006','evidence','未将成人剂量外推给儿童。','成人活动时长不能直接套给儿童。')
add('basics-007','evidence','未替每一种成分完成独立疗效综述。','一般补剂指导不能代替具体成分、用途与剂量的疗效证据。')
add('basics-009','evidence','未比较每款电子烟。','不能据此给每款电子烟的风险排名。')
add('basics-010','evidence','不是中国诊断界值或肥胖处方全谱。','不能直接当作中国诊断界值或自行减重用药的依据。')
add('bodyskin-005','evidence','未按照片自定菌种。','不能仅凭照片确定病原。')
add('bodyskin-021','sources','康复新液检索范围和未采用资料另记研究审计。','','检索审计属于维护记录，读者来源栏只显示可核查依据。')
add('bodyskin-022','evidence','不提供照片确诊。','照片线索不能代替确诊。')
add('feet-006','evidence','未证明某品牌优于其他保湿剂。','不能据此认定某品牌优于其他保湿剂。')
add('feet-013','evidence','未据此认定定制鞋垫优于成品或规定人人同一训练量。','不能据此认定定制鞋垫优于成品，也不能给所有人设定同一训练量。')
add('hands-001','evidence','本条不凭表现自诊或开抗生素。','症状用于及时求助，不能自行确定病原或抗生素处方。')
add('hands-003','evidence','未提供不同品牌、手膜和普通霜的直接疗效排名。','不能据此给不同品牌、手膜和普通霜作直接疗效排名。')
add('hands-008','evidence','未给出凭照片分型或通用抗菌处方。','外观不能代替病因鉴别，也不足以支持一套通用抗菌方案。')
add('legs-005','evidence','没有把所有急性或特定病因腰痛治疗全称化。','不适用于所有急性腰痛或已有明确病因的腰痛。')
add('legs-007','evidence','未设置所有人同一训练处方。','训练量需要按功能和耐受制定。')
add('legs-010','evidence','未给所有人的固定周增量或比赛处方。','跑量和训练安排要按起点与恢复调整，不宜统一设定固定周增量。')
add('neck-004','evidence','没有据此给所有枕头材料作临床优劣排名。','不能据此给所有枕头材料作临床优劣排名。')
add('neck-006','evidence','不提供个体处方，不认为口服越强就越好。','实际选择取决于风险和用途，不是口服药效越强越好。')
add('private-029','sources','本篇睾丸和尿路急症来源。','NHS睾丸痛和尿路感染急症指导。')
add('private-030','sources','本篇睾丸急症。','睾丸急症指导。')
add('private-031','sources','本篇睾丸及上尿路感染分流。','NHS睾丸痛和上尿路感染分流。')
add('private-035','sources','本篇异常出血指导。','NHS异常出血指导。')
add('private-019','sources','CDC2024HIV暴露后预防与2026STI检测。','CDC：HIV暴露后预防及性传播感染检测。')
add('private-037','evidence','并非本项目重新计算的中国人群比较试验。','汇总来自其所述人群，不能作为中国所有使用者的个体预测。')
add('private-039','sources','CDC2024CHC、POP及紧急避孕。','CDC2024复方与孕激素单方避孕药的临床使用，以及紧急避孕指导。')
add('private-043','sources','CDC紧急药后续、NHS紧急药呕吐、验孕与骨盆急症。','CDC紧急避孕后的衔接；NHS服药后呕吐、验孕和骨盆痛指导。')
add('private-044','evidence','不提供个体风险概率保证。','人群风险资料不能保证个人结局。')
add('private-047','sources','CDC2024MEC、方法与哺乳闭经条件。','CDC2024避孕方法医学适用标准、临床使用与哺乳闭经条件。')
add('private-053','evidence','不提供自行激素调整方案。','具体激素治疗需要专科评估，不自行调整。')

for x in patches:
    _,e = entries[x['id']]
    old = x['old']; new = x['new']
    assert re.findall(r'\[@[^\]]+\]',old) == re.findall(r'\[@[^\]]+\]',new), (x['id'],'citation changed')

coverage = []
for p,ch in chapters.values():
    for e in ch['entries']:
        values = {f:e['fields'][f] for f in ['cost','evidence','sources']}
        coverage.append(dict(id=e['id'],file=p.relative_to(ROOT).as_posix(),
            fields_read=['cost','evidence','sources'],manual_read_complete=True,
            input_sha256=hashlib.sha256(json.dumps(values,ensure_ascii=False,sort_keys=True).encode()).hexdigest(),
            cost_result='原字段为空，保持省略，不添加占位成本' if not values['cost'] else '已读，按原有具体内容审看',
            changed=any(x['id']==e['id'] for x in patches),
            result='已实际通读，不将来源编号/等级当作临床审核；必要替换见patches。'))
out=dict(version='2026-10-30',input='original body JSON + prose-patches.json (164 patches); before head/bodyextra',
    coverage_count=len(coverage),patches=patches,coverage=coverage,
    limits='本次是文字、引用呈现和逻辑衔接审读，未重做174条的系统证据检索；完整Vancouver和DOI仍以来源账本为准。')
(HERE/'extra-fields-patches-body.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(coverage=len(coverage),patches=len(patches),changed_entries=len(set(x['id'] for x in patches))),ensure_ascii=False))
