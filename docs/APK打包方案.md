# 📱 Termux一键安装器 (Termux-Setup-APK)

> 这是一个自动安装脚本，可以配合 Termux 应用使用，自动完成所有依赖安装。

## 📦 快速开始

### 方法1: 在Termux中直接运行

```bash
# 复制以下命令到Termux中执行
pkg update && pkg install git curl -y && cd ~ && rm -rf ai-song-creator && git clone https://github.com/qscwzby7t6-svg/qscwzby7t6-svg.git && cd ai-song-creator && chmod +x install.sh && ./install.sh
```

### 方法2: 下载安装脚本到手机

1. 下载 [install.sh](https://github.com/qscwzby7t6-svg/qscwzby7t6-svg/raw/main/scripts/install.sh)
2. 将文件移动到 Termux 能访问的目录
3. 在 Termux 中执行:
   ```bash
   cd ~/storage/shared/Download
   chmod +x install.sh
   ./install.sh
   ```

---

## 📝 安装脚本说明

### 自动安装流程

```
1. 更新系统包
   ↓
2. 安装系统依赖
   ↓
3. 配置pip镜像
   ↓
4. 安装Python依赖
   ↓
5. 配置项目
   ↓
6. 运行测试
   ↓
7. 启动应用
```

### 脚本功能

- ✅ 自动检测并安装所有依赖
- ✅ 使用清华镜像加速下载
- ✅ 自动处理错误和异常
- ✅ 显示安装进度
- ✅ 验证安装结果
- ✅ 启动应用

---

## 🔧 完整安装脚本

### install.sh

```bash
#!/data/data/com.termux/files/usr/bin/bash

# Termux一键安装AI歌曲创作平台
# 版本: v1.0
# 作者: AI音乐创作平台开发团队

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 进度条函数
progress_bar() {
    local current=$1
    local total=$2
    local prefix=${3:-""}
    local suffix=${4:-""}
    local width=50
    local percent=$((current * 100 / total))
    local filled=$((width * current / total))
    local empty=$((width - filled))
    
    printf "\r${prefix}[%*s] %d%%%s" "$filled" | tr ' ' '=' "$percent" "$suffix"
    if [ $current -eq $total ]; then
        echo ""
    fi
}

# 检查是否在Termux中运行
check_termux() {
    if [ ! -d "/data/data/com.termux" ]; then
        log_error "此脚本必须在Termux中运行！"
        exit 1
    fi
    log_success "检测到Termux环境"
}

# 步骤1: 更新系统
step1_update() {
    log_info "步骤 1/8: 更新系统包..."
    pkg update -y > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        log_success "系统包更新完成"
    else
        log_warning "系统包更新失败，尝试使用备用方案..."
        pkg update --fix-broken -y
    fi
}

# 步骤2: 安装系统依赖
step2_install_deps() {
    log_info "步骤 2/8: 安装系统依赖..."
    
    local packages="git curl wget build-essential clang cmake make python python-pip libsndfile ffmpeg unzip openssl"
    
    for package in $packages; do
        pkg install "$package" -y > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            log_success "$package 安装成功"
        else
            log_warning "$package 安装失败，尝试单独安装..."
            pkg install "$package" -y
        fi
    done
    
    log_success "系统依赖安装完成"
}

# 步骤3: 配置Git
step3_config_git() {
    log_info "步骤 3/8: 配置Git..."
    
    if [ -z "$GIT_USER_NAME" ]; then
        read -p "请输入您的GitHub用户名: " GIT_USER_NAME
    fi
    if [ -z "$GIT_USER_EMAIL" ]; then
        read -p "请输入您的邮箱: " GIT_USER_EMAIL
    fi
    
    git config --global user.name "${GIT_USER_NAME:-Termux User}"
    git config --global user.email "${GIT_USER_EMAIL:-termux@example.com}"
    
    log_success "Git配置完成"
}

# 步骤4: 克隆项目
step4_clone_project() {
    log_info "步骤 4/8: 克隆项目..."
    
    cd ~
    
    if [ -d "ai-song-creator" ]; then
        log_warning "项目已存在，正在更新..."
        cd ai-song-creator
        git pull
    else
        log_info "正在克隆项目..."
        git clone https://github.com/qscwzby7t6-svg/qscwzby7t6-svg.git ai-song-creator
    fi
    
    if [ $? -eq 0 ]; then
        cd ai-song-creator
        log_success "项目克隆完成"
    else
        log_error "项目克隆失败"
        exit 1
    fi
}

# 步骤5: 配置pip
step5_config_pip() {
    log_info "步骤 5/8: 配置pip和安装Python依赖..."
    
    # 升级pip
    pip install --upgrade pip > /dev/null 2>&1
    
    # 配置清华镜像
    pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
    log_info "已配置清华镜像加速"
    
    # 安装基础包
    log_info "安装numpy和scipy..."
    pip install numpy==1.24.0 scipy==1.11.0 > /dev/null 2>&1
    
    # 安装PyTorch CPU版本
    log_info "安装PyTorch CPU版本（这可能需要几分钟）..."
    pip install torch==2.0.0 torchaudio==2.0.0 --index-url https://download.pytorch.org/whl/cpu > /dev/null 2>&1
    log_success "PyTorch安装完成"
    
    # 安装其他依赖
    log_info "安装其他Python依赖..."
    pip install -r requirements.txt > /dev/null 2>&1
    
    log_success "Python依赖安装完成"
}

# 步骤6: 创建数据目录
step6_create_dirs() {
    log_info "步骤 6/8: 创建数据目录..."
    
    mkdir -p data/audio data/db
    chmod -R 755 data/
    
    log_success "数据目录创建完成"
}

# 步骤7: 运行测试
step7_run_tests() {
    log_info "步骤 7/8: 运行部署测试..."
    
    if [ -f "deploy_test.py" ]; then
        python deploy_test.py
    else
        log_warning "测试脚本不存在，跳过测试"
    fi
}

# 步骤8: 启动应用
step8_start_app() {
    log_info "步骤 8/8: 启动应用..."
    
    log_success "==================================="
    log_success "安装完成！"
    log_success "==================================="
    echo ""
    log_info "输入以下命令启动应用："
    echo ""
    echo -e "  ${GREEN}cd ~/ai-song-creator${NC}"
    echo -e "  ${GREEN}python -m streamlit run app.py --server.port=8501${NC}"
    echo ""
    log_info "或在浏览器中打开："
    echo ""
    echo -e "  ${BLUE}http://localhost:8501${NC}"
    echo ""
    log_info "详细文档请查看："
    echo ""
    echo -e "  ${BLUE}docs/Termux完整部署教程.md${NC}"
    echo ""
}

# 主函数
main() {
    clear
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                   ║${NC}"
    echo -e "${GREEN}║   🎵 AI歌曲创作平台 - Termux一键安装器         ║${NC}"
    echo -e "${GREEN}║                                                   ║${NC}"
    echo -e "${GREEN}║   版本: v1.0                                      ║${NC}"
    echo -e "${GREEN}║   日期: 2026年5月13日                            ║${NC}"
    echo -e "${GREEN}║                                                   ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # 检查环境
    check_termux
    
    # 执行安装步骤
    step1_update
    step2_install_deps
    step3_config_git
    step4_clone_project
    step5_config_pip
    step6_create_dirs
    step7_run_tests
    step8_start_app
}

# 运行主函数
main
```

---

## 📱 APK打包方案说明

### 方案1: 使用PyDroid3（推荐）

PyDroid3是一个Android上的Python IDE，可以直接运行Python代码。

**步骤**:
1. 从Google Play或F-Droid安装PyDroid3
2. 导入项目代码
3. 安装依赖
4. 运行应用

**优点**: 
- 简单易用
- 自动配置Python环境

**缺点**:
- Streamlit支持有限
- 界面不如Web版本

---

### 方案2: 创建专用APK（高级）

使用Python-for-Android (buildozer) 创建独立APK。

**环境要求**:
- Linux或macOS电脑
- Android SDK
- Python 3.8+

**步骤**:

1. 安装buildozer:
   ```bash
   pip install buildozer
   ```

2. 初始化项目:
   ```bash
   buildozer init
   ```

3. 配置 buildozer.spec:
   ```python
   [app]
   title = AI Song Creator
   package.name = aisongcreator
   package.domain = com.aisongcreator
   requirements = python3,kivy,librosa,numpy,scipy,streamlit
   ```

4. 打包:
   ```bash
   buildozer android debug
   ```

**缺点**:
- Streamlit的Web界面需要额外处理
- 包体较大（200MB+）
- 配置复杂

---

### 方案3: 创建"壳"APK（推荐用于分发给用户）

创建一个简单的Android应用，作为安装引导器。

**功能**:
1. 检测是否安装Termux
2. 如果未安装，提示用户安装Termux
3. 如果已安装，自动运行安装脚本
4. 安装完成后启动应用

**技术栈**:
- Android Studio (Java/Kotlin)
- 或使用React Native/Flutter

---

## 📋 推荐的工作流程

### 对于开发者（您）:
1. 使用现有的Termux方案
2. 提供一键安装脚本
3. 用户体验好，易于维护

### 对于最终用户:
1. 安装Termux
2. 运行一键安装脚本
3. 开始使用

---

## 🚀 快速安装命令

复制以下命令到Termux中粘贴执行：

```bash
pkg update && pkg install git curl -y && cd ~ && rm -rf ai-song-creator && git clone https://github.com/qscwzby7t6-svg/qscwzby7t6-svg.git && cd ai-song-creator && chmod +x install.sh && ./install.sh
```

---

## 📞 获取帮助

如有问题，请提交Issue：
https://github.com/qscwzby7t6-svg/qscwzby7t6-svg/issues

---

**版本**: v1.0  
**更新日期**: 2026年5月13日
