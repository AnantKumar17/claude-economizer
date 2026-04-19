# Skill: Prompt Economizer Reference

This project is installed as a Claude Code hook that auto-optimizes prompts.

## Operating Modes
- `auto`: All prompts are classified and optimized (default)
- `manual`: Only prompts tagged with `#opt` are optimized
- `off`: Disabled

## Bypass Prefixes
Start any prompt with `*`, `//`, `##`, or `#noopt` to skip optimization entirely.

## Tier Behavior
| Tier | Action | Token Impact |
|------|--------|-------------|
| passthrough | No change | 0 |
| small | Compressed to imperative form | -40% average |
| medium | Restructured with XML context blocks | +20% but saves 80% downstream |
| large | Full prompt engineering with decomposition | +60% but saves 200%+ downstream |

## Config File
User config: `~/.claude/prompt-economizer/config.json`
Override any key from `default-config.json` here.

## Stats Log
`~/.claude/prompt-economizer/stats.json` — token savings by tier

## Troubleshooting
Logs: `~/.claude/prompt-economizer/economizer.log`
If the hook fails for any reason, prompts pass through unchanged — nothing breaks.
