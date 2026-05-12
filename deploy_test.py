#!/usr/bin/env python3
"""
部署测试脚本 - 验证项目能否正常运行
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version < (3, 10):
        print("❌ Python版本要求 >= 3.10，当前版本: {}.{}".format(version[0], version[1]))
        return False
    print("✅ Python版本: {}.{}.{}".format(version[0], version[1], version[2]))
    return True

def check_dependencies():
    """检查依赖是否安装"""
    required_packages = [
        'streamlit', 'librosa', 'numpy', 'scipy',
        'pydantic', 'soundfile', 'pytest'
    ]
    
    missing = []
    for pkg in required_packages:
        try:
            __import__(pkg)
            print("✅ {} 已安装".format(pkg))
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print("❌ 缺失依赖: {}".format(", ".join(missing)))
        return False
    return True

def check_directory_structure():
    """检查目录结构"""
    required_dirs = [
        'src/',
        'src/services/',
        'src/models/',
        'data/audio/',
        'data/db/',
        'tests/'
    ]
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print("✅ 目录存在: {}".format(dir_path))
        else:
            print("❌ 目录缺失: {}".format(dir_path))
            os.makedirs(dir_path)
            print("   已创建目录")

def run_unit_tests():
    """运行单元测试"""
    print("\n🚀 运行单元测试...")
    try:
        result = subprocess.run(
            ['python', '-m', 'pytest', 'tests/', '-v', '--tb=short'],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print("✅ 所有测试通过")
            return True
        else:
            print("❌ 测试失败")
            print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
            print(result.stderr[-200:] if len(result.stderr) > 200 else result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("❌ 测试超时")
        return False
    except FileNotFoundError:
        print("❌ pytest未安装")
        return False

def test_streamlit_app():
    """测试Streamlit应用能否启动"""
    print("\n🚀 测试Streamlit应用...")
    try:
        import streamlit as st
        print("✅ Streamlit模块加载成功")
        
        # 测试基本功能
        from src.config import settings
        print("✅ 配置模块加载成功")
        
        from src.services import song_search_service
        print("✅ 服务模块加载成功")
        
        return True
    except Exception as e:
        print("❌ Streamlit应用测试失败: {}".format(e))
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("🎵 AI歌曲创作平台 - 部署测试")
    print("=" * 60)
    
    all_passed = True
    
    # 检查Python版本
    print("\n📋 1. 检查Python版本")
    if not check_python_version():
        all_passed = False
    
    # 检查依赖
    print("\n📋 2. 检查依赖")
    if not check_dependencies():
        all_passed = False
    
    # 检查目录结构
    print("\n📋 3. 检查目录结构")
    check_directory_structure()
    
    # 运行单元测试
    print("\n📋 4. 运行单元测试")
    if not run_unit_tests():
        all_passed = False
    
    # 测试Streamlit应用
    print("\n📋 5. 测试Streamlit应用")
    if not test_streamlit_app():
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过！项目可以正常部署！")
        print("=" * 60)
        print("\n📝 部署命令:")
        print("   开发模式: streamlit run app.py")
        print("   生产模式: streamlit run app.py --server.port=8501")
        return 0
    else:
        print("❌ 部分测试失败，请修复后重新测试")
        return 1

if __name__ == "__main__":
    sys.exit(main())
