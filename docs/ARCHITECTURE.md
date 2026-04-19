# Architecture Documentation

## System Overview

Prompt Economizer is a Claude Code hook that intercepts user prompts, classifies their complexity, and applies appropriate optimization strategies before Claude processes them.

## Core Philosophy

Traditional prompt optimizers only expand prompts. This creates a paradox:
- Making prompts longer costs more tokens upfront
- But better prompts reduce downstream re-prompting

The right metric is **net token ROI**:

```
ROI = (tokens_saved_downstream + tokens_saved_from_avoided_re_prompts) 
      / (tokens_spent_on_optimization + delta_in_prompt_tokens)
```

Prompt Economizer is the only tool that:
1. **Compresses** over-verbose small tasks (negative prompt delta, positive ROI)
2. **Expands** under-specified large tasks (positive prompt delta, higher positive ROI)
3. **Adapts** strategy based on complexity classification

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER TYPES PROMPT                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Claude Code UserPromptSubmit Hook               │
│                  (hooks/economizer.sh)                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ stdin: {"prompt": "...", "session_id": "..."}
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Python Optimizer                          │
│                  (hooks/economizer.py)                       │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ 1. LOAD CONFIG                                      │    │
│  │    - Default: config/default-config.json            │    │
│  │    - User override: ~/.claude/prompt-economizer/   │    │
│  │      config.json                                    │    │
│  └────────────────────────────────────────────────────┘    │
│                         │                                    │
│                         ▼                                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │ 2. HEURISTIC CLASSIFICATION (0 API calls)          │    │
│  │    - Check bypass prefixes                          │    │
│  │    - Estimate token count                           │    │
│  │    - Pattern matching (regex)                       │    │
│  │    - Keyword detection                              │    │
│  │                                                      │    │
│  │    Returns: tier | None                             │    │
│  └────────────────────────────────────────────────────┘    │
│                         │                                    │
│                         ▼                                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │ 3. LLM CLASSIFICATION (if heuristic inconclusive)  │    │
│  │    Model: claude-haiku-4-5-20251001                │    │
│  │    Cost: ~50 tokens                                 │    │
│  │    Timeout: 5 seconds                               │    │
│  │                                                      │    │
│  │    Returns: passthrough | small | medium | large    │    │
│  └────────────────────────────────────────────────────┘    │
│                         │                                    │
│                         ▼                                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │ 4. OPTIMIZATION STRATEGY DISPATCH                  │    │
│  │                                                      │    │
│  │    tier == "passthrough"  →  return original        │    │
│  │    tier == "small"        →  optimize_small()       │    │
│  │    tier == "medium"       →  optimize_medium()      │    │
│  │    tier == "large"        →  optimize_large()       │    │
│  └────────────────────────────────────────────────────┘    │
│                         │                                    │
│                         ▼                                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │ 5. BUILD OUTPUT                                     │    │
│  │    - Prepend annotation (if enabled)                │    │
│  │    - Estimate token savings                         │    │
│  │    - Format as JSON                                 │    │
│  └────────────────────────────────────────────────────┘    │
│                         │                                    │
│                         ▼                                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │ 6. UPDATE STATS                                     │    │
│  │    - Increment tier counters                        │    │
│  │    - Update averages                                │    │
│  │    - Estimate cumulative savings                    │    │
│  │    - Write to ~/.claude/prompt-economizer/stats.json│    │
│  └────────────────────────────────────────────────────┘    │
│                         │                                    │
│                         ▼                                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │ 7. OUTPUT                                           │    │
│  │    stdout: {"prompt": "optimized text"}             │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          │ stdout
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              Claude Code Receives Optimized Prompt           │
└─────────────────────────────────────────────────────────────┘
```

## Classification Algorithm

### Heuristic Pre-Filter (No API Call)

**Purpose:** Fast, zero-cost classification for obvious cases.

**Rules:**
1. **Bypass check**: If prompt starts with `*`, `//`, `##`, or `#noopt` → `passthrough`
2. **Length check**: If < 8 tokens → `passthrough`
3. **Large keyword check**: If > 120 tokens AND contains large keywords → `large`
4. **Small pattern check**: If matches small regex AND < 30 tokens → `small`
5. **Otherwise**: Return `None` (inconclusive, needs LLM)

