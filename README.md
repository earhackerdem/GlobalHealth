# sandbox

A **development** project of Saúl Pérez, with the agentic layer of the `harness` template: memory in the repo, EPE cycle with a
human gate, profiles and hooks. Rules in [AGENTS.md](AGENTS.md); the cycle in [docs/epe-cycle.md](docs/epe-cycle.md).

```bash
make profile     # who the agent works with (supervised blocks / autonomous warns)
make doctor      # does everything check out?
make epe-new SLUG=C-01-my-first-change   # then, in the agent: /epe-1-explore → /epe-2-plan → /epe-3-execute
```
