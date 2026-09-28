# Downloads Deno if it is not already installed.
# Deno is required by yt-dlp for current YouTube extraction.

import os
import platform
import stat
import tarfile
import urllib.request


DENO_VERSION = "2.6.0"
DENO_DIR = os.path.expanduser("~/.deno")
DENO_PATH = os.path.join(DENO_DIR, "deno")


def install_deno():
    # Skip installation if Deno already exists.
    if os.path.exists(DENO_PATH):
        print("Deno already installed.")
        return DENO_PATH

    print("Installing Deno...")

    os.makedirs(DENO_DIR, exist_ok=True)

    system = platform.system().lower()
    machine = platform.machine().lower()

    if system != "linux":
        raise RuntimeError("This installer is intended for Linux deployment.")

    if machine in ("x86_64", "amd64"):
        architecture = "x86_64"
    elif machine in ("aarch64", "arm64"):
        architecture = "aarch64"
    else:
        raise RuntimeError(f"Unsupported architecture: {machine}")

    url = (
        f"https://github.com/denoland/deno/releases/download/"
        f"v{DENO_VERSION}/deno-{architecture}-unknown-linux-gnu.zip"
    )

    zip_path = os.path.join(DENO_DIR, "deno.zip")

    print("Downloading Deno...")
    urllib.request.urlretrieve(url, zip_path)

    import zipfile

    with zipfile.ZipFile(zip_path, "r") as zip_file:
        zip_file.extractall(DENO_DIR)

    os.remove(zip_path)

    # Make Deno executable.
    current_permissions = os.stat(DENO_PATH).st_mode
    os.chmod(
        DENO_PATH,
        current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    )

    print(f"Deno installed: {DENO_PATH}")

    return DENO_PATH


if __name__ == "__main__":
    install_deno()