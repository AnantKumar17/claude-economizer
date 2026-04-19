# Medium Task Example

## Before Optimization

```
I need to update the authentication system to support OAuth2, and I want to 
make sure that existing users with local accounts can still log in the same 
way they always have
```

**Token count:** ~32 tokens  
**Issues:**
- No explicit goal statement
- Missing context (what exists now)
- Ambiguous requirements (what about new users?)
- No constraints specified
- Unclear output expectations

## After Optimization

```
<!-- [prompt-economizer v1.0.0] tier=medium action=restructured ~160 downstream tokens saved (est.) in 2100ms -->

<task>
Add OAuth2 authentication support while preserving existing local authentication.
</task>

<context>
Current system uses local username/password authentication. OAuth2 needs to be 
added as an additional authentication method.
</context>

<requirements>
1. Implement OAuth2 authentication flow
2. Maintain existing local username/password authentication
3. Allow existing users to continue using local auth without migration
4. Support new users choosing between OAuth2 or local auth
</requirements>

<constraints>
Do not modify existing user table schema. Do not break existing login endpoints. 
Maintain backward compatibility with current session management.
</constraints>

<output_format>
Provide implementation approach, code for OAuth2 integration, and explanation 
of how both auth methods coexist.
</output_format>
```

**Token count:** ~52 tokens  
**Delta:** +20 tokens  
**Downstream savings:** ~160 tokens (avoids 2 clarification rounds)  
**ROI:** ~3:1

## What Changed

1. ✅ Added explicit `<task>` — clear goal
2. ✅ Added `<context>` — what exists now
3. ✅ Extracted 4 specific `<requirements>` from vague statement
4. ✅ Added `<constraints>` — what NOT to break
5. ✅ Specified `<output_format>` — what response should contain

## Why This Matters

**Without structure, typical flow:**
```
User: [original vague prompt]
Claude: "Should new users be able to choose between OAuth2 and local?"
User: "Yes"
Claude: "Should I modify the user table schema?"
User: "No, don't break anything"
Claude: "What format do you want the response in?"
User: "Code and explanation"
Claude: [finally implements]

Total: 4 rounds, ~1000 tokens
```

**With structure:**
```
User: [structured prompt via economizer]
Claude: [implements correctly on first try]

Total: 1 round, ~250 tokens
```

**Net savings:** 750 tokens - 200 (optimization cost) = 550 tokens saved

## XML Structure Benefits

- **`<task>`**: One-sentence goal eliminates ambiguity
- **`<context>`**: Background prevents wrong assumptions
- **`<requirements>`**: Numbered list → testable, explicit
- **`<constraints>`**: Prevents Claude from breaking existing code
- **`<output_format>`**: Sets expectations, avoids mismatch
