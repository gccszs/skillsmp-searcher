---
name: skillsmp-searcher
description: SkillsMP技能商城搜索和管理工具。提供在 https://skillsmp.com/ 网站上搜索、查看详情、安装和更新技能的完整功能。支持关键词搜索和AI语义搜索两种模式。当用户需要：(1) 搜索特定主题的技能（如"SEO"、"视频制作"），(2) 通过自然语言描述查找相关技能（如"如何创建网络爬虫"），(3) 查看技能详细信息（版本、作者、评分、示例），(4) 一键安装发现的技能，(5) 检查已安装技能的更新，(6) 管理本地技能库时使用此技能。
---

# SkillsMP 技能搜索

此技能提供对 SkillsMP 技能商城的搜索功能，帮助用户快速发现和定位所需的技能。

## API 配置

首次使用前，需要配置 API Key。支持三种配置方式（按优先级排序）：

1. **环境变量**（推荐）：设置 `SKILLSMP_API_KEY` 环境变量
2. **开发密钥文件**：创建 `references/api_key_real.txt`（已在 .gitignore 中）
3. **模板文件**：编辑 `references/api_key.txt`

格式：纯文本的 API Key 字符串（例如：`sk_live_skillsmp_eb_6A4Y9LJAhtzPFsmX0v67zhingVC0CrQZ4Qqlin4`）

**注意**：
- `api_key_real.txt` 已加入 .gitignore，不会被提交到公共仓库
- 请勿将包含真实 API Key 的文件提交到公共仓库
- 文件支持 `#` 开头的注释行，会自动跳过

## 搜索模式

### 1. 关键词搜索

使用 `scripts/search_skills.py` 进行基于关键词的搜索。

**适用场景**：
- 用户使用明确的关键词搜索（如 "SEO"、"PDF"、"翻译"）
- 需要按热门度或最新时间排序
- 需要分页浏览结果

**参数**：
- `q` (必需): 搜索关键词
- `page`: 页码，默认 1
- `limit`: 每页数量，默认 20，最大 100
- `sortBy`: 排序方式，`stars`（热门，默认）或 `recent`（最新）

**示例**：
```bash
python scripts/search_skills.py "SEO" --page 1 --limit 10 --sortBy stars
```

### 2. AI 语义搜索

使用 `scripts/ai_search.py` 进行基于语义理解的搜索。

**适用场景**：
- 用户使用自然语言描述需求（如"如何制作视频"、"帮我处理PDF文档"）
- 搜索意图复杂，需要理解上下文
- 不确定具体关键词，希望AI智能匹配

**参数**：
- `q` (必需): 自然语言搜索查询

**示例**：
```bash
python scripts/ai_search.py "How to create a web scraper"
```

### 3. 一键安装技能

使用 `scripts/install_skill.py` 搜索并安装技能。

**适用场景**：
- 用户搜索到技能后直接安装
- 从URL直接安装技能文件
- 管理已安装的技能

**命令**：
- `install` [query] [--index N]: 搜索并安装第N个技能（默认第1个）
- `install` [url/path]: 直接从URL或本地路径安装
- `list`: 列出所有已安装的技能

**示例**：
```bash
# 搜索并安装第一个结果
python scripts/install_skill.py install "视频编辑"

# 搜索并安装指定索引的技能
python scripts/install_skill.py install "PDF" --index 2

# 从URL直接安装
python scripts/install_skill.py install "https://example.com/skill.skill"

# 从本地文件安装
python scripts/install_skill.py install "/path/to/skill.skill"

# 列出已安装的技能
python scripts/install_skill.py list
```

**功能**：
- 自动解压并安装技能到Claude Code技能目录
- 支持从URL或本地文件安装
- 列出已安装的所有技能

### 4. 查看技能详情

使用 `scripts/skill_info.py` 查看特定技能的详细信息。

**适用场景**：
- 需要了解技能的完整信息
- 查看技能的版本、作者、评分、标签
- 获取技能的使用示例和安装命令

**参数**：
- `skill_id` (必需): 技能ID或名称
- `--json`: 输出原始JSON格式
- `--api-key`: 自定义API密钥

**示例**：
```bash
# 查看技能详细信息
python scripts/skill_info.py "pdf-processor"

# 以JSON格式输出
python scripts/skill_info.py "video-editor" --json
```

**显示内容**：
- 技能名称、作者、星级评分
- 版本号和详细描述
- 分类标签
- 仓库链接和安装命令
- 依赖要求
- 使用示例

### 5. 检查技能更新

使用 `scripts/check_updates.py` 检查已安装技能的更新。

**适用场景**：
- 定期检查已安装技能是否有新版本
- 获取最新版本的版本号和评分
- 决定是否需要更新技能

**参数**：
- `--force`: 强制检查（忽略缓存）
- `--json`: 输出JSON格式
- `--api-key`: 自定义API密钥

**示例**：
```bash
# 检查所有已安装技能的更新
python scripts/check_updates.py

# 强制检查（绕过1小时缓存）
python scripts/check_updates.py --force

# 以JSON格式输出
python scripts/check_updates.py --json
```

**功能**：
- 自动扫描Claude Code技能目录
- 对比本地版本与SkillsMP商城最新版本
- 智能缓存机制（1小时内不重复检查）
- 显示可更新技能的升级路径和安装命令

## API 端点

详细的 API 文档请参考 `references/api_documentation.md`。

**基础 URL**: `https://skillsmp.com/api/v1`

| 端点 | 方法 | 功能 |
|------|------|------|
| `/skills/search` | GET | 关键词搜索 |
| `/skills/ai-search` | GET | AI 语义搜索 |

## 错误处理

API 错误码：

| 错误码 | HTTP状态 | 说明 |
|--------|----------|------|
| `MISSING_API_KEY` | 401 | 未提供 API Key |
| `INVALID_API_KEY` | 401 | API Key 无效 |
| `MISSING_QUERY` | 400 | 缺少必需的查询参数 |
| `INTERNAL_ERROR` | 500 | 服务器内部错误 |

错误响应格式：
```json
{
  "success": false,
  "error": {
    "code": "INVALID_API_KEY",
    "message": "The provided API key is invalid"
  }
}
```

## 使用流程

**搜索和安装技能**：
1. 确保 API Key 已配置（优先使用环境变量 `SKILLSMP_API_KEY`）
2. 根据需求选择搜索模式：
   - 明确关键词 → 关键词搜索（`search_skills.py`）
   - 自然语言描述 → AI 语义搜索（`ai_search.py`）
3. 搜索后可直接安装：
   - 使用索引安装：`install_skill.py install "关键词" --index N`
   - 从URL直接安装：`install_skill.py install "URL"`

**管理已安装技能**：
1. 列出已安装技能：`install_skill.py list`
2. 查看技能详情：`skill_info.py "技能名"`
3. 检查更新：`check_updates.py`

**注意事项**：
- 首次使用必须配置 API Key
- 搜索结果默认按热门度排序
- 技能安装到 `~/.claude/skills/` 或系统对应的技能目录
- 更新检查有1小时缓存，使用 `--force` 可绕过
