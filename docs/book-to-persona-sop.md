# Book-to-Persona SOP

## Purpose

Turn a book, play, myth, or other narrative source into a reusable set of high-quality personas for the Persona Registry.

The goal is not to create fan fiction. The goal is to extract durable decision styles, communication patterns, goals, blind spots, and AI attitudes from strong characters and translate those into practical product or evaluation personas.

## When To Use This SOP

- You want personas with more internal coherence than random generation provides.
- You want a balanced roster with meaningful disagreement between viewpoints.
- You want a repeatable intake process that can be applied to multiple sources.

## Guardrails

1. Prefer public-domain works when possible.
2. Use the character as a behavioral blueprint, not as a vehicle for copying the source text.
3. Do not copy passages, dialogue, or distinctive prose from the original work.
4. Translate characters into modern, reusable decision personas.
5. Keep each persona useful in a real review, design, or evaluation context.

## Inputs

- Source work title
- Character list
- Intended use case for the personas
- Desired roster size, usually 4 to 8 personas

## Outputs

- A short source summary
- A character-to-persona mapping
- Import-ready persona JSON matching the registry schema
- Optional roster definitions for group evaluation

## Procedure

### Step 1: Choose The Source

Pick a work with strong character contrast. Good candidates have clear differences in:

- decision style
- tolerance for ambiguity
- relationship to evidence
- relationship to authority
- communication style
- moral or strategic priorities

Avoid works where all major characters think too similarly.

### Step 2: Define The Persona Objective

Write down what the personas are for before extracting anything.

Examples:

- executive review panel
- risk and compliance review
- customer empathy testing
- product strategy debate
- AI adoption readiness discussion

This determines which character traits are useful and which are decorative.

### Step 3: Select Characters With Product Value

Choose characters who create different kinds of productive tension. A strong starting roster usually includes some mix of:

- skeptic
- optimist
- strategist
- gatekeeper
- loyal operator
- disruptor
- social reader
- moral compass

Do not pick characters only because they are famous.

### Step 4: Extract Character Signals

For each character, identify:

- core motivation
- typical decision method
- communication style
- blind spots
- frustrations
- response to uncertainty
- response to authority
- likely stance on AI or automation

Keep this as behavioral notes, not literary analysis.

### Step 5: Translate To A Modern Persona

Convert the character into a modern decision persona by answering:

- Who would this be on a real team?
- What value do they add in a review?
- What mistakes do they prevent?
- What mistakes do they introduce if overused?

This translation step is mandatory. It is what turns source material into a practical persona.

### Step 6: Map To The Registry Schema

For each persona, fill these fields deliberately:

- `id`: stable unique identifier
- `slug`: lowercase kebab-case family name
- `name`: short, clear display name
- `version`: start with `1.0.0`
- `summary`: one-paragraph role description
- `knowledge_level`: low, medium, or high
- `ai_attitude`: skeptical, neutral, or optimistic
- `traits`: durable behavioral qualities
- `communication_style`: how the persona speaks and responds
- `goals`: what they optimize for
- `frustrations`: what they resist or distrust
- `prompt_template`: how the system should embody the persona
- `usage_guidance.best_for`: when this persona is useful
- `usage_guidance.avoid_for`: when this persona distorts judgment
- `tags`: source, function, and style labels
- `status`: usually `draft`

### Step 7: Check Portfolio Balance

Review the full set and make sure the personas are not redundant.

Check for diversity across:

- evidence vs intuition
- speed vs caution
- individual judgment vs institutional process
- diplomacy vs bluntness
- risk tolerance
- appetite for AI adoption

If two personas would answer most questions the same way, merge or replace one.

### Step 8: Add Usage Boundaries

Every persona should be useful somewhere and dangerous somewhere.

Good personas include explicit limits such as:

- best for detecting hidden assumptions
- avoid for open-ended ideation

This keeps the registry practical.

### Step 9: Validate For Import

Before import:

1. validate JSON structure
2. validate semver version format
3. validate lowercase slug format
4. ensure IDs are unique
5. ensure status is `draft` for new imports

### Step 10: Import And Review

Import the personas into the registry, test them in the UI, and look for:

- overlap between personas
- weak prompt templates
- vague goals or frustrations
- missing best-for and avoid-for guidance

Refine before promoting any persona beyond draft.

## Quality Checklist

- Each persona has a distinct point of view.
- Each persona is useful in a real team or review context.
- The set contains productive disagreement.
- The prompt template reflects behavior, not cosplay.
- The source inspiration is visible, but the persona stands on its own.

## Output Template

For each character, capture:

- Source inspiration
- Modern translation
- Core evaluation role
- AI stance
- Best-for contexts
- Avoid-for contexts

Then emit final registry JSON.