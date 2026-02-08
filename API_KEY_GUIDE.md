# API Key Configuration Guide / API密钥配置指南

[English](#english) | [中文](#chinese)

---

## English

### 🔐 Why API Key Security Matters

Your SkillsMP API key is a sensitive credential that grants access to the SkillsMP marketplace API. **Never share it publicly or commit it to version control.**

### 📋 Prerequisites

Before configuring your API key, ensure you have:

1. A SkillsMP account (sign up at https://skillsmp.com/)
2. Access to the SkillsMP Dashboard

### 🔑 Obtaining Your API Key

1. **Visit SkillsMP Dashboard**
   - Go to https://skillsmp.com/
   - Log in to your account

2. **Navigate to API Settings**
   - Look for "API Keys" or "Developer Settings" in your dashboard
   - Click on "Generate New API Key" or "Create Key"

3. **Copy Your API Key**
   - Your API key will look like: `sk_live_skillsmp_xxxxxxxxxxxxxxxxx`
   - **Copy it immediately** - you won't be able to see it again for security reasons
   - Store it securely (password manager, encrypted file, etc.)

### ⚙️ Configuration Methods

We provide **three** methods to configure your API key, ordered from most secure to least secure:

#### Method 1: Environment Variable (Recommended) ✅

**Most secure** - keeps API key out of your codebase and git history.

**For Linux/macOS:**
```bash
# Add to your ~/.bashrc, ~/.zshrc, or ~/.profile
export SKILLSMP_API_KEY="sk_live_skillsmp_your_actual_key_here"

# Reload your shell configuration
source ~/.bashrc  # or ~/.zshrc
```

**For Windows (PowerShell):**
```powershell
# Add to your PowerShell profile
[System.Environment]::SetEnvironmentVariable('SKILLSMP_API_KEY', 'sk_live_skillsmp_your_actual_key_here', 'User')

# Restart PowerShell to apply changes
```

**For Windows (Command Prompt):**
```cmd
setx SKILLSMP_API_KEY "sk_live_skillsmp_your_actual_key_here"
```

**Usage:** The scripts will automatically detect and use the environment variable.

#### Method 2: Configuration File (For Development)

**Moderately secure** - file can be gitignored, but be careful not to accidentally commit it.

1. Create a new file at `skills/skillsmp-searcher/references/api_key_real.txt`
2. Paste your API key (only the key, nothing else):
   ```
   sk_live_skillsmp_your_actual_key_here
   ```
3. **Important:** Verify that `.gitignore` includes this file path:
   ```
   skills/skillsmp-searcher/references/api_key_real.txt
   ```

**⚠️ Security Note:** Always verify this file is in `.gitignore` before committing!

#### Method 3: Command-Line Argument (For One-Time Use)

**Least secure** - API key visible in shell history and process list.

```bash
python skills/skillsmp-searcher/scripts/search_skills.py "SEO" --api-key "sk_live_skillsmp_your_actual_key_here"
```

**⚠️ Warning:** This method should only be used for testing or one-off commands.

### 🔒 Security Best Practices

1. **Never commit API keys to git**
   - Always add API key files to `.gitignore`
   - Use `git-secrets` or similar tools to prevent accidental commits
   - Regularly audit your git history for accidentally committed secrets

2. **Rotate compromised keys**
   - If you suspect your API key has been exposed:
     - Go to SkillsMP Dashboard
     - Delete the compromised key
     - Generate a new key
     - Update your configuration

3. **Use different keys for different environments**
   - Development key for local testing
   - Production key for deployed applications
   - This limits the impact if one key is compromised

4. **Monitor API usage**
   - Check your SkillsMP Dashboard regularly for unusual activity
   - Set up usage alerts if available

### 🧪 Testing Your Configuration

Verify your API key is working:

```bash
# Test with environment variable or config file
python skills/skillsmp-searcher/scripts/search_skills.py "test"

# Expected output:
# Successfully connected to SkillsMP API
# Search results for "test"...
```

### 🆘 Troubleshooting

**Error: "API key not found"**
- Verify your environment variable is set: `echo $SKILLSMP_API_KEY` (Linux/macOS) or `$env:SKILLSMP_API_KEY` (PowerShell)
- Check that your config file exists and contains only the API key

**Error: "Invalid API key"**
- Double-check your API key for typos or extra spaces
- Ensure you copied the entire key (starts with `sk_live_skillsmp_`)
- Verify the key hasn't been revoked in the SkillsMP Dashboard

**Error: "API rate limit exceeded"**
- You're making too many requests. Wait a few minutes before trying again
- Consider implementing caching to reduce API calls

### 📚 Additional Resources

- SkillsMP Documentation: https://skillsmp.com/docs
- API Reference: See `skills/skillsmp-searcher/references/api_documentation.md`
- Security Best Practices: https://skillsmp.com/security

---

## Chinese

### 🔐 为什么API密钥安全很重要

您的SkillsMP API密钥是访问SkillsMP商城API的敏感凭证。**永远不要公开分享或将其提交到版本控制系统。**

### 📋 前置条件

在配置API密钥之前，请确保您拥有：

1. SkillsMP账户（在 https://skillsmp.com/ 注册）
2. 访问SkillsMP控制台的权限

### 🔑 获取您的API密钥

1. **访问SkillsMP控制台**
   - 访问 https://skillsmp.com/
   - 登录您的账户

2. **导航到API设置**
   - 在控制台中查找"API Keys"或"开发者设置"
   - 点击"生成新API密钥"或"创建密钥"

3. **复制您的API密钥**
   - 您的API密钥格式如下：`sk_live_skillsmp_xxxxxxxxxxxxxxxxx`
   - **立即复制** - 出于安全原因，您无法再次查看完整密钥
   - 安全存储（密码管理器、加密文件等）

### ⚙️ 配置方法

我们提供**三种**方法来配置您的API密钥，按安全性从高到低排序：

#### 方法1：环境变量（推荐）✅

**最安全** - 将API密钥保留在代码库和git历史之外。

**Linux/macOS系统：**
```bash
# 添加到 ~/.bashrc、~/.zshrc 或 ~/.profile
export SKILLSMP_API_KEY="sk_live_skillsmp_您的实际密钥"

# 重新加载shell配置
source ~/.bashrc  # 或 ~/.zshrc
```

**Windows（PowerShell）：**
```powershell
# 添加到PowerShell配置文件
[System.Environment]::SetEnvironmentVariable('SKILLSMP_API_KEY', 'sk_live_skillsmp_您的实际密钥', 'User')

# 重启PowerShell以应用更改
```

**Windows（命令提示符）：**
```cmd
setx SKILLSMP_API_KEY "sk_live_skillsmp_您的实际密钥"
```

**使用方法：** 脚本将自动检测并使用环境变量。

#### 方法2：配置文件（用于开发）

**中等安全性** - 文件可以被gitignore，但要注意不要意外提交。

1. 在 `skills/skillsmp-searcher/references/api_key_real.txt` 创建新文件
2. 粘贴您的API密钥（仅密钥本身，不要有其他内容）：
   ```
   sk_live_skillsmp_您的实际密钥
   ```
3. **重要：** 验证 `.gitignore` 包含此文件路径：
   ```
   skills/skillsmp-searcher/references/api_key_real.txt
   ```

**⚠️ 安全提示：** 提交前务必验证此文件在 `.gitignore` 中！

#### 方法3：命令行参数（用于一次性使用）

**安全性最低** - API密钥在shell历史记录和进程列表中可见。

```bash
python skills/skillsmp-searcher/scripts/search_skills.py "SEO" --api-key "sk_live_skillsmp_您的实际密钥"
```

**⚠️ 警告：** 此方法应仅用于测试或单次命令。

### 🔒 安全最佳实践

1. **永远不要将API密钥提交到git**
   - 始终将API密钥文件添加到 `.gitignore`
   - 使用 `git-secrets` 或类似工具防止意外提交
   - 定期审查git历史中是否有意外提交的密钥

2. **轮换已泄露的密钥**
   - 如果您怀疑API密钥已泄露：
     - 前往SkillsMP控制台
     - 删除被泄露的密钥
     - 生成新密钥
     - 更新您的配置

3. **为不同环境使用不同的密钥**
   - 开发密钥用于本地测试
   - 生产密钥用于已部署的应用程序
   - 这样可以在某个密钥泄露时限制影响范围

4. **监控API使用情况**
   - 定期检查SkillsMP控制台是否有异常活动
   - 如果可用，设置使用警报

### 🧪 测试您的配置

验证您的API密钥是否正常工作：

```bash
# 使用环境变量或配置文件测试
python skills/skillsmp-searcher/scripts/search_skills.py "test"

# 预期输出：
# Successfully connected to SkillsMP API
# Search results for "test"...
```

### 🆘 故障排除

**错误："找不到API密钥"**
- 验证环境变量已设置：`echo $SKILLSMP_API_KEY`（Linux/macOS）或 `$env:SKILLSMP_API_KEY`（PowerShell）
- 检查配置文件是否存在且仅包含API密钥

**错误："无效的API密钥"**
- 仔细检查API密钥是否有拼写错误或多余空格
- 确保复制了完整密钥（以 `sk_live_skillsmp_` 开头）
- 验证密钥未在SkillsMP控制台中被撤销

**错误："API速率限制超出"**
- 您的请求过于频繁。等待几分钟后重试
- 考虑实现缓存以减少API调用

### 📚 其他资源

- SkillsMP文档：https://skillsmp.com/docs
- API参考：见 `skills/skillsmp-searcher/references/api_documentation.md`
- 安全最佳实践：https://skillsmp.com/security
