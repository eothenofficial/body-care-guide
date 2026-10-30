"""Package a local, unpublished reader and reproducible project sources."""
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEST = ROOT.parent
DIST = ROOT / '.draft-preview/head-care-audience/dist'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    report = json.loads((HERE / 'build-report.json').read_text(encoding='utf-8'))
    old_names = ['五官与头皮头发_2026-10-29.html', '五官与头皮头发_校对包_2026-10-29.zip',
                 '五官篇_待校对_2026-10-29.html', '五官篇_校对包_2026-10-29.zip']
    archive = ROOT.parents[1] / 'analysis/20261029-audience/baseline'
    archive.mkdir(parents=True, exist_ok=True)
    for name in old_names:
        original = DEST / name
        if original.exists() and not (archive / name).exists():
            shutil.copyfile(original, archive / name)
    html_name = '五官与头皮头发_年龄分层校对版_2026-10-29.html'
    html = DEST / html_name
    shutil.copyfile(DIST / 'downloads/guide-offline.html', html)
    for name in (old_names[0], old_names[2]):
        shutil.copyfile(html, DEST / name)
    zip_path = DEST / '五官与头皮头发_年龄分层校对包_2026-10-29.zip'
    readme = f'''五官与头皮头发：年龄分层校对包\n\n先双击根目录“{html_name}”阅读，无需安装软件。右上角“年龄与男女”可以输入年龄或选择年龄段；清除筛选恢复全部内容。\n\n本版{report['entries']}条、{report['sources']}项实际引用来源，7个模块。新增耳廓耳后和耳饰护理，口腔重组，换牙/分龄正畸/地包天/缺牙修复与儿童视力入口。未核对的儿童或老年应用会如实说明。\n\n网页目录包含全部静态分享页、下载和JSON接口。项目源文件保留正文、来源、SOP、Prompt、审计、测试和构建代码，供后续开发维护。进入项目源文件后，按drafts/head-care-audience/README.md复现；普通读者当前只需打开HTML。\n\n本轮仅本地交用户校对，未发布线上。来源与AI交叉复核不等于持证临床人员签审，工程测试不证明医学结论。\n'''
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as archive_zip:
        archive_zip.writestr('先读我.txt', readme)
        archive_zip.write(html, html_name)
        for path in sorted(DIST.rglob('*')):
            if path.is_file():
                archive_zip.write(path, '网页/' + path.relative_to(DIST).as_posix())
        for folder in ['content', 'docs', 'scripts', 'tests', 'web', '.github', 'drafts/head-care-audience']:
            for path in sorted((ROOT / folder).rglob('*')):
                if path.is_file() and '__pycache__' not in path.parts and path.name != 'delivery-receipt.json':
                    archive_zip.write(path, '项目源文件/' + path.relative_to(ROOT).as_posix())
        for name in ['README.md', 'build.py', '.gitignore']:
            archive_zip.write(ROOT / name, '项目源文件/' + name)
    for name in (old_names[1], old_names[3]):
        shutil.copyfile(zip_path, DEST / name)
    with zipfile.ZipFile(zip_path) as archive_zip:
        assert archive_zip.testzip() is None
        count = len(archive_zip.namelist())
        assert archive_zip.read(html_name) == html.read_bytes()
        assert archive_zip.read('网页/downloads/guide-offline.html') == html.read_bytes()
    for name in (old_names[0], old_names[2]):
        assert (DEST / name).read_bytes() == html.read_bytes()
    receipt = dict(status='local_review_package_not_published', content_version=report['content_version'],
        entries=report['entries'], sources=report['sources'], zip_files=count,
        html=dict(path=str(html), bytes=html.stat().st_size, sha256=sha(html)),
        zip=dict(path=str(zip_path), bytes=zip_path.stat().st_size, sha256=sha(zip_path)),
        reusable_sop=str(ROOT / 'docs/身体护理指南全书规划与调用SOP.md'),
        prompt=str(ROOT / 'docs/继续写作Prompt.txt'),
        familiar_aliases_updated=old_names, old_artifacts_preserved=str(archive),
        clinical_review_status='not_clinically_reviewed')
    (HERE / 'delivery-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == '__main__':
    main()
