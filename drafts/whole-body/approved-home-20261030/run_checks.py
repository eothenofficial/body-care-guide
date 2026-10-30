"""Bind the actual current test run to the delivered visual edition."""
import hashlib,io,json,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests'))
if __name__=='__main__':
    stream=io.StringIO()
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.discover(str(ROOT/'tests')))
    (HERE/'test-output.txt').write_text(stream.getvalue(),encoding='utf-8')
    report=dict(testsRun=result.testsRun,returncode=0 if result.wasSuccessful() else 1,failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),reader_sha256=hashlib.sha256((ROOT/'.draft-preview/approved-home-20261030/dist/downloads/guide-offline.html').read_bytes()).hexdigest())
    (HERE/'test-results.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))
    if not result.wasSuccessful():print(stream.getvalue())
    sys.exit(report['returncode'])
