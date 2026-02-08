# SkillsMP Searcher

**SkillsMP Searcher** 是一个 Claude Code 技能，为 [SkillsMP](https://skillsmp.com/) 技能商城提供强大的搜索功能。它支持关键词搜索和AI驱动的语义搜索，帮助您快速发现和安装有用的技能。

## 功能特性

- **关键词搜索**: 通过特定关键词搜索技能，支持分页和排序
- **AI语义搜索**: 使用自然语言查询查找相关技能，由Cloudflare AI驱动
- **跨平台**: 支持Windows、macOS和Linux
- **Python 3.9+**: 支持Python 3.9、3.10、3.11和3.12
- **安全的API密钥管理**: 多种配置方式和安全最佳实践

## 安装

1. 从[发布页面](https://github.com/gccszs/skillsmp-searcher/releases)下载最新的 `skillsmp-searcher.skill`
2. 在Claude Code中安装技能：
   ```bash
   claude skill install skillsmp-searcher.skill
   ```

## 配置

### 🔑 API密钥设置

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

### ⚠️ 安全最佳实践

- **永远不要将API密钥提交**到版本控制系统
- **使用环境变量**进行生产部署
- **密钥泄露后立即轮换**，访问[SkillsMP控制台](https://skillsmp.com/)
- **监控API使用情况**，发现异常活动

> 💡 **提示**：将 `.env.example` 复制为 `.env` 并填入您的API密钥用于本地开发。`.env` 文件会自动被git忽略。

## 使用方法

### 关键词搜索

使用特定关键词搜索技能：

```bash
python skills/skillsmp-searcher/scripts/search_skills.py "SEO" --limit 10 --sortBy stars
```

**参数：**
- `query`: 搜索关键词（必需）
- `--page`: 页码（默认：1）
- `--limit`: 每页项目数（默认：20，最大：100）
- `--sort`: 按`stars`（默认）或`recent`排序

### AI语义搜索

使用自然语言搜索：

```bash
python skills/skillsmp-searcher/scripts/ai_search.py "如何创建网络爬虫"
```

## API文档

- **官方API文档**: [https://skillsmp.com/docs/api](https://skillsmp.com/docs/api)
- **中文API文档**: [https://skillsmp.com/zh/docs/api](https://skillsmp.com/zh/docs/api)
- **本地参考文档**: `skills/skillsmp-searcher/references/api_documentation.md`

## 开发

### 运行测试

```bash
# 安装依赖
pip install -r requirements.txt

# 运行测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=scripts
```

### 代码质量检查

```bash
# 格式化代码
black scripts/

# 检查代码风格
flake8 scripts/

# 类型检查
mypy scripts/
```

## 项目结构

```
skillsmp-searcher/
├── .github/
│   └── workflows/          # CI/CD工作流
├── skills/
│   └── skillsmp-searcher/  # Skill包
│       ├── SKILL.md        # Skill元数据
│       ├── scripts/        # 可执行脚本
│       ├── references/     # 文档和配置
│       └── assets/         # 资源文件
├── tests/                  # 测试套件
├── requirements.txt        # Python依赖
└── README.md              # 本文件
```

## 贡献

欢迎贡献！请随时提交Pull Request。

## 许可证

本项目采用MIT许可证 - 详见[LICENSE](LICENSE)文件。

## 相关链接

- [SkillsMP技能商城](https://skillsmp.com/)
- [GitHub仓库](https://github.com/gccszs/skillsmp-searcher)
- [问题追踪](https://github.com/gccszs/skillsmp-searcher/issues)
