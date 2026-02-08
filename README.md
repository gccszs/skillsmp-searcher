# SkillsMP Searcher

[English](README.md) | [简体中文](README_CN.md)

---

**SkillsMP Searcher** is a Claude Code skill that enables powerful search capabilities for the [SkillsMP](https://skillsmp.com/) skill marketplace. It provides both keyword-based search and AI-powered semantic search to help you quickly discover and install useful skills.

## Features

- **Keyword Search**: Search skills by specific keywords with pagination and sorting options
- **AI Semantic Search**: Use natural language queries to find relevant skills powered by Cloudflare AI
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Python 3.9+**: Supports Python 3.9, 3.10, 3.11, and 3.12
- **Secure API Key Management**: Multiple configuration methods with security best practices

## Installation

1. Download the latest `skillsmp-searcher.skill` from [Releases](https://github.com/gccszs/skillsmp-searcher/releases)
2. Install the skill in Claude Code:
   ```bash
   claude skill install skillsmp-searcher.skill
   ```

## Configuration

### 🔑 API Key Setup

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

### ⚠️ Security Best Practices

- **Never commit API keys** to version control
- **Use environment variables** for production deployments
- **Rotate compromised keys** immediately at [SkillsMP Dashboard](https://skillsmp.com/)
- **Monitor API usage** for unusual activity

> 💡 **Tip**: Copy `.env.example` to `.env` and fill in your API key for local development. The `.env` file is automatically gitignored.

## Usage

### Keyword Search

Search for skills using specific keywords:

```bash
python skills/skillsmp-searcher/scripts/search_skills.py "SEO" --limit 10 --sortBy stars
```

**Parameters:**
- `query`: Search keyword (required)
- `--page`: Page number (default: 1)
- `--limit`: Items per page (default: 20, max: 100)
- `--sort`: Sort by `stars` (default) or `recent`

### AI Semantic Search

Search using natural language:

```bash
python skills/skillsmp-searcher/scripts/ai_search.py "How to create a web scraper"
```

## API Documentation

- **Official API Documentation**: [https://skillsmp.com/docs/api](https://skillsmp.com/docs/api)
- **Local Reference**: `skills/skillsmp-searcher/references/api_documentation.md`

## Development

### Running Tests

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Run tests with coverage
pytest --cov=scripts
```

### Code Quality

```bash
# Format code
black scripts/

# Check code style
flake8 scripts/

# Type checking
mypy scripts/
```

## Project Structure

```
skillsmp-searcher/
├── .github/
│   └── workflows/          # CI/CD workflows
├── skills/
│   └── skillsmp-searcher/  # Skill package
│       ├── SKILL.md        # Skill metadata
│       ├── scripts/        # Executable scripts
│       ├── references/     # Documentation and configs
│       └── assets/         # Resource files
├── tests/                  # Test suite
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Links

- [SkillsMP Marketplace](https://skillsmp.com/)
- [GitHub Repository](https://github.com/gccszs/skillsmp-searcher)
- [Issue Tracker](https://github.com/gccszs/skillsmp-searcher/issues)
