#!/data/data/com.termux/files/usr/bin/bash

# Termux一键安装AI歌曲创作平台
# 版本: v1.0
# 作者: AI音乐创作平台开发团队

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
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

log_step() {
    echo -e "${CYAN}[STEP]${NC} ${BOLD}$1${NC}"
}

# 检查是否在Termux中运行
check_termux() {
    if [ ! -d "/data/data/com.termux" ]; then
        echo ""
        log_error "=============================================="
        log_error "此脚本必须在Termux中运行！"
        log_error "请先安装Termux: https://f-droid.org/packages/com.termux/"
        log_error "=============================================="
        exit 1
    fi
}

# 步骤1: 更新系统
step1_update() {
    log_step "1/9: 更新系统包..."
    echo ""
    
    pkg update -y 2>&1 | while read line; do
        echo -e "  $line"
    done
    
    if [ $? -eq 0 ]; then
        log_success "系统包更新完成"
    else
        log_warning "部分包更新失败，继续安装..."
    fi
    echo ""
}

# 步骤2: 安装系统依赖
step2_install_deps() {
    log_step "2/9: 安装系统依赖..."
    echo ""
    
    local packages=(
        "git"
        "curl"
        "wget"
        "vim"
        "build-essential"
        "clang"
        "cmake"
        "make"
        "python"
        "python-pip"
        "libsndfile"
        "ffmpeg"
        "unzip"
        "openssl"
        "tree"
    )
    
    for package in "${packages[@]}"; do
        echo -n "  安装 $package... "
        pkg install "$package" -y > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓${NC}"
        else
            echo -e "${YELLOW}跳过${NC}"
        fi
    done
    
    log_success "系统依赖安装完成"
    echo ""
}

# 步骤3: 配置Git
step3_config_git() {
    log_step "3/9: 配置Git..."
    echo ""
    
    # 自动配置Git（使用默认值）
    git config --global user.name "Termux User" 2>/dev/null
    git config --global user.email "termux@localhost" 2>/dev/null
    git config --global credential.helper store 2>/dev/null
    git config --global color.ui auto 2>/dev/null
    
    log_success "Git配置完成"
    echo ""
}

# 步骤4: 配置pip镜像
step4_config_pip() {
    log_step "4/9: 配置pip镜像..."
    echo ""
    
    # 配置清华镜像
    pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple 2>/dev/null
    
    # 验证镜像配置
    local mirror=$(pip config get global.index-url 2>/dev/null)
    if [ "$mirror" != "" ]; then
        log_success "已配置pip镜像: $mirror"
    else
        log_warning "镜像配置失败，将使用默认源"
    fi
    echo ""
}

# 步骤5: 升级pip
step5_upgrade_pip() {
    log_step "5/9: 升级pip..."
    echo ""
    
    echo -n "  升级pip... "
    pip install --upgrade pip > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC}"
        log_success "pip升级完成"
    else
        log_warning "pip升级失败，继续安装..."
    fi
    echo ""
}

# 步骤6: 克隆项目
step6_clone_project() {
    log_step "6/9: 克隆项目..."
    echo ""
    
    cd ~
    
    if [ -d "ai-song-creator" ]; then
        log_warning "项目目录已存在，正在更新..."
        cd ai-song-creator
        git pull > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            log_success "项目更新完成"
        else
            log_warning "项目更新失败，使用现有版本"
        fi
    else
        echo "  正在克隆项目..."
        git clone https://github.com/qscwzby7t6-svg/qscwzby7t6-svg.git ai-song-creator 2>&1 | while read line; do
            echo -e "  $line"
        done
        
        if [ $? -eq 0 ]; then
            cd ai-song-creator
            log_success "项目克隆完成"
        else
            log_error "项目克隆失败，请检查网络连接"
            exit 1
        fi
    fi
    echo ""
}

# 步骤7: 安装Python依赖
step7_install_python_deps() {
    log_step "7/9: 安装Python依赖（这可能需要10-30分钟）..."
    echo ""
    
    cd ~/ai-song-creator
    
    # 创建数据目录
    mkdir -p data/audio data/db
    chmod -R 755 data/
    log_info "数据目录创建完成"
    
    # 单独安装numpy（使用预编译wheel避免编译问题）
    echo ""
    log_info "安装numpy..."
    pip install numpy --prefer-binary --no-build-isolation > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        log_success "numpy安装完成"
    else
        log_warning "numpy安装失败，尝试备用方案..."
        pip install numpy==1.23.5 --prefer-binary --no-cache-dir > /dev/null 2>&1
    fi
    
    # 单独安装scipy
    echo ""
    log_info "安装scipy（这可能需要几分钟）..."
    pip install scipy --prefer-binary --no-build-isolation > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        log_success "scipy安装完成"
    else
        log_warning "scipy安装失败，尝试备用版本..."
        pip install scipy==1.10.1 --prefer-binary --no-cache-dir > /dev/null 2>&1
    fi
    
    # 单独安装soundfile
    echo ""
    log_info "安装soundfile..."
    pip install soundfile --prefer-binary > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        log_success "soundfile安装完成"
    else
        log_warning "soundfile安装失败，尝试备用方案..."
        pip install pysoundfile --prefer-binary > /dev/null 2>&1
    fi
    
    # 单独安装librosa
    echo ""
    log_info "安装librosa（这可能需要几分钟）..."
    pip install librosa --prefer-binary > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        log_success "librosa安装完成"
    else
        log_warning "librosa安装失败，部分音频分析功能将不可用"
    fi
    
    # 安装PyTorch
    echo ""
    log_info "安装PyTorch CPU版本（较大，请耐心等待）..."
    pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        log_success "PyTorch安装完成"
    else
        log_warning "PyTorch安装失败，继续安装其他依赖（部分功能可能受限）"
    fi
    
    # 安装其他依赖
    echo ""
    log_info "安装其他Python依赖..."
    pip install pydub matplotlib pydantic pydantic-settings streamlit fastapi uvicorn pytest pytest-asyncio > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        log_success "其他依赖安装完成"
    fi
    
    echo ""
}

