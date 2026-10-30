"""One-time independent review corrections; never run the author's generator after this."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NAMES = ['medications-entries.json', 'medications-sources.json', 'medications-audit.json']
INITIAL = {
    'medications-entries.json': 'ce4ca640d999486cf5a70ccc5f924f870a0590cce653102e68e75667f7e9a78f',
    'medications-sources.json': 'fadadaca87f904dfdc50aeb02be0491b9e003b177b9eeb3942f74629990e3662',
    'medications-audit.json': '4960cf926fdfa4312bc052e7a0635bfc1c8bb05ef68f1f7e7ff771500e147f1f',
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

for name in NAMES:
    assert sha(ROOT / name) == INITIAL[name], f'Input changed: {name}'

entries, sources, audit = [json.loads((ROOT / n).read_text(encoding='utf-8')) for n in NAMES]
ee = {e['id']: e for e in entries}
ss = {s['id']: s for s in sources}
patches = []

def replace(obj, key, old, new, why):
    assert old in obj[key], (key, old)
    obj[key] = obj[key].replace(old, new)
    patches.append(dict(field=key, before=old, after=new, reason=why))

replace(ee['nutrition-017'], 'title', '符合减重适应证再选针剂，用同一项试验判断药物差别',
        '符合减重适应证再选针剂，比较效果优先看直接对照试验',
        '并非所有药均来自同一项试验，原标题有误导。')
replace(ee['nutrition-017']['fields'], 'notes', '其他选择见下一条。',
        '其他选择见[其他药物与渠道核验](#/entry/nutrition-019)。',
        '018为安全条目，其他选择实际在019；使用明确链接。')

replace(ee['nutrition-018']['fields'], 'plain',
        '不要把前两种的月份直接套给所有药；正在用药又准备怀孕、哺乳或依赖口服避孕药时，让处方团队逐药核对停药窗口和避孕方案。',
        '不要把前两种的月份直接套给所有药；准备怀孕或哺乳时，先让处方团队逐药核对停药窗口与替代方案。**使用穆峰达且服用口服激素避孕药，应改用非口服避孕措施，或在开始治疗、每次增加剂量后的前4周，在原口服避孕药基础上加用避孕套等屏障措施。** 这条相互作用建议来自该药中国说明书，不能套给所有GLP-1药。',
        '独立实读穆峰达2025-08-20中国PI第19页，存在明确四周措施；原文仅让咨询不足以传达已知安全行动。')

replace(ss['NFM-S01'], 'citation', '2024 Oct 17', '2024',
        '17日无可直接核实依据；原指南版本年份明确，去掉虚假精确日。')
ss['NFM-S01']['published_at'] = '2024'
patches.append(dict(field='NFM-S01.published_at', before='2024-10-17', after='2024', reason='日期精度降到实际确认范围。'))

s3 = ss['NFM-S03']
old_url = s3['url']
new_url = old_url.replace('%E5%A4%9A%E5%89%82%E9%A2%84', '%E5%A4%9A%E5%89%82%E9%87%8F%E9%A2%84')
assert new_url != old_url
replace(s3, 'url', old_url, new_url, '原URL漏“量”导致失效，已正常公开打开44页正确PDF。')
replace(s3, 'citation', '多剂预装', '多剂量预装', '按说明书和实际文件名核对制剂名称。')
replace(s3, 'citation', old_url, new_url, '题录使用同一正确来源URL。')
s3['support'] += ' 其第19页还明确：口服激素避孕者改用非口服措施，或起始及每次递增后的前4周加屏障措施。'
s3['limitations'] = '官方当前产品索引标2026-09-20修订，但新版全文链接需专业登录；本条实际核到2025-08-20多剂量版，不能宣称覆盖2026全部标签变化。四周避孕措施已从中国PI第19页直接核到；未给替尔泊肽生造统一备孕停药月份。'
s3['reading_depth'] = '直接读取官方公开44页PDF：p1–4版本/适应证/制剂，p13–19禁忌、安全、孕哺、老年和口服激素避孕相互作用；另核p43持有人确为Eli Lilly Nederland B.V.。已读当前官方索引的2026-09-20版本提示，未绕过HCP登录或声称读到新版全文。'
patches.append(dict(field='NFM-S03.support/limitations/reading_depth', reason='补充已实读中国口服激素避孕四周要求；保留新版未取得的限制，并核持有人。'))

ss['NFM-S05']['published_at'] = '2025-05-11'
ss['NFM-S05']['issue_date'] = '2025-07-03'
ss['NFM-S06']['published_at'] = '2025-05-25'
ss['NFM-S06']['issue_date'] = '2025-06-12'
patches.append(dict(field='NFM-S05/S06.published_at', reason='明确线上发表日与正式期刊日；GLORY-1原2025-05-29错误，改原刊PDF及PubMed均确认的2025-05-25。'))

for c in audit['claims_checks']:
    if c['claim'] == '孕备/禁忌/谨慎人群按成分':
        c['result'] = '司美至少2个月、玛仕至少3个月均按中国PI；独立复核已确认穆峰达中国PI第19页包含口服激素避孕起始/每次递增后前4周加屏障或改非口服要求，已补正文；不将其套给其他GLP-1药，未生造替尔泊肽统一备孕停药月份。'
audit['independent_corrections'] = [
    '017标题改为优先直接对照试验，修正其他选择错指为019明确链接。',
    'S03原来源URL漏“量”已修复；其中国PI第19页实际有口服激素避孕四周措施，已落实到018及来源描述。',
    'S01不确切的2024-10-17降为已确认年份；S05/S06区分线上日及正式期刊日，修GLORY1错误5月29日。',
]
audit['status'] = 'independently_reviewed_with_stated_limits_not_clinically_reviewed'

for name, value in zip(NAMES, [entries, sources, audit]):
    (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

ids = set(ss)
for e in entries:
    assert 100 <= len(e['summary']) <= 180
    assert e['fields']['cost'] == ''
    assert set(e['fields']) == {'cost','plain','benefit','evidence','sources','notes'}
    assert set(re.findall(r'\[@([^\]]+)\]', json.dumps(e, ensure_ascii=False))) <= ids
    assert e['audience']['age_groups'] == ['adult','older']
    assert e['audience']['sexes'] == ['all']

review = {
    'checked_at': '2026-10-30',
    'reviewer_role': 'independent_content_and_source_audit_not_clinical_review',
    'input_sha256': INITIAL,
    'output_sha256': {n:sha(ROOT / n) for n in NAMES},
    'reviewed_entries': list(ee),
    'reviewed_sources': list(ss),
    'changes_applied': patches,
    'blocking_unresolved': [],
    'checks': [
        '已逐句读取009及017–019的标题、摘要和六字段，核引用指向与人群；未修改共享构建器、旧条目或其他分工文件。',
        '中国一般超重/肥胖24/28，与诺和盈30/27、穆峰达及信尔美28/24伴病门槛分开；均不是达到门槛就自动用药。',
        '实读诺和盈2026-07-27中国PI的适应证、MTC/MEN2、NAION、肝肾/胃轻瘫、孕哺和至少2月停药；未套美国青少年批准或处方方案。',
        '实读穆峰达2025-08-20多剂量中国PI的适应证、安全、孕哺和相互作用；MTC/MEN2/严重超敏禁忌存在。孕期减重禁用与糖尿病孕期特殊权衡未混成统一绝对标签；哺乳不是本版标签中一概禁用。',
        '实读信尔美前部体重管理PI，至少3月备孕停药、孕哺不得使用及65岁以上仅3人；未将后部糖尿病适应证的老年数据混用。',
        '实读SURMOUNT-5原刊PDF方法、主modified treatment-regimen estimand、基线及结果：20.2%/13.7%、72周、751人、最大耐受剂量方案正确；不称无条件纯ITT。',
        'GLORY-1原刊PDF和PubMed题录、完整摘要核610人、基线87.2kg/BMI31.1及疗法策略48周-11.00%/-14.01%/+0.30%；主终点32周与次要48周分开。',
        'SURMOUNT-5系两活性药直接比较，GLORY-1是安慰剂对照；各自资助披露保留，没有跨试验排名或把最高剂量当个人用法。',
        '实读STEP1延伸完整摘要与利益披露：327人探索性随访、停药及生活方式干预均终止，回升约三分之二不能变成每个人必须终身治疗。',
        '实读奥利司他2012监管范本及2024指南相关段；BMI24、机制、孕期禁用、哺乳/18岁以下不宜、吸收/胆汁/药物相互作用和肝肾警讯有依据，没有给个人剂量。',
        '已实读埃诺格鲁肽2026-03-06持有人原始声明，仅用于获批声明，不据公告排序、补精确BMI或安全禁忌；未假称拿到完整PI。',
        '已实读FDA质量/单位误算/盐形式/科研标签相关段、上海药监查询答复和湖南西布曲明风险原页；未将美国名单变成中国名单、旧通告变成2026抽检。',
    ],
    'reading_depth_and_limits': [
        '独立复核用了本地原始PDF提取文本（NHC、诺和盈、信尔美、SURMOUNT5）与web可读的穆峰达44页原PDF、GLORY1原PDF及相关原刊/监管网页；不是只接受作者的来源摘要。',
        '未逐条复算RCT数据、重读所有试验附录，亦未完成任何品牌全规格/全国药品库穷尽核查。',
        '穆峰达官方2026-09-20新版索引已看到，完整新版未取得；本条限定实际读到的2025-08-20版及其稳定事实，当前临床使用仍须核现行PI。',
        '诺和盈未取得2026-10储运更新原件；正文没有给储运温度/小时数，故未以旧储运规定替代新规定。',
        '该独立复核是文字和证据核对，不是持证临床人员签审；未声称结论100%正确。',
    ],
    'validation': {'summary_lengths':{e['id']:len(e['summary']) for e in entries}, 'all_source_ids_resolve':True, 'six_fields_present':True, 'costs_empty':True},
    'freeze': '完成后不再运行write-medications.mjs；若再次改原始JSON，须重核并更新hash记录。',
}
(ROOT / 'medications-independent-review.json').write_text(json.dumps(review, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'reviewed':list(ee),'patches':len(patches),'blocking_unresolved':[],'output_sha256':review['output_sha256']}, ensure_ascii=False))
