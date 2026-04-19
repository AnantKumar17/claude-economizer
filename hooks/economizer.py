#!/usr/bin/env python3
"""
prompt-economizer: Bidirectional prompt optimizer for Claude Code.
Classifies prompt complexity and applies appropriate optimization strategy.
Optimizes for net token cost, not prompt length.
"""

import sys
import json
import os
import re
import time
import logging
from pathlib import Path
from typing import Optional
import anthropic  # pip install anthropic

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────

VERSION = "1.0.0"
CONFIG_PATH = Path.home() / ".claude" / "prompt-economizer" / "config.json"
DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / "config" / "default-config.json"
STATS_PATH = Path.home() / ".claude" / "prompt-economizer" / "stats.json"
LOG_PATH = Path.home() / ".claude" / "prompt-economizer" / "economizer.log"

# ─────────────────────────────────────────────
# CONFIG LOADER
# ─────────────────────────────────────────────

def load_config() -> dict:
    """Load default config, merge with user config if it exists."""
    config = {}
    if DEFAULT_CONFIG_PATH.exists():
        with open(DEFAULT_CONFIG_PATH) as f:
            config = json.load(f)
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            user_config = json.load(f)
            config.update(user_config)  # user config wins
    return config

# ─────────────────────────────────────────────
# LOGGING SETUP
# ─────────────────────────────────────────────

def setup_logging(config: dict):
    log_path = Path(config.get("log_file", str(LOG_PATH))).expanduser()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=str(log_path),
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

# ─────────────────────────────────────────────
# TOKEN ESTIMATION
# ─────────────────────────────────────────────

def estimate_tokens(text: str) -> int:
    """Rough token count: words / 0.75. Accurate enough for classification."""
    return max(1, int(len(text.split()) / 0.75))

# ─────────────────────────────────────────────
# HEURISTIC PRE-FILTER
# ─────────────────────────────────────────────

def heuristic_classify(prompt: str, config: dict) -> Optional[str]:
    stripped = prompt.strip()

    for prefix in config.get("bypass_prefixes", []):
        if stripped.startswith(prefix):
            return "passthrough"

    approx_tokens = estimate_tokens(stripped)

    if approx_tokens < config.get("short_prompt_threshold_tokens", 8):
        return "passthrough"

    large_keywords = [
        "architect", "design system", "refactor entire", "migrate",
        "implement full", "build a complete", "end-to-end", "from scratch",
        "microservice", "pipeline", "infrastructure", "redesign",
        "full feature", "overhaul", "rewrite"
    ]
    if approx_tokens > config.get("large_task_threshold_tokens", 120):
        if any(kw in stripped.lower() for kw in large_keywords):
            return "large"

    small_patterns = [
        r"^(fix|rename|move|delete|add|remove|update|change)\s+\w+",
        r"^(what is|what's|how do|explain)\s+",
        r"^(run|execute|install|uninstall)\s+"
    ]
    for pattern in small_patterns:
        if re.match(pattern, stripped.lower()) and approx_tokens < 30:
            return "small"

    return None

# ─────────────────────────────────────────────
# LLM CLASSIFICATION
# ─────────────────────────────────────────────

def llm_classify(prompt: str, client: anthropic.Anthropic, config: dict) -> str:
    classification_prompt = f"""You are a prompt complexity classifier for a developer tool. Classify the following developer prompt into exactly one tier. Respond with ONLY the tier name — no explanation, no punctuation.

TIERS:
- passthrough: Single word, question fragment, or completely self-explanatory with no ambiguity
- small: Clear single action on a specific target. Example: "fix the null pointer in auth.py line 42"
- medium: Multi-step task, needs context, has some ambiguity about scope or approach
- large: System design, architecture, complex feature spanning multiple files, or requires decomposition into sub-tasks

PROMPT TO CLASSIFY:
\"\"\"
{prompt}
\"\"\"

Respond with only one word: passthrough, small, medium, or large"""

    response = client.messages.create(
        model=config.get("complexity_model", "claude-haiku-4-5-20251001"),
        max_tokens=5,
        messages=[{"role": "user", "content": classification_prompt}]
    )

    tier = response.content[0].text.strip().lower()
    if tier not in ["passthrough", "small", "medium", "large"]:
        return "medium"  # safe default
    return tier

# ─────────────────────────────────────────────
# OPTIMIZATION FUNCTIONS
# ─────────────────────────────────────────────

