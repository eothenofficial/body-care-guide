"""Integrate reviewed additions and editorial readership scopes into this edition."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def unit(identifier, title, intro, ids):
    return dict(id=identifier, title=title, intro=intro, order=0, entry_ids=ids)


def main():
    chapters = {p.stem: read(p) for p in (HERE / 'chapters').glob('*.json')}
    all_entries = {e['id']: e for ch in chapters.values() for e in ch['entries']}
    additions = read(HERE / 'parts/dental-age.json')
    if isinstance(additions, list):
        records = additions
    else:
        records = additions.get('entries', [])
        replacements = additions.get('replacement', additions.get('replacements', []))
        if isinstance(replacements, dict):
            replacements = [replacements] if 'id' in replacements else list(replacements.values())
        records = records + replacements
    for entry in records:
        all_entries[entry['id']] = entry
    # The original ID records allocation, not current placement. Share links survive.
    moved = {'oral-014', 'oral-015', 'oral-008'}
    oral_ids = {e['id'] for e in chapters['oral']['entries']} - moved
    oral_ids.update(e['id'] for e in records)
    lip_ids = {e['id'] for e in chapters['lips']['entries']} | moved
    oral = chapters['oral']
    oral.update(title='牙齿与牙周', subtitle='从刷牙、牙龈与换牙，到正畸、美白和缺牙修复',
        intro='牙齿的照顾从刷到牙面、清到牙缝开始，但疼痛、牙龈出血、牙列不齐与缺牙，需要走不同的路。先判断是否要尽快处理，再看日常维护、发育与正畸、美容和修复；不把一套牙齿推销方案用在所有年龄。\n\n儿童与青少年从换牙和正畸评估进入，成年人比较牙周条件、牙套和长期保持，老年缺牙先分清活动假牙、固定桥和种植。嘴唇干裂、口腔溃疡、口干和舌面问题已归入嘴唇与口腔黏膜章，可从[口腔溃疡](#/entry/oral-014)等条目进入；原条目链接仍保留。')
    oral['units'] = [
        unit('oral-u1', '牙痛与出血，先分清要处理的问题', '发热脸肿、持续疼痛和反复牙龈出血不能只靠换清洁用品解决。', ['oral-018', 'oral-013', 'oral-007']),
        unit('oral-u2', '把牙面和牙缝清到，再挑辅助用品', '先建立清洁基础，再按防龋、牙龈或其他目标比较牙刷、牙线和漱口水。', ['oral-001', 'oral-002', 'oral-003', 'oral-004', 'oral-016', 'oral-005', 'oral-006']),
        unit('oral-u3', '从换牙到成人正畸，按发育和牙周条件决定时机', '首次评估、开始治疗和治疗保持是不同阶段；地包天等异常不能一律等到换牙结束。', ['oral-019', 'oral-020', 'oral-021', 'oral-012']),
        unit('oral-u4', '想美白或修饰牙形，先比较少磨牙的方案', '去渍、美白、贴面与全冠改变的东西不同，后续维护和不可逆处理应在决定前讲清楚。', ['oral-009', 'oral-010']),
        unit('oral-u5', '智齿与磨牙，按检查结果处理', '是否拔除和是否需要保护装置，都围绕具体病变和损伤风险判断。', ['oral-011', 'oral-017']),
        unit('oral-u6', '缺牙先选修复路径，再学会维护假牙', '活动假牙、固定桥和种植各有条件；年龄本身不是统一的入场证或排除条件。', ['oral-022', 'oral-023'])
    ]
    expected = {eid for u in oral['units'] for eid in u['entry_ids']}
    if oral_ids != expected:
        raise ValueError('Dental integration IDs differ: ' + str(oral_ids ^ expected))
    oral['entries'] = [all_entries[eid] for u in oral['units'] for eid in u['entry_ids']]
    lips = chapters['lips']
    lips.update(title='嘴唇与口腔黏膜', subtitle='从干裂、口角与唇疱疹，到溃疡、口干和口气',
        intro='嘴唇和口腔内壁都会被干燥、唾液、摩擦和接触物影响。先把普通干裂与反复炎症分开，再看溃疡、口干、舌苔和口气；同一处久不愈不能只当上火。\n\n润唇用品、唇妆、抗病毒治疗和润口产品解决不同问题。牙面、牙缝、牙龈、换牙、正畸与修复请到牙齿与牙周章；这里只保留各条的主要归属，跨章仍用原链接连接。')
    lips['units'] = [
        unit('lips-u1', '先照顾普通干裂，再选润唇与防晒用品', '先减少舔、撕和刺激，再比较能耐受的产品，不靠清凉感判断修护。', ['lips-001', 'lips-002', 'lips-003']),
        unit('lips-u2', '反复红痒、裂口和水疱，按表现换处理路径', '接触问题、唇疱疹与口角炎不能仅凭一个裂字使用同一种药膏。', ['lips-004', 'lips-005', 'lips-006']),
        unit('lips-u3', '口腔内壁溃疡或口干，先找原因与持续时间', '短时刺激与持续异常分开判断；留意摩擦、用药和影响吃说的变化。', ['oral-014', 'oral-015']),
        unit('lips-u4', '舌面轻柔清洁，口气问题再查来源', '舌苔可以处理，但持续口臭不应只靠刮舌或香味压住。', ['oral-008'])
    ]
    if lip_ids != {eid for u in lips['units'] for eid in u['entry_ids']}:
        raise ValueError('Mucosa membership mismatch')
    lips['entries'] = [all_entries[eid] for u in lips['units'] for eid in u['entry_ids']]
    pins = {'eyes-005', 'eyes-023', 'nose-006', 'oral-018', 'ears-005', 'ears-010'}
    explicit = {
        'eyes-008': (['child', 'teen', 'adult'], '正文分别比较儿童控制与成人矫正便利；不能把儿童研究移作成人同效。'),
        'eyes-020': (['child', 'teen', 'adult', 'older'], '报告概念可跨年龄阅读；儿童正常参考范围仍需结合发育阶段。'),
        'eyes-021': (['child', 'teen', 'adult', 'older'], '验光原理可供各年龄理解；散瞳、处方与恢复按具体检查判断。'),
        'eyes-025': (['adult', 'older'], '成人及老年高度近视的风险与检查入口；不是儿童随访方案。'),
        'eyes-030': (['child', 'teen', 'adult', 'older'], '用于辨别视力宣传的结局，不提供跨年龄通用的矫正或训练处方。')
    }
    scopes = {}
    for chapter in chapters.values():
        for entry in chapter['entries']:
            origin = ('original_adult_scope_not_new_population_review' if entry.get('audience', {}).get('scope_note', '').startswith('沿用成人原稿') else 'author_annotated')
            if 'audience' not in entry:
                entry['audience'] = dict(age_groups=['adult'], sexes=['all'],
                    scope_note='沿用成人原稿；儿童及老年应用尚未在本条专门核对，不据此推定不适用。', safety_pin=False)
                origin = 'original_adult_scope_not_new_population_review'
            if entry['id'] in explicit:
                ages, note = explicit[entry['id']]
                entry['audience'].update(age_groups=ages, scope_note=note)
                origin = 'editorial_scope_checked_against_existing_source_and_body'
            if entry['id'] in pins:
                entry['audience']['safety_pin'] = True
                if entry['id'] in {'eyes-005', 'eyes-023', 'oral-018', 'nose-006'}:
                    entry['audience']['scope_note'] = '危险信号入口在人群筛选中保留；本条不提供跨年龄通用的药物处方，具体处置按检查判断。'
            if entry['id'] == 'eyes-031':
                entry['title'] = '孩子用眼先安排户外和间歇，别只换防蓝光镜片'
            scopes[entry['id']] = dict(audience=entry['audience'], annotation_basis=origin)
        for index, u in enumerate(chapter['units'], 1):
            u['order'] = index
            for eid in u['entry_ids']:
                e = next(e for e in chapter['entries'] if e['id'] == eid)
                e['chapter_id'] = chapter['id']; e['unit_id'] = u['id']
        save(HERE / 'chapters' / (chapter['id'] + '.json'), chapter)
    save(HERE / 'evidence/audience-scope-review.json', dict(
        status='editorial_scope_annotation_not_clinical_eligibility', checked_on='2026-10-29',
        notes=['年龄分段是导览约定，不是诊断或治疗界值', '没有根据关键词或刻板印象分配男女',
               '旧成人稿未复核的人群不标全龄，未来可逐条扩充', '保留原条目ID，移动章节不破坏分享链接'],
        entries=scopes))
    print('Integrated:', {k: len(c['entries']) for k, c in chapters.items()})


if __name__ == '__main__':
    main()
