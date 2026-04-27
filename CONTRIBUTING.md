# Contributing to Prompt Economizer

👋 Want to contribute to claude-economizer?

This project optimizes Claude Code prompts for net token ROI. We welcome contributions that improve optimization strategies, classification accuracy, or user experience.

## How to Contribute

### 1. Bug Reports & Feature Requests
- Check existing [issues](https://github.com/AnantKumar17/claude-economizer/issues) first
- For bugs: include your prompt, config file, and economizer.log output
- For features: explain the optimization strategy and expected token savings

### 2. Code Contributions

**We accept:**
- Small, focused patches that are easy to review manually
- Prompts you used to generate LLM-based changes (with evidence of manual testing)
- New optimization strategies with before/after examples
- Documentation improvements and README updates

**Please avoid:**
- Large, unreviewed LLM-generated patches without testing evidence
- Changes that increase net token cost
- Breaking changes to existing config format

### 3. Testing Requirements

All contributions must include evidence of testing:
- Show before/after prompt examples
- Demonstrate token savings (use `/economizer-stats`)
- Test with at least 5 real-world prompts
- Verify hook still works after changes

## Development Setup

### Prerequisites
- Python 3.8+
- Claude Code CLI or desktop app
- Anthropic API key

### Installation for Development

```bash
git clone https://github.com/AnantKumar17/claude-economizer.git
cd claude-economizer

# Install in development mode
python3 scripts/install.py

# Your changes in the repo will now be used by Claude Code
```

### Testing Your Changes

```bash
# 1. Make changes to hooks/economizer.py

# 2. Test with sample prompts
echo "test prompt here" | python3 hooks/economizer.py

# 3. Test in Claude Code
# Open Claude Code and try various prompts
# Check ~/.claude/prompt-economizer/economizer.log for issues

# 4. Verify token savings
# Use /economizer-stats in Claude Code
```

## Contribution Guidelines

### Code Style
- **Python**: Follow PEP 8, use type hints
- Keep functions focused and well-documented
- Add docstrings for new optimization strategies
- No external dependencies unless absolutely necessary (keep it lightweight)

### Commit Messages
- Use present tense ("Add compression strategy" not "Added compression strategy")
- Keep first line under 70 characters
- Include token impact if applicable ("Add XML restructuring (+15%, saves ~180 downstream)")

### Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/optimization-strategy-name`
3. Make your changes with clear commits
4. Test thoroughly (see Testing Requirements above)
5. Update documentation (README.md, docs/) if needed
6. Submit PR with:
   - Clear description of the optimization strategy
   - Before/after examples with token counts
   - Evidence of testing (logs, stats screenshots)
   - If LLM-generated: include the prompts used

### What to Include in Your PR

- **Description**: What optimization strategy does this add/improve? Why?
- **Token impact**: Show expected savings (e.g., "-40% for small tasks")
- **Testing evidence**: Before/after examples, economizer.log output, stats screenshots
- **Edge cases**: What prompts should NOT be optimized this way?
- **Documentation**: Update README.md tier behavior table if needed

## Areas We Need Help With

Check the [issues page](https://github.com/AnantKumar17/claude-economizer/issues) for backlog. High-priority areas:

- **Classification improvements**: Better heuristics to detect task complexity
- **New optimization strategies**: Template patterns for specific task types
- **Testing framework**: Automated regression tests for optimization quality
- **Bypass improvements**: Smarter detection of "don't optimize" intent
- **Config validation**: Better error messages for invalid config
- **Performance**: Reduce classification latency

## Optimization Strategy Guidelines

When proposing new optimization strategies:

1. **Define the trigger**: What heuristics detect this task type?
2. **Show the transformation**: Provide 3-5 before/after examples
3. **Measure token impact**: Use actual token counts from Claude API
4. **Test edge cases**: What prompts should NOT use this strategy?
5. **Consider net cost**: Does this save tokens downstream?

## Questions?

- Open an issue for discussion before starting major work
- For quick questions, comment on related issues
- Be respectful and constructive

## License

By contributing, you agree that your contributions will be licensed under the MIT License that covers this project.

---

**Note for AI-assisted development**: If you use LLM tools to generate code:
1. Review and understand all generated code before submitting
2. Test with real prompts in Claude Code — AI can miss edge cases
3. Mention AI assistance in your PR description
4. Include the prompts you used for transparency
5. For optimization strategies: manually verify token savings

**Remember**: This tool optimizes prompts. Ironic if the contributions aren't optimized themselves. Keep PRs focused and well-tested.