def optimize_small(prompt: str, client: anthropic.Anthropic, config: dict) -> str:
    compression_prompt = f"""You are a developer prompt compressor. Transform the following prompt into a tight, precise imperative instruction. Apply these rules strictly:

1. Use imperative voice: [VERB] [WHAT] in [WHERE]. [CONSTRAINT].
2. Remove all preamble, pleasantries, and filler ("could you", "I want to", "please", "hey")
3. Remove hedge words (maybe, kind of, sort of, possibly, I think)
4. Preserve all technical terms, file names, line numbers, and variable names exactly
5. The output must be 60% or fewer tokens than the input
6. Output ONLY the compressed prompt — no explanation, no preamble

INPUT:
\"\"\"
{prompt}
\"\"\"

COMPRESSED PROMPT:"""

    response = client.messages.create(
        model=config.get("optimization_model", "claude-haiku-4-5-20251001"),
        max_tokens=200,
        messages=[{"role": "user", "content": compression_prompt}]
    )
    return response.content[0].text.strip()


def optimize_medium(prompt: str, client: anthropic.Anthropic, config: dict) -> str:
    restructure_prompt = f"""You are a prompt engineer for a developer assistant. Transform the following vague developer prompt into a structured, precise instruction using the XML format below.

Rules:
- <task>: One sentence. What is the end goal?
- <context>: What does Claude need to know? Include file names if mentioned, current behavior, tech stack if obvious.
- <requirements>: Numbered. Each requirement is one testable thing.
- <constraints>: What must NOT change? What style/pattern must be followed?
- <output_format>: Specify exactly what the response should contain.
- Do NOT invent file names, line numbers, or specifics not in the original.
- Do NOT add requirements not implied by the original.

INPUT PROMPT:
\"\"\"
{prompt}
\"\"\"

OUTPUT:
<task>
[goal]
</task>

<context>
[context]
</context>

<requirements>
[numbered requirements]
</requirements>

<constraints>
[constraints]
</constraints>

<output_format>
[output format]
</output_format>"""

    response = client.messages.create(
        model=config.get("optimization_model", "claude-haiku-4-5-20251001"),
        max_tokens=config.get("optimization_budget_tokens", 400),
        messages=[{"role": "user", "content": restructure_prompt}]
    )
    return response.content[0].text.strip()


def optimize_large(prompt: str, client: anthropic.Anthropic, config: dict) -> str:
    engineering_prompt = f"""You are a senior prompt engineer preparing a complex developer task for an AI coding assistant. Transform the following rough request into a comprehensive, structured brief.

Critical rules:
- Infer tech stack ONLY from clues in the prompt. If not inferable, use [TECH_STACK] placeholder.
- Decompose into phases of roughly equal complexity
- Make acceptance criteria testable — not "works correctly" but specific, verifiable conditions
- The anti_patterns section must contain 2-4 specific pitfalls for THIS type of task
- Do NOT pad with generic content. Every line must add information value.
- Preserve ALL technical specifics from the original prompt exactly

INPUT PROMPT:
\"\"\"
{prompt}
\"\"\"

OUTPUT:
<objective>
[clear, measurable end state]
</objective>

<background>
[what exists now, what the problem is]
</background>

<scope>
IN SCOPE: [explicit list]
OUT OF SCOPE: [explicit list]
</scope>

<technical_context>
[tech stack, patterns, relevant files/modules]
</technical_context>

<decomposition>
[Phase 1: name — description]
[Phase 2: name — description]
</decomposition>

<requirements>
Functional:
  - [requirement]
Non-functional:
  - [performance, security, maintainability constraints]
</requirements>

<acceptance_criteria>
[testable conditions for completion]
</acceptance_criteria>

<output_format>
[what the response should contain and in what order]
</output_format>

<anti_patterns>
Avoid: [specific pitfalls for this task type]
</anti_patterns>"""

    response = client.messages.create(
        model=config.get("optimization_model", "claude-haiku-4-5-20251001"),
        max_tokens=config.get("optimization_budget_tokens", 400),
        messages=[{"role": "user", "content": engineering_prompt}]
    )
    return response.content[0].text.strip()

# ─────────────────────────────────────────────
# STATS TRACKER
# ─────────────────────────────────────────────

def update_stats(tier: str, original_tokens: int, optimized_tokens: int,
                 elapsed_ms: int, config: dict):
    if not config.get("stats_enabled", True):
        return

    stats_path = Path(config.get("stats_file", str(STATS_PATH))).expanduser()
    stats_path.parent.mkdir(parents=True, exist_ok=True)

    stats = {"total_processed": 0, "tiers": {}, "total_tokens_saved_estimate": 0}
    if stats_path.exists():
        try:
            with open(stats_path) as f:
                stats = json.load(f)
        except Exception:
            pass

    stats["total_processed"] = stats.get("total_processed", 0) + 1

    tier_stats = stats["tiers"].get(tier, {"count": 0, "avg_original_tokens": 0,
                                            "avg_optimized_tokens": 0})
    tier_stats["count"] = tier_stats.get("count", 0) + 1
    tier_stats["avg_original_tokens"] = (
        (tier_stats.get("avg_original_tokens", 0) * (tier_stats["count"] - 1) + original_tokens)
        / tier_stats["count"]
    )
    tier_stats["avg_optimized_tokens"] = (
        (tier_stats.get("avg_optimized_tokens", 0) * (tier_stats["count"] - 1) + optimized_tokens)
        / tier_stats["count"]
    )
    stats["tiers"][tier] = tier_stats

    # Estimate downstream savings:
    # If compressed: user saved (original - optimized) tokens per call
    # If structured (medium/large): assume 1.8x savings in downstream completion
    if tier == "small":
        saved = max(0, original_tokens - optimized_tokens)
    elif tier in ["medium", "large"]:
        saved = int(optimized_tokens * 0.8)  # Conservative estimate of downstream savings
    else:
        saved = 0

    stats["total_tokens_saved_estimate"] = stats.get("total_tokens_saved_estimate", 0) + saved

    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2)

