import os
import subprocess


def run_alembic_upgrade(path):
    print(f"Running alembic upgrade head in {path}")
    subprocess.run(["alembic", "upgrade", "head"], cwd=path, check=True)


if __name__ == "__main__":
    framework_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..'))
    run_alembic_upgrade(framework_dir)

    # Run seeds.py in framework
    seeds_path = os.path.join(framework_dir, "seeds.py")
    if os.path.exists(seeds_path):
        print(f"Running seeds.py in {framework_dir}")
        subprocess.run(["python", seeds_path], check=True)

    app_folder = os.environ.get("APPLICATION_FOLDER")
    if app_folder:
        app_folder_path = os.path.join(
            framework_dir, "..", "contributors", app_folder)
        alembic_ini_path = os.path.join(app_folder_path, "alembic.ini")
        if os.path.exists(alembic_ini_path):
            run_alembic_upgrade(app_folder_path)
        # Run seeds.py in APPLICATION_FOLDER if it exists
        app_seeds_path = os.path.join(app_folder_path, "seeds.py")
        if os.path.exists(app_seeds_path):
            print(f"Running seeds.py in {app_folder_path}")
            subprocess.run(["python", app_seeds_path], check=True)
