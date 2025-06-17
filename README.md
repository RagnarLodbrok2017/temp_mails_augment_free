# Free AugmentCode - Multi-Account Management Tool

## 🚀 Overview

**Free AugmentCode** is a comprehensive multi-account management tool designed to help developers manage multiple AugmentCode accounts on the same computer without conflicts. This tool provides both data cleanup capabilities and advanced temporary email management features, making it easy to create and manage multiple development accounts.

## ✨ Key Features

### 🧹 **Data Cleanup & Management**
- **Telemetry ID Reset**: Automatically generates new device and machine IDs to avoid account conflicts
- **Database Cleanup**: Safely removes AugmentCode-related records from SQLite databases with automatic backup
- **Workspace Storage Management**: Cleans workspace storage files while preserving important data through backups
- **Automatic Backup System**: All operations include automatic backup creation for data safety

### 📧 **Advanced Temporary Email System**
- **Real Email Services**: Integration with multiple providers including Mail.tm, TempMail.lol, and others
- **Smart Domain Selection**: Automatic selection of the best available domains or manual domain preference
- **Real-time Monitoring**: Continuous inbox monitoring with 10-second intervals for instant email detection
- **Intelligent Code Extraction**: Advanced parsing system that recognizes various verification code formats
- **Multi-service Fallback**: Automatic switching between email providers for maximum reliability
- **AugmentCode Optimized**: Specifically designed and tested for AugmentCode verification workflows

### 🖥️ **User-Friendly Interface**
- **Modern GUI**: Clean, intuitive graphical interface with tabbed navigation
- **Console Mode**: Command-line interface for automation and scripting
- **Real-time Feedback**: Live status updates and detailed operation logs
- **One-click Operations**: Simplified workflows for common tasks

## 🛠️ Installation & Setup

### Prerequisites
- **Python 3.10+** (Required for all features)
- **Windows, macOS, or Linux** (Cross-platform support)

### Quick Installation
1. **Clone the repository**:
   ```bash
   git clone https://github.com/RagnarLodbrok2017/temp_mails_augment_free.git
   cd temp_mails_augment_free
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the application**:
   ```bash
   python index.py --gui
   ```

## 📖 Usage Guide

### 🎯 **Complete Workflow for New Account Creation**

#### Step 1: Generate Temporary Email
1. Launch the GUI and navigate to the "📧 Temp Email" tab
2. Select your preferred domain or use "Auto (Best Available)"
3. Click "🎲 Generate REAL Email" to create a functional email address
4. Copy the generated email address using "📋 Copy Email"

#### Step 2: Monitor for Verification
1. Click "▶️ Start Monitoring" to begin real-time email checking
2. Use the copied email to register your new AugmentCode account
3. Verification codes will automatically appear in the interface
4. Copy verification codes with "📋 Copy Code" for easy pasting

#### Step 3: Clean Previous Account Data
1. Switch to the "🧹 Cleanup Tools" tab
2. Ensure VS Code is completely closed
3. Click "🧹 Clean All Data" to reset all AugmentCode-related data
4. Restart VS Code and log in with your new account

### 🔧 **Advanced Usage Options**

#### Command Line Interface
```bash
# Launch with automatic interface detection
python index.py

# Force GUI mode
python index.py --gui

# Force console mode for scripting
python index.py --console
```

#### Individual Operations
- **Telemetry ID Reset Only**: `🔄 Modify Telemetry IDs`
- **Database Cleanup Only**: `🗃️ Clean Database`
- **Workspace Reset Only**: `💾 Clean Workspace`

## 📁 Project Architecture

```
temp_mails_augment_free/
├── 📄 index.py                    # Main application entry point
├── 🖥️ gui.py                      # GUI implementation with email features
├── 🚀 FreeAugmentCode.bat         # Windows quick launcher
├── 📋 requirements.txt            # Python dependencies
├── 📖 README.md                   # This documentation
├── 📖 QUICK_START.md              # Quick start guide
├── 📖 TEMP_EMAIL_FEATURES.md      # Email features documentation
├── 🛠️ augutils/                   # Core utility modules
│   ├── json_modifier.py          # JSON configuration management
│   ├── sqlite_modifier.py        # Database cleanup operations
│   └── workspace_cleaner.py      # Workspace storage management
├── 📧 tempmail/                   # Email service modules
│   ├── real_email_service.py     # Real email provider integration
│   ├── temp_email_service.py     # Fallback email service
│   ├── verification_parser.py    # Smart code extraction engine
│   └── error_handler.py          # Robust error handling system
└── 🔧 utils/                      # Common utilities
    ├── paths.py                   # System path management
    └── device_codes.py            # Device ID generation
```

## 🔒 **Security & Privacy**

- **Local Operation**: All data processing happens locally on your machine
- **No Data Collection**: No personal information is transmitted or stored externally
- **Automatic Backups**: All cleanup operations create backups before making changes
- **Temporary Email Privacy**: Email addresses are temporary and automatically expire
- **Open Source**: Full source code available for security review

## 🚀 **Performance & Reliability**

- **Multi-service Architecture**: Redundant email providers ensure high availability
- **Smart Retry Logic**: Automatic retry mechanisms for network operations
- **Resource Efficient**: Minimal system resource usage
- **Cross-platform Compatibility**: Tested on Windows, macOS, and Linux

## 🤝 **Contributing**

We welcome contributions from the community! Here's how you can help:

- **Bug Reports**: Submit detailed bug reports with reproduction steps
- **Feature Requests**: Suggest new features or improvements
- **Code Contributions**: Submit pull requests with new features or fixes
- **Documentation**: Help improve documentation and guides
- **Testing**: Test the application on different systems and configurations

## 📄 **License**

This project is licensed under the **MIT License**, allowing for both personal and commercial use. See the [LICENSE](LICENSE) file for complete details.

## 👨‍💻 **Developer**

**Developed by AhmedElnakieb**
- GitHub: [RagnarLodbrok2017](https://github.com/RagnarLodbrok2017)
- Specialized in automation tools and developer productivity solutions

---

## 🆘 **Support & Troubleshooting**

### Common Issues
- **Python Version**: Ensure you're using Python 3.10 or higher
- **Dependencies**: Run `pip install -r requirements.txt` if you encounter import errors
- **VS Code**: Make sure VS Code is completely closed before running cleanup operations
- **Permissions**: Run as administrator on Windows if you encounter permission errors

### Getting Help
- Check the [QUICK_START.md](QUICK_START.md) for step-by-step instructions
- Review [TEMP_EMAIL_FEATURES.md](TEMP_EMAIL_FEATURES.md) for email feature details
- Submit issues on GitHub for bug reports and feature requests

---

*This tool is designed to help developers manage multiple accounts efficiently while maintaining security and privacy. Use responsibly and in accordance with AugmentCode's terms of service.*