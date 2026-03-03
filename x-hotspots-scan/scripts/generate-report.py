#!/usr/bin/env python3
"""
X Hotspots Scan - Report Generator
Processes bird CLI JSON output and generates a structured Markdown report.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# KOL list (from references/kol-list.md)
KOL_ACCOUNTS = {
    "levelsio", "trq212", "karpathy", "bcherny", "zackbshapiro",
    "frxiaobei", "seekjourney", "realNyarime", "ring_hyacinth", "sitinme",
    "heynavtoor", "chuhaiqu", "AI_Jasonyu", "GitHubDaily",
    "elonmusk", "AnthropicAI", "OpenAI", "GoogleAI"
}

# Keywords for filtering
RELEVANT_KEYWORDS = {
    "AI agent", "Claude", "Anthropic", "OpenAI", "GPT",
    "OpenClaw", "skill", "agent", "workflow",
    "GitHub", "launch", "release", "product",
    "research", "paper", "breakthrough", "trend"
}

def load_timeline(json_path):
    """Load timeline from bird CLI JSON output."""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_text(tweet):
    """Get tweet text, handling both 'text' and 'fullText' fields."""
    # bird CLI uses 'text' (not 'full_text')
    return tweet.get('text', '')

def get_author_username(tweet):
    """Get author username from author object."""
    author = tweet.get('author', {})
    return author.get('username', '').lower() if isinstance(author, dict) else ''

def get_author_name(tweet):
    """Get author display name."""
    author = tweet.get('author', {})
    return author.get('name', '') if isinstance(author, dict) else ''

def get_engagement(tweet):
    """Get engagement metrics."""
    # bird CLI uses camelCase
    return {
        'likes': tweet.get('likeCount', 0),
        'retweets': tweet.get('retweetCount', 0),
        'replies': tweet.get('replyCount', 0)
    }

def get_urls(tweet):
    """Extract URLs from tweet."""
    # bird CLI may have URLs in the text or entities
    entities = tweet.get('entities', {})
    if isinstance(entities, dict):
        urls = entities.get('urls', [])
        return [u.get('expandedUrl', u.get('url', '')) for u in urls]
    return []

def get_tweet_url(tweet):
    """Get tweet URL."""
    username = get_author_username(tweet)
    tweet_id = tweet.get('id', '')
    if username and tweet_id:
        return f"https://x.com/{username}/status/{tweet_id}"
    return ''

def calculate_priority(tweet):
    """Calculate priority score for a tweet."""
    score = 0
    author = get_author_username(tweet)
    eng = get_engagement(tweet)
    text = get_text(tweet).lower()
    
    likes = eng['likes']
    retweets = eng['retweets']
    replies = eng['replies']
    
    # High engagement
    if likes > 1000:
        score += 10
    elif likes > 500:
        score += 5
        
    if retweets > 100:
        score += 10
    elif retweets > 50:
        score += 5
        
    if replies > 50:
        score += 5
        
    # KOL author
    if author in KOL_ACCOUNTS:
        score += 15
        
    # Relevant keywords
    for keyword in RELEVANT_KEYWORDS:
        if keyword.lower() in text:
            score += 3
            break
            
    # Has links
    urls = get_urls(tweet)
    if urls:
        score += 2
        
    return score

def categorize_tweet(tweet):
    """Categorize a tweet into one of the standard categories."""
    text = get_text(tweet).lower()
    author = get_author_username(tweet)
    
    # OpenClaw ecosystem
    openclaw_keywords = {"openclaw", "clawhub", "clawfeed", "agent-reach"}
    openclaw_authors = {"frxiaobei", "seekjourney", "realNyarime", "ring_hyacinth", "sitinme"}
    if any(kw in text for kw in openclaw_keywords) or author in openclaw_authors:
        return "OpenClaw 生态"
        
    # AI Agent / Claude ecosystem
    claude_keywords = {"claude", "anthropic", "ai agent", "agentic", "claude code"}
    claude_authors = {"trq212", "bcherny", "zackbshapiro"}
    if any(kw in text for kw in claude_keywords) or author in claude_authors:
        return "AI Agent / Claude 生态"
        
    # Other AI/tech
    ai_keywords = {"openai", "gpt", "github", "research", "paper", "launch", "release"}
    ai_authors = {"karpathy", "levelsio", "GitHubDaily", "AI_Jasonyu"}
    if any(kw in text for kw in ai_keywords) or author in ai_authors:
        return "其他 AI/技术热点"
        
    # Other
    return "其他热点"

def generate_report(timeline, output_path):
    """Generate a structured Markdown report."""
    # Filter and score tweets
    scored_tweets = []
    for tweet in timeline:
        text = get_text(tweet)
        # Skip retweets
        if text.startswith('RT '):
            continue
            
        score = calculate_priority(tweet)
        if score >= 5:  # Only include relevant tweets
            scored_tweets.append((score, tweet))
            
    # Sort by score descending
    scored_tweets.sort(key=lambda x: x[0], reverse=True)
    
    # Categorize
    categories = {
        "AI Agent / Claude 生态": [],
        "OpenClaw 生态": [],
        "其他 AI/技术热点": [],
        "其他热点": []
    }
    
    for score, tweet in scored_tweets[:20]:  # Top 20
        category = categorize_tweet(tweet)
        categories[category].append((score, tweet))
        
    # Generate Markdown
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    md = f"# X 热点报告（{date_str}）\n\n"
    
    for category, tweets in categories.items():
        if not tweets:
            continue
            
        md += f"## {category}\n\n"
        
        for score, tweet in tweets:
            username = get_author_username(tweet)
            name = get_author_name(tweet)
            text = get_text(tweet).strip()
            tweet_url = get_tweet_url(tweet)
            urls = get_urls(tweet)
            
            # Create a headline (first sentence or first 80 chars)
            headline = text.split('\n')[0][:80]
            if len(headline) < len(text):
                headline += "..."
                
            md += f"- **{headline}**\n"
            md += f"  - 摘要：{text[:200]}{'...' if len(text) > 200 else ''}\n"
            md += f"  - 来源：@{username} ({name})\n"
            if tweet_url:
                md += f"  - 链接：{tweet_url}\n"
            elif urls:
                md += f"  - 链接：{urls[0]}\n"
            md += "\n"
            
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md)
        
    print(f"Report generated: {output_path}")
    print(f"Total hotspots found: {len(scored_tweets)}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate-report.py <timeline.json> [output.md]")
        sys.exit(1)
        
    json_path = sys.argv[1]
    if len(sys.argv) >= 3:
        output_path = sys.argv[2]
    else:
        date_str = datetime.now().strftime('%Y-%m-%d')
        output_path = f"x-hotspots-{date_str}.md"
        
    timeline = load_timeline(json_path)
    generate_report(timeline, output_path)

if __name__ == "__main__":
    main()
