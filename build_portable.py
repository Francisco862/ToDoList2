import os
import zipfile
import psutil
import subprocess
from pathlib import Path

APP_NAME = "ToDo PRO"
MAIN_FILE = "main.py"
ICON_PATH = "icons/app.ico"

DIST_DIR = Path("dist")
OUTPUT_ZIP = f"{APP_NAME}-portable.zip"


# 1) ZAMYKANIE DZIAŁAJĄCEGO EXE
def kill_running_exe():
    target = f"{APP_NAME}.exe".lower()
    for proc in psutil.process_iter(["name"]):
        try:
            if proc.info["name"] and proc.info["name"].lower() == target:
                print("⚠ Zamykam działający proces aplikacji...")
                proc.kill()
        except:
            pass


# 2) TWORZENIE ZIP BEZ USUWANIA FOLDERU
def create_zip():
    exe_path = DIST_DIR / f"{APP_NAME}.exe"

    if not exe_path.exists():
        print("❌ EXE nie istnieje.")
        return

    print("📦 Tworzę portable ZIP...")
    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(exe_path, arcname=f"{APP_NAME}.exe")

    print("✔ ZIP gotowy:", OUTPUT_ZIP)


# 3) BUILD EXE
def build_exe():
    print("\n⚙ Buduję EXE...")

    cmd = [
        "pyinstaller",
        "--name", APP_NAME,
        "--onefile",
        "--noconsole",
        "--icon", ICON_PATH,
        MAIN_FILE
    ]

    subprocess.run(cmd, check=True)
    print("✔ Kompilacja zakończona\n")


# MAIN
def main():
    print("=== BUILD PORTABLE ===")

    kill_running_exe()
    build_exe()
    create_zip()

    print("\n🎉 GOTOWE – portable ZIP jest gotowy!\n")


if __name__ == "__main__":
    main()
