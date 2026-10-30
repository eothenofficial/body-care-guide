"""Apply the two source-checked child vision additions, keeping prior IDs."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    chapter_path = HERE / 'chapters/eyes.json'
    chapter = json.loads(chapter_path.read_text(encoding='utf-8'))
    definitions = [
        ('eyes-031', '孩子用眼先安排户外和间歇，别只换防蓝光镜片',
         '给孩子安排课间、放学后的户外时间，比只买护眼灯或防蓝光镜片更值得先做。读书和屏幕都属于近距离任务，可以用每二十分钟看远二十秒的提醒打断连续用眼。这种间歇主要缓解疲劳，不能保证不近视；已经近视还要验光、矫正和随访，不能靠户外活动替代治疗。',
         '把户外时间实际排进课间、放学后和周末；不要只在家换一盏“护眼灯”，却让孩子一直近距离看书或玩屏幕。儿童户外时间较多与较低的近视发生风险有关，近视的发生和进展也受遗传等因素影响。户外不是盯太阳，不能把“自然光好”理解为直接看强光。这里建议安排生活方式，不承诺把已有近视逆转。[@VISION-S07][@CHILDVIEW-S01]\n\n连续近距离任务既包括手机，也包括作业和课外阅读。可以设置每20分钟看约6米外至少20秒的提醒；先抬头、眨眼、换远近任务，不必把学习全部停掉。这是专业组织用于减轻屏幕相关眼疲劳的实用提醒，不是经试验证明照这个节拍就能防住近视。屏幕位置略低于视线、避免反光，字太小先放大，也比贴得更近更合适。[@CHILDVIEW-S02]\n\n买镜片时分别问：它是矫正度数、减少反光，还是有儿童近视控制的直接研究？防蓝光标签不能替代这些不同任务。孩子仍眯眼、看黑板不清楚或反复头痛，转到[儿童看不清的检查与配镜](#/entry/eyes-032)；已经确诊近视，再看[控制镜片与护理条件](#/entry/eyes-008)。[@CHILDVIEW-S01][@CHILDVIEW-S02]',
         '减少连续近距离任务带来的不适，并把户外活动纳入儿童近视预防；不能据此承诺不发病、度数下降或替代已经需要的矫正。',
         'C，儿科与国家眼科研究机构的患者指导；户外与风险的关联不在此换算成个人获益，20-20-20作为舒适用眼提醒，不宣称为近视控制疗法。',
         'NEI近视说明；AAP儿童近视及屏幕用眼建议。[@VISION-S07][@CHILDVIEW-S01][@CHILDVIEW-S02]',
         '本条给家长和学生安排日常活动使用；儿童视力筛查、验光和近视控制的复查节点另按诊疗方案，不由读书时长或本页年龄筛选替代。'),
        ('eyes-032', '孩子眯眼看黑板先验光，配镜与减慢近视加深分开决定',
         '孩子看黑板模糊、总眯眼，或学校筛查没通过，先做正规的眼部检查和验光，不用手机测视力直接买镜。确认近视后，镜片帮助看清，近视控制还要另看进展、眼轴和适用条件；不能靠故意少配度数来控制。是否全天戴镜按处方与学习活动决定，不跟别的孩子照抄。',
         '孩子说黑板看不清、经常眯眼，或学校筛查异常时，先预约眼科或有儿童验光能力的正规医疗机构。学校视力筛查是在找可能的问题，不是完整诊断；眼睛看不清也不能仅凭症状认定就是近视。检查需要结合眼部状态和验光，部分儿童还需要散瞳验光——用药暂时放松聚焦调节，帮助取得更可靠的屈光结果。[@CHILDVIEW-S01][@src-ef3d7b7a8fb9]\n\n确诊后分两件事：镜片先让孩子在课堂、走路和活动时看清；如果需要减慢近视加深，再结合度数、眼轴和进展讨论控制方案。眼轴是眼球前后长度，不是把视力表分数换算成近视度数。普通单焦框架、特定近视控制框架、特殊软镜和OK镜的目标与护理要求不同，比较路径见[镜片选择](#/entry/eyes-008)。不能把控制套餐直接说成治愈近视，也不靠故意欠矫来延缓加深。[@CHILDVIEW-S01][@src-ef3d7b7a8fb9][@src-609e76825b6e]\n\n选能稳稳戴住、不压痛的镜架，运动场景再选相应防护。是否全天戴、仅某些任务戴及复查间隔，要由处方和实际视物需求确定；不要套用“越少戴越好”或“所有轻度近视都必须同一戴法”。即使使用接触镜，也要有备用框架；戴镜红痛或突然看不清时提前检查。[@CHILDVIEW-S01]',
         '把异常筛查接到诊断与合适矫正，并把看清和控制加深分开比较；不把眼镜本身说成近视越来越深的原因。',
         'C，儿童近视诊疗与配镜指导；具体控制方式的效果证据见相应镜片条目，不能因这条导览而把所有方式评级相同。',
         'AAP儿童近视；国家2026近视指南；IMI2025干预综述。[@CHILDVIEW-S01][@src-ef3d7b7a8fb9][@src-609e76825b6e]',
         '本条的儿童入口不包含一张通用药物处方，也不以筛选中的0–11岁或12–17岁替代具体产品批准年龄、禁忌或监护能力。突然下降、眼痛、外伤等先读[急症分流](#/entry/eyes-005)。')
    ]
    by_id = {e['id']: e for e in chapter['entries']}
    for eid, title, summary, plain, benefit, evidence, sources, notes in definitions:
        by_id[eid] = dict(id=eid, chapter_id='eyes', unit_id='eyes-u9', ordinal=0,
            title=title, summary=summary,
            fields=dict(cost='', plain=plain, benefit=benefit, evidence=evidence, sources=sources, notes=notes),
            audience=dict(age_groups=['child', 'teen'], sexes=['all'],
                scope_note='儿童和青少年入口，供学生与照护者阅读；具体验光和干预仍按发育、检查与产品条件判断。', safety_pin=False),
            evidence_labels=['C'], tags=[], source_ids=[], content_checked_at='2026-10-29',
            clinical_review_status='not_clinically_reviewed')
    chapter['entries'] = list(by_id.values())
    chapter['units'] = [u for u in chapter['units'] if u['id'] != 'eyes-u9']
    position = next(i for i, u in enumerate(chapter['units']) if u['id'] == 'eyes-u7')
    chapter['units'].insert(position, dict(id='eyes-u9', title='孩子看不清，先接上检查、矫正与预防',
        intro='家长先帮孩子解决看清和规范用眼，再看是否需要近视控制。年龄只是入口，不能代替检查和具体方案的适用条件。',
        order=position+1, entry_ids=['eyes-031', 'eyes-032']))
    for i, u in enumerate(chapter['units'], 1): u['order'] = i
    save(chapter_path, chapter)
    sources = []
    for sid, title, day, url, support, limitations, depth in [
        ('CHILDVIEW-S01', 'Myopia (nearsightedness) in children & teens', '2023 Sep 6',
         'https://www.healthychildren.org/English/health-issues/conditions/eyes/Pages/Myopia-Nearsightedness.aspx',
         '儿童眯眼/远处模糊、筛查后需完整检查；矫正和控制分别讨论；镜架贴合与备用框架；户外和接触镜安全。',
         '不使用该2023页将现行控制器械统称尚在研究，不借美国专业资质分类推中国验光权限；不据此规定全国统一戴镜时长。',
         '2026-10-29打开AAP原页，核读症状、诊断、Glasses、Contact lenses、控制与户外段及页脚实际更新日。'),
        ('CHILDVIEW-S02', "Give your child's eyes a screen-time break: here's why", '2024 Feb 29',
         'https://www.healthychildren.org/English/health-issues/conditions/eyes/Pages/What-Too-Much-Screen-Time-Does-to-Your-Childs-Eyes.aspx',
         '儿童用屏幕间歇、20-20-20提醒、眨眼、屏幕位置及不把防蓝光镜列为必买。',
         '患者教育不是近视预防节拍RCT；不使用其旧二手屏幕时长数据、特殊橙色镜片或照明亮度说法作购买建议。休息用于舒适，不承诺延缓眼轴增长。',
         '2026-10-29打开AAP原页，核读What parents can do与blue-light部分，核对2024-02-29为更新日。')]:
        sources.append(dict(id=sid, citation=f'American Academy of Pediatrics. {title} [Internet]. {day}. [cited 2026 Oct 29]. Available from: {url}',
            url=url, type='专业学会患者指导', support=support, limitations=limitations, reading_depth=depth, content_checked_at='2026-10-29'))
    save(HERE / 'evidence/child-vision-sources.json', sources)
    save(HERE / 'evidence/child-vision-audit.json', dict(date='2026-10-29', status='editorial_not_clinical',
        additions=['eyes-031', 'eyes-032'], reused=['VISION-S07', 'src-ef3d7b7a8fb9', 'src-609e76825b6e'],
        reading_note='新增两篇AAP原页及既有NEI近视页已实读。NHC PDF本轮重新请求超时；沿用同日上一轮已核第9–14页的验光与镜片结论，不声称新读其全文。',
        boundaries=['年龄分组用于导览，不是药物或镜片年龄许可', '20-20-20不包装成经试验证明的近视控制治疗', '儿童干预不得由筛选器自动推荐药物浓度或产品']))
    print('Added child vision entries:', [d[0] for d in definitions])


if __name__ == '__main__':
    main()