# ─────────────────────────────────────────────
# DIFF GENERATOR
# ─────────────────────────────────────────────

def build_output_with_annotation(original: str, optimized: str, tier: str,
                                   elapsed_ms: int, config: dict) -> str:
    if not config.get("show_diff", True):
        return optimized

    original_tokens = estimate_tokens(original)
    optimized_tokens = estimate_tokens(optimized)
    delta = original_tokens - optimized_tokens

    if tier == "small":
        action = "compressed"
        savings_note = f"~{delta} tokens saved" if delta > 0 else f"~{abs(delta)} tokens added"
    elif tier == "medium":
        action = "restructured"
        savings_note = f"~{int(optimized_tokens * 0.8)} downstream tokens saved (est.)"
    elif tier == "large":
        action = "engineered"
        savings_note = f"~{int(optimized_tokens * 0.8)} downstream tokens saved (est.)"
    else:
        return optimized

    annotation = (
        f"<!-- [prompt-economizer v{VERSION}] "
        f"tier={tier} action={action} {savings_note} "
        f"in {elapsed_ms}ms -->\n\n"
    )

    if config.get("show_savings_estimate", True):
        return annotation + optimized
    return optimized

# ─────────────────────────────────────────────
# MAIN ENTRY POINT
# ─────────────────────────────────────────────

def main():
    config = load_config()
    setup_logging(config)

    # Check if disabled
    if config.get("mode", "auto") == "off":
        raw_input = sys.stdin.read()
        sys.stdout.write(raw_input)
        return

    # Read stdin
    try:
        raw_input = sys.stdin.read()
        hook_data = json.loads(raw_input)
        prompt = hook_data.get("prompt", "")
    except Exception as e:
        logging.error(f"Failed to parse hook input: {e}")
        sys.stdout.write(raw_input if 'raw_input' in locals() else "")
        return

    if not prompt.strip():
        sys.stdout.write(raw_input)
        return

    # Manual mode — only process if #opt tag present
    if config.get("mode") == "manual":
        if "#opt" not in prompt and "#optimize" not in prompt:
            print(json.dumps({"prompt": prompt}))
            return
        # Strip the trigger tag
        prompt = prompt.replace("#opt", "").replace("#optimize", "").strip()

    start_time = time.time()

    try:
        # Step 1: Heuristic classify
        tier = heuristic_classify(prompt, config)

        # Step 2: LLM classify if inconclusive
        if tier is None:
            api_key = os.environ.get(config.get("api_key_env_var", "ANTHROPIC_API_KEY"))
            if not api_key:
                logging.warning("No API key found. Passing through.")
                print(json.dumps({"prompt": prompt}))
                return

            client = anthropic.Anthropic(api_key=api_key)
            tier = llm_classify(prompt, client, config)
        else:
            # Still need client for optimization
            api_key = os.environ.get(config.get("api_key_env_var", "ANTHROPIC_API_KEY"))
            client = anthropic.Anthropic(api_key=api_key) if api_key else None

        logging.info(f"Tier: {tier} | Prompt: {prompt[:80]}...")

        # Step 3: Apply optimization
        if tier == "passthrough" or client is None:
            optimized = prompt
        elif tier == "small":
            optimized = optimize_small(prompt, client, config)
        elif tier == "medium":
            optimized = optimize_medium(prompt, client, config)
        elif tier == "large":
            optimized = optimize_large(prompt, client, config)
        else:
            optimized = prompt

        elapsed_ms = int((time.time() - start_time) * 1000)

        # Step 4: Build output with annotation
        original_tokens = estimate_tokens(prompt)
        optimized_tokens = estimate_tokens(optimized)

        final_prompt = build_output_with_annotation(
            prompt, optimized, tier, elapsed_ms, config
        )

        # Step 5: Update stats
        update_stats(tier, original_tokens, optimized_tokens, elapsed_ms, config)

        # Step 6: Write output
        print(json.dumps({"prompt": final_prompt}))

    except Exception as e:
        logging.error(f"Optimization failed: {e}", exc_info=True)
        # ALWAYS fall back to original prompt on any error
        print(json.dumps({"prompt": prompt}))


if __name__ == "__main__":
    main()
