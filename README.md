# AI歌曲创作平台

一款基于人工智能技术的音乐创作工具，用户仅需提供喜欢的歌名和歌手，系统即可自动生成风格相似但原创的新歌曲。

## 功能特性

- 🎵 **极简用户体验**：仅需歌名+歌手即可生成
- 🎨 **风格精准对齐**：多维度风格特征分析
- ✅ **原创保障**：内置版权检测机制
- 💰 **成本可控**：核心模块采用开源方案
- 🌐 **美观Web界面**：Streamlit打造优秀的用户体验

## 项目结构

```
ai-song-generator/
├── docs/              # 项目文档
│   ├── PRD.md        # 产品需求文档
│   ├── 技术架构.md   # 技术架构文档
│   └── 开发计划.md   # 开发计划文档
├── src/               # 源代码
│   ├── models/       # 数据模型
│   ├── services/     # 业务逻辑服务
│   └── config.py     # 配置管理
├── tests/            # 测试代码
├── data/             # 数据存储
│   ├── audio/        # 音频文件
│   └── db/           # 数据库文件
├── app.py            # Web应用入口
├── requirements.txt  # Python依赖
└── README.md         # 项目说明
```

## 快速开始

### 环境要求

- Python 3.9+
- 内存 4GB+

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行测试

```bash
pytest tests/ -v
```

### 启动Web应用

```bash
streamlit run app.py
```

然后在浏览器访问 http://localhost:8501

## 开发文档

- [产品需求文档 (PRD)](docs/PRD.md)
- [技术架构文档](docs/技术架构.md)
- [开发计划](docs/开发计划.md)

## 技术栈

- 前端：Streamlit
- 音频处理：Librosa, SoundFile
- 机器学习：NumPy, SciPy
- 数据库：SQLite
- 测试：pytest

## 已实现模块

✅ **歌曲搜索模块** - 搜索和浏览歌曲数据库
✅ **风格特征提取模块** - 使用Librosa分析音频风格
✅ **版权检测模块** - 音频指纹和相似度计算
✅ **AI音乐生成模块** - 基于算法的音乐创作
✅ **Web用户界面** - 完整的操作界面
✅ **完整的单元测试** - 37个测试用例全部通过

## 许可证

MIT License
