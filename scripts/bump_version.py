import re
from pathlib import Path

VERSION_FILE = Path("src/markitecture/version.py")


def read_version():
    content = VERSION_FILE.read_text()
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    if match:
        return match.group(1)
    raise ValueError("Version not found in version.py")


def bump_version(version: str, part: str = "patch") -> str:
    major, minor, patch = map(int, version.split("."))
    if part == "patch":
        patch += 1
    elif part == "minor":
        minor += 1
        patch = 0
    elif part == "major":
        major += 1
        minor = 0
        patch = 0
    else:
        raise ValueError("Invalid version part. Use 'major', 'minor', or 'patch'.")
    return f"{major}.{minor}.{patch}"


def write_version(new_version: str):
    content = f'__version__ = "{new_version}"\n'
    VERSION_FILE.write_text(content)


if __name__ == "__main__":
    current_version = read_version()
    new_version = bump_version(current_version, part="patch")
    write_version(new_version)
    print(f"Bumped version: {current_version} -> {new_version}")
