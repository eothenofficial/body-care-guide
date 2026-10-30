"""Deliver a completed part, update the cumulative reader, preserve review history."""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEST = ROOT.parent / '全身护理逐篇交付'


def read(path): return json.loads(path.read_text(encoding='utf-8'))
def write(path, obj): path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def run(script, *args): subprocess.run([sys.executable, '-X', 'utf8', str(HERE / script), *args], check=True, cwd=ROOT)


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('part'); args = parser.parse_args()
    plan = read(HERE / 'plan.json'); item = next(p for p in plan['parts'] if p['id'] == args.part)
    review_path = HERE / 'evidence' / (args.part + '-independent-review.json')
    if not review_path.exists(): raise ValueError('Independent editorial review is required before delivery')
    review = read(review_path)
    if review.get('blocking_unresolved'): raise ValueError('Unresolved editorial issue')
    run('preview.py', '--part', args.part); run('verify.py', '--part', args.part)
    part_dist = ROOT / '.draft-preview/whole-body' / args.part / 'dist'
    report = read(HERE / 'compiled' / args.part / 'build-report.json')
    DEST.mkdir(exist_ok=True)
    suffix = '_' + item['delivery_suffix'] if item.get('delivery_suffix') else ''
    stem = str(item['order']).zfill(2) + '_' + item['title'] + suffix + '_2026-10-29'
    html = DEST / (stem + '.html'); archive = DEST / (stem + '_校对包.zip')
    shutil.copyfile(part_dist / 'downloads/guide-offline.html', html)
    notes = f"{item['title']}：本地待校对稿\n\n本篇{report['entries']}条，{report['sources']}项实际引用来源。双击HTML即可阅读。完整正文、参考文献、年龄范围、产品边界与危险分流均在其中；无需安装软件。\n\n校对包保留网页、结构化原稿、来源、审计与SOP。源记录的阅读深度和局限如实保留；独立AI编辑复核不是临床专业签审。未自动发布线上。\n"
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('先读我.txt', notes); z.write(html, html.name)
        for p in sorted(part_dist.rglob('*')):
            if p.is_file(): z.write(p, '网页/' + p.relative_to(part_dist).as_posix())
        z.write(HERE / 'chapters' / (args.part + '.json'), '可编辑源稿/章节.json')
        for p in sorted((HERE / 'evidence').glob(args.part + '-*.json')): z.write(p, '可编辑源稿/' + p.name)
        z.write(HERE / 'compiled' / args.part / 'sources.json', '可编辑源稿/统一参考来源.json')
        z.write(ROOT / 'docs/身体护理指南全书规划与调用SOP.md', '写作与研究SOP.md')
        z.write(ROOT / 'docs/继续写作Prompt.txt', '继续写作Prompt.txt')
        z.write(HERE / 'compiled' / args.part / 'validation.json', '工程核对.json')
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None and z.read(html.name) == html.read_bytes()
    item['status'] = 'delivered_for_review'
    if args.part not in plan['delivered']: plan['delivered'].append(args.part)
    write(HERE / 'plan.json', plan)
    run('preview.py'); run('verify.py')
    master = DEST / '身体护理指南_从头到脚合订稿_2026-10-29.html'
    shutil.copyfile(ROOT / '.draft-preview/whole-body/master/dist/downloads/guide-offline.html', master)
    receipt = dict(part=args.part, title=item['title'], entries=report['entries'], sources=report['sources'],
        status='delivered_locally_for_review_not_published', html=str(html), zip=str(archive), master=str(master),
        html_sha256=sha(html), zip_sha256=sha(archive), clinical_review_status='not_clinically_reviewed')
    write(HERE / 'deliveries' / (args.part + '.json'), receipt)
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == '__main__': main()
