import os
from pathlib import Path
import shutil
import subprocess
import re
import sys
from typing import List
import threading


main_process = None


def copy_file(source_path, destination_path):
    source_path = Path(source_path)
    dest_path = Path(destination_path)

    # Create parent directories
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    # Copy the file
    shutil.copy2(source_path, dest_path)

    return dest_path


def copy_directory(source, destination, ignore_patterns=None):
    def ignore_function(directory, files):
        ignored = []
        if ignore_patterns:
            for pattern in ignore_patterns:
                ignored.extend([f for f in files if pattern in f])
        return ignored

    try:
        if ignore_patterns:
            result = shutil.copytree(
                source, destination, ignore=ignore_function, dirs_exist_ok=True
            )
        else:
            result = shutil.copytree(source, destination, dirs_exist_ok=True)

        return result
    except Exception as e:
        print(f"Copy failed: {e}")


def get_new_contributor_dir():
    def extract_app_directory(file_path):
        pattern = r"backend/contributors/([A-Za-z0-9]+\/[A-Za-z0-9]+)/main.py"
        m = re.match(pattern=pattern, string=file_path)
        if m:
            return m.group(1)

    try:
        result = subprocess.run(
            [
                "git",
                "diff",
                "--name-only",
                "main..HEAD",
                "--",
                "./backend/contributors",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        directories = {
            extract_app_directory(line)
            for line in result.stdout.strip().split("\n")
            if line.strip() and "contributors" in line
        }

        directories.remove(None)
        return directories.pop()

    except Exception as e:
        print(f"Error: {e}")
        return None


def quick_venv_setup(folder_path, requirements_files: List[str] = [], dry_run=False):
    venv_path = Path(folder_path)
    python_exe = venv_path / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if dry_run:
        return python_exe
    subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
    subprocess.run(
        [str(python_exe), "-m", "pip", "install", "--upgrade", "pip"], check=True
    )

    if requirements_files:
        for rq in requirements_files:
            subprocess.run(
                [str(python_exe), "-m", "pip", "install", "-r", rq], check=True
            )

    return str(python_exe)


def replace_in_file(file_path, pattern, replacement):
    try:
        with open(file_path, "r") as file:
            content = file.read()

        updated_content = re.sub(pattern, replacement, content)

        with open(file_path, "w") as file:
            file.write(updated_content)

    except Exception as e:
        print(f"❌ Error updating file: {e}")
        return False


def setup_env(dry_run: bool = False):
    application_folder = get_new_contributor_dir()
    app_requirements = "./tests/tmp/app/requirements.txt"
    contributor_app_requirements = (
        f"./tests/tmp/app/contributors/{application_folder}/requirements.txt"
    )
    if not dry_run:
        try:
            shutil.rmtree("./tests/tmp")
        except FileNotFoundError:
            print("path ./tests/tmp does not exists")
        copy_file("./backend/requirements.txt", app_requirements)
        copy_file(
            f"./backend/contributors/{application_folder}/requirements.txt",
            contributor_app_requirements,
        )
        copy_directory(
            "./backend",
            "./tests/tmp/app",
            ignore_patterns=[".git", "__pycache__", ".pyc"],
        )
    python_exe = quick_venv_setup(
        "./tests/tmp/app/.venv",
        [app_requirements, contributor_app_requirements],
        dry_run=dry_run,
    )
    local_db = "database.db"
    db_replacement = f'DATABASE_URL = "sqlite:///{local_db}"'
    pattern = r'DATABASE_URL\s*=\s*f?"postgresql\+psycopg://[^"]*"'
    replace_in_file("./tests/tmp/app/framework/database.py", pattern, db_replacement.replace(local_db, "tests/tmp/database.db"))
    replace_in_file(
        "./tests/tmp/app/framework/scripts/reset_db.py", pattern, db_replacement
    )
    replace_in_file("./tests/tmp/app/framework/alembic/env.py", pattern, db_replacement)
    return application_folder, python_exe


def run(app_directory, python_exe):
    os.environ["FLASK_APP"] = f"./tests/tmp/app/contributors/{app_directory}/main.py"
    os.environ["FLASK_ENV"] = "development"
    subprocess.run(
        [
            "./app/.venv/bin/alembic",
            "-c",
            "./app/framework/alembic.ini",
            "upgrade",
            "head",
        ],
        check=True,
        cwd="./tests/tmp/",
    )
    global main_process
    main_process = subprocess.run([python_exe, os.environ.get("FLASK_APP")], check=True)


def quick_kill_python_on_port(port=4000):
    result = subprocess.run(
        ["lsof", "-ti", f":{port}"], capture_output=True, text=True, check=True
    )
    if result.stdout.strip():
        pids = result.stdout.strip().split("\n")
        print(f"🔍 Found {len(pids)} process(es) on port {port}: {pids}")
        for pid in pids:
            try:
                subprocess.run(["kill", "-TERM", pid], check=True)
                try:
                    subprocess.run(["kill", "-0", pid], check=True, capture_output=True)
                    subprocess.run(["kill", "-KILL", pid], check=True)
                    print(f"⚠️  Force killed PID {pid}")
                except subprocess.CalledProcessError:
                    print(f"✅ PID {pid} terminated gracefully")
            except subprocess.CalledProcessError:
                print(f"❌ Could not process PID {pid}")
                continue
    else:
        print(f"ℹ️  No processes found on port {port}")


def setup():
    app_directoy, python_exe = setup_env(dry_run=False)
    run(app_directoy, python_exe)


def teardown():
    try:
        print("Cleaning up Flask process...")
        if main_process:
            main_process.terminate()
            try:
                main_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                main_process.kill()
    finally:
        quick_kill_python_on_port(4000)


if __name__ == "__main__":
    try:
        thread = threading.Thread(target=setup, daemon=True)
        thread.start()
        thread.join(timeout=30)
        print("Main Flask thread started")
        try:
            print("Running Python tests:")
            subprocess.run(
                ["./tests/tmp/app/.venv/bin/pytest", ".", "-vv", "-s", "--tb=short"],
                check=True,
            )
        except Exception as pytest_exception:
            f"pytest found exception {pytest_exception=}"
    finally:
        print("Tear down")
        teardown()
