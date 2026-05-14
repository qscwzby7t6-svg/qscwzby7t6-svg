# 📱 Termux 完整版部署教程

> **适用设备**: Android 手机/平板 + Termux 应用  
> **Termux版本**: Termux 0.118+  
> **系统版本**: Android 7.0+（推荐 Android 10+）  
> **作者**: AI音乐创作平台开发团队

---

## 📋 教程特点

- ✅ **逐条命令**：每个步骤都有明确命令
- ✅ **验证方法**：每步都提供验证命令
- ✅ **备用方案**：每个步骤都有备选方案
- ✅ **Termux优化**：针对Termux特殊环境优化
- ✅ **存储说明**：解决Termux存储权限问题

---

## 📝 目录

1. [准备工作](#1-准备工作)
2. [基础配置](#2-基础配置)
3. [安装系统依赖](#3-安装系统依赖)
4. [克隆项目](#4-克隆项目)
5. [创建Python环境](#5-创建python环境)
6. [安装Python依赖](#6-安装python依赖)
7. [配置应用](#7-配置应用)
8. [运行测试](#8-运行测试)
9. [启动应用](#9-启动应用)
10. [常见问题](#10-常见问题)

---

## 1. 准备工作

### 1.1 安装 Termux

**下载渠道**:

| 渠道 | 地址 | 说明 |
|------|------|------|
| F-Droid | https://f-droid.org/packages/com.termux/ | 推荐，最新稳定版 |
| GitHub | https://github.com/termux/termux-app/releases | 需要手动安装APK |

**安装步骤**:
1. 从 F-Droid 下载 Termux APK
2. 允许安装来自未知来源的应用
3. 点击安装 Termux
4. 等待安装完成

**✅ 验证方法**:
```bash
# 打开Termux应用，查看是否正常启动
# 如果看到命令行提示符 ($)，说明安装成功
```

---

## 2. 基础配置

### 2.1 更新 Termux 源（必须！）

**⚠️ 重要**: 首次使用必须更换国内镜像源，否则下载极慢

```bash
# 查看当前源（可跳过）
pkg show termux-mirrors 2>/dev/null || echo "需要配置源"

# 方案A: 使用清华源（推荐）
pkg update
pkg install vim curl wget git tree -y
termux-change-repo

# 方案B: 如果上面的命令失败，手动配置源
vim $PREFIX/etc/apt/sources.list
```

**手动配置源的步骤**:
1. 执行 `vim $PREFIX/etc/apt/sources.list`
2. 按 `i` 进入编辑模式
3. 删除原有内容，添加以下内容：
   ```
   deb https://mirrors.tuna.tsinghua.edu.cn/termux/apt/termux-main stable main
   ```
4. 按 `Esc`，输入 `:wq` 保存退出

**✅ 验证方法**:
```bash
pkg update
# 如果出现 "All packages are up to date" 或正常更新列表，说明源配置成功
```

**🔄 备用方案**（清华源不可用时）:
```bash
# 使用华为云镜像
echo 'deb https://mirrors.huaweicloud.com/repository/termux/termux-main stable main' > $PREFIX/etc/apt/sources.list

# 或使用北外镜像
echo 'deb https://mirrors.bfsu.edu.cn/termux/termux-main stable main' > $PREFIX/etc/apt/sources.list

# 重新更新
pkg update
```

---

### 2.2 安装基础工具

```bash
# 安装必需的基础工具
pkg install vim curl wget git tree nano -y
```

**✅ 验证方法**:
```bash
# 逐个检查命令是否存在
which vim && echo "vim ✅"
which curl && echo "curl ✅"
which wget && echo "wget ✅"
which git && echo "git ✅"
which tree && echo "tree ✅"
which nano && echo "nano ✅"
```

**🔄 备用方案**（某个工具安装失败时）:
```bash
# 单独安装
pkg install vim -y
pkg install curl -y
pkg install wget -y
pkg install git -y

# 如果 pkg 安装失败，使用 Termux 内置工具
# Termux 自带 curl，可以直接使用
```

---

### 2.3 配置存储权限

**⚠️ 重要**: Termux 需要存储权限才能访问手机文件

```bash
# 方法A: 使用 Termux API（推荐）
pkg install termux-api -y

# 授予存储权限
termux-setup-storage

# 在弹出的对话框中选择 "允许"

# 方法B: 如果方法A失败，手动创建目录链接
mkdir -p ~/storage/shared
ln -sf /sdcard ~/storage/internal
```

**✅ 验证方法**:
```bash
# 检查 storage 目录是否创建
ls -la ~/storage/

# 应该看到以下目录：
# dcim/  downloads/  movies/  music/  pictures/  shared/
```

**🔄 备用方案**（termux-setup-storage 失败时）:
```bash
# 使用 ADB 授予权限（需要在电脑上操作）
adb shell pm grant com.termux android.permission.WRITE_EXTERNAL_STORAGE
adb shell pm grant com.termux android.permission.READ_EXTERNAL_STORAGE

# 或使用第三方工具 Grant Permissions for Termux
```

---

### 2.4 配置 Git

```bash
# 配置 Git 用户信息（必须填写）
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 配置 Git 推送方式
git config --global credential.helper store

# 启用颜色输出
git config --global color.ui auto
```

**✅ 验证方法**:
```bash
git config --list
# 应该看到 user.name 和 user.email 配置
```

---

## 3. 安装系统依赖

### 3.1 安装编译工具链

```bash
# 安装 C/C++ 编译器和其他构建工具
pkg install build-essential clang cmake make -y
```

**✅ 验证方法**:
```bash
gcc --version
g++ --version
make --version
cmake --version
```

**预期输出示例**:
```
gcc (GCC) 11.x.x
g++ (GCC) 11.x.x
GNU Make 4.x
cmake version 3.x.x
```

**🔄 备用方案**（编译工具安装失败时）:
```bash
# 单独安装各个组件
pkg install gcc -y
pkg install g++ -y
pkg install make -y
pkg install cmake -y

# 如果存储空间不足，跳过 cmake（后续可使用 pip 安装）
pkg install build-essential -y
```

---

### 3.2 安装 Python 环境

**⚠️ 重要**: Termux 有多个 Python 版本，推荐使用 Python 3.11

```bash
# 安装 Python 3.11（推荐版本）
pkg install python python3.11 -y

# 安装 pip
pkg install python-pip -y
```

**✅ 验证方法**:
```bash
python --version
python3 --version
pip --version
pip3 --version
```

**预期输出**:
```
Python 3.11.x
Python 3.11.x
pip 23.x from /data/data/com.termux/... (python 3.11)
```

**🔄 备用方案**（Python 安装失败时）:
```bash
# 方案A: 只安装 python（不指定版本）
pkg install python -y

# 方案B: 使用 python 3.10
pkg install python3.10 -y

# 方案C: 如果 pip 有问题，重新安装
pkg reinstall python-pip
```

---

### 3.3 安装音频处理依赖

```bash
# 安装音频处理必需库
pkg install libsndfile ffmpeg -y

# 安装音频处理开发库（可选但推荐）
pkg install libsndfile-dev -y
```

**✅ 验证方法**:
```bash
# 检查 ffmpeg
ffmpeg -version

# 检查 libsndfile
pkg show libsndfile

# 检查库文件是否存在
ls $PREFIX/lib/libsndfile*
```

**预期输出**:
```
ffmpeg version 5.x ... Copyright (c) 2000-2023 the FFmpeg developers
Package: libsndfile
Version: 1.1.x
```

**🔄 备用方案**（音频库安装失败时）:
```bash
# 方案A: 只安装 ffmpeg（最重要的音频处理工具）
pkg install ffmpeg -y

# 方案B: 如果 libsndfile 安装失败，使用 pip 安装
pip install soundfile

# 方案C: 检查是否有空间问题
df -h
# 如果 /data 分区空间不足，清理
pkg clean
```

---

### 3.4 安装科学计算库（可选）

```bash
# 安装 BLAS/LAPACK（加速科学计算）
pkg install liblapack libblas -y
```

**✅ 验证方法**:
```bash
# 检查库文件
ls $PREFIX/lib/liblapack*
ls $PREFIX/lib/libblas*
```

**🔄 备用方案**（可选，跳过不影响基本功能）:
```bash
# 如果存储空间不足，可以跳过此步骤
# pip 安装 scipy 时会自动下载预编译版本
echo "此步骤可选，已跳过"
```

---

### 3.5 安装其他依赖

```bash
# 安装 unzip（解压用）
pkg install unzip zip -y

# 安装 OpenSSL（网络请求用）
pkg install openssl openssl-tool -y

# 安装 libxml（某些Python包需要）
pkg install libxml2 libxslt -y
```

**✅ 验证方法**:
```bash
unzip --version
zip --version
openssl version
```

**🔄 备用方案**:
```bash
# 逐个安装
pkg install unzip -y
pkg install openssl -y
```

---

## 4. 克隆项目

### 4.1 创建项目目录

```bash
# 创建项目目录
mkdir -p ~/projects
cd ~/projects
```

**✅ 验证方法**:
```bash
# 检查目录是否存在
ls -la ~/projects/
pwd  # 应该显示 /data/data/com.termux/files/home/projects
```

---

### 4.2 克隆 GitHub 项目

```bash
# 主方案：克隆项目
cd ~/projects
git clone https://github.com/qscwzby7t6-svg/qscwzby7t6-svg.git
cd qscwzby7t6-svg
```

**✅ 验证方法**:
```bash
# 检查目录内容
ls -la

# 应该看到以下文件和目录：
# app.py  requirements.txt  deploy_test.py  src/  tests/  data/  docs/
```

**🔄 备用方案**（网络问题）:

```bash
# 方案A: 使用代理（如果有代理）
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890
git clone https://github.com/qscwzby7t6-svg/qscwzby7t6-svg.git

# 方案B: 使用镜像站点
git clone https://ghproxy.com/https://github.com/qscwzby7t6-svg/qscwzby7t6-svg.git

# 方案C: 使用加速镜像
git clone https://hub.fastgit.xyz/qscwzby7t6-svg/qscwzby7t6-svg.git

# 方案D: 手动下载 ZIP 包
# 1. 在浏览器打开 https://github.com/qscwzby7t6-svg/qscwzby7t6-svg
# 2. 点击 "Code" -> "Download ZIP"
# 3. 将 ZIP 文件移动到 Termux 的 ~/projects 目录
# 4. 解压
cd ~/projects
unzip qscwzby7t6-svg-main.zip
mv qscwzby7t6-svg-main qscwzby7t6-svg
cd qscwzby7t6-svg
```

---

### 4.3 检查克隆结果

```bash
# 查看项目结构
tree -L 2

# 或使用 ls
ls -la
```

**✅ 验证方法**:
```bash
# 确认关键文件存在
test -f app.py && echo "app.py ✅"
test -f requirements.txt && echo "requirements.txt ✅"
test -f deploy_test.py && echo "deploy_test.py ✅"
test -d src && echo "src/ ✅"
test -d tests && echo "tests/ ✅"
```

---

## 5. 创建Python环境

### 5.1 升级 pip

```bash
# 进入项目目录
cd ~/projects/qscwzby7t6-svg

# 升级 pip（强烈推荐）
pip install --upgrade pip
```

**✅ 验证方法**:
```bash
pip --version
# 应该显示 pip 23.x 或更高版本
```

**🔄 备用方案**（pip 升级失败时）:
```bash
# 使用国内镜像
pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用阿里云镜像
pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/
```

---

### 5.2 配置 pip 镜像（强烈推荐！）

```bash
# 设置 pip 使用清华镜像（加速下载）
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 验证配置
pip config list
```

**✅ 验证方法**:
```bash
pip config list
# 应该看到：
# global.index-url='https://pypi.tuna.tsinghua.edu.cn/simple'
```

**🔄 备用方案**（清华源不可用时）:
```bash
# 方案A: 使用阿里云镜像
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/

# 方案B: 使用腾讯云镜像
pip config set global.index-url https://mirrors.cloud.tencent.com/pypi/simple

# 方案C: 使用华为云镜像
pip config set global.index-url https://repo.huaweicloud.com/repository/pypi/simple

# 方案D: 临时使用镜像
pip install xxx -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

### 5.3 安装基础 Python 包（必须！）

**⚠️ 重要**: 先安装 numpy 和 scipy，避免后续从源码编译

```bash
# 安装 numpy（科学计算基础库）
pip install numpy==1.24.0

# 安装 scipy（科学计算库）
pip install scipy==1.11.0
```

**✅ 验证方法**:
```bash
python -c "import numpy; print(f'numpy {numpy.__version__}')"
python -c "import scipy; print(f'scipy {scipy.__version__}')"
```

**预期输出**:
```
numpy 1.24.0
scipy 1.11.0
```

**🔄 备用方案**（安装失败时）:
```bash
# 方案A: 增加超时时间
pip install numpy==1.24.0 --default-timeout=300

# 方案B: 使用镜像
pip install numpy==1.24.0 -i https://pypi.tuna.tsinghua.edu.cn/simple

# 方案C: 尝试不指定版本（安装最新兼容版本）
pip install "numpy>=1.24.0,<2.0.0"

# 方案D: 如果编译失败，使用预编译版本
pip install numpy --only-binary=:all:
```

---

### 5.4 安装 PyTorch（重要但可选）

**⚠️ 注意**: PyTorch 体积较大（500MB+），手机存储空间有限时可跳过

```bash
# 方案A: 安装 PyTorch CPU 版本（推荐）
pip install torch==2.0.0 torchaudio==2.0.0 --index-url https://download.pytorch.org/whl/cpu
```

**✅ 验证方法**:
```bash
python -c "import torch; print(f'torch {torch.__version__}')"
```

**预期输出**:
```
torch 2.0.0
```

**🔄 备用方案**（PyTorch 安装问题）:

```bash
# 方案A: 使用镜像安装
pip install torch==2.0.0 -i https://pypi.tuna.tsinghua.edu.cn/simple --extra-index-url https://download.pytorch.org/whl/cpu

# 方案B: 安装 CPU 优化版本
pip install torch --index-url https://download.pytorch.org/whl/cpu

# 方案C: 如果下载太慢，跳过 PyTorch（系统会使用纯 NumPy 实现）
echo "跳过 PyTorch 安装，使用纯 NumPy 实现"

# 方案D: 安装最小版 PyTorch
pip install torch==1.13.0 --index-url https://download.pytorch.org/whl/cpu
```

---

### 5.5 安装其他 Python 依赖

```bash
# 安装 requirements.txt 中的依赖
pip install -r requirements.txt
```

**✅ 验证方法**:
```bash
# 检查关键包是否安装成功
python -c "import librosa; print(f'librosa {librosa.__version__}')"
python -c "import soundfile; print(f'soundfile ✅')"
python -c "import streamlit; print(f'streamlit {streamlit.__version__}')"
python -c "import fastapi; print(f'fastapi {fastapi.__version__}')"
```

**预期输出**:
```
librosa 0.10.0
soundfile ✅
streamlit 1.28.0
fastapi 0.104.0
```

**🔄 备用方案**（部分依赖安装失败时）:

```bash
# 方案A: 逐个安装，跳过失败的包
pip install librosa==0.10.0
pip install soundfile==0.12.1
pip install pydub==0.25.1
pip install matplotlib==3.7.0
pip install streamlit==1.28.0
pip install fastapi==0.104.0
pip install uvicorn==0.24.0

# 方案B: 使用 --no-deps 安装（跳过依赖检查）
pip install librosa --no-deps

# 方案C: 强制重新安装
pip install -r requirements.txt --force-reinstall

# 方案D: 只安装核心依赖（跳过可选依赖）
pip install streamlit fastapi librosa soundfile pydub numpy scipy
```

---

### 5.6 验证所有依赖

```bash
# 综合验证脚本
python -c "
import numpy
import scipy
import soundfile
import librosa
print('✅ 核心依赖全部安装成功！')
print(f'numpy: {numpy.__version__}')
print(f'scipy: {scipy.__version__}')
try:
    import torch
    print(f'torch: {torch.__version__}')
except ImportError:
    print('torch: 未安装（可选）')
"
```

**✅ 验证方法**:
```bash
# 运行验证脚本，应该看到所有包版本信息
```

---

## 6. 配置应用

### 6.1 创建数据目录

```bash
# 创建数据目录
mkdir -p data/audio data/db

# 设置权限
chmod -R 755 data/

# 查看目录
ls -la data/
```

**✅ 验证方法**:
```bash
# 检查目录是否存在且可写
test -d data/audio && echo "data/audio ✅"
test -d data/db && echo "data/db ✅"
test -w data/audio && echo "data/audio 可写 ✅"
```

---

### 6.2 配置环境变量（可选）

```bash
# 设置 Python 线程数（避免内存不足）
export OMP_NUM_THREADS=2
export MKL_NUM_THREADS=2
export NUMEXPR_NUM_THREADS=2

# 将环境变量写入 .bashrc（永久生效）
echo 'export OMP_NUM_THREADS=2' >> ~/.bashrc
echo 'export MKL_NUM_THREADS=2' >> ~/.bashrc
echo 'export NUMEXPR_NUM_THREADS=2' >> ~/.bashrc

# 重新加载配置
source ~/.bashrc
```

**✅ 验证方法**:
```bash
echo $OMP_NUM_THREADS
# 应该显示 2
```

---

### 6.3 配置 Streamlit（可选）

```bash
# 创建 Streamlit 配置目录
mkdir -p ~/.streamlit

# 创建配置文件
cat > ~/.streamlit/config.toml << 'EOF'
[server]
port = 8501
headless = true
enableCORS = false
enableXsrfProtection = true

[browser]
serverAddress = "localhost"

[theme]
primaryColor = "#0078D4"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
EOF
```

**✅ 验证方法**:
```bash
cat ~/.streamlit/config.toml
```

---

## 7. 运行测试

### 7.1 运行部署测试脚本

```bash
# 进入项目目录
cd ~/projects/qscwzby7t6-svg

# 运行部署测试
python deploy_test.py
```

**✅ 验证方法**:
```bash
# 检查脚本退出码
echo $?
# 0 表示成功
```

**预期输出**:
```
============================================================
🎵 AI歌曲创作平台 - 部署测试
============================================================

📋 1. 检查Python版本
✅ Python版本: 3.11.x

📋 2. 检查依赖
✅ numpy 已安装
✅ scipy 已安装
✅ torch 已安装（可选）
✅ librosa 已安装
✅ soundfile 已安装
...

📋 3. 检查目录结构
✅ 目录存在: data/audio/
✅ 目录存在: data/db/

📋 4. 检查配置文件
✅ 配置文件存在

============================================================
🎉 所有检查通过！项目可以正常部署！
============================================================
```

**🔄 备用方案**（测试失败时）:

```bash
# 方案A: 查看具体错误
python deploy_test.py 2>&1 | head -100

# 方案B: 手动检查每个依赖
python -c "import numpy"
python -c "import scipy"
python -c "import librosa"
python -c "import soundfile"
python -c "import streamlit"

# 方案C: 重新安装失败的依赖
pip install numpy scipy librosa soundfile streamlit --force-reinstall
```

---

### 7.2 运行单元测试（可选）

```bash
# 运行所有单元测试
cd ~/projects/qscwzby7t6-svg
python -m pytest tests/ -v
```

**✅ 验证方法**:
```bash
# 检查测试结果
echo $?
# 0 表示所有测试通过
```

---

## 8. 启动应用

### 8.1 前台运行（调试模式）

```bash
# 进入项目目录
cd ~/projects/qscwzby7t6-svg

# 启动应用
python -m streamlit run app.py --server.port=8501
```

**✅ 验证方法**:
```bash
# 应该看到类似输出：
#  You can now view your Streamlit app in your browser.
#  Local URL: http://localhost:8501
#  Network URL: http://192.168.x.x:8501
```

**访问应用**:
1. 在 Termux 中按 `Ctrl+点击` 本地链接
2. 或在浏览器中打开 `http://localhost:8501`

---

### 8.2 后台运行（推荐）

```bash
# 后台运行应用
cd ~/projects/qscwzby7t6-svg
nohup python -m streamlit run app.py --server.port=8501 --server.headless=true > app.log 2>&1 &

# 查看进程是否启动
ps aux | grep streamlit
```

**✅ 验证方法**:
```bash
# 检查进程
ps aux | grep streamlit
# 应该看到 python 进程

# 查看日志
tail -f app.log
```

---

### 8.3 使用 tmux 运行（推荐，Termux 专属）

**⚠️ 推荐**: Termux 推荐使用 tmux，可以随时查看和控制会话

```bash
# 安装 tmux
pkg install tmux -y

# 启动 tmux 会话
tmux new -s ai-song-creator

# 在 tmux 会话中运行应用
cd ~/projects/qscwzby7t6-svg
python -m streamlit run app.py --server.port=8501

# 按 Ctrl+B 然后按 D 退出 tmux 会话（应用继续运行）

# 重新进入 tmux 会话
tmux attach -t ai-song-creator
```

**✅ 验证方法**:
```bash
# 查看 tmux 会话
tmux ls

# 查看应用日志
tmux capture-pane -t ai-song-creator -p | tail -20
```

**🔄 备用方案**（tmux 安装失败时）:
```bash
# 使用 screen（如果可用）
pkg install screen -y
screen -S ai-song
python -m streamlit run app.py --server.port=8501
# Ctrl+A 然后按 D 退出
```

---

## 9. 访问应用

### 9.1 本地访问

```bash
# 在 Termux 内置浏览器打开
am start -a android.intent.action.VIEW -d http://localhost:8501

# 或使用 termux-open
termux-open-url http://localhost:8501
```

---

### 9.2 局域网访问（其他设备）

```bash
# 查看本机 IP 地址
ifconfig | grep inet

# 应该看到类似输出：
# inet addr:192.168.1.100

# 在其他设备的浏览器中打开
# http://192.168.1.100:8501
```

**✅ 验证方法**:
```bash
# 检查端口是否监听
netstat -tlnp | grep 8501
# 或
ss -tlnp | grep 8501
```

---

## 10. 常见问题

### Q1: pkg install 提示 " Repository橱柜不存在"

**原因**: Termux 源配置错误或过期

**解决方案**:
```bash
# 重新配置源
vim $PREFIX/etc/apt/sources.list
# 确保文件内容为：
deb https://mirrors.tuna.tsinghua.edu.cn/termux/apt/termux-main stable main

# 更新
pkg update
```

---

### Q2: pip install 一直超时

**原因**: 网络问题或 PyPI 被墙

**解决方案**:
```bash
# 设置镜像
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 增加超时时间
pip install xxx --default-timeout=300

# 使用国内镜像
pip install xxx -i https://mirrors.aliyun.com/pypi/simple/
```

---

### Q3: 存储空间不足

**原因**: 手机存储空间不够

**解决方案**:
```bash
# 查看存储使用
df -h

# 清理 Termux 缓存
pkg clean

# 清理 pip 缓存
pip cache purge

# 清理 apt 缓存
apt clean

# 删除不需要的包
pkg uninstall unused-package
```

---

### Q4: 内存不足，安装被杀死

**原因**: 手机 RAM 不足

**解决方案**:
```bash
# 关闭其他应用释放内存

# 创建 swap（如果有空间）
dd if=/dev/zero of=/data/data/com.termux/files/data/swaptfile bs=1M count=512
mkswap /data/data/com.termux/files/data/swaptfile
swapon /data/data/com.termux/files/data/swaptfile

# 使用较小的线程数
export OMP_NUM_THREADS=1
```

---

### Q5: libsndfile-dev 包找不到

**原因**: Termux 包名不同

**解决方案**:
```bash
# Termux 中使用 libsndfile
pkg install libsndfile -y

# libsndfile-dev 在 Termux 中不存在
```

---

### Q6: ffmpeg 安装失败

**原因**: 存储空间或网络问题

**解决方案**:
```bash
# 清理后重试
pkg clean
pkg update
pkg install ffmpeg -y

# 如果还是失败，使用 Termux API 的音频处理
pkg install termux-api -y
pkg install sox -y  # 替代 ffmpeg 的音频处理工具
```

---

### Q7: Termux 权限被撤销

**原因**: 手机省电策略或手动撤销

**解决方案**:
```bash
# 重新授予存储权限
termux-setup-storage

# 如果权限对话框不出现
# 在手机设置中手动找到 Termux -> 权限 -> 允许所有权限

# 或使用 ADB 授予权限
adb shell pm grant com.termux android.permission.WRITE_EXTERNAL_STORAGE
```

---

### Q8: 应用启动后无法访问

**原因**: 防火墙或网络配置

**解决方案**:
```bash
# 检查端口
ss -tlnp | grep 8501

# 如果端口正常，检查防火墙
# Android 防火墙通常不会阻止本地应用

# 尝试使用 localhost 访问
curl http://localhost:8501

# 如果是网络访问，确保在同一局域网
ping <手机IP>
```

---

## 📞 技术支持

如有问题，欢迎提交 Issue：  
https://github.com/qscwzby7t6-svg/qscwzby7t6-svg/issues

---

## 📋 快速命令清单

```bash
# 一键安装所有系统依赖（从零开始）
pkg update && pkg install git vim curl wget build-essential clang cmake make python python-pip libsndfile ffmpeg unzip openssl -y

# 一键安装 Python 依赖
pip install --upgrade pip
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip install numpy==1.24.0 scipy==1.11.0 torch==2.0.0 --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt

# 一键克隆并配置项目
cd ~/projects
git clone https://github.com/qscwzby7t6-svg/qscwzby7t6-svg.git
cd qscwzby7t6-svg
mkdir -p data/audio data/db

# 一键启动
python -m streamlit run app.py --server.port=8501
```

---

**版本**: v1.0  
**更新日期**: 2026年5月13日  
**适用设备**: Android 手机/平板 + Termux
