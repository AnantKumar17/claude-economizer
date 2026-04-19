# SAP Employee Setup Guide

## Using Claude Economizer with Hyperspace LLM Proxy

SAP employees should use the **Hyperspace LLM Proxy** instead of direct Anthropic API access. This guide shows you how.

## Quick Setup (3 Steps)

### Step 1: Install hai CLI

Follow the [Hyperspace Quickstart Guide](https://hAIperspace.github.io/docs/quickstart) to install hai CLI for your platform.

**macOS (Homebrew):**
```bash
# Install GitHub CLI first
brew install gh
gh auth login --hostname github.tools.sap

# Add the hAIperspace tap
brew tap hAIperspace/hai https://github.tools.sap/hAIperspace/hai-homebrew

# Install hai
brew install hai

# Verify
hai version
```

### Step 2: Start the Proxy

```bash
hai proxy start
```

You'll see output like this:
```
⚡ Hyperspace AI - Local LLM Proxy
┌ 📊 Information ────────────────────────────────────────────┐
│  Status:         🟢 Ready                                  │
│  Proxy URL:      http://localhost:6655                     │
│  API Key:        282fa5fc-7025-42f0-9ad0-b003022ff8f7      │
└────────────────────────────────────────────────────────────┘
```

**Important:** Keep this terminal window open while using Claude Economizer.

### Step 3: Configure Claude Economizer for Proxy

Copy the API key from the proxy output above, then set these environment variables:

```bash
# Copy the API key from your hai proxy terminal
export ANTHROPIC_API_KEY="282fa5fc-7025-42f0-9ad0-b003022ff8f7"

# Set the proxy URL
export ANTHROPIC_BASE_URL="http://localhost:6655/anthropic/"
```

**That's it!** Claude Economizer will now route all API calls through the Hyperspace proxy.

## Permanent Setup

To avoid setting these variables every time, add them to your shell profile:

**For zsh (macOS default):**
```bash
echo 'export ANTHROPIC_BASE_URL="http://localhost:6655/anthropic/"' >> ~/.zshrc
```

**For bash:**
```bash
echo 'export ANTHROPIC_BASE_URL="http://localhost:6655/anthropic/"' >> ~/.bashrc
```

**Note:** You'll still need to copy the API key each time you start the proxy, as it changes with each session.

## Quick Start Script (Optional)

Create a helper script to start the proxy and set variables automatically:

```bash
#!/bin/bash
# save as: ~/start-claude-economizer.sh

echo "Starting Hyperspace Proxy..."
hai proxy start &
PROXY_PID=$!

sleep 3  # Give proxy time to start

# Extract API key from proxy output (if running in same terminal)
# Note: You may need to copy this manually from the proxy terminal
echo ""
echo "================================================"
echo "Copy the API key from the proxy terminal above"
echo "Then run:"
echo "  export ANTHROPIC_API_KEY='your-api-key-here'"
echo "================================================"
```

Make it executable:
```bash
chmod +x ~/start-claude-economizer.sh
```

## Verification

Test that Claude Economizer can reach the proxy:

```bash
# Test with a simple prompt
echo '{"prompt":"test"}' | python3 ~/.claude/claude-economizer/hooks/economizer.py
```

If working correctly, you should see the prompt pass through (since it's very short).

Check the logs:
```bash
tail -f ~/.claude/prompt-economizer/economizer.log
```

You should see log entries without "No API key found" warnings.

## Configuration Notes

### Model Names

The Hyperspace proxy uses different model names than direct Anthropic API. Update your config if needed:

**Default (works with proxy):**
```json
{
  "model": "claude-haiku-4-5-20251001",
  "complexity_model": "claude-haiku-4-5-20251001",
  "optimization_model": "claude-haiku-4-5-20251001"
}
```

**If you get model errors, try:**
```json
{
  "model": "anthropic--claude-haiku-latest",
  "complexity_model": "anthropic--claude-haiku-latest",
  "optimization_model": "anthropic--claude-haiku-latest"
}
```

Edit: `~/.claude/prompt-economizer/config.json`

### Checking Proxy Usage

Monitor proxy activity in the hai proxy terminal. You'll see requests like:
```
level=INFO msg="Proxying request" method=POST source=/anthropic/v1/messages
```

This confirms Claude Economizer is routing through the proxy.

## Troubleshooting

### "No API key found" in logs

**Problem:** ANTHROPIC_API_KEY not set

**Solution:** 
```bash
export ANTHROPIC_API_KEY="your-key-from-proxy"
```

### "Connection refused" errors

**Problem:** Proxy not running

**Solution:**
```bash
hai proxy start
```

Keep that terminal open!

### "Invalid model" errors

**Problem:** Model name incompatible with proxy

**Solution:** Update config to use `anthropic--claude-haiku-latest` format (see Configuration Notes above)

### API key changes every session

**Expected behavior:** The proxy generates a new API key each time it starts. This is normal.

**Solution:** Copy the new key each time you run `hai proxy start`

## Production Use

When using Claude Economizer with Hyperspace proxy at SAP:

[PERMITTED] Using approved Anthropic models (Haiku, Sonnet, Opus)
[PERMITTED] Claude Code CLI and VS Code extension with proxy
[REQUIRED] Follow [SAP Production Use Guide](https://hAIperspace.github.io/docs/guides/production-use)

[NOT PERMITTED] Direct Anthropic API access (use proxy instead)
[NOT PERMITTED] Claude Desktop App (separate from CLI)

## Comparison: Direct API vs Proxy

| Aspect | Direct Anthropic API | Hyperspace Proxy (SAP) |
|--------|---------------------|------------------------|
| API Key | Static, set once | Dynamic, changes per session |
| Base URL | api.anthropic.com | localhost:6655 |
| Setup | `export ANTHROPIC_API_KEY` | `hai proxy start` + export key |
| Cost | Billed to your account | Tracked via SAP proxy |
| Compliance | Self-managed | SAP-managed |
| Best for | Individual developers | SAP employees |

## Integration with Claude Code

If you're also using Claude Code CLI with the proxy:

**Shared configuration:**
Both Claude Code and Claude Economizer can use the same proxy! Just make sure:
1. Proxy is running: `hai proxy start`
2. Both tools have `ANTHROPIC_BASE_URL` set to the proxy
3. Both tools have `ANTHROPIC_API_KEY` set to the current proxy key

**No conflicts:**
They'll both route through the proxy simultaneously without issues.

## Support

**Hyperspace Proxy Issues:**
- [Hyperspace AI Community (LLM Proxy Channel)](https://hAIperspace.github.io/docs/support)
- Frontrunners DL: Subscribe for updates

**Claude Economizer Issues:**
- Check logs: `~/.claude/prompt-economizer/economizer.log`
- See main [README.md](../README.md) troubleshooting section

## Quick Reference

```bash
# Start proxy
hai proxy start

# Set environment (copy key from proxy output)
export ANTHROPIC_API_KEY="<key-from-proxy>"
export ANTHROPIC_BASE_URL="http://localhost:6655/anthropic/"

# Verify economizer works
echo '{"prompt":"test connection"}' | python3 hooks/economizer.py

# Check logs
tail -f ~/.claude/prompt-economizer/economizer.log

# View stats (after using it)
# In Claude Code session:
/economizer-stats
```

---

**You're all set!** Claude Economizer will now route all optimizations through your SAP Hyperspace proxy, keeping you compliant and tracked within SAP's AI usage system.
