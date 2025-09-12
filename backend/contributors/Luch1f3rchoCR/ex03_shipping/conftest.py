import os, sys, subprocess, pathlib

repo_root = pathlib.Path(__file__).resolve().parents[4]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

try:
    import flask  # noqa: F401
except ModuleNotFoundError:
    reqs = pathlib.Path(__file__).resolve().parent / "requirements.txt"
    if reqs.exists():
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(reqs)])
    else:
        subprocess.check_call([sys.executable, "-m", "pip", "install",
                               "Flask==3.0.3", "PyJWT==2.9.0", "marshmallow==3.21.2", "SQLAlchemy==2.0.43"])

os.environ.setdefault("TESTING", "1")
os.environ.setdefault("TEST_DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("RUN_SEEDS_ON_BOOT", "0")
