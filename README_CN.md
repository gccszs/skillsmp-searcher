# SkillsMP Searcher

[English](README.md) | [简体中文](README_CN.md)

---

**SkillsMP Searcher** 是一�?Claude Code 技能，�?[SkillsMP](https://skillsmp.com/) 技能商城提供强大的搜索功能。它支持关键词搜索和AI驱动的语义搜索，帮助您快速发现和安装有用的技能�?
## 功能特�?
- **关键词搜�?*: 通过特定关键词搜索技能，支持分页和排�?- **AI语义搜索**: 使用自然语言查询查找相关技能，由Cloudflare AI驱动
- **跨平�?*: 支持Windows、macOS和Linux
- **Python 3.9+**: 支持Python 3.9�?.10�?.11�?.12
- **安全的API密钥管理**: 多种配置方式和安全最佳实�?
## 安装

选择以下任一方法安装 SkillsMP Searcher�?
### 方法1：NPX 快速安�?⚡（推荐�?
最快的安装方式，直接从 GitHub 安装�?
```bash
npx skills add gccszs/skillsmp-searcher
```

这将自动下载并安装最新版本的技能�?
### 方法2：从发布文件安装

1. 从[发布页面](https://github.com/gccszs/skillsmp-searcher/releases)下载最新的 `skillsmp-searcher.skill`
2. 使用 Claude Code CLI 安装�?   ```bash
   claude skill install skillsmp-searcher.skill
   ```

### 方法3：从 GitHub 安装

```bash
# 克隆仓库
git clone https://github.com/gccszs/skillsmp-searcher.git

# 从本地目录安�?claude skill install skillsmp-searcher/skills/skillsmp-searcher
```

### 方法4：一行命令安装（PowerShell�?
```powershell
# 下载并安装，一条命令完�?Invoke-WebRequest -Uri "https://github.com/gccszs/skillsmp-searcher/releases/latest/download/skillsmp-searcher.skill" -OutFile "skillsmp-searcher.skill"; claude skill install skillsmp-searcher.skill
```

### 方法5：一行命令安装（Bash�?
```bash
# 下载并安装，一条命令完�?curl -L https://github.com/gccszs/skillsmp-searcher/releases/latest/download/skillsmp-searcher.skill -o skillsmp-searcher.skill && claude skill install skillsmp-searcher.skill
```

### 验证安装

```bash
claude skill list
```

您应该能在已安装技能列表中看到 `skillsmp-searcher`�?
## 配置

### 🔑 API密钥设置

使用此技能前，需要配置您的SkillsMP API密钥。选择以下任一方法�?
**方法1：环境变量（推荐）✅**

```bash
# Linux/macOS - 添加�?~/.bashrc �?~/.zshrc
export SKILLSMP_API_KEY="sk_live_skillsmp_您的实际密钥"

# Windows PowerShell
[System.Environment]::SetEnvironmentVariable('SKILLSMP_API_KEY', 'sk_live_skillsmp_您的实际密钥', 'User')
```

**方法2：配置文件（用于开发）**

```bash
# 创建文件：skills/skillsmp-searcher/references/api_key_real.txt
# 粘贴您的API密钥（仅密钥本身，不要有其他内容�?sk_live_skillsmp_您的实际密钥
```

**方法3：命令行参数（一次性使用）**

```bash
python skills/skillsmp-searcher/scripts/search_skills.py "SEO" --api-key "您的密钥"
```

### ⚠️ 安全最佳实�?
- **永远不要将API密钥提交**到版本控制系�?- **使用环境变量**进行生产部署
- **密钥泄露后立即轮�?*，访问[SkillsMP控制台](https://skillsmp.com/)
- **监控API使用情况**，发现异常活�?
> 💡 **提示**：将 `.env.example` 复制�?`.env` 并填入您的API密钥用于本地开发。`.env` 文件会自动被git忽略�?
## 使用方法

### 关键词搜�?
使用特定关键词搜索技能：

```bash
python skills/skillsmp-searcher/scripts/search_skills.py "SEO" --limit 10 --sort stars
```

**参数�?*
- `query`: 搜索关键词（必需�?- `--page`: 页码（默认：1�?- `--limit`: 每页项目数（默认�?0，最大：100�?- `--sort`: 按`stars`（默认）或`recent`排序

### AI语义搜索

使用自然语言搜索�?
```bash
python skills/skillsmp-searcher/scripts/ai_search.py "如何创建网络爬虫"
```

### 一键安装技�?🔧

直接从搜索结果安装技能：

```bash
# 搜索并安装第一个结�?python skills/skillsmp-searcher/scripts/install_skill.py "视频编辑"

# 搜索并按索引安装
python skills/skillsmp-searcher/scripts/install_skill.py "PDF" --index 2

# 从直接URL安装
python skills/skillsmp-searcher/scripts/install_skill.py install "https://github.com/user/repo/releases/latest/download/skill.skill"

# 列出已安装的技能
python skills/skillsmp-searcher/scripts/install_skill.py list
```

**安装选项：**
- `query`: 搜索查询或 `.skill` 文件的直接URL/路径
- `--index N`: 安装搜索结果中的第N个技能（默认：1）
- `--page N`: 搜索页码（默认：1）
- `--sort`: 按`stars`（默认）或`recent`排序

### 查看技能详情 ℹ️

获取特定技能的详细信息：

```bash
python skills/skillsmp-searcher/scripts/skill_info.py "技能名称"
```

**详情包括：**
- 作者和星标数
- 版本信息
- 完整描述
- 标签和分类
- 安装命令
- 使用示例

### 检查技能更新 🔄

检查所有已安装技能的可用更新：

```bash
# 检查更新（遵守1小时缓存）
python skills/skillsmp-searcher/scripts/check_updates.py

# 强制检查，即使最近检查过
python skills/skillsmp-searcher/scripts/check_updates.py --force

# 以JSON格式输出
python skills/skillsmp-searcher/scripts/check_updates.py --json
```

**功能：**
- 检查所有已安装技能与SkillsMP商城的对比
- 智能缓存（最多每小时检查一次）
- 显示当前版本与最新版本
- 一行更新命令

## API文档

- **官方API文档**: [https://skillsmp.com/docs/api](https://skillsmp.com/docs/api)
- **中文API文档**: [https://skillsmp.com/zh/docs/api](https://skillsmp.com/zh/docs/api)
- **本地参考文�?*: `skills/skillsmp-searcher/references/api_documentation.md`

## 开�?
### 运行测试

```bash
# 安装依赖
pip install -r requirements.txt

# 运行测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=scripts
```

### 代码质量检�?
```bash
# 格式化代�?black scripts/

# 检查代码风�?flake8 scripts/

# 类型检�?mypy scripts/
```

## 项目结构

```
skillsmp-searcher/
├── .github/
�?  └── workflows/          # CI/CD工作�?├── skills/
�?  └── skillsmp-searcher/  # Skill�?�?      ├── SKILL.md        # Skill元数�?�?      ├── scripts/        # 可执行脚�?�?      ├── references/     # 文档和配�?�?      └── assets/         # 资源文件
├── tests/                  # 测试套件
├── requirements.txt        # Python依赖
└── README.md              # 本文�?```

## 贡献

欢迎贡献！请随时提交Pull Request�?
## 许可�?
本项目采用MIT许可�?- 详见[LICENSE](LICENSE)文件�?
## 相关链接

- [SkillsMP技能商城](https://skillsmp.com/)
- [GitHub仓库](https://github.com/gccszs/skillsmp-searcher)
- [问题追踪](https://github.com/gccszs/skillsmp-searcher/issues)
