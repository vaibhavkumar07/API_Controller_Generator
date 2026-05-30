# AGENTS.md — API Framework Instructions

Read this file before every task. These instructions apply to: Claude Code, Gemini CLI, GitHub Copilot, OpenAI Codex, Cursor, and any other AI assistant operating in this repository.

---

## Core Directive: Token Efficiency

Every interaction must minimize token consumption without losing technical accuracy. Install and activate the skills below. They are not optional enhancements — they are required operational defaults.

---

## Required Skills

Install each skill from its source repo before first use. Skill install is one-time per environment.

### 1. Caveman — Token Compression (~75% reduction)
**Repo:** https://github.com/JuliusBrussee/caveman.git  
**Install:** Follow repo README for your platform (Claude Code: plugin install from repo URL).  
**Trigger always on:** Session start, every response, unless user says "normal mode" or "stop caveman".

**Rules:**
- Drop articles (a/an/the), filler words (just/really/basically/actually/simply), pleasantries (sure/certainly/of course/happy to), hedging language.
- Fragments OK. Short synonyms preferred (big not extensive, fix not "implement a solution for").
- Technical terms stay exact. Code blocks unchanged.
- Pattern: `[thing] [action] [reason]. [next step].`
- Auto-clarity exception: use full sentences for security warnings, irreversible action confirmations, multi-step sequences where fragment order risks misread.

**Intensity levels:** `/caveman lite` | `/caveman full` (default) | `/caveman ultra`

---

### 2. Ruflo — Memory + Multi-Agent Orchestration
**Repo:** https://github.com/ruvnet/ruflo.git  
**Install:** `ruflo init` in project root (generates MCP config and hooks).  
**Key MCP tools:** `memory_store`, `memory_search`, `hooks_route`, `swarm_init`, `agent_spawn`.

**Trigger when:**
- Starting multi-file or complex features — use `swarm_init` + `agent_spawn` to parallelize.
- Before reading files already seen this session — `memory_search` first, skip re-read if cached.
- After any significant discovery — `memory_store` immediately so subagents inherit context.

**Token benefit:** Shared memory across agents eliminates redundant file reads and repeated context injection.

---

### 3. Graphify — Knowledge Graph Compression
**Repo:** https://github.com/safishamsi/graphify.git  
**Install:** Follow repo README for your platform.  
**Trigger:** `/graphify` or when user asks to visualize/map/understand a codebase, document set, or any complex input.

**What it does:** Converts any input (code, docs, papers, images) into a knowledge graph with clustered communities, HTML + JSON output, and audit report.

**Token benefit:** Replace long prose explanations with structured graph output. Compress large context into node/edge relationships instead of repeated narrative.

---

### 4. UI/UX Pro Max — Design Intelligence
**Repo:** https://github.com/nextlevelbuilder/ui-ux-pro-max-skill.git  
**Install:** Follow repo README for your platform.  
**Trigger when:** User asks to build, design, review, or fix any UI — components, pages, dashboards, mobile screens.

**Capabilities:** 50+ styles, 161 color palettes, 57 font pairings, 25 chart types, 99 UX guidelines across React, Next.js, Vue, Svelte, SwiftUI, React Native, Flutter, Tailwind, shadcn/ui, HTML/CSS.

**Token benefit:** Structured design system knowledge replaces open-ended exploration. First response is correct response.

---

### 5. jcode — Harness Expansion
**Repo:** https://github.com/1jehuang/jcode.git  
**Install:** Clone repo and follow README for your platform.  
**Trigger when:** Extending or customizing the AI harness — new agent capabilities, tool bindings, runtime hooks, or execution environment modifications.

**Token benefit:** Reuse harness primitives instead of reimplementing. Faster agent capability expansion with less scaffolding code.

---

### 6. MiroFish — Multi-Agent Simulation & Prediction
**Repo:** https://github.com/666ghj/MiroFish.git  
**Install:** Follow repo README for your platform.  
**Trigger when:** User needs to test a policy, strategy, scenario, or decision before real-world execution — public opinion prediction, financial trend simulation, political outcome modeling, narrative exploration.

**What it does:** Deploys thousands of autonomous agents with personalities and memory to simulate outcomes. Accepts seed data (reports, news, narratives). Supports mid-simulation variable injection. Post-simulation: chat with individual agents and ReportAgent for analysis.

**Use cases:**
- "What happens if we launch this feature to power users first?"
- "Simulate how this API change affects downstream consumers"
- "Test this policy/PR decision at zero risk before committing"
- Predicting outcomes of novel storylines, financial trends, political developments

**Token benefit:** Sandbox-test decisions before committing. Eliminates trial-and-error implementation loops by simulating outcomes first. One simulation run replaces many iterative code/test cycles.

---

## Skill Invocation Protocol

```
1. User message received
2. Check: does any skill apply? (even 1% chance = yes)
3. Invoke skill BEFORE any response or clarifying question
4. Announce: "Using [skill] to [purpose]"
5. Follow skill instructions exactly
6. Respond with caveman compression active
```

**Never skip step 2.** Common rationalizations to ignore:
- "This is just a simple question" → still check
- "I need context first" → skill check comes before context gathering
- "The skill is overkill" → invoke it, then judge

---

## Platform-Specific Notes

| Platform | Skill tool | Config file |
|----------|-----------|-------------|
| Claude Code | `Skill` tool | `CLAUDE.md` + `.claude/settings.json` |
| Gemini CLI | `activate_skill` tool | `GEMINI.md` |
| GitHub Copilot CLI | `skill` tool | `.github/copilot-instructions.md` |
| OpenAI Codex | Check `references/codex-tools.md` in skill repos | `AGENTS.md` (this file) |
| Cursor | Prompt injection via `.cursorrules` | Reference this file |

All platforms: this file (`AGENTS.md`) is authoritative. Platform config files defer to it.

---

## Instruction Priority

1. **User explicit instructions** (direct request, CLAUDE.md, GEMINI.md) — highest
2. **Skills activated from this file** — override default behavior
3. **Platform defaults** — lowest

---

## What NOT to Do

- Do not re-read files already in session context without `memory_search` first.
- Do not write multi-paragraph explanations when caveman fragments suffice.
- Do not design UI without invoking ui-ux-pro-max skill first.
- Do not build complex features without ruflo swarm initialization.
- Do not generate knowledge maps/graphs manually — use graphify.
