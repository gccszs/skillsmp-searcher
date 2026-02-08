# SkillsMP Searcher

[English](#english) | [中文](#chinese)

---

## English

### Overview

**SkillsMP Searcher** is a Claude Code skill that enables powerful search capabilities for the [SkillsMP](https://skillsmp.com/) skill marketplace. It provides both keyword-based search and AI-powered semantic search to help you quickly discover and install useful skills.

### Features

- **Keyword Search**: Search skills by specific keywords with pagination and sorting options
- **AI Semantic Search**: Use natural language queries to find relevant skills powered by Cloudflare AI
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Python 3.9+**: Supports Python 3.9, 3.10, 3.11, and 3.12

### Installation

1. Download the latest `skillsmp-searcher.skill` from [Releases](https://github.com/gccszs/skillsmp-searcher/releases)
2. Install the skill in Claude Code:
   ```
   claude skill install skillsmp-searcher.skill
   ```

### Configuration

#### 🔑 API Key Setup

Before using this skill, you need to configure your SkillsMP API key. Choose one of the following methods:

**Method 1: Environment Variable (Recommended) ✅**
```bash
# Linux/macOS - Add to ~/.bashrc or ~/.zshrc
export SKILLSMP_API_KEY="sk_live_skillsmp_your_actual_key_here"

# Windows PowerShell
[System.Environment]::SetEnvironmentVariable('SKILLSMP_API_KEY', 'sk_live_skillsmp_your_actual_key_here', 'User')
```

**Method 2: Configuration File (For Development)**
```bash
# Create file: skills/skillsmp-searcher/references/api_key_real.txt
# Paste your API key (only the key, nothing else)
sk_live_skillsmp_your_actual_key_here
```

**Method 3: Command-Line Argument (One-Time Use)**
```bash
python skills/skillsmp-searcher/scripts/search_skills.py "SEO" --api-key "your_key_here"
```

#### ⚠️ Security Best Practices

- **Never commit API keys** to version control
- **Use environment variables** for production deployments
- **Rotate compromised keys** immediately at [SkillsMP Dashboard](https://skillsmp.com/)
- **Monitor API usage** for unusual activity

> 💡 **Tip**: Copy `.env.example` to `.env` and fill in your API key for local development. The `.env` file is automatically gitignored.

### Usage

#### Keyword Search

Search for skills using specific keywords:

```bash
python skills/skillsmp-searcher/scripts/search_skills.py "SEO" --limit 10 --sortBy stars
```

Parameters:
- `query`: Search keyword (required)
- `--page`: Page number (default: 1)
- `--limit`: Items per page (default: 20, max: 100)
- `--sort`: Sort by `stars` (default) or `recent`

#### AI Semantic Search

Search using natural language:

```bash
python skills/skillsmp-searcher/scripts/ai_search.py "How to create a web scraper"
```

### API Documentation

- **Official API Documentation**: [https://skillsmp.com/docs/api](https://skillsmp.com/docs/api)
- **中文API文档**: [https://skillsmp.com/zh/docs/api](https://skillsmp.com/zh/docs/api)
- **Local Reference**: `skills/skillsmp-searcher/references/api_documentation.md`

### Development

#### Running Tests

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Run tests with coverage
pytest --cov=scripts
```

#### Code Quality

```bash
# Format code
black scripts/

# Check code style
flake8 scripts/

# Type checking
mypy scripts/
```

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Chinese

### 概述

**SkillsMP Searcher** 是一个 Claude Code 技能，为 [SkillsMP](https://skillsmp.com/) 技能商城提供强大的搜索功能。它支持关键词搜索和AI驱动的语义搜索，帮助您快速发现和安装有用的技能。

### 功能特性

- **关键词搜索**: 通过特定关键词搜索技能，支持分页和排序
- **AI语义搜索**: 使用自然语言查询查找相关技能，由Cloudflare AI驱动
- **跨平台**: 支持Windows、macOS和Linux
- **Python 3.9+**: 支持Python 3.9、3.10、3.11和3.12

### 安装

1. 从[发布页面](https://github.com/gccszs/skillsmp-searcher/releases)下载最新的 `skillsmp-searcher.skill`
2. 在Claude Code中安装技能：
   ```
   claude skill install skillsmp-searcher.skill
   ```

### 配置

#### 🔑 API密钥设置

使用此技能前，需要配置您的SkillsMP API密钥。选择以下任一方法：

**方法1：环境变量（推荐）✅**
```bash
# Linux/macOS - 添加到 ~/.bashrc 或 ~/.zshrc
export SKILLSMP_API_KEY="sk_live_skillsmp_您的实际密钥"

# Windows PowerShell
[System.Environment]::SetEnvironmentVariable('SKILLSMP_API_KEY', 'sk_live_skillsmp_您的实际密钥', 'User')
```

**方法2：配置文件（用于开发）**
```bash
# 创建文件：skills/skillsmp-searcher/references/api_key_real.txt
# 粘贴您的API密钥（仅密钥本身，不要有其他内容）
sk_live_skillsmp_您的实际密钥
```

**方法3：命令行参数（一次性使用）**
```bash
python skills/skillsmp-searcher/scripts/search_skills.py "SEO" --api-key "您的密钥"
```

#### ⚠️ 安全最佳实践

- **永远不要将API密钥提交**到版本控制系统
- **使用环境变量**进行生产部署
- **密钥泄露后立即轮换**，访问[SkillsMP控制台](https://skillsmp.com/)
- **监控API使用情况**，发现异常活动

> 💡 **提示**：将 `.env.example` 复制为 `.env` 并填入您的API密钥用于本地开发。`.env` 文件会自动被git忽略。

### 使用方法

#### 关键词搜索

使用特定关键词搜索技能：

```bash
python skills/skillsmp-searcher/scripts/search_skills.py "SEO" --limit 10 --sortBy stars
```

参数：
- `query`: 搜索关键词（必需）
- `--page`: 页码（默认：1）
- `--limit`: 每页项目数（默认：20，最大：100）
- `--sort`: 按`stars`（默认）或`recent`排序

#### AI语义搜索

使用自然语言搜索：

```bash
python skills/skillsmp-searcher/scripts/ai_search.py "如何创建网络爬虫"
```

### API文档

- **官方API文档**: [https://skillsmp.com/docs/api](https://skillsmp.com/docs/api)
- **中文API文档**: [https://skillsmp.com/zh/docs/api](https://skillsmp.com/zh/docs/api)
- **本地参考文档**: `skills/skillsmp-searcher/references/api_documentation.md`

### 开发

#### 运行测试

```bash
# 安装依赖
pip install -r requirements.txt

# 运行测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=scripts
```

#### 代码质量检查

```bash
# 格式化代码
black scripts/

# 检查代码风格
flake8 scripts/

# 类型检查
mypy scripts/
```

### 贡献

欢迎贡献！请随时提交Pull Request。

### 许可证

本项目采用MIT许可证 - 详见[LICENSE](LICENSE)文件。
