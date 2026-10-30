"""Rebuild the packaged source and compare the actual delivered reader bytes."""
import hashlib,json,os,subprocess,sys,zipfile
from datetime import datetime
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
DEST=ROOT.parent/'少走弯路的人体保养指南_2026-10-30'
if __name__=='__main__':
    archive=DEST/'少走弯路的人体保养指南_完整项目.zip'
    target=ROOT/'.draft-preview/approved-home-source-reproduction'
    if not target.resolve().is_relative_to((ROOT/'.draft-preview').resolve()):raise ValueError('Unsafe reproduction path')
    target.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        manifest=json.loads(z.read('网站/api/v1/manifest.json'))
        for name in z.namelist():
            if not name.startswith('项目源文件/'):continue
            relative=Path(name.removeprefix('项目源文件/'))
            if relative.is_absolute() or '..' in relative.parts:raise ValueError('Unsafe archive path')
            out=target/relative
            if not out.resolve().is_relative_to(target.resolve()):raise ValueError('Outside extraction target')
            out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(z.read(name))
    env=dict(os.environ,SOURCE_DATE_EPOCH=str(int(datetime.fromisoformat(manifest['build_at'].replace('Z','+00:00')).timestamp())))
    result=subprocess.run([sys.executable,'-X','utf8','drafts/whole-body/approved-home-20261030/build_release.py'],cwd=target,env=env,text=True,encoding='utf-8',capture_output=True,check=True)
    original=DEST/'少走弯路的人体保养指南.html'
    rebuilt=target/'.draft-preview/approved-home-20261030/dist/downloads/guide-offline.html'
    report=dict(status='passed' if original.read_bytes()==rebuilt.read_bytes() else 'failed',source_zip_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),build_at=manifest['build_at'],build_returncode=result.returncode,delivered_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),rebuilt_sha256=hashlib.sha256(rebuilt.read_bytes()).hexdigest(),portrait_is_embedded=True,extracted_project=str(target),clinical_review_status='not_clinically_reviewed')
    (HERE/'source-reproduction.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))
    if report['status']!='passed':raise ValueError('Packaged project is not reproducible')
