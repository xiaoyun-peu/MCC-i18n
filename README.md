# Minecraft地图汉化工具 (MCC i18n)

一个功能强大的Minecraft地图文本汉化工具，支持世界文件扫描、自动翻译、批量编辑和一键导出。

## 功能特性

### 🎯 核心功能
- **世界文件选择** - 智能识别Minecraft世界文件夹
- **深度文本扫描** - 扫描命令方块、实体名称、Boss栏等所有可翻译文本
- **智能翻译管理** - 支持手动编辑、自动翻译、批量操作
- **安全写入** - 自动备份，支持JSON验证，确保数据安全
- **一键导出** - 生成mcworld格式，包含语言文件，便于分享

### 🎨 界面特色
- **现代化UI** - 使用PyQt6 + Qt-Material，支持深浅主题切换
- **无边框设计** - 圆角窗口，可拖拽，自定义标题栏
- **实时日志** - 三色日志输出（INFO/WARNING/ERROR）
- **三栏布局** - 导航、工作区、日志区域分离，操作流畅

### ⚡ 技术特性
- **多线程处理** - 扫描、翻译、写入操作不卡顿界面
- **异常处理** - 完善的错误捕获和提示机制
- **配置管理** - 支持用户偏好设置保存
- **日志系统** - 文件+界面双重日志输出

## 安装使用

### 系统要求
- Python 3.8+
- Windows 10/11, macOS 10.15+, Linux (Ubuntu 18.04+)

### 快速开始

#### 方法一：直接运行源码
```bash
# 克隆项目
git clone https://github.com/BiliBiliACEGE/MCC-i18n.git
cd mcc_i18n

# 安装依赖
pip install -r requirements.txt

# 运行程序
python main.py
```

#### 方法二：使用可执行文件
1. 下载发布的可执行文件
2. 双击运行 `mcc_i18n.exe` (Windows)

### 构建可执行文件
```bash
# 检查依赖
python build.py --check-only

# 构建可执行文件
python build.py

# 构建完成后，可执行文件位于 dist/ 目录
```

## 使用指南

### 1. 选择世界
- 点击"浏览"按钮选择Minecraft世界文件夹
- 程序会自动验证世界有效性
- 有效世界会显示详细信息

### 2. 扫描文本
- 配置扫描选项（Region文件、Data文件、实体名称）
- 点击"开始扫描"，程序会后台扫描所有可翻译文本
- 扫描结果会显示原文、出现次数等信息

### 3. 翻译管理
- **手动翻译** - 双击表格单元格直接编辑
- **自动翻译** - 使用一键机翻功能（支持en→zh-cn / zh-cn→en）
- **批量操作** - 支持导入/导出CSV文件
- **搜索过滤** - 快速查找特定文本

### 4. 写入地图
- 程序会自动创建备份文件
- 支持JSON格式验证，确保数据有效性
- 写入完成后可一键打开世界目录

### 5. 打包导出
- 生成标准的mcworld格式文件
- 自动创建语言文件（zh_cn.json）
- 支持压缩，减小文件体积

## 项目结构

```
mcc_i18n/
├── main.py                 # 程序入口
├── ui/                     # 用户界面模块
│   ├── main_window.py     # 主窗口
│   ├── navigation_widget.py # 导航组件
│   ├── world_select_page.py # 世界选择页面
│   ├── scan_page.py       # 扫描页面
│   ├── translation_page.py # 翻译页面
│   ├── write_page.py      # 写入页面
│   └── export_page.py     # 导出页面
├── workers/               # 工作线程
│   ├── scan_worker.py     # 扫描工作线程
│   ├── translate_worker.py # 翻译工作线程
│   ├── write_worker.py    # 写入工作线程
│   └── export_worker.py   # 导出工作线程
├── utils/                 # 工具模块
│   ├── logger.py          # 日志系统
│   ├── config.py          # 配置管理
│   ├── nbt_helper.py      # NBT文件助手
│   ├── json_validator.py  # JSON验证器
│   ├── exceptions.py      # 异常定义
│   └── mock_translator.py # 模拟翻译器
├── resources/             # 资源文件
│   ├── icons/            # 图标文件
│   ├── styles/           # 样式文件
│   └── styles.qrc        # Qt资源文件
├── build.py              # 构建脚本
├── requirements.txt      # 依赖列表
└── README.md             # 项目文档
```

## 技术栈

### 核心库
- **PyQt6** - 跨平台GUI框架
- **Qt-Material** - 现代化主题样式
- **nbtlib** - NBT文件读写
- **googletrans** - Google翻译API
- **openpyxl** - Excel文件处理

### 开发工具
- **PyInstaller** - 打包工具
- **Python 3.8+** - 开发语言

## 开发指南

### 代码规范
- 使用类型标注（Type Hints）
- 遵循PEP 8编码规范
- 统一的异常处理机制
- 信号/槽命名规范（scan_started、scan_finished等）

### 添加新功能
1. 在对应的工作线程中实现核心逻辑
2. 在UI页面中添加界面元素
3. 连接信号和槽
4. 添加异常处理和日志输出

### 调试技巧
- 查看实时日志输出
- 检查mcc_i18n.log文件
- 使用--debug模式运行

## 常见问题

### Q: 程序无法启动？
A: 检查Python版本和依赖包是否正确安装

### Q: 扫描不到文本？
A: 确认世界文件夹包含有效的Minecraft存档

### Q: 翻译功能不可用？
A: 检查网络连接，或使用离线翻译模式

### Q: 写入失败？
A: 确保有足够的文件权限，程序会自动创建备份

## 版本历史

### v1.0.0 (2024-10-13)
- 初始版本发布
- 支持世界文件扫描和翻译
- 支持自动备份和导出
- 现代化UI界面

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 联系

如有问题或建议，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件到项目维护者

---

**享受您的Minecraft汉化之旅！** 🎮✨