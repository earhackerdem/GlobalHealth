# product/

The optional product layer, above `changes/`. Three artefacts, each optional, in this order:

| Artefact | Skill | When |
|---|---|---|
| `brief.md` | `/product-brief` | there is a product behind the stories; one page |
| `prd.md` | `/product-prd` | more than one person must agree on the product, or more than one epic must not diverge |
| `technical-brief.md` | `/product-tech-brief` | before the first plan: team and existing stack first, then candidates, then the NFR budget every change inherits |

Brownfield: `/codebase-context` verifies conventions into an `AGENTS.md` block instead of documenting the system.
Stories carry an `Origin:` line pointing here. Nothing in this folder is gated by hooks; its value is traceability.
