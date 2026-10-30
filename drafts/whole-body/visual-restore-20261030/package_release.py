"""Package the compact visual edition without replacing dated previous deliveries."""
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
spec=importlib.util.spec_from_file_location('visual_packager',HERE.parent/'revision-20261030/package_release.py')
package=importlib.util.module_from_spec(spec);spec.loader.exec_module(package)
package.HERE=HERE;package.ROOT=ROOT
package.TARGET=ROOT/'.draft-preview/visual-restore-20261030';package.DIST=package.TARGET/'dist'
package.DEST=ROOT.parent/'身体护理指南_2026-10-30_简洁视觉版'
if __name__=='__main__':
    spec=importlib.util.spec_from_file_location('visual_builder',HERE/'build_release.py')
    builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
    builder.previous().verify_reviews()
    package.main()
