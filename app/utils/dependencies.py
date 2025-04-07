import importlib
import subprocess
import sys


def check_and_install_dependencies():
    """检查并安装必要的依赖"""
    required_packages = ["speech_recognition", "pydub", "tomli", "gtts"]

    # 检查每个包是否可以导入
    for package in required_packages:
        try:
            importlib.import_module(package)
        except ImportError:
            print(f"正在安装 {package}...")
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", package], check=True
                )
            except subprocess.CalledProcessError as e:
                print(f"安装 {package} 失败: {str(e)}")
                return False

    return True
