# Prompt Economizer

**Bidirectional prompt optimizer for Claude Code**

Optimize for net token cost, not just prompt length. Compresses small tasks, structures large ones.

## What It Does

Most prompt optimizers only expand prompts. This is wrong. The right metric is **net token ROI**:

```
net_cost = optimizer_tokens + prompt_tokens - downstream_savings - re-prompt_savings
```

Prompt Economizer optimizes in BOTH directions:
- **Small task** → Compress + tighten (save prompt tokens)
- **Medium task** → Restructure with context (save re-prompt cycles)
- **Large task** → Full prompt engineering (save massive downstream waste)

## Quick Start

### For SAP Employees

**Using Hyperspace LLM Proxy?** See [SAP Setup Guide](docs/SAP_SETUP.md) for proxy configuration.

### For Everyone Else

```bash
git clone https://github.com/AnantKumar17/claude-economizer.git
cd claude-economizer
python3 scripts/install.py
```

Set your API key:
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

**Or if using a proxy (like SAP Hyperspace):**
```bash
export ANTHROPIC_API_KEY="your-proxy-api-key"
export ANTHROPIC_BASE_URL="http://localhost:6655/anthropic/"
```

Restart Claude Code. Done. Every prompt you type will be automatically optimized.

## How It Works

```
User types prompt
     ↓
Heuristic classification (instant)
     ↓
LLM classification if needed (~50 tokens)
     ↓
Apply optimization strategy
     ├─ passthrough: no change
     ├─ small: compress (~100 tokens)
     ├─ medium: restructure (~200 tokens)
     └─ large: engineer (~400 tokens)
     ↓
Add annotation with savings estimate
     ↓
Claude processes optimized prompt
```

## Tier Behavior

| Tier | What It Detects | What It Does | Token Impact |
|------|----------------|--------------|--------------|
| **passthrough** | Too short, bypass prefix, trivial | Nothing | 0 |
| **small** | Single action, clear target | Compress to imperative | -40% avg |
| **medium** | Multi-step, some ambiguity | Restructure with XML | +20%, saves 80% downstream |
| **large** | Architecture, system design | Full engineering | +60%, saves 200%+ downstream |

## Operating Modes

Set in `~/.claude/prompt-economizer/config.json`:

- **`auto`** (default): Always runs
- **`manual`**: Only runs when you add `#opt` to your prompt
- **`off`**: Disabled

## Bypass Optimization

Start any prompt with these to skip optimization:
- `*` — "* don't optimize this"
- `//` — "// quick question"
- `##` — "## raw prompt"
- `#noopt` — "#noopt just pass through"

## Slash Commands

- `/economizer-stats` — View token savings summary
- `/economizer-toggle` — Enable/disable
- `/economizer-mode [auto|manual|off]` — Change mode

## Configuration

All options in `~/.claude/prompt-economizer/config.json`:

| Key | Default | Description |
|-----|---------|-------------|
| `mode` | `"auto"` | Operating mode |
| `model` | `"claude-haiku-4-5-20251001"` | Model to use |
| `bypass_prefixes` | `["*","//","##","#noopt"]` | Skip optimization |
| `short_prompt_threshold_tokens` | `8` | Below this → passthrough |
| `large_task_threshold_tokens` | `120` | Above this + keywords → large |
| `show_diff` | `true` | Show annotation |
| `stats_enabled` | `true` | Track usage |
| `optimization_budget_tokens` | `400` | Max tokens for optimizer |

## Example Transformations

### Small Task (Compression)

**Before:**
```
hey could you maybe look at the login function in auth.py, I think there might 
be a bug when users try to authenticate
```

**After:**
```
<!-- [prompt-economizer v1.0.0] tier=small action=compressed ~8 tokens saved in 1200ms -->

Fix authentication bug in login function (auth.py).
```

### Medium Task (Restructure)

**Before:**
```
update the authentication system to support OAuth2 and make sure existing users 
still work
```

**After:**
```
<!-- [prompt-economizer v1.0.0] tier=medium action=restructured ~180 downstream tokens saved (est.) in 2100ms -->

<task>
Add OAuth2 support to authentication system while maintaining backward compatibility.
</task>

<context>
Existing authentication system handles local users. OAuth2 support needs to be added.
</context>

<requirements>
1. Implement OAuth2 authentication flow
2. Preserve existing local authentication
3. Ensure existing user accounts remain functional
</requirements>

<constraints>
Do not modify existing user database schema. Maintain current API contracts.
</constraints>

<output_format>
Implementation plan, code changes, and migration strategy if needed.
</output_format>
```

### Large Task (Full Engineering)

**Before:**
```
build a microservice for handling payments with Stripe
```

