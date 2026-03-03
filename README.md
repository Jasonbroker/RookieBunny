<h1 align="center">RookieBunny</h1>

<p align="center">
  <a href="https://awesome.re">
    <img src="https://awesome.re/badge.svg" alt="Awesome" />
  </a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square" alt="License: MIT" />
  </a>
</p>

A collection of practical Claude Skills for enhancing productivity with AI agents.

---

## Skills

### bird

X/Twitter CLI for reading, searching, and posting tweets via cookies or Sweetistics API.

**Features:**
- Read tweets and threads
- Search tweets
- Post new tweets and replies
- Multiple auth sources (browser cookies or Sweetistics API)

**Quick Start:**
```bash
bird whoami
bird read <url-or-id>
bird thread <url-or-id>
bird search "query" -n 5
```

**Usage:**
```bash
# Read a tweet
bird read https://x.com/user/status/123456789

# Search tweets
bird search "AI agents" -n 10

# Post a tweet (confirm first)
bird tweet "Hello from Claude!"

# Reply to a tweet
bird reply 123456789 "Great point!"
```

**Installation:**
```bash
brew install steipete/tap/bird
```

---

### x-hotspots-scan

Scan X (Twitter) home timeline, extract and organize high-value AI/tech/industry hotspots into a structured report.

**Use Cases:**
- "What's new on X?"
- "What are the X hotspots?"
- "Give me a curated summary of recent X activity"

**Features:**
- Automatic credential detection
- Filters noise and prioritizes high-engagement content
- Categorizes by topic (AI Agents, OpenClaw, Tech Trends, etc.)
- Generates Markdown reports

**Quick Start:**
```bash
./x-hotspots-scan/scripts/simple-scan.sh
```

**Requirements:**
- Logged into x.com in Chrome (Default profile)
- bird CLI installed

**Report Categories:**
1. **AI Agent / Claude 生态** - Agentic AI, Claude Code, Anthropic products
2. **OpenClaw 生态** - OpenClaw tools, skills, community projects
3. **其他 AI/技术热点** - Other AI news, new projects, research
4. **其他热点** - Global news, major platform announcements

---

## Getting Started

### Using Skills in Claude Code

1. Place skills in `~/.config/claude-code/skills/`:
   ```bash
   mkdir -p ~/.config/claude-code/skills/
   cp -r RookieBunny/bird ~/.config/claude-code/skills/
   cp -r RookieBunny/x-hotspots-scan ~/.config/claude-code/skills/
   ```

2. Verify:
   ```bash
   head ~/.config/claude-code/skills/bird/SKILL.md
   ```

3. Start Claude Code:
   ```bash
   claude
   ```

### Skill Structure

```
skill-name/
├── SKILL.md          # Required: Skill instructions and metadata
├── scripts/          # Optional: Helper scripts
├── templates/        # Optional: Document templates
└── resources/       # Optional: Reference files
```

---

## Contributing

Contributions welcome! Please open an issue or submit a PR.

---

## License

MIT License
