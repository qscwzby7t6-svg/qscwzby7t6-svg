# 📱 独立APK打包详细指南

> 如果您希望创建可以直接安装的APK文件（无需Termux），请按照以下步骤操作。

---

## ⚠️ 重要说明

创建独立APK需要使用电脑进行编译，推荐使用**Linux系统**或**WSL**。

### 环境要求

- Python 3.8+
- Java JDK 11+
- Android SDK
- 至少10GB可用空间
- 稳定的网络连接

---

## 方案A: 使用PyDroid3（最简单）

### 步骤1: 安装PyDroid3

在Android设备上安装PyDroid3：
- Google Play: 搜索 "PyDroid3"
- F-Droid: https://f-droid.org/packages/ru.iiec.pydroid3/

### 步骤2: 创建启动脚本

在PyDroid3中创建 `start_app.py`：

```python
import subprocess
import os

# 进入项目目录
os.chdir('/storage/emulated/0/ai-song-creator')

# 安装依赖（首次运行）
subprocess.run(['pip', 'install', '-r', 'requirements.txt'])

# 启动Streamlit
subprocess.run(['python', '-m', 'streamlit', 'run', 'app.py', '--server.port=8501'])
```

### 步骤3: 运行

1. 将项目代码复制到手机存储
2. 在PyDroid3中打开 `start_app.py`
3. 点击运行按钮

---

## 方案B: 使用Buildozer（推荐用于发布）

### 步骤1: 安装Buildozer

```bash
# 在Linux或WSL中
pip install buildozer

# 安装Android SDK依赖（Ubuntu/Debian）
sudo apt install -y \
    python3-dev \
    python3-pip \
    cmake \
    swig \
    git \
    unzip \
    openjdk-11-jdk \
    zipalign \
    autoconf \
    libtool \
    pkg-config \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libtinfo5 \
    libffi-dev \
    libssl-dev
```

### 步骤2: 初始化项目

```bash
mkdir ai-song-apk
cd ai-song-apk
buildozer init
```

### 步骤3: 配置buildozer.spec

编辑 `ai-song-apk/buildozer.spec`：

```spec
[app]

# 应用基本信息
title = AI Song Creator
package.name = aisongcreator
package.domain = com.aisongcreator

# 源码位置
source.dir = .

# Python版本
pypi_version = 3.11.0

# 权限
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# 依赖包
requirements = python3,kivy,librosa,numpy,scipy,streamlit,aiofiles

# Android配置
android.minapi = 21
android.api = 33
android.ndk = 25b
android.ndk_api = 21

# 图标（可选）
android.icon = icon.png
```

### 步骤4: 创建main.py

由于Streamlit不直接支持Kivy，需要创建简化界面：

```python
"""
AI歌曲创作平台 - Android简化版
"""
import os
import sys

def main():
    print("🎵 AI歌曲创作平台启动中...")
    
    # 检查依赖
    try:
        import numpy
        import scipy
        print(f"✓ numpy {numpy.__version__}")
        print(f"✓ scipy {scipy.__version__}")
    except ImportError as e:
        print(f"✗ 缺少依赖: {e}")
        print("请运行: pip install numpy scipy")
        return
    
    # 显示提示
    print("\n" + "="*50)
    print("AI歌曲创作平台已准备就绪！")
    print("="*50)
    print("\n功能模块:")
    print("  1. 歌曲搜索")
    print("  2. 风格提取")
    print("  3. 歌曲生成")
    print("  4. 原创检测")
    print("="*50)
    print("\n请使用电脑访问 Web 版本获得完整功能")
    print("GitHub: https://github.com/qscwzby7t6-svg/qscwzby7t6-svg")

if __name__ == "__main__":
    main()
```

### 步骤5: 编译APK

```bash
# 安装依赖
buildozer install_requirements

# 调试编译
buildozer android debug

# 如果编译成功，APK文件在:
# bin/aisongcreator-0.1-debug.apk
```

---

## 方案C: 使用Flutter创建"壳"APK（推荐用于分发）

### 优点
- 可以自动检测和安装Termux
- 提供更好的用户体验
- APK体积小（~5MB）

### 步骤1: 创建Flutter项目

```bash
flutter create --org com.aisongcreator ai_song_shell
cd ai_song_shell
```

### 步骤2: 添加依赖

编辑 `pubspec.yaml`：

```yaml
dependencies:
  flutter:
    sdk: flutter
  url_launcher: ^6.1.0
  package_info: ^2.0.2
```

### 步骤3: 创建主界面

```dart
import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

void main() {
  runApp(AISongApp());
}

class AISongApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AI歌曲创作平台',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: HomePage(),
    );
  }
}

class HomePage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('🎵 AI歌曲创作平台')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.music_note, size: 100, color: Colors.blue),
            SizedBox(height: 20),
            Text(
              'AI歌曲创作平台',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 40),
            ElevatedButton.icon(
              onPressed: () {
                _openApp('termux');
              },
              icon: Icon(Icons.download),
              label: Text('安装Termux版本'),
            ),
            SizedBox(height: 10),
            OutlinedButton.icon(
              onPressed: () {
                _openBrowser('https://github.com/qscwzby7t6-svg/qscwzby7t6-svg');
              },
              icon: Icon(Icons.open_in_browser),
              label: Text('访问GitHub'),
            ),
          ],
        ),
      ),
    );
  }

  void _openApp(String app) async {
    // 检测是否安装Termux
    // 如果未安装，引导用户下载
  }

  void _openBrowser(String url) async {
    await launch(url);
  }
}
```

### 步骤4: 编译APK

```bash
flutter build apk --release
```

---

## 📋 推荐的工作流程

### 对于开发者（您）

1. **使用Termux方案**（当前推荐）
   - 维护简单：代码更新后用户重新运行安装脚本即可
   - 功能完整：保留所有Web功能
   - 易于调试：可以看到所有日志

2. **发布安装指南**
   - 文档: docs/荣耀平板部署教程.md
   - 文档: docs/Termux完整部署教程.md
   - 脚本: scripts/install.sh

### 对于最终用户

**推荐步骤**:
1. 从F-Droid安装Termux
2. 运行一键安装脚本
3. 开始使用

---

## 🚀 快速开始（Termux方案）

### 在Termux中粘贴以下命令：

```bash
pkg update && pkg install git curl -y && cd ~ && rm -rf ai-song-creator && git clone https://github.com/qscwzby7t6-svg/qscwzby7t6-svg.git && cd ai-song-creator && chmod +x install.sh && ./install.sh
```

### 安装完成后启动：

```bash
cd ~/ai-song-creator
python -m streamlit run app.py --server.port=8501
```

### 在浏览器打开：

```
http://localhost:8501
```

---

## ❓ 常见问题

### Q1: 能否直接生成APK而不需要Termux？

**答**: 可以，但需要使用buildozer或Flutter。详细步骤见上文"方案B"和"方案C"。

### Q2: Termux安装的应用能直接在桌面创建快捷方式吗？

**答**: 可以！
1. 在Termux中安装 `termux-widget`：
   ```bash
   pkg install termux-widget
   ```
2. 创建快捷方式脚本
3. 在桌面添加快捷方式

### Q3: 如何更新到最新版本？

```bash
cd ~/ai-song-creator
git pull
./install.sh
```

### Q4: 如何卸载？

```bash
cd ~
rm -rf ai-song-creator
```

---

## 📞 获取帮助

如有问题，请提交Issue：
https://github.com/qscwzby7t6-svg/qscwzby7t6-svg/issues

---

**版本**: v1.0  
**更新日期**: 2026年5月13日
