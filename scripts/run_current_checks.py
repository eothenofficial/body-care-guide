"""Run all offline tests, treating skipped reader checks as an incomplete release."""
import io
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tests'))

if __name__ == '__main__':
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(
        unittest.defaultTestLoader.discover(str(ROOT / 'tests')))
    report = dict(tests=result.testsRun, failures=len(result.failures), errors=len(result.errors),
                  skipped=len(result.skipped), passed=result.wasSuccessful() and not result.skipped)
    out = ROOT / 'reports'
    out.mkdir(exist_ok=True)
    (out / 'current-tests.txt').write_text(stream.getvalue(), encoding='utf-8')
    (out / 'current-tests.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report))
    if not report['passed']:
        print(stream.getvalue())
    raise SystemExit(0 if report['passed'] else 1)
