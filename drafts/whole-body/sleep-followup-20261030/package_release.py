"""Reuse export and source-package checks for the sleep extension edition."""
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
spec=importlib.util.spec_from_file_location('sleep_packager',HERE.parent/'revision-20261030/package_release.py')
package=importlib.util.module_from_spec(spec);spec.loader.exec_module(package)
package.HERE=HERE;package.ROOT=ROOT
package.TARGET=ROOT/'.draft-preview/sleep-followup-20261030';package.DIST=package.TARGET/'dist'
package.DEST=ROOT.parent/'身体护理指南_2026-10-30_睡眠增补版'
if __name__=='__main__':package.main()
