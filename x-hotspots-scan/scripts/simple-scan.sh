#!/bin/bash
# Simple X Hotspots Scan - no complex setup, just scan

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$PWD"
COOKIES_FILE="$WORKSPACE_DIR/bird.cookies"

# Create output directory
OUTPUT_DIR="$WORKSPACE_DIR/x_hotspot"
mkdir -p "$OUTPUT_DIR"

# Date with timestamp (for multiple runs per day)
DATE=$(date +%Y-%m-%d)
DATETIME=$(date +%Y-%m-%d-%H%M)
TIMELINE_FILE="$OUTPUT_DIR/x-timeline-$DATETIME.json"
REPORT_FILE="$OUTPUT_DIR/x-hotspots-$DATETIME.md"

echo "=== X Hotspots Scan ==="
echo "Date: $DATE"
echo "Output: $OUTPUT_DIR"
echo ""

# Function to load cookies from bird.cookies
load_cookies_from_file() {
    if [ -f "$COOKIES_FILE" ]; then
        echo "📄 Found bird.cookies file, trying to load..."
        if [ -s "$COOKIES_FILE" ]; then
            # Read the raw cookie string (header format)
            local raw_cookie
            raw_cookie=$(cat "$COOKIES_FILE" | tr -d '\n\r')
            
            # Try to extract auth_token and ct0 from header string format
            # Format: auth_token=xxx; ct0=xxx; other=cookie...
            AUTH_TOKEN=$(echo "$raw_cookie" | grep -oE 'auth_token=[^;]+' | cut -d'=' -f2 || echo "")
            CT0=$(echo "$raw_cookie" | grep -oE 'ct0=[^;]+' | cut -d'=' -f2 || echo "")
            
            # Also try KEY=value format (env var format in the same file)
            if [ -z "$AUTH_TOKEN" ]; then
                AUTH_TOKEN=$(grep -E '^AUTH_TOKEN=' "$COOKIES_FILE" 2>/dev/null | cut -d'=' -f2 | tr -d '"' || echo "")
            fi
            if [ -z "$CT0" ]; then
                CT0=$(grep -E '^CT0=' "$COOKIES_FILE" 2>/dev/null | cut -d'=' -f2 | tr -d '"' || echo "")
            fi
            
            if [ -n "$AUTH_TOKEN" ] && [ -n "$CT0" ]; then
                echo "🔑 Loaded AUTH_TOKEN and CT0 from bird.cookies"
                export AUTH_TOKEN
                export CT0
                return 0
            else
                echo "⚠️  bird.cookies is missing AUTH_TOKEN or CT0"
            fi
        else
            echo "⚠️  bird.cookies is empty"
        fi
    fi
    return 1
}

# Function to verify credentials
verify_creds() {
    if bird whoami &> /dev/null; then
        return 0
    fi
    return 1
}

# Step 1: Check if credentials work
echo "🔍 Checking credentials..."
if ! verify_creds; then
    echo "⚠️  Credentials not valid or missing."
    echo ""
    
    # Try Chrome first
    echo "🔧 Trying to get credentials from Chrome Default profile..."
    echo ""
    if bird --chrome-profile Default whoami 2>&1; then
        echo ""
        echo "✅ Credentials found! Saving config..."
        mkdir -p ~/.config/bird
        cat > ~/.config/bird/config.json5 <<EOF
{
  chromeProfile: "Default"
}
EOF
        echo ""
        echo "✅ Credentials set up successfully!"
    else
        echo ""
        echo "⚠️  Can't get credentials from Chrome."
        echo ""
        
        # Try bird.cookies file
        if load_cookies_from_file; then
            echo ""
            echo "🔍 Verifying credentials from bird.cookies..."
            if verify_creds; then
                echo "✅ Credentials from bird.cookies are valid!"
            else
                echo ""
                echo "❌ Credentials from bird.cookies are invalid."
                echo ""
                echo "💡 Please update bird.cookies with valid AUTH_TOKEN and CT0, then press Enter to retry..."
                read -r
                
                # Try again after user update
                echo ""
                echo "🔍 Re-checking credentials..."
                if load_cookies_from_file && verify_creds; then
                    echo "✅ Credentials now valid!"
                else
                    echo ""
                    echo "❌ Still invalid. Stopping here - no further attempts."
                    exit 1
                fi
            fi
        else
            echo ""
            echo "❌ No bird.cookies file found or file is invalid."
            echo ""
            echo "💡 Please create bird.cookies in the workspace with:"
            echo "  AUTH_TOKEN=your_auth_token_here"
            echo "  CT0=your_ct0_here"
            echo ""
            echo "Then press Enter to retry..."
            read -r
            
            # Try again after user creates file
            echo ""
            echo "🔍 Checking bird.cookies..."
            if load_cookies_from_file && verify_creds; then
                echo "✅ Credentials now valid!"
            else
                echo ""
                echo "❌ Still invalid. Stopping here - no further attempts."
                exit 1
            fi
        fi
    fi
fi

echo "✅ Credentials OK"
echo ""

# Step 2: Fetch timeline
echo "📥 Fetching home timeline..."
bird home --json -n 40 > "$TIMELINE_FILE"
echo "✅ Timeline saved"
echo ""

# Step 3: Generate report
echo "📊 Generating report..."
python3 "$SCRIPT_DIR/generate-report.py" "$TIMELINE_FILE" "$REPORT_FILE"
echo ""
echo "✅ Report generated: $REPORT_FILE"

# Step 4: Send to Telegram by sections
if command -v openclaw &> /dev/null; then
    echo "📤 Sending report to Telegram by sections..."
    
    # Send header
    openclaw message send --message "📊 X 热点报告 $(date +%Y-%m-%d)" --best-effort 2>/dev/null || true
    
    # Extract and send each section
    section_num=0
    awk '/^## /{section=$0; content=""; getline} /^- \*\*/{content=content $0 "\n"; getline; while(/^  - /){content=content $0 "\n"; getline}} content!=""{print section; print content; print "---"; content=""}' "$REPORT_FILE" | \
    while IFS= read -r line; do
        if [[ "$line" == "## "* ]]; then
            # Section header
            section_title="${line#### }"
            openclaw message send --message "📌 $section_title" --best-effort 2>/dev/null || true
            sleep 0.5
        elif [[ "$line" == "---" ]]; then
            continue
        elif [[ -n "$line" ]]; then
            # Content line
            openclaw message send --message "$line" --best-effort 2>/dev/null || true
            sleep 0.3
        fi
    done
    
    echo "✅ Report sent to Telegram by sections"
else
    echo "⚠️  openclaw CLI not found, skipping Telegram send"
fi
echo ""
echo "✅ Done!"
