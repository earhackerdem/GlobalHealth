---
name: product-discovery
description: Elicitation interview BEFORE the brief for any product that manages structured data. Extracts the data catalogs (entities, attributes, relations, STATES), the processes (who/when/with whom) and the roles-permissions matrix by iterative questioning that never accepts the stakeholder's first simplification; closes with a navigable mock prototype the stakeholder validates by clicking, not by reading. Produces product/dominio.md and product/roles-permisos.md. Use when the user describes a product idea with data behind it ("quiero gestionar…", "registrar…", "un sistema de…"), before /product-brief, or says "/product-discovery".
argument-hint: [one-line product idea, or nothing to interview from scratch]
---

# /product-discovery — interview the stakeholder like a good analyst would

People simplify their own domain. Ask "what do you want to store about teachers?" and they answer "the name" —
then subjects, semesters and careers appear three questions later. An AI that takes the first answer builds the
wrong product politely. This skill is that analyst's interview, as a protocol: measured in origin (GlobalHealth,
2026-10-12), skipping it cost one full change cycle built on a wrong model of a Mexican prescription.

## The one hard rule
**Never accept the first simplification.** Every catalog answer gets the follow-up ("¿solo eso? ¿y cuando pase X?")
until two consecutive rounds add no new entity, attribute, relation or state. Then it is closed, say so, and move on
— over-interviewing is friction too.

## Procedure (one conversation, four sweeps, then the prototype)
1. **Data catalogs.** For each thing the stakeholder names: what do you need to keep about it? → attributes. Does it
   relate to something else? → relations (which pull NEW entities into the interview: "saber qué materia toma el
   alumno" implies the subjects catalog). Write everything **in the stakeholder's words** — the glossary is the
   future source of names (i18n keys, table names, screen labels).
2. **States and lifecycle** (the sweep everyone forgets): for each entity, "¿qué le puede pasar a lo largo del
   tiempo?" (una receta: emitida → surtida → vencida; un enlace: activo → revocado). States later become status
   fields, filters and reminders; invented states become phantom requirements.
3. **Processes.** Who does what, when, and with whom? Each answer is a functional requirement candidate with its
   actor and trigger. Capture the exceptional paths the stakeholder mentions in passing ("cuando la foto sale
   borrosa…"): those become Given/When/Then later, not prototype screens.
4. **Roles and permissions.** From the processes: which roles exist, what each can and cannot do, per entity and
   operation. Ask for the negatives explicitly ("¿el profesional puede borrar algo del expediente?").
   While here: which data is **sensitive**, who may see it, how long it is kept, who can erase it (in México:
   ARCO/LFPDPPP) — the stakeholder knows what leaking would hurt.
5. **Record**: `product/dominio.md` (template-dominio.md) and `product/roles-permisos.md`
   (template-roles-permisos.md). Create `product/` with `make product-init` if missing.
6. **Prototype gate.** Build a navigable mock of the whole product from the catalogs and processes: mock data from
   the glossary, screens per role, every actionable element labeled with the acceptance-criterion id it will
   satisfy (a toggleable `AC-n` badge), and the user story verbatim at the top of the criteria legend — the badges
   tell *where*, the story tells *why*. Ship it as a clickable page (or, if the person prefers an external tool,
   emit a ready prompt for Claude Design / v0 / Stitch). **The mock's HTML is committed to the repo**
   (`product/prototipos/<slug>.html`) and opened locally: mock data only, never real data. **No hosted copy
   unless the person asks for one** (an artifact link, v0, etc.): it is bound to one account and its sharing
   permissions, so another person, or the same person on another account, may not be able to open it. The repo
   file is the source of truth and outlives accounts and sessions.
   **The human gate is navigating it**: the stakeholder clicks, corrects, and approves flows — they are never
   asked to read delta specs. When interaction is genuinely uncertain, two cheap variants beat one debate: let
   them choose.
7. Close: write what changed during the interview back into the artifacts, note open questions (max 4), and hand
   off to `/product-brief` (which now interviews only what discovery did not answer).

## Rules
- The interview is with whoever owns the need — including when that is the person you work with wearing the
  stakeholder hat. Attribute answers by name and role.
- Artifacts verify understanding; the prototype validates it. Neither replaces the other: the prototype covers the
  happy paths, the scenarios cover errors, limits and regulations.
- Everything [VERIFIED] vs [ASSUMPTION], as always. An attribute nobody asked for is an assumption, marked.
- Calibrate: a single-story change or a product with no structured data does not need discovery; `/triage` decides.
