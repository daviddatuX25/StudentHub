## The Framework

Think of each title slot as a 5-minute persuasion arc. The panel doesn't need to fully understand the system yet — they need to believe three things by the end:

- **The problem is real**
- **The solution is the right shape**
- **The scope is doable**

Everything in the format serves one of those three beliefs.


## The 8-Section Structure

### Section 1 — The Title (15 sec)
Start with the full formal title. Establish the project name and focus immediately so the panel can anchor the presentation.

### Section 2 — The Scene (30 sec)
Open with a concrete, human scenario. Not a statistic. Not a definition. A situation someone in the room recognizes.

> "A student org treasurer collects dues in an envelope. Three weeks later, money is missing and no one can prove anything."

One sentence that makes the panel feel the problem before you name it. This is the only moment you're allowed to be a little dramatic.

### Section 3 — The Problem (60 sec)
Now name the problem clearly and in layers — who experiences it, what the specific pain is, and why the current workaround fails. Hit at least two stakeholder angles if you can. Keep it grounded: avoid abstract language like "lack of efficient system." Say what actually breaks and for whom.

### Section 4 — The Proposed System (60-90 sec)
One clean sentence stating what the system is and what it does. Then a simple architecture view — not a full technical diagram, just enough to show the moving parts and how they connect. The goal here is shape, not depth. Panelists should be able to picture it in their head by the end of this section.

### Section 5 — Component Coverage Map (30 sec)
This is your compliance moment — explicitly account for all required components. Show a simple row or grid: Web, Mobile, ML, IoT, Mapping — and for each one, one line on where it lives in your system. Don't skip this. Panels notice when a component is hand-waved. Be specific even if brief:

> "ML is used for bandwidth prediction via a regression model on usage logs" beats "the system uses machine learning."

### Section 6 — The Novelty Claim (30-45 sec)
State clearly what gap this fills — in local literature, in the institution, or in practice. This doesn't need to be a literature review, just a one or two sentence claim:

> "No existing study in Philippine BSIT literature has documented X."
> "Existing systems do A but none address B in the context of C."

This is what separates a research title from a project title, and panelists will probe here.

### Section 7 — Scope (30 sec)
State the boundary of what the system covers and — importantly — name at least one thing that is explicitly out of scope. This shows the panel you've thought about limits. Anything left ambiguous in scope will become a question, so preempt it here.

### Section 8 — Difficulty Acknowledgment & Roadmap (45-60 sec)
This is the trust section. The panel already heard what the system is and why it matters — now they're quietly asking "can this group actually build it?" Don't wait for them to ask. Address it directly.

The structure inside this section has two moves.

First move — name the hard parts honestly. Pick the two or three genuinely difficult components and say them out loud. Not weaknesses, not apologies — just honest technical acknowledgment. Something like "the hardest parts of this system are the IoT hardware integration and the ML model training pipeline, because both require real deployment data we don't have yet." Panels respect this more than confidence theater. If you pretend everything is easy, they'll find the hard part themselves and it will feel like you were hiding it.

Second move — show the roadmap shape. Not a Gantt chart, not week-by-week. Just three phases with rough time bounds and a clear deliverable per phase. The point is to show the group has thought about sequence — what has to be built before what else can be built. IoT hardware can't be tested without a running server. ML can't be trained without usage data. The panel needs to see you understand the dependency order, not just the feature list.

A simple way to frame it verbally: "We're approaching this in three phases — infrastructure first, then application layer, then analytics and optimization. Each phase has a working deliverable we can demo independently, so even if one component is delayed it doesn't block the entire defense."

What this section signals to the panel
It signals three things at once: the group is technically self-aware, the workload has been thought through, and there's a fallback logic built in. Panels are more likely to approve a title where the group demonstrates awareness of risk than one where everything sounds frictionless — because they know nothing in capstone is frictionless.

The honest difficulty scale
Optional but powerful: close this section with a one-line difficulty rating on your own system. Something like "We rate this as high-complexity but within our capability — the core components are open-source and documented, and two of our group members have prior experience with the hardware layer." This kind of self-assessment shows maturity. It also gives you a chance to quietly mention relevant group strengths without it sounding like a resume.


## The Ratio That Matters

Problem and proposed system together should take up more than half the slot. Novelty and scope are brief but non-negotiable. The component map is housekeeping but do it visually so it takes no cognitive load. The hook is a scalpel — short, sharp, one cut.


## What to Build Per Title

Each title needs exactly four prepared assets going into the defense:

1. **The hook sentence** — Written out, rehearsed, not improvised.
2. **The architecture sketch** — Can be a simple block diagram. The point is to have something to point at when you describe the system.
3. **The component map** — A literal five-row table: component name, where it appears in your system, what it does. Fill it before the defense so you're never caught guessing.
4. **The novelty statement** — One or two sentences, sourced if possible. Know what related systems exist and what they don't do that yours does.


## One Rule Across All Eight

Never let a title defense become a features tour. The panel is not evaluating your feature list — they're evaluating whether the problem is worth solving and whether your approach makes sense. Features are evidence, not the argument. Lead with the title and problem, use features to support, end on scope.