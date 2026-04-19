# Small Task Example

## Before Optimization

```
hey could you maybe look at the login function in auth.py, I think there 
might be a null pointer exception when users try to log in with invalid 
credentials
```

**Token count:** ~25 tokens  
**Issues:**
- Preamble ("hey", "could you maybe")
- Hedge words ("I think", "might")
- Over-explained (Claude can infer from context)

## After Optimization

```
<!-- [prompt-economizer v1.0.0] tier=small action=compressed ~10 tokens saved in 1200ms -->

Fix null pointer exception in login function (auth.py) for invalid credentials.
```

**Token count:** ~15 tokens  
**Savings:** 10 tokens immediate, avoids 1 clarification round (~500 tokens)  
**Total ROI:** ~51:1 (saved ~510 tokens, spent ~10 for optimization)

## What Changed

1. ✅ Removed preamble
2. ✅ Removed hedge words
3. ✅ Converted to imperative voice
4. ✅ Preserved all technical details (file name, error type, condition)
5. ✅ Tightened to single sentence

## Compression Rules Applied

- Strip conversational opening ("hey")
- Remove politeness padding ("could you maybe")
- Remove hedge qualifiers ("I think", "might")
- Use verb-first structure: `Fix [WHAT] in [WHERE] for [CONDITION]`
- Preserve: file names, error types, technical context
