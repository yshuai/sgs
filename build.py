import os
import subprocess
import shutil
from pathlib import Path

def build_exe():
    # 确保构建目录存在
    build_dir = Path("build")
    dist_dir = Path("dist")
    
    # 清理之前的构建
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    # 使用 rye 环境中的 PyInstaller
    pyinstaller_cmd = [
        "pyinstaller",
        "--noconfirm",
        "--clean",
        "--windowed",  # 不显示控制台窗口
        "--name=SGS断线器",  # exe的名称
        "--add-data=src/sgs/config.json;src/sgs",  # 添加配置文件
        "--icon=assets/icon.ico",  # 如果你有图标的话
        "src/sgs/disconnect_manager.py"  # 入口文件
    ]
    
    subprocess.run(pyinstaller_cmd)
    
    print("构建完成！exe文件位于 dist/SGS断线器 目录下")

if __name__ == "__main__":
    build_exe() 