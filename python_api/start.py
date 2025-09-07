#!/usr/bin/env python3
"""
Python 后端启动脚本
用于开发环境启动 FastAPI 服务器
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """检查 Python 版本"""
    if sys.version_info < (3, 8):
        print("错误: 需要 Python 3.8 或更高版本")
        sys.exit(1)
    print(f"Python 版本: {sys.version}")

def install_dependencies():
    """安装依赖"""
    requirements_file = Path(__file__).parent / "requirements.txt"
    if requirements_file.exists():
        print("正在安装 Python 依赖...")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], check=True)
            print("依赖安装完成")
        except subprocess.CalledProcessError as e:
            print(f"依赖安装失败: {e}")
            sys.exit(1)
    else:
        print("未找到 requirements.txt 文件")

def setup_environment():
    """设置环境变量"""
    env_file = Path(__file__).parent / ".env"
    env_example_file = Path(__file__).parent / ".env.example"
    
    if not env_file.exists() and env_example_file.exists():
        print("创建 .env 文件...")
        import shutil
        shutil.copy(env_example_file, env_file)
        print("请编辑 .env 文件配置相关参数")

def start_server():
    """启动服务器"""
    print("启动 FastAPI 服务器...")
    os.chdir(Path(__file__).parent)
    
    # 设置环境变量
    os.environ.setdefault("PORT", "3001")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0",
            "--port", os.environ.get("PORT", "3001"),
            "--reload",
            "--log-level", "info"
        ], check=True)
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except subprocess.CalledProcessError as e:
        print(f"服务器启动失败: {e}")
        sys.exit(1)

def main():
    """主函数"""
    print("=== Let's Go Python 后端启动器 ===")
    
    # 检查 Python 版本
    check_python_version()
    
    # 安装依赖
    if "--install" in sys.argv or "--setup" in sys.argv:
        install_dependencies()
    
    # 设置环境
    setup_environment()
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main()