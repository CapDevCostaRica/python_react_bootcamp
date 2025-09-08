import os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("TESTING", "1")
os.environ.setdefault("RUN_SEEDS_ON_BOOT", "0")
os.environ.setdefault("TEST_DATABASE_URL", "sqlite:///:memory:")