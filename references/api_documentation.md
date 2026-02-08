# SkillsMP API Documentation

## Base URL
```
https://skillsmp.com/api/v1
```

## Authentication

All API requests require authentication using an API Key via Bearer token.

**Header**: `Authorization: Bearer <api_key>`

**Example API Key**: `sk_live_skillsmp_eb_6A4Y9LJAhtzPFsmX0v67zhingVC0CrQZ4Qqlin4`

**Key Management**:
- Regenerate Key: Click "Regenerate Key" button in the dashboard
- Delete Key: Click "Delete Key" button in the dashboard
- Usage Tracking: Monitor creation date and last used timestamp

## Endpoints

### 1. Keyword Search

Search skills using keywords.

**Endpoint**: `GET /skills/search`

**Parameters**:

| Parameter | Type   | Required | Description                                |
|-----------|--------|----------|--------------------------------------------|
| q         | string | Yes      | Search query (keyword)                    |
| page      | number | No       | Page number (default: 1)                   |
| limit     | number | No       | Items per page (default: 20, max: 100)    |
| sortBy    | string | No       | Sort by: `stars` (default) or `recent`     |

**Example Request**:
```bash
curl -X GET "https://skillsmp.com/api/v1/skills/search?q=SEO" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Example Request with Pagination**:
```bash
curl -X GET "https://skillsmp.com/api/v1/skills/search?q=SEO&page=1&limit=10&sortBy=stars" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### 2. AI Semantic Search

AI-powered semantic search using Cloudflare AI.

**Endpoint**: `GET /skills/ai-search`

**Parameters**:

| Parameter | Type   | Required | Description                    |
|-----------|--------|----------|--------------------------------|
| q         | string | Yes      | Natural language search query  |

**Example Request**:
```bash
curl -X GET "https://skillsmp.com/api/v1/skills/ai-search?q=How+to+create+a+web+scraper" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## Response Format

### Success Response

```json
{
  "success": true,
  "data": {
    "skills": [
      {
        "id": "skill_id",
        "name": "Skill Name",
        "description": "Skill description...",
        "author": "Author Name",
        "stars": 42,
        "relevance_score": 0.95
      }
    ],
    "total": 100,
    "page": 1,
    "limit": 20
  }
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message"
  }
}
```

## Error Codes

| Error Code         | HTTP Status | Description                           |
|--------------------|-------------|---------------------------------------|
| MISSING_API_KEY    | 401         | API key not provided                  |
| INVALID_API_KEY    | 401         | The provided API key is invalid       |
| MISSING_QUERY      | 400         | Missing required query parameter      |
| INTERNAL_ERROR     | 500         | Internal server error                 |

## Rate Limiting

Please refer to the SkillsMP dashboard for current rate limits and usage statistics.

## SDK Examples

### Python

```python
import requests

def search_skills(query, api_key):
    url = "https://skillsmp.com/api/v1/skills/search"
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {"q": query}

    response = requests.get(url, headers=headers, params=params)
    return response.json()

# Usage
results = search_skills("SEO", "your_api_key_here")
```

### JavaScript

```javascript
async function searchSkills(query, apiKey) {
  const url = new URL('https://skillsmp.com/api/v1/skills/search');
  url.searchParams.append('q', query);

  const response = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${apiKey}`
    }
  });

  return await response.json();
}

// Usage
const results = await searchSkills('SEO', 'your_api_key_here');
```
