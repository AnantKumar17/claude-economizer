# Large Task Example

## Before Optimization

```
build a microservice for handling payments with Stripe
```

**Token count:** ~8 tokens  
**Issues:**
- Extremely vague scope
- No technical context
- No requirements specified
- No decomposition
- Missing critical constraints (security, compliance)
- No acceptance criteria

**What Claude would need to ask:**
1. What tech stack?
2. Which Stripe API version?
3. What endpoints are needed?
4. How to handle webhooks?
5. Database requirements?
6. Error handling strategy?
7. Testing approach?
8. Deployment target?

**Estimated back-and-forth:** 5-8 rounds, 2000-3000 tokens wasted

## After Optimization

```
<!-- [prompt-economizer v1.0.0] tier=large action=engineered ~400 downstream tokens saved (est.) in 3500ms -->

<objective>
Design and implement a payment processing microservice with Stripe integration.
</objective>

<background>
New microservice needed to centralize payment processing. Stripe chosen as 
payment provider. Service will be called by existing application backend.
</background>

<scope>
IN SCOPE:
- Payment intent creation and confirmation
- Stripe webhook handling (success, failure, refunds)
- Transaction logging to database
- Error handling and retry logic
- API endpoints for payment operations

OUT OF SCOPE:
- User management (handled by main app)
- Product catalog (separate service)
- Email notifications (separate concern)
- Subscription billing (future phase)
</scope>

<technical_context>
Tech stack: [TECH_STACK - infer from project or specify: Node.js/Python/Go/etc]
Payment provider: Stripe API (latest stable version)
Architecture: Microservice pattern with REST API
Database: Required for transaction persistence
Deployment: [DEPLOY_TARGET - infer or specify: Docker/K8s/serverless]
</technical_context>

<decomposition>
Phase 1: Core Integration
  - Set up Stripe SDK
  - Implement payment intent creation
  - Handle payment confirmation flow

Phase 2: Webhook System
  - Verify webhook signatures
  - Handle payment.succeeded event
  - Handle payment.failed event
  - Implement idempotent processing

Phase 3: Persistence Layer
  - Design transaction schema
  - Implement transaction logging
  - Add transaction query endpoints

Phase 4: Error Handling
  - Add retry logic for transient failures
  - Implement dead letter queue for failed webhooks
  - Add comprehensive logging
</decomposition>

<requirements>
Functional:
  - Accept payment intent creation requests via API
  - Process Stripe webhook events
  - Store transaction records with status
  - Support refund requests
  - Provide transaction lookup by ID

Non-functional:
  - PCI DSS compliant (never store raw card data)
  - Idempotent webhook processing (no duplicate charges)
  - 99.9% uptime for payment endpoints
  - < 200ms response time for payment intent creation
  - Comprehensive audit logging
</requirements>

<acceptance_criteria>
1. Payment intent created successfully returns intent ID
2. Webhook signature verification rejects invalid requests
3. payment.succeeded webhook updates transaction to "completed"
4. payment.failed webhook updates transaction to "failed"
5. Duplicate webhook events are ignored (idempotency)
6. Transaction records persist to database with correct status
7. Integration tests pass with Stripe test mode
8. No raw card data stored anywhere in the system
</acceptance_criteria>

<output_format>
1. System architecture overview (ASCII diagram or description)
2. API endpoint specifications with request/response examples
3. Database schema design
4. Core implementation code with comments
5. Webhook handler implementation
6. Error handling strategy
7. Testing approach (unit + integration)
8. Deployment checklist
</output_format>

<anti_patterns>
Avoid these common payment service mistakes:
1. Storing raw card data (PCI compliance violation)
2. Non-idempotent webhook processing (can cause double charges)
3. Synchronous payment confirmation (timeout risk, poor UX)
4. Missing webhook signature verification (security vulnerability)
5. Not handling partial refunds (common requirement)
6. Insufficient logging (debugging payment issues is critical)
</anti_patterns>
```

**Token count:** ~68 tokens  
**Delta:** +60 tokens  
**Downstream savings:** 2000-3000 tokens (avoids 5-8 clarification rounds + 1-2 re-work cycles)  
**ROI:** ~6:1 or better

## What Changed

1. ✅ **Objective:** Clear, measurable end state
2. ✅ **Background:** Why this is needed, context
3. ✅ **Scope:** Explicit IN/OUT prevents scope creep
4. ✅ **Technical context:** Tech stack guidance (with placeholders where needed)
5. ✅ **Decomposition:** Breaks into 4 implementable phases
6. ✅ **Requirements:** Functional + non-functional (security, performance)
7. ✅ **Acceptance criteria:** 8 testable conditions for "done"
8. ✅ **Output format:** Exact structure of expected response
9. ✅ **Anti-patterns:** 6 specific pitfalls to avoid

## Why This Transforms the Task

**Original prompt:** "build a microservice for handling payments with Stripe"
- Could mean anything
- No boundaries
- No quality criteria
- Likely to require 5+ rounds of refinement

**Optimized prompt:** Comprehensive brief
- Clear boundaries (scope)
- Phased approach (decomposition)
- Quality gates (acceptance criteria)
- Warns about common mistakes (anti-patterns)
- Specifies output structure (prevents mismatch)

## Real-World Impact

**Without optimization:**
```
Round 1: User sends vague prompt
Round 2: Claude asks for tech stack, requirements, scope
Round 3: User clarifies some things, Claude asks more questions
Round 4: Claude implements Phase 1
Round 5: User realizes security issues, asks for fixes
Round 6: Claude asks about webhook handling
Round 7: Claude implements Phase 2
Round 8: User asks for error handling
Round 9: Claude adds retry logic
Round 10: User requests tests
Round 11: Claude adds tests

Total: 11 rounds, 8000-10000 tokens, 2-3 hours
```

**With optimization:**
```
Round 1: User sends prompt → Economizer engineers it
Round 2: Claude implements entire system correctly
Round 3: Minor tweaks if needed

Total: 2-3 rounds, 2000-3000 tokens, 30-45 minutes
```

**Net savings:**
- **5000-7000 tokens** (~90% reduction)
- **1.5-2.5 hours time** saved
- **Far fewer errors** (anti-patterns warned upfront)
- **Better quality** (acceptance criteria specified)

## Key Innovation

This is the only tool that can take an 8-token prompt and turn it into a 
68-token comprehensive brief that saves 6000+ tokens downstream.

Traditional prompt optimizers would refuse this task because:
- They only expand prompts
- They don't understand ROI
- They optimize for prompt length, not net cost

Prompt Economizer understands that spending 60 extra tokens upfront to save 
6000 downstream is a 100:1 ROI.