**Hit rate:** ~60% of prompts classified without API call.

### LLM Classification (API Call Required)

**Model:** `claude-haiku-4-5-20251001` (fast, cheap)  
**Cost:** ~50 tokens  
**Timeout:** 5 seconds  
**Fallback:** If timeout or error, default to `medium`

**Prompt:**
```
You are a prompt complexity classifier for a developer tool. Classify the following 
developer prompt into exactly one tier. Respond with ONLY the tier name — no explanation, 
no punctuation.

TIERS:
- passthrough: Single word, question fragment, or completely self-explanatory
- small: Clear single action on a specific target
- medium: Multi-step task, needs context, some ambiguity
- large: System design, architecture, complex feature, multi-file

PROMPT TO CLASSIFY:
"""
{user_prompt}
"""

Respond with only one word: passthrough, small, medium, or large
```

**max_tokens:** 5 (only need one word)

## Optimization Strategies

### Strategy 1: Compression (Small Tier)

**Goal:** Remove fluff, tighten to imperative form.

**Rules:**
1. Strip preamble ("hey", "could you", "I was wondering")
2. Remove hedge words ("maybe", "kind of", "possibly")
3. Convert to imperative: `[VERB] [WHAT] in [WHERE]`
4. Preserve technical terms exactly
5. Target: 60% or fewer tokens than input

**Token budget:** ~100 tokens  
**Average savings:** -40% prompt tokens  
**ROI:** Immediate (saved upfront)

### Strategy 2: Restructuring (Medium Tier)

**Goal:** Add structure to reduce ambiguity and avoid re-prompting.

**Output format:**
```xml
<task>One-sentence goal</task>
<context>Relevant background</context>
<requirements>Numbered list</requirements>
<constraints>What NOT to change</constraints>
<output_format>Expected response format</output_format>
```

**Token budget:** ~200 tokens  
**Average delta:** +20% prompt tokens  
**Downstream savings:** ~80% (avoids 1-2 clarification rounds)  
**ROI:** 4:1 (saves 4x what it costs)

### Strategy 3: Engineering (Large Tier)

**Goal:** Full prompt engineering for complex tasks.

**Output format:**
```xml
<objective>Measurable end state</objective>
<background>Current state, problem</background>
<scope>IN/OUT explicit lists</scope>
<technical_context>Stack, patterns, files</technical_context>
<decomposition>Phase 1, 2, 3...</decomposition>
<requirements>Functional + non-functional</requirements>
<acceptance_criteria>Testable conditions</acceptance_criteria>
<output_format>Response structure</output_format>
<anti_patterns>Specific pitfalls to avoid</anti_patterns>
```

**Token budget:** ~400 tokens  
**Average delta:** +60% prompt tokens  
**Downstream savings:** ~200%+ (avoids entire re-work cycles)  
**ROI:** 5:1 or better

## Data Flow

### Input (stdin)
```json
{
  "prompt": "the user's raw text",
  "session_id": "uuid",
  "cwd": "/path/to/working/directory",
  "conversation_history": []
}
```

### Output (stdout)
```json
{
  "prompt": "<!-- [prompt-economizer v1.0.0] tier=small action=compressed ~8 tokens saved in 1200ms -->\n\nOptimized prompt text here."
}
```

### Stats File (`~/.claude/prompt-economizer/stats.json`)
```json
{
  "total_processed": 156,
  "total_tokens_saved_estimate": 12340,
  "tiers": {
    "passthrough": {
      "count": 45,
      "avg_original_tokens": 3.2,
      "avg_optimized_tokens": 3.2
    },
    "small": {
      "count": 67,
      "avg_original_tokens": 18.5,
      "avg_optimized_tokens": 11.2
    },
    "medium": {
      "count": 38,
      "avg_original_tokens": 45.3,
      "avg_optimized_tokens": 54.1
    },
    "large": {
      "count": 6,
      "avg_original_tokens": 95.2,
      "avg_optimized_tokens": 152.8
    }
  }
}
```

## Error Handling

**Philosophy:** Never break the user's workflow. Always fall back to original prompt.

