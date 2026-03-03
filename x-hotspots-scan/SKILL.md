---
name: x-hotspots-scan
description: "Scan X (Twitter) home timeline, extract and organize high-value AI/tech/industry hotspots into a structured report. Use when user asks what's new on X, wants X hotspots, or needs a curated summary of recent X activity focused on AI, agents, OpenClaw, and tech trends."
---

# X Hotspots Scan

## Overview

Quickly scan X (Twitter) home timeline, filter out noise, extract high-value hotspots, and organize into a structured, information-dense Markdown report.

## Simple Workflow

### 1. Run the scan
```bash
./skills/x-hotspots-scan/scripts/simple-scan.sh
```

That's it! The script will:
1. Check if credentials work with `bird whoami`
2. If not, try to auto-extract from Chrome Default profile
3. If that fails, remind you to login to x.com in Chrome
4. Fetch timeline and generate report

### 2. Requirements
- You must be logged into https://x.com in Chrome (Default profile)
- bird CLI installed

## Filter & Prioritize

Prioritize based on:
- **High engagement**: `likeCount > 500`, `retweetCount > 100`, `replyCount > 50`
- **Key authors**: Known KOLs (levelsio, trq212, karpathy, frxiaobei, etc.)
- **Valuable content**: Contains `article`, `media` links, GitHub repos, concrete data points
- **Relevant domains**: AI agents, Claude/OpenAI/Anthropic, OpenClaw, tech trends, productivity

Filter out:
- Pure rants/emotion without substance
- Ads/promos (unless major product launch)
- Duplicate content
- Off-topic (pure politics/entertainment, unless global breaking news)

## Categories

1. **AI Agent / Claude 生态** - Agentic AI, Claude Code, Anthropic products, skill design
2. **OpenClaw 生态** - OpenClaw tools, skills, community projects
3. **其他 AI/技术热点** - Other AI news, new projects, research, tools
4. **其他热点** - Global news, major platform announcements

## Report Template

```markdown
## X 热点报告（YYYY-MM-DD）

### 1. AI Agent / Claude 生态
- **标题**：一句话总结
  - 摘要：...
  - 来源：@用户名
  - 链接：...

### 2. OpenClaw 生态
- **标题**：一句话总结
  - 摘要：...
  - 来源：@用户名
  - 链接：...

### 3. 其他 AI/技术热点
- **标题**：一句话总结
  - 摘要：...
  - 来源：@用户名
  - 链接：...

### 4. 其他热点
- **标题**：一句话总结
  - 摘要：...
  - 来源：@用户名
  - 链接：...
```

## Key Judgment Reference

| Signal | Priority |
|--------|----------|
| likeCount > 1000 | 🔴 High |
| retweetCount > 100 | 🔴 High |
| replyCount > 50 | 🟡 Medium |
| Contains `article` link | 🟡 Medium |
| Author is known KOL | 🟡 Medium |
| Contains GitHub link | 🟡 Medium |

## Resources

### references/
- `judgment-criteria.md` - Detailed filtering and prioritization guidelines
- `kol-list.md` - List of X accounts to prioritize