# 步骤8: 验证安装
step8_verify() {
    log_step "8/9: 验证安装..."
    echo ""
    
    cd ~/ai-song-creator
    
    # 验证Python包
    echo "  验证Python依赖..."
    
    local deps=("numpy" "scipy" "soundfile")
    for dep in "${deps[@]}"; do
        echo -n "    $dep... "
        python -c "import $dep" 2>/dev/null
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓${NC}"
        else
            echo -e "${RED}✗${NC}"
        fi
    done
    
    echo -n "    librosa... "
    python -c "import librosa" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${YELLOW}可选${NC}"
    fi
    
    echo -n "    streamlit... "
    python -c "import streamlit" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${YELLOW}可选${NC}"
    fi
    
    # 验证目录
    echo ""
    echo "  验证目录结构..."
    [ -d "data/audio" ] && echo -e "    data/audio ${GREEN}✓${NC}" || echo -e "    data/audio ${RED}✗${NC}"
    [ -d "data/db" ] && echo -e "    data/db ${GREEN}✓${NC}" || echo -e "    data/db ${RED}✗${NC}"
    
    echo ""
}

# 步骤9: 启动应用
step9_start() {
    log_step "9/9: 安装完成！"
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                                ║${NC}"
    echo -e "${GREEN}║   🎵 AI歌曲创作平台 - 安装完成！                            ║${NC}"
    echo -e "${GREEN}║                                                                ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BOLD}启动应用:${NC}"
    echo ""
    echo -e "  1. 进入项目目录"
    echo -e "    ${CYAN}cd ~/ai-song-creator${NC}"
    echo ""
    echo -e "  2. 运行部署测试（可选）"
    echo -e "    ${CYAN}python deploy_test.py${NC}"
    echo ""
    echo -e "  3. 启动应用"
    echo -e "    ${CYAN}python -m streamlit run app.py --server.port=8501${NC}"
    echo ""
    echo -e "${BOLD}访问应用:${NC}"
    echo ""
    echo -e "  在浏览器中打开: ${CYAN}http://localhost:8501${NC}"
    echo ""
    echo -e "${BOLD}后台运行（推荐）:${NC}"
    echo ""
    echo -e "  1. 安装tmux"
    echo -e "    ${CYAN}pkg install tmux -y${NC}"
    echo ""
    echo -e "  2. 创建tmux会话"
    echo -e "    ${CYAN}tmux new -s ai-song${NC}"
    echo ""
    echo -e "  3. 在会话中运行应用"
    echo -e "    ${CYAN}cd ~/ai-song-creator && python -m streamlit run app.py --server.port=8501${NC}"
    echo ""
    echo -e "  4. 按 ${YELLOW}Ctrl+B${NC} 然后按 ${YELLOW}D${NC} 退出会话"
    echo ""
    echo -e "${BOLD}详细文档:${NC}"
    echo ""
    echo -e "  查看: ${CYAN}docs/Termux完整部署教程.md${NC}"
    echo ""
    echo -e "${GREEN}感谢使用AI歌曲创作平台！${NC}"
    echo ""
}

# 主函数
main() {
    clear
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                                                                ║${NC}"
    echo -e "${CYAN}║   🎵 AI歌曲创作平台 - Termux一键安装器                    ║${NC}"
    echo -e "${CYAN}║                                                                ║${NC}"
    echo -e "${CYAN}║   版本: v1.0                                                 ║${NC}"
    echo -e "${CYAN}║   日期: 2026年5月13日                                       ║${NC}"
    echo -e "${CYAN}║                                                                ║${NC}"
    echo -e "${CYAN}║   GitHub: https://github.com/qscwzby7t6-svg/qscwzby7t6-svg ║${NC}"
    echo -e "${CYAN}║                                                                ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # 检查环境
    check_termux
    
    # 执行安装步骤
    step1_update
    step2_install_deps
    step3_config_git
    step4_config_pip
    step5_upgrade_pip
    step6_clone_project
    step7_install_python_deps
    step8_verify
    step9_start
}

# 运行主函数
main