**After:**
```
<!-- [prompt-economizer v1.0.0] tier=large action=engineered ~400 downstream tokens saved (est.) in 3500ms -->

<objective>
Design and implement a payment microservice with Stripe integration.
</objective>

<background>
New microservice needed to handle payment processing. Stripe chosen as payment provider.
</background>

<scope>
IN SCOPE: Payment processing, Stripe webhooks, transaction logging, error handling
OUT OF SCOPE: User management, product catalog, email notifications
</scope>

<technical_context>
Tech stack: [TECH_STACK - infer from project or specify]
Payment provider: Stripe API v2023+
Microservice architecture pattern expected
</technical_context>

<decomposition>
Phase 1: Core Stripe integration — payment intent creation, confirmation
Phase 2: Webhook handling — payment success, failure, refunds
Phase 3: Transaction persistence — database schema, logging
Phase 4: Error handling and retry logic
</decomposition>

<requirements>
Functional:
  - Accept payment intent creation requests
  - Process Stripe webhook events
  - Store transaction records
  - Handle refund requests
Non-functional:
  - Idempotent webhook handling
  - PCI DSS compliant (never store card data)
  - 99.9% uptime for payment endpoints
</requirements>

<acceptance_criteria>
- Payment intent created successfully via API
- Webhook signatures verified correctly
- Transaction records persisted to database
- Failed payments handled gracefully
- Integration tests pass with Stripe test mode
</acceptance_criteria>

<output_format>
1. Architecture diagram (ASCII or description)
2. API endpoint specifications
3. Implementation code
4. Test strategy
</output_format>

<anti_patterns>
Avoid:
- Storing raw card data (PCI violation)
- Non-idempotent webhook processing (double charges)
- Synchronous payment confirmation (timeout risk)
- Missing webhook signature verification (security risk)
</anti_patterns>
```

## Why This Matters

**Typical workflow without optimization:**
```
User: "fix the login bug"
Claude: "Which file? What bug? What behavior?"
User: "auth.py, users can't log in"
Claude: "What authentication method?"
User: "Google OAuth"
Claude: [finally implements]

Total: 3 rounds, ~3000 tokens wasted
```

**With Prompt Economizer:**
```
User: "fix the login bug"
[Economizer: "Fix login bug in auth.py (Google OAuth)."]
Claude: [implements correctly first try]

Total: 1 round, ~1500 tokens
```

**Net savings: 1500 tokens per task + faster iteration**

## Troubleshooting

**Hook not running?**
- Check `~/.claude/settings.json` has the hook registered
- Verify `ANTHROPIC_API_KEY` is set
- Check logs: `~/.claude/prompt-economizer/economizer.log`

**Optimization too aggressive?**
- Set `mode: "manual"` in config, then add `#opt` only when needed
- Adjust `compression_aggressiveness: "low"` in config

**Want to skip certain prompts?**
- Start with `*` or other bypass prefix
- Use `mode: "manual"` and only tag specific prompts with `#opt`

## Architecture

### Directory Structure

This project uses two separate directories:

1. **`claude-economizer/`** (this repository)
   - Source code and installation files
   - Location: wherever you cloned/downloaded this repo
   - Contains: hooks, scripts, config templates, documentation
   - Purpose: The installation source (version-controlled, shareable)

2. **`~/.claude/prompt-economizer/`** (user data directory)
   - Your personal runtime data and settings
   - Location: `~/.claude/prompt-economizer/`
   - Contains: `config.json`, `economizer.log`, `stats.json`
   - Purpose: User-specific configuration and state
   - Created automatically by installer

**Why separate?** This separation allows you to:
- Update the source repo without losing your stats/config
- Have multiple users on the same system with different configs
- Keep personal data separate from version-controlled code
- Delete the source repo after installation without breaking functionality

### Execution Flow

```
UserPromptSubmit hook
  ↓
economizer.sh (shell wrapper)
  ↓
economizer.py
  ├─ load_config()
  ├─ heuristic_classify() [no API call]
  ├─ llm_classify() [~50 tokens if needed]
  ├─ optimize_small/medium/large() [100-400 tokens]
  ├─ build_output_with_annotation()
  ├─ update_stats()
  └─ output JSON
  ↓
Claude Code receives optimized prompt
```

## Comparison with Other Tools

| Tool | Approach | Token Impact | Our Difference |
|------|----------|--------------|----------------|
| Generic prompt enhancers | Always expand | +50-200% | We compress when appropriate |
| Template systems | Static rules | Variable | We adapt to complexity |
| Manual optimization | Requires expertise | Depends | Fully automated |
| **Prompt Economizer** | **Bidirectional, adaptive** | **Optimizes net cost** | **Only tool that compresses** |

## Stats

View your savings:
```
/economizer-stats
```

Sample output:
```
Prompt Economizer Stats
─────────────────────────
Total prompts processed: 156
Total tokens saved (est): 12,340

By tier:
  passthrough: 45 prompts (0 tokens saved)
  small:       67 prompts (avg -40% tokens)
  medium:      38 prompts (avg +18%, ~180 downstream saved)
  large:        6 prompts (avg +55%, ~400 downstream saved)
```

## Uninstallation

```bash
# 1. Remove hook from ~/.claude/settings.json (edit manually)
# 2. Delete user data directory (your config, logs, stats)
rm -rf ~/.claude/prompt-economizer

# 3. Remove skills and commands
rm ~/.claude/skills/prompt-economizer.md
rm ~/.claude/commands/economizer-*.md

# 4. (Optional) Remove source repository
cd .. && rm -rf claude-economizer
```

## License

MIT

## Credits

Built for Claude Code. Optimizes for token efficiency, not prompt length.

---

**Remember:** Start prompts with `*` to bypass. Use `/economizer-toggle` to disable temporarily. Check `/economizer-stats` to see your savings.
