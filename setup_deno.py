# Installs Deno for yt-dlp on Streamlit Community Cloud.
# Deno is required for current YouTube JavaScript challenge solving.

import os
import platform
import stat
import urllib.request
import zipfile


DENO_VERSION = "2.9.6"

DENO_DIR = os.path.expanduser("~/.deno")
DENO_PATH = os.path.join(DENO_DIR, "deno")


def install_deno() -> str:
    # Reuse Deno if it is already installed.
    if os.path.isfile(DENO_PATH):
        os.environ["PATH"] = f"{DENO_DIR}:{os.environ.get('PATH', '')}"
        print(f"Deno already installed: {DENO_PATH}")
        return DENO_PATH

    print("Installing Deno...")

    os.makedirs(DENO_DIR, exist_ok=True)

    system = platform.system().lower()
    machine = platform.machine().lower()

    if system != "linux":
        raise RuntimeError(
            f"Unsupported operating system: {system}"
        )

    if machine in ("x86_64", "amd64"):
        architecture = "x86_64"
    elif machine in ("aarch64", "arm64"):
        architecture = "aarch64"
    else:
        raise RuntimeError(
            f"Unsupported CPU architecture: {machine}"
        )

    download_url = (
        f"https://github.com/denoland/deno/releases/download/"
        f"v{DENO_VERSION}/deno-{architecture}-unknown-linux-gnu.zip"
    )

    zip_path = os.path.join(
        DENO_DIR,
        "deno-download.zip"
    )

    print(f"Downloading Deno {DENO_VERSION}...")

    urllib.request.urlretrieve(
        download_url,
        zip_path
    )

    print("Extracting Deno...")

    with zipfile.ZipFile(zip_path, "r") as zip_file:
        zip_file.extractall(DENO_DIR)

    if os.path.exists(zip_path):
        os.remove(zip_path)

    if not os.path.isfile(DENO_PATH):
        raise RuntimeError(
            f"Deno installation failed: {DENO_PATH}"
        )

    # Make Deno executable.
    permissions = os.stat(DENO_PATH).st_mode

    os.chmod(
        DENO_PATH,
        permissions
        | stat.S_IXUSR
        | stat.S_IXGRP
        | stat.S_IXOTH
    )

    # Make Deno available to yt-dlp.
    os.environ["PATH"] = (
        f"{DENO_DIR}:{os.environ.get('PATH', '')}"
    )

    print(f"Deno installed successfully: {DENO_PATH}")

    # Verify installation.
    result = os.popen(
        f'"{DENO_PATH}" --version'
    ).read()

    print(f"Deno version:\n{result}")

    return DENO_PATH