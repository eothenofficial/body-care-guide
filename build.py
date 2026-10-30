"""Public entry point: python build.py [--check]."""
import sys
from scripts.build_current import main
from scripts.content_model import ContentError

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ContentError, OSError, ValueError) as exc:
        print(f"Build failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
