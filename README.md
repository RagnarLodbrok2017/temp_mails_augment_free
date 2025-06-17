# Free AugmentCode

[English](#english) | [中文](#chinese)

# <a name="chinese"></a>中文版

Free AugmentCode 是一个用于清理AugmentCode相关数据的工具，可以在同一台电脑上无限次登录不同的账号，避免账号被锁定。

## 功能特性

- 📝 修改Telemetry ID
  - 重置设备 ID 和机器 ID
  - 自动备份原始数据
  - 生成新的随机 ID

- 🗃️ 数据库清理
  - 清理 SQLite 数据库中的特定记录
  - 自动备份数据库文件
  - 删除包含 'augment' 关键字的记录

- 💾 工作区存储管理
  - 清理工作区存储文件
  - 自动备份工作区数据

- 📧 临时邮箱管理 (新功能!)
  - 🌐 **真实邮箱服务** - 集成 Mail.tm、TempMail.lol 等多个真实临时邮箱服务
  - 📧 **功能邮箱地址** - 生成真实可用的临时邮箱地址
  - 👁️ **实时监控** - 每10秒检查一次真实邮箱收件
  - 🧠 **智能验证码提取** - 自动识别"Your verification code is:"等多种格式
  - 📋 **一键复制** - 快速复制邮箱地址和验证码
  - 🔄 **多服务备用** - 自动切换可用的邮箱服务
  - ✅ **AugmentCode兼容** - 专门优化用于接收AugmentCode验证邮件

## 安装说明

1. 确保你的系统已安装 Python 3.10及以上
2. 克隆此仓库到本地：
   ```bash
   git clone https://github.com/yourusername/free-augmentcode.git
   cd free-augmentcode
   ```
3. 安装依赖包（临时邮箱功能需要）：
   ```bash
   pip install -r requirements.txt
   ```

## 使用方法

### 🖥️ 图形界面模式（推荐）

1. 退出AugmentCode插件
2. 完全退出 VS Code
3. 启动图形界面：
   - **Windows**: 双击 `run_gui.bat`
   - **Linux/Mac**: 运行 `bash run_gui.sh`
   - **或者**: `python index.py --gui`

#### 使用临时邮箱功能：
4. 切换到"📧 Temp Email"标签页
5. 点击"🎲 Generate Temp Email"生成临时邮箱
6. 点击"📋 Copy Email"复制邮箱地址
7. 点击"▶️ Start Monitoring"开始监控邮件
8. 使用复制的邮箱地址注册AugmentCode账号
9. 验证码会自动显示在界面上，点击"📋 Copy Code"复制验证码
10. 完成AugmentCode注册后，使用"🧹 Cleanup Tools"标签页清理数据

### 📟 命令行模式

```bash
# 自动检测最佳界面
python index.py

# 强制使用命令行模式
python index.py --console

# 强制使用图形界面模式
python index.py --gui
```

### 🎭 演示模式

如果你想先体验临时邮箱功能而不安装依赖：
```bash
python demo_temp_email.py
```

## 项目结构

```
free-augmentcode/
├── index.py              # 主程序入口（支持GUI和命令行）
├── gui.py                # 图形用户界面（包含临时邮箱功能）
├── demo_temp_email.py    # 临时邮箱功能演示
├── run_gui.bat           # Windows GUI启动器
├── run_gui.sh            # Linux/Mac GUI启动器
├── requirements.txt      # Python依赖包列表
├── augutils/             # 工具类目录
│   ├── json_modifier.py      # JSON 文件修改工具
│   ├── sqlite_modifier.py    # SQLite 数据库修改工具
│   └── workspace_cleaner.py  # 工作区清理工具
├── tempmail/             # 临时邮箱模块
│   ├── temp_email_service.py # 临时邮箱服务
│   ├── verification_parser.py # 验证码解析器
│   └── error_handler.py      # 错误处理和重试机制
└── utils/                # 通用工具目录
    ├── paths.py             # 路径管理工具
    └── device_codes.py      # 设备代码生成工具
```

## 贡献

欢迎提交 Issue 和 Pull Request 来帮助改进这个项目。

## 许可证

此项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

# <a name="english"></a>English Version

Free AugmentCode is a tool for cleaning AugmentCode-related data, allowing unlimited logins with different accounts on the same computer while avoiding account lockouts.

## Features

- 📝 Telemetry ID Modification
  - Reset device ID and machine ID
  - Automatic backup of original data
  - Generate new random IDs

- 🗃️ Database Cleanup
  - Clean specific records in SQLite database
  - Automatic database file backup
  - Remove records containing 'augment' keyword

- 💾 Workspace Storage Management
  - Clean workspace storage files
  - Automatic workspace data backup

- 📧 Temporary Email Manager (New!)
  - 🌐 **Real Email Services** - Integrated with Mail.tm, TempMail.lol and other real temporary email providers
  - 📧 **Functional Email Addresses** - Generates real, working temporary email addresses
  - 👁️ **Real-time Monitoring** - Checks real inbox every 10 seconds for new messages
  - 🧠 **Smart Code Extraction** - Automatically recognizes "Your verification code is:" and various formats
  - 📋 **One-click Copy** - Quick copy for email addresses and verification codes
  - 🔄 **Multiple Service Fallback** - Automatically switches to available email services
  - ✅ **AugmentCode Optimized** - Specifically optimized for receiving AugmentCode verification emails

## Installation

1. Ensure Python 3.10 or above is installed on your system
2. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/free-augmentcode.git
   cd free-augmentcode
   ```

## Usage

### 🖥️ GUI Mode (Recommended)

1. Exit the AugmentCode plugin
2. Completely close VS Code
3. Launch the GUI:
   - **Windows**: Double-click `run_gui.bat`
   - **Linux/Mac**: Run `bash run_gui.sh`
   - **Or**: `python index.py --gui`

4. Click "Clean All Data" button in the GUI
5. Restart VS Code
6. Log in to the AugmentCode plugin with a new email

### 📟 Console Mode

```bash
# Auto-detect best interface
python index.py

# Force console mode
python index.py --console

# Force GUI mode
python index.py --gui
```

## Project Structure

```
free-augmentcode/
├── index.py              # Main program entry (supports GUI and console)
├── gui.py                # Graphical user interface
├── run_gui.bat           # Windows GUI launcher
├── run_gui.sh            # Linux/Mac GUI launcher
├── augutils/             # Utility classes directory
│   ├── json_modifier.py      # JSON file modification tool
│   ├── sqlite_modifier.py    # SQLite database modification tool
│   └── workspace_cleaner.py  # Workspace cleanup tool
└── utils/                # Common utilities directory
    └── paths.py             # Path management tool
```

## Contributing

Issues and Pull Requests are welcome to help improve this project.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details. 