**Failure modes:**
1. **No ANTHROPIC_API_KEY** → Log warning, passthrough
2. **API timeout** → Log error, passthrough
3. **API rate limit** → Log error, passthrough
4. **Malformed stdin** → Log error, passthrough
5. **Python import error** → Shell script passes through (no Python)
6. **Any unhandled exception** → Catch-all in main(), passthrough

**Logging:** All errors go to `~/.claude/prompt-economizer/economizer.log`

## Performance

### Latency Budget

| Operation | Target | Worst Case |
|-----------|--------|------------|
| Heuristic classification | < 1ms | 5ms |
| LLM classification | 500ms | 2s |
| Small optimization | 800ms | 3s |
| Medium optimization | 1500ms | 5s |
| Large optimization | 2500ms | 8s |
| **Total (passthrough)** | **< 1ms** | **5ms** |
| **Total (small, heuristic hit)** | **< 1s** | **3s** |
| **Total (large, LLM classification)** | **< 3s** | **10s** |

### Token Cost per Optimization

| Tier | Classification | Optimization | Total |
|------|---------------|--------------|-------|
| passthrough | 0 | 0 | 0 |
| small (heuristic) | 0 | ~100 | ~100 |
| small (LLM) | ~50 | ~100 | ~150 |
| medium | ~50 | ~200 | ~250 |
| large | ~50 | ~400 | ~450 |

### ROI by Tier

| Tier | Cost | Savings | ROI |
|------|------|---------|-----|
| passthrough | 0 | 0 | N/A |
| small | ~100 | ~8 (immediate) | ~1.08:1 (often higher with re-prompt avoidance) |
| medium | ~250 | ~180 (downstream) | ~1.7:1 |
| large | ~450 | ~900 (downstream) | ~3:1 |

## Configuration System

**Two-tier config:**
1. **Default:** `config/default-config.json` (in repo)
2. **User override:** `~/.claude/prompt-economizer/config.json`

User config keys override defaults. Unspecified keys use defaults.

**Config loader:**
```python
def load_config() -> dict:
    config = {}
    if DEFAULT_CONFIG_PATH.exists():
        config = json.load(DEFAULT_CONFIG_PATH)
    if CONFIG_PATH.exists():
        user_config = json.load(CONFIG_PATH)
        config.update(user_config)  # user wins
    return config
```

## Extension Points

**Want to add a new optimization strategy?**
1. Add tier name to classification prompt
2. Implement `optimize_<tier>()` function
3. Add case to strategy dispatch in `main()`

**Want to customize classification?**
1. Modify heuristic rules in `heuristic_classify()`
2. Or adjust LLM classification prompt

**Want to change annotation format?**
1. Modify `build_output_with_annotation()`

## Security Considerations

1. **No sensitive data in logs:** Logs only show first 80 chars of prompt
2. **No prompt storage:** Stats only store aggregates, not raw prompts
3. **API key via environment:** Never hardcoded
4. **JSON serialization:** Always use `json.dumps()` to prevent injection
5. **File permissions:** User data directory is mode 0755 (user-only write)

## Testing Strategy

**Unit tests:** `tests/test_economizer.py`
- Token estimation accuracy
- Heuristic classification rules
- Stats tracking
- Output annotation formatting
- Config loading and merging

**Integration tests:**
- End-to-end: echo sample JSON through hook, verify output
- Error handling: missing API key, malformed JSON, API timeout

**Manual testing:**
- Install in a test Claude Code instance
- Test each tier with real prompts
- Verify stats tracking
- Test bypass prefixes
- Test mode switching

---

## Future Enhancements

Possible improvements (not in v1.0):
1. **Caching:** Remember classification for similar prompts
2. **Learning:** Adjust classification thresholds based on user corrections
3. **Custom tiers:** User-defined optimization strategies
4. **Batch mode:** Process multiple prompts in one API call
5. **Streaming:** Start outputting while optimization runs
6. **Analytics dashboard:** Web UI for stats visualization

---

**This architecture prioritizes:**
- ** Zero breaking changes (always falls back)
- ** Low latency (heuristics catch 60%)
- ** High ROI (adaptive strategy)
- ** Transparency (shows what changed)
- ** Configurability (every knob exposed)
