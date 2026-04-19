# Quick Start Guide

Get Prompt Economizer running in 5 minutes.

## For SAP Employees

**Using Hyperspace LLM Proxy?** Follow the [SAP Setup Guide](docs/SAP_SETUP.md) instead of this quickstart.

## For Everyone Else

Continue with the standard setup below.

## Step 1: Install (2 minutes)

```bash
cd claude-economizer
python3 scripts/install.py
```

You'll see:
```
╔══════════════════════════════════╗
║   Prompt Economizer Installer    ║
╚══════════════════════════════════╝

  ✓ Python 3.x OK
  ✓ anthropic package installed
  ✓ chmod +x hooks/economizer.sh
  ✓ Created ~/.claude/prompt-economizer
  ✓ Hook registered in settings.json
  ✓ Skill installed
  ✓ Command installed: /economizer-stats
  ✓ Command installed: /economizer-toggle
  ✓ Command installed: /economizer-mode

╔══════════════════════════════════╗
║   Installation Complete! 🎉      ║
╚══════════════════════════════════╝
```

## Step 2: Set API Key (30 seconds)

**For Direct Anthropic API:**
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

Or add to your `~/.zshrc` or `~/.bashrc`:
```bash
echo 'export ANTHROPIC_API_KEY="your-key"' >> ~/.zshrc
```

**For Proxy Users (e.g., SAP Hyperspace):**
```bash
# Start your proxy first (e.g., hai proxy start)
# Then copy the API key from proxy output
export ANTHROPIC_API_KEY="your-proxy-api-key"
export ANTHROPIC_BASE_URL="http://localhost:6655/anthropic/"
```

See [SAP Setup Guide](docs/SAP_SETUP.md) for detailed proxy setup.
```

## Step 3: Restart Claude Code (30 seconds)

Exit and restart Claude Code, or start a new session.

## Step 4: Test It (1 minute)

Type a vague prompt:
```
hey could you maybe look at fixing that bug in the auth system
```

You'll see the optimized version prepended:
```
<!-- [prompt-economizer v1.0.0] tier=small action=compressed ~6 tokens saved in 1200ms -->

Fix bug in auth system.
```

## Step 5: Check Stats (30 seconds)

```
/economizer-stats
```

You'll see:
```
Prompt Economizer Stats
─────────────────────────
Total prompts processed: 1
Total tokens saved (est): 6

By tier:
  small: 1 prompts (avg -40% tokens)
```

## That's It!

Every prompt you type is now automatically optimized.

## Quick Tips

**Skip optimization for a prompt:**
```
* just a quick question, no optimization needed
```

**Manual mode (only optimize when you tag with #opt):**
```
/economizer-mode manual
```

Then use:
```
#opt build a payment service with Stripe
```

**Disable temporarily:**
```
/economizer-toggle
```

Toggle again to re-enable.

**Check your savings:**
```
/economizer-stats
```

## Common First-Time Questions

**Q: Will this slow down my prompts?**  
A: Most prompts are classified instantly via heuristics (no API call). Only ambiguous prompts need ~50 tokens for classification. Total overhead: 0.5-2 seconds.

**Q: What if I don't want a prompt optimized?**  
A: Start it with `*` or use `/economizer-mode manual` to only optimize tagged prompts.

**Q: Can I customize the optimization?**  
A: Yes! Edit `~/.claude/prompt-economizer/config.json`. See README for all options.

**Q: What happens if it fails?**  
A: Graceful fallback — your original prompt always passes through on any error.

**Q: Does it work offline?**  
A: No, it requires the Anthropic API for classification and optimization. But if the API is unavailable, prompts pass through unchanged.

## Next Steps

- Read the full [README.md](README.md) for examples and configuration
- Check [ARCHITECTURE.md](docs/ARCHITECTURE.md) to understand how it works
- Customize `~/.claude/prompt-economizer/config.json` to your preferences

---

**Happy optimizing!** Your token bill will thank you.
