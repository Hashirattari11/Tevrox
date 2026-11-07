# AI Ingredient Analysis (Phase 4)

## Overview

Tevrox's AI ingredient analysis generates educational, personalized ingredient
reports for cosmetic products. The pipeline is deterministic where possible
(rules engine, caching) and uses an LLM only for narrative synthesis, with
strict validation and a safe fallback.

## 7-Step Pipeline

1. **Retrieve** – Load the product and its ordered ingredient list from the
   database. If no ingredients are parsed, return `400 ANALYSIS_NO_INGREDIENTS`
   without calling the LLM.
2. **Normalize** – Use existing normalized ingredient records (from Phase 3
   ingredient service).
3. **Reference** – Attach reference data per ingredient: description, function
   category, safety notes, irritation potential, reviewed flag. Ingredients
   with no reference data are marked "limited information".
4. **Rules** – Run a deterministic, versioned Python rules engine that produces
   findings (fragrance, drying alcohol, actives, comedogenic, ingredient order,
   unreviewed ingredients).
5. **LLM** – Send only structured, minimal data to the model: product name,
   ordered ingredients with reference data, rule findings, `skin_type`,
   `skin_concerns`. Never email, name, or user id.
6. **Validate** – Parse output against a strict Pydantic schema; run
   post-validation checks (no invented ingredient IDs, no banned medical phrases,
   caution-level rule findings reflected in cautions). Retry once with a
   corrective instruction; if still failing, return a rules-only fallback
   report with `model_used="fallback"`.
7. **Display** – Store and return the validated report, including limitations
   and the standard non-medical disclaimer.

## Prompt Versioning

System prompts live in versioned files under
`backend/app/modules/analysis/prompts/`. Current version: `v1`.
Every analysis row stores `prompt_version` and `rules_version` so results are
reproducible and auditable. To change a prompt, create a new versioned file
(never edit in place).

## Rules Engine

Deterministic, pure Python, versioned (`RULES_VERSION = "v1"`).
Rules are data-driven (dicts in `rules_data.py`) so they can be reviewed by
non-developers. Each rule has an id, description, severity, source note, and
a `needs_expert_review` flag.

Initial rules:
- `fragrance_present` – fragrance/parfum detected; relevant for sensitive skin.
- `drying_alcohol_present` – drying alcohol detected; relevant for dry/sensitive.
- `active_ingredients_present` – retinoids, AHAs, BHAs, vitamin C; "introduce gradually".
- `comedogenic_tagged` – comedogenic-tagged ingredients; relevant for oily/acne.
- `ingredient_order` – first 5 ingredients make up the bulk (informational).
- `unreviewed_ingredients` – >20% unreviewed/limited info (caution).

To add a rule: append to `RULES` in `rules_data.py`, implement handling in
`run_rules()`, bump `RULES_VERSION`.

## Validation Layers

1. **Pydantic schema** (`AnalysisResult`): summary ≤600 chars, confidence
   low/medium/high, key_ingredients non-empty, etc.
2. **No invented ingredients**: every `ingredient_id` must exist in the input.
3. **Banned phrases**: `cure`, `treat`, `heal`, `diagnose`, `prescribe`,
   `clinically proven`, `guaranteed`, disease names as outcomes. Case-insensitive.
4. **Caution merge**: rule findings with severity `caution` must appear in
   `cautions`; missing ones are merged deterministically.
5. **Standard limitations**: the disclaimer + two educational limitations are
   always present, regardless of model output.

## Caching

Cache key = `input_hash` = SHA-256 of
`{product_id, ingredient_ids, skin_type, skin_concerns, prompt_version,
rules_version}`. Cached completed analyses are returned without calling the LLM
and do not count toward daily limits.

## Cost Controls

- Per-minute limit: 10 analyses per user.
- Per-day limit: `ANALYSIS_DAILY_LIMIT` (default 20) per user.
- Cached results are exempt from limits.
- Admin stats endpoint: `GET /api/v1/analysis/admin/stats` (total, completed,
  fallback, fallback_rate, recent_7_days, total_tokens, avg_latency_ms).

## Fallback Behavior

If the LLM provider is unavailable, rate-limited, or returns invalid output
twice, the service returns a rules-only fallback report with:
- `status = "fallback"`
- `model_used = "fallback"`
- `error_code` set (e.g. `AI_PROVIDER_UNAVAILABLE`)
- No raw 500 errors are ever returned to the client.

## Provider Swap

The `AIProvider` abstract interface (`generate_structured`) allows swapping
providers. Current implementations:
- `FakeAIProvider` (default, `AI_PROVIDER=fake`) – deterministic, no network.
- `AnthropicProvider` (`AI_PROVIDER=anthropic`) – official Anthropic SDK, with
  retries and backoff for 429/5xx.
- `OpenRouterProvider` (`AI_PROVIDER=openrouter`) – OpenAI-compatible
  chat-completions call to OpenRouter. Uses free models only: the primary
  `OPENROUTER_MODEL` (default `nvidia/nemotron-3-ultra-550b-a55b:free`) plus
  `OPENROUTER_FALLBACK_MODELS`, because free models share an upstream pool and
  are often rate-limited. Free models still require an `OPENROUTER_API_KEY`;
  JSON wrapped in markdown fences is tolerated.

Set `AI_PROVIDER=anthropic` and `AI_PROVIDER_API_KEY` to use the real provider.

## Privacy

What IS sent to the LLM:
- Product name
- Ingredient names, functions, reference data
- Rule findings
- `skin_type`, `skin_concerns` (from user profile)

What is NOT sent:
- Email, name, user id, or any other personal data
- Full conversation history
- IP address, device info

Prompts and model outputs are not logged in full. API keys are never logged.

## Standard Disclaimer

> "Tevrox provides educational information about cosmetic ingredients. It is not
> medical advice and does not diagnose or treat any condition. If you have skin
> concerns or a reaction, talk to a qualified professional."

Shown on every report in web, mobile, and API response.

## Expert Review Required

Before public launch, a qualified person must review:
- All rules in `rules_data.py` (descriptions, severities, source notes).
- Ingredient reference data: `function_tags`, `safety_notes`,
  `irritation_potential` (seed data is development-only).
- The banned-phrase list.
- Prompt text (v1).
