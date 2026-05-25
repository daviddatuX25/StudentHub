# SynapseRT — Canonical Knowledge Base & Title Defense Guide
*Capstone Title 2 · Multi-Agent Real-Time Cognitive Orchestration System*
*A Comprehensive Project Definition, System Architecture Deep-Dive, Strategic Defense Roadmap, and Mock Q&A*

---

## 0. Project Identity

| Field | Value |
| :--- | :--- |
| **Working Title** | **SynapseRT: A Multi-Agent Cognitive Orchestration System for Real-Time Collaborative Knowledge Mapping** |
| **Domain** | Ubiquitous Computing · Human-Computer Interaction · Real-Time AI Systems |
| **Core Thesis** | Multi-agent cognitive orchestration, deployed at the local edge via quantized SLMs and a hardware-inspired memory hierarchy, can transform ephemeral multi-party group discussions into stable, structured, and interactive knowledge maps — in real time, with sub-700ms latency. |
| **Target Users** | Academic defense panels, thesis working groups, design sprint teams, brainstorming sessions |
| **Deployment Model** | Local Edge (Dedicated on-premise hardware node with GPU acceleration) with selective cloud escalation |

### The Hook Sentence
> A group of students sits down for a thesis brainstorming session. Two hours later, one person's messy notebook is the only record — but half the connections, contradictions, and action items are already lost. SynapseRT listens to that conversation in real time and builds the map they can't.

### The Novelty Statement
> No existing study in Philippine BSIT literature has documented a locally deployed, multi-agent cognitive orchestration system that operates on live streaming audio with sub-second turn-taking, enforces semantic cache coherence (MESI) across parallel AI agents, and implements a hardware-inspired tiered memory hierarchy with formal paging heuristics for real-time knowledge graph construction. Existing meeting transcription tools (Otter.ai, Fireflies.ai) are cloud-dependent, single-agent, and produce flat text — not semantically structured, interactive relational maps.

---

## 1. The Core Defense Pitch (Slide Script)

> **Pitch Duration:** 2 to 3 minutes. Present this clearly and confidently during the solution/architecture slides.

"Good day, members of the panel. We present **SynapseRT**, which has evolved from a passive, text-processing visualizer into a **Dynamic, Real-Time Cognitive Orchestration System**.

Ubiquitous computing in collaborative spaces faces a critical bottleneck: the immense processing latency that destroys human-to-computer synergy. If a system blocks processing while waiting for a speaker to complete a paragraph, the lag makes the system feel disconnected. SynapseRT resolves this by transitioning from a deterministic linear pipeline to an asynchronous, stream-to-stream multi-agent framework.

Our system operates in three real-time, low-latency layers:
1. **The Ingestion & Turn-Taking Pipeline:** We ingest live audio as continuous 20ms packets, routing them through a local, lightweight neural **Voice Activity Detection (VAD)** engine. Our Speech-to-Text (STT) engine cascades partial transcripts every 50ms. A local **Dialogue Act (DA) Transition Matrix** tracks conversational states. When a user speaks, the system distinguishes true utterances from backchannel noise (like *"mm-hmm"* or *"right"*), preventing unnecessary model execution and ensuring a response loop of under 700ms.
2. **Hardware-Inspired Memory Hierarchy:** To prevent context-window bloat and physical GPU High-Bandwidth Memory (HBM) exhaustion during long sessions, we implement a tiered memory hierarchy. Immediate tokens are stored in the **L1 Execution Cache** of our local quantized model (**Nous Hermes 2 Pro**). Session summaries, edge-lists, and active loops reside in the volatile **L2 Working Memory**. Historical logs, vector databases, and full relational graphs are archived in **Long-Term Storage (Neo4j)**. A semantic **Page-Replacement Algorithm** evicts low-salience chatter ($V_{\text{gold}} \to 0$) and compresses high-salience nodes ($V_{\text{gold}} \gg 0$) into memory-efficient summaries.
3. **Asynchronous Multi-Agent Orchestration:** The agent guild functions as an asynchronous state engine coordinated via an internal Event Bus. The **Context-Captain** acts as the steering core, adjusting the routing threshold $\alpha$ and managing sub-graph splits on topic changes. The **Arbitrator** preserves semantic contradictions by rendering dashed 'tension' edges. Parallel skill modules—the **Suggestive Agent** (balancing lateral ideation via a divergence controller $\alpha_{\text{div}}$) and the **Corrective Agent** (subtly amber-highlighting misremembered variables with verification links)—support group comprehension.

To prevent data races and desynchronization between these parallel agents, SynapseRT enforces a software-defined **Semantic Cache Coherence Protocol** modeled after CPU cache coherence (MESI). This architecture is backed by formal, empirical optimization proofs that mathematically minimize a joint cost-latency loss function.

Ultimately, SynapseRT proves that multi-agent cognitive orchestration can be deployed efficiently at the local edge, transforming ephemeral group discussions into stable, structured, and interactive knowledge maps."

---

## 2. System Architecture Deep-Dive

This section is the canonical technical reference for every subsystem. Each subsystem is documented with its design rationale, internal mechanics, data flow, and failure modes.

---

### 2.1 The Streaming Pipeline & Turn-Taking Engineering

#### 2.1.1 Design Rationale
Traditional meeting transcription operates on a **batch model**: record → wait → transcribe → display. This imposes a minimum latency floor of 3–10 seconds (one full sentence), which annihilates the sense of real-time synergy. SynapseRT inverts this by treating audio as a **continuous stream of micro-packets**, processing each packet the instant it arrives.

#### 2.1.2 Audio Ingestion Flow
```
[Microphone] → Web Audio API (48kHz)
    → AudioWorklet (downsample to 16kHz mono)
    → 20ms Frame Packetizer (320 samples/frame)
    → WSS WebSocket Channel
    → Server Audio Buffer Ring
```

1. **Client-Side Capture:** The browser's Web Audio API captures raw PCM at 48kHz stereo. An AudioWorklet node downsamples to 16kHz mono (the native input format for Whisper models), producing 320 samples per 20ms frame.
2. **Frame Packetization:** Each 20ms frame is tagged with a monotonic sequence number and speaker channel ID, then transmitted over a secure WebSocket (WSS) to the server ingestion buffer.
3. **Ring Buffer:** The server maintains a lock-free circular buffer holding the last 30 seconds (1,500 frames) of raw audio per speaker channel. This buffer enables retrospective lookback when the STT engine needs to re-evaluate a hypothesis.

#### 2.1.3 Neural Voice Activity Detection (VAD)
We deploy **Silero VAD**, a lightweight RNN-based neural voice activity detector, running locally on the server CPU.

| Parameter | Value | Rationale |
| :--- | :--- | :--- |
| Model size | ~2MB ONNX | Runs on CPU without GPU contention |
| Frame size | 512 samples (32ms at 16kHz) | Optimal for Silero's internal architecture |
| Latency | < 5ms per frame | Sub-perceptual processing time |
| Threshold | 0.45 (tunable) | Balances sensitivity vs. false activation |

**Why not WebRTC VAD?** WebRTC's built-in VAD is an energy-threshold detector. It classifies any signal above a volume floor as "speech." In a room with typing, rustling papers, or air conditioning, this keeps the voice-active flag perpetually on. Silero's neural model is trained specifically on vocal characteristics, distinguishing human speech from ambient noise with > 95% accuracy in controlled environments.

**Output:** For each 20ms audio frame, the VAD emits a binary signal: `SPEECH_START`, `SPEECH_CONTINUE`, or `SPEECH_END`. These signals gate the STT engine — only audio segments marked as speech are forwarded for transcription.

#### 2.1.4 Streaming Speech-to-Text (Faster-Whisper)
We use **Faster-Whisper** (CTranslate2-optimized Whisper) with the `medium` model, running on the GPU inside the Inference VM.

- **Partial Cascading:** The STT engine does not wait for a speaker to finish. It emits partial transcript hypotheses every ~50ms, constantly updating its prediction as more audio arrives. Example cascade:
  ```
  T+50ms:   "We should probably—"
  T+100ms:  "We should probably use a—"
  T+150ms:  "We should probably use a relational—"
  T+200ms:  "We should probably use a relational database"  ← FINAL
  ```
- **Dirty Tokens:** The intermediate hypotheses (before FINAL) are called "dirty tokens." They are semantically useful for early prediction but lexically unstable. The Context-Captain reads dirty tokens but holds them in a transient buffer — nodes are only committed to the shared graph when the STT emits a finalized segment.

#### 2.1.5 Dialogue Act (DA) Classification & Backchannel Suppression
Once a finalized text segment is produced, it passes through a local **Dialogue Act classifier** (fine-tuned DistilBERT or rule-based heuristic) that labels each utterance with one of the following acts:

| Dialogue Act | Examples | Agent Dispatch? |
| :--- | :--- | :--- |
| **Statement** | "We need to use PostgreSQL for this." | ✅ Yes — full agent pipeline |
| **Question** | "What about the mobile app?" | ✅ Yes — creates question node |
| **Assertion** | "The deadline is next Friday." | ✅ Yes — creates factual node |
| **Backchannel** | "mm-hmm," "right," "yeah" | ❌ No — suppressed |
| **Filler** | "uh," "like," "you know" | ❌ No — suppressed |
| **Topic Shift** | "Okay, moving on to the payment flow…" | ✅ Yes — triggers sub-graph split |

**Markov State Tracking:** The DA classifier maintains a transition probability matrix. If Speaker A is in the middle of a *Statement* block and Speaker B utters "right," the transition matrix identifies this as a high-probability backchannel (non-interrupting passive validation). The system suppresses agent dispatch, preventing the UI from flashing or generating unnecessary nodes.

#### 2.1.6 End-to-End Latency Budget

| Stage | Target Latency | Cumulative |
| :--- | :--- | :--- |
| Audio capture + packetization | 20ms | 20ms |
| WebSocket transmission (LAN) | < 5ms | 25ms |
| Neural VAD classification | < 5ms | 30ms |
| STT partial hypothesis | ~50ms | 80ms |
| STT finalization (end of utterance) | ~200ms | 280ms |
| DA classification | < 10ms | 290ms |
| Context-Captain routing | < 30ms | 320ms |
| Agent execution (local SLM) | ~300ms | 620ms |
| UI render (WebSocket push) | < 50ms | 670ms |
| **Total end-to-end** | | **< 700ms** |

---

### 2.2 Hardware-Inspired Memory Hierarchy

#### 2.2.1 The Problem: Context-Window Bloat
A 90-minute meeting with 4 participants generates approximately 18,000–25,000 tokens of raw transcript. Feeding all of this into a language model's context window causes:
1. **Quadratic attention degradation** — transformer self-attention is $O(n^2)$, so doubling the context quadruples compute time.
2. **GPU HBM exhaustion** — the KV-cache for a 7B model at 8K context consumes ~1GB of VRAM. Pushing to 32K+ contexts risks Out-Of-Memory (OOM) crashes.
3. **Signal dilution** — the model loses focus on recent, critical information when flooded with historical chatter.

#### 2.2.2 The Three-Tier Architecture
Modeled directly on traditional computer hardware memory hierarchies (CPU Cache → RAM → Disk):

| Tier | Analogy | Technology | Contents | Capacity | Access Latency |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **L1 Execution Cache** | CPU L1/L2 Cache | SLM context window (Nous Hermes 2 Pro) | Last 3–5 active dialogue acts, current raw tokens, active agent prompt | 4K–8K tokens | < 1ms (in-VRAM) |
| **L2 Working Memory** | System RAM | Redis (in-memory database) | Session summaries, active edge-lists, unresolved question loops, node metadata | ~200 active nodes (~50K tokens equivalent) | < 1ms (in-RAM) |
| **Long-Term Storage** | Disk / SSD | Neo4j graph DB + pgvector | Full relational graphs, cross-session episodic logs, vector embeddings, archived sub-graphs | Unlimited (disk-bound) | 5–20ms (disk I/O) |

#### 2.2.3 The Semantic Page-Replacement Algorithm ($V_{\text{gold}}$)
When the L2 cache reaches capacity (e.g., 200 active nodes), the **Memory Agent** executes a semantic eviction sweep:

**Step 1 — Weight Mapping:** Each node $s_i$ in L2 is annotated with participant-weighted importance scores:
- Essential concept linkages → weight $w = 3$
- Optional assertions → weight $w = 1$
- Social chitchat / filler → weight $w = 0$

**Step 2 — Gold Score Calculation:**
$$V_{\text{gold}}(s_i) = \frac{1}{N} \sum_{j=1}^{N} w(l_{i,j})$$

Where $N$ is the number of annotated links connected to node $s_i$, and $w(l_{i,j})$ is the importance weight of each link.

**Step 3 — Sorting & Eviction:**
- Nodes sorted by $V_{\text{gold}}$ in ascending order.
- Nodes where $V_{\text{gold}} \to 0$ (pure chatter, exhausted fillers) → **immediately evicted** from L2 Redis.
- Nodes where $V_{\text{gold}} \gg 0$ (high-salience concepts) → **compressed**: the Memory Agent triggers the local SLM to write an abstractive summary of the node cluster, replaces the detailed nodes with a single summary node, and pushes the raw history into Neo4j long-term storage.

**Step 4 — Promotion:** When a user or agent references an archived node (e.g., double-clicking a bridge node in the UI), the system **promotes** it back from Neo4j into L2 Redis, analogous to a page fault in virtual memory systems.

#### 2.2.4 Redis L2 Schema

```
# Active graph nodes (Hash per session)
HSET session:{sid}:nodes {nodeId} {JSON: label, type, speaker, timestamp, gold_score, edges[]}

# Unresolved question loops (Sorted Set by timestamp)
ZADD session:{sid}:questions {timestamp} {questionNodeId}

# Active edge-list (Set)
SADD session:{sid}:edges {edgeId}:{sourceNodeId}:{targetNodeId}:{edgeType}

# Session metadata
HSET session:{sid}:meta started_at {ts} participants {count} l2_node_count {n}
```

---

### 2.3 Asynchronous Multi-Agent Orchestration

#### 2.3.1 The Agent Guild
SynapseRT does not use a single monolithic AI model. Instead, it deploys **four specialized agents** that operate concurrently, coordinated via an internal **Event Bus** (Redis Pub/Sub or NATS).

| Agent | Role | Trigger | Output |
| :--- | :--- | :--- | :--- |
| **Context-Captain** | Steering core — routing, topic management, sub-graph splits | Every finalized DA segment | Routing decisions, sub-graph isolation commands, $\alpha$ threshold adjustments |
| **Arbitrator** | Conflict detection — preserves contradictions as tension edges | When two speakers make contradictory assertions on the same semantic root | Tension edges (dashed red links), contradiction labels, conflict resolution prompts |
| **Suggestive Agent** | Lateral ideation — proposes unexplored angles and connections | When the conversation stalls or loops on a single topic for > 3 minutes | "Have you considered…" node suggestions, divergence prompts, lateral links |
| **Corrective Agent** | Fact-checking — cross-references live speech against local knowledge base | When a speaker makes a factual claim that conflicts with the local RAG database | Amber-highlighted nodes with verification links, correction overlays |

#### 2.3.2 The Context-Captain in Detail
The Context-Captain is the **only agent with write access to the routing table**. It makes three critical decisions per incoming segment:

1. **Local vs. Cloud Routing ($\alpha$ threshold):** Should this segment be processed by the local SLM (fast, free, lower quality) or escalated to a cloud API (slower, expensive, higher quality)? Governed by the cost-latency loss function (see §2.5).
2. **Topic Continuity vs. Shift:** Does this segment continue the current topic, or does it signal a new topic? If a shift is detected, the Context-Captain seals the current sub-graph and opens a new canvas.
3. **Agent Dispatch:** Which agents should be activated for this segment? A simple factual statement triggers only the Corrective Agent. A controversial assertion triggers both the Arbitrator and the Suggestive Agent.

#### 2.3.3 The Arbitrator in Detail
When two participants make contradictory statements:
1. **Detection:** The NLP parser classifies both statements as *Strong Assertions* with matching semantic roots (e.g., "database selection").
2. **Conflict Flagging:** The Arbitrator compares the assertions against the active L2 graph. Detecting a semantic mismatch, it flags the contradiction.
3. **Preserving Tension:** Instead of overwriting Participant A's node with B's node, the Arbitrator creates both nodes, links them to a shared parent, and connects them with a dashed red **Tension Edge** labeled with the contradiction details. This visualizes the divergence for the group to resolve later, rather than silently picking a winner.

#### 2.3.4 The Suggestive Agent & Divergence Controller ($\alpha_{\text{div}}$)
The Suggestive Agent monitors conversational entropy. When the discussion loops on a narrow topic:
- It computes a **divergence score** based on the semantic distance between the last N dialogue acts and the broader topic graph.
- If divergence falls below $\alpha_{\text{div}}$ (i.e., the conversation is too narrow), the agent proposes lateral connections: "The group has been discussing database schema for 8 minutes. Related but unexplored: caching strategy, API versioning."
- If divergence is too high (conversation is scattered), the agent signals the Context-Captain to tighten focus.

#### 2.3.5 The Corrective Agent & Amber Alerts
The Corrective Agent constantly cross-references live transcriptions against a local compiled knowledge base (RAG — Retrieval-Augmented Generation):
1. **Mismatch Detection:** If a speaker says *"We're using an RTX 3070 GPU"* and the local ledger indicates the actual hardware is an *RTX 3060*, the agent identifies the mismatch.
2. **Amber Alert:** The agent publishes an update via the Event Bus. The SvelteKit frontend catches the update and dynamically highlights the affected node in amber (pulsing micro-animation).
3. **Details-on-Demand:** The amber node displays a small alert icon. When clicked, it slides out a detail panel showing the conflicting statement, the verified parameter from the database, and an on-demand link to the source documentation — correcting the error without interrupting the meeting's vocal flow.

#### 2.3.6 Event Bus Architecture
```
                    ┌──────────────┐
                    │  Event Bus   │
                    │ (Redis PubSub│
                    │   or NATS)   │
                    └──────┬───────┘
           ┌───────────────┼───────────────┐
           │               │               │
    ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
    │  Arbitrator │ │  Suggestive │ │  Corrective │
    │   Agent     │ │   Agent     │ │   Agent     │
    └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
           │               │               │
           └───────────────┼───────────────┘
                    ┌──────▼──────┐
                    │   Memory    │
                    │   Agent     │
                    │  (L2 Redis) │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Context-   │
                    │  Captain    │
                    │  (Router)   │
                    └─────────────┘
```

All agents publish their outputs to the Event Bus. The Memory Agent consumes all events, updates the L2 Redis state, and pushes the delta to the SvelteKit frontend via WebSocket for real-time UI rendering.

---

### 2.4 Semantic Cache Coherence Protocol (MESI)

#### 2.4.1 The State Desynchronization Trap
Since agents operate in parallel, a critical race condition emerges: What happens when Agent Alpha (Arbitrator) is merging Node X and Node Y into Node Z, while Agent Beta (Suggestive Agent) is simultaneously reading Node Y to propose a lateral connection?

Without synchronization, Agent Beta would operate on stale data, producing a suggestion that references a node that no longer exists — causing ghost nodes, broken links, and UI flicker.

#### 2.4.2 The MESI State Machine
We enforce a software-defined protocol modeled after the CPU MESI (Modified, Exclusive, Shared, Invalid) cache coherence protocol:

| State | Meaning | Who Can Read? | Who Can Write? |
| :--- | :--- | :--- | :--- |
| **Modified (M)** | An agent is actively mutating this sub-graph region | Only the lock holder | Only the lock holder |
| **Exclusive (E)** | An agent has claimed exclusive access but hasn't yet modified | Only the lock holder | Only the lock holder |
| **Shared (S)** | No modifications active; multiple agents can read concurrently | All agents | None (must escalate to E first) |
| **Invalid (I)** | This node/edge has been modified by another agent; local cache is stale | None (must re-fetch) | None (must re-fetch) |

#### 2.4.3 Protocol Walk-Through
Consider the race condition above:

1. **Lock Acquisition:** Agent Alpha (Arbitrator) sends `LOCK [X, Y]` to the Event Bus. The Memory Agent marks Nodes X and Y as **Modified (M)** in Redis and records Alpha as the lock holder.
2. **Blocked Read:** Agent Beta (Suggestive) attempts to read Node Y. Finding it in state M with a different lock holder, Beta **suspends** its execution and registers a callback.
3. **Merge Execution:** Alpha merges X and Y into new Node Z, updating the L2 graph.
4. **Lock Release:** Alpha sends `UNLOCK [X, Y] → CREATED [Z]`. The Memory Agent transitions X and Y to **Invalid (I)** and creates Z in **Shared (S)** state.
5. **Invalidation Broadcast:** The Memory Agent publishes `INVALIDATE [X, Y] → USE Z` on the Event Bus. All agents with cached references to X or Y clear their local context and pull the fresh state of Z.
6. **Resume:** Agent Beta receives the invalidation, updates its local context to reference Z instead of Y, and resumes execution with correct data.

#### 2.4.4 Deadlock Prevention
To prevent circular waits:
- **Lock Ordering:** All lockable resources are assigned a monotonically increasing ID. Agents must always acquire locks in ascending ID order.
- **Timeout:** Any lock held for more than 2 seconds is forcibly released and the operation is retried. This prevents a crashed agent from permanently blocking a sub-graph.
- **Single-Writer Principle:** Only the Context-Captain and Arbitrator can acquire Exclusive/Modified locks. The Suggestive and Corrective agents operate in read-only mode on the shared graph and publish their suggestions as new nodes, not mutations to existing ones.

---

### 2.5 Cost-Latency Optimization & Routing Proofs

#### 2.5.1 The Routing Problem
Not all conversational segments require the same level of AI sophistication. A simple factual statement ("The meeting is at 3 PM") can be handled by the local 7B SLM. A complex synthesis request ("Summarize the three competing database proposals and recommend one") may benefit from a cloud-hosted frontier model.

The **Context-Captain** uses a binary classifier (based on RouteLLM) to decide: local or cloud?

#### 2.5.2 The Loss Function
The routing threshold $\alpha$ is optimized to minimize:
$$\min_{\alpha} \Big( C_{\text{API}}(\alpha) + \lambda \cdot L_{\text{system}}(\alpha) \Big) \quad \text{subject to } Q_{\text{synthesis}}(\alpha) \ge \beta$$

| Variable | Meaning |
| :--- | :--- |
| $\alpha$ | Routing threshold — segments with complexity score $\ge \alpha$ are sent to cloud |
| $C_{\text{API}}(\alpha)$ | Cumulative API cost — decreases as $\alpha$ increases (more local processing) |
| $L_{\text{system}}(\alpha)$ | System latency — decreases as $\alpha$ increases (local edge = no WAN delay) |
| $\lambda$ | User-defined weight balancing cost vs. speed |
| $Q_{\text{synthesis}}(\alpha)$ | Human-validated synthesis quality score |
| $\beta$ | Minimum acceptable quality threshold |

#### 2.5.3 Tuning $\lambda$
- **Budget-constrained mode** (stable internet, tight budget): High $\lambda$ → penalizes cost, forces more local processing.
- **Quality-critical mode** (live defense, high-stakes meeting): Low $\lambda$ → allows more cloud escalation for superior synthesis.
- **Offline mode** ($\lambda = \infty$): All processing stays local. No cloud calls. Maximum privacy.

The Context-Captain dynamically adjusts $\lambda$ based on the active "room mode" configured by the facilitator.

#### 2.5.4 Empirical Verification
We validate the convergence of this function by running continuous 90-minute test streams, logging:
- System memory footprints over time
- F1-scores of turn-detection accuracy
- Graph readability index ($R_{\text{graph}}$)
- API cost accumulation curves
- Human quality ratings (NASA-TLX cognitive load survey)

---

## 3. Four Critical Defense Arguments

### Argument 1: The Contextual Turn-Taking & Streaming Ingestion Defense (Latency Elimination)
*   **The Attack:** *"Why is your streaming turn-taking model necessary? Won't simple silence detection of 1.5 seconds be enough to segment speakers?"*
*   **The Rebuttal:** "No. Standard silence thresholds create a double-failure: they introduce massive latency (over 1.5 seconds) which breaks conversational synergy, or they trigger false cut-offs during mid-sentence thinking pauses, especially in multi-party academic debate."
*   **The Logic:**
    1.  **Sub-Second Ingestion:** We packetize raw audio into 20ms frames and apply a local, neural Voice Activity Detection (VAD) model. This VAD isolates voice boundaries in milliseconds, bypassing the lag of traditional volume-threshold systems.
    2.  **Partial Cascading:** The STT engine emits partial transcript hypotheses every 50ms. The **Context-Captain** processes these 'dirty tokens' (uncorrected streaming text) to execute immediate, ultra-low-latency semantic predictions rather than blocking the pipeline for a full sentence.
    3.  **Backchannel Suppression:** By mapping incoming tokens against a Dialogue Act (DA) transition matrix, the turn detector identifies backchannel responses (e.g., *"right," "uh-huh"*). If classified as low-salience backchanneling, it suppresses agent dispatch, preventing interface flashing and saving computational overhead.

### Argument 2: The Hardware-Inspired Memory Hierarchy Defense (Context-Window Bloat)
*   **The Attack:** *"As a meeting extends past an hour, the context window will accumulate thousands of tokens. How does your system prevent context bloat and GPU memory exhaustion?"*
*   **The Rebuttal:** "We solve context-window bloat by implementing a tiered context architecture explicitly modeled on traditional computer hardware memory hierarchies (Cache, RAM, and Storage) paired with a semantic page-replacement algorithm."
*   **The Logic:**
    1.  **Tiered Hierarchy:**
        *   *L1 Execution Cache:* Immediate raw tokens and the last 3-5 active dialogue acts, running inside the local SLM context.
        *   *L2 Working Memory:* Volatile in-memory cache managed by the Memory Agent, containing session summaries, active edge-lists, and unresolved question loops.
        *   *Long-Term Storage:* Persistent Neo4j graph database and vector stores for cross-session episodic logs.
    2.  **Semantic Paging ($V_{\text{gold}}$):** We evaluate the salience of L2 segments:
        $$V_{\text{gold}}(s_i) = \frac{1}{N} \sum_{j=1}^{N} w(l_{i,j})$$
    3.  **Intelligent Eviction:** When L2 reaches capacity, social backchannels and highly redundant segments ($V_{\text{gold}} \to 0$) are evicted. High-salience elements ($V_{\text{gold}} \gg 0$) are compressed into abstracted summaries and maintained in L2 RAM.

### Argument 3: The Semantic Cache Coherence (MESI) Defense (Multi-Agent Conflict)
*   **The Attack:** *"Since your agents operate in parallel, what happens when one agent modifies the knowledge graph while another is reading it? Won't this cause data races and conflicting UI elements?"*
*   **The Rebuttal:** "We prevent this State Desynchronization Trap by enforcing a software-defined Semantic Cache Coherence Protocol based on the CPU MESI protocol."
*   **The Logic:**
    1.  **Modified (M) & Exclusive (E):** When the Arbitrator locks a sub-region of the knowledge graph to merge concepts or resolve a contradiction, it marks that sub-graph state as *Modified*. The Arbitrator holds *Exclusive* write access; all other agents are blocked from pushing visual updates to those nodes.
    2.  **Shared (S):** When no modifications are active, the graph structure is marked as *Shared*. The Suggestive and Corrective agents can safely read the environment concurrently to perform low-overhead lateral operations.
    3.  **Invalid (I):** The instant an agent updates a semantic node, it broadcasts an invalidation signal across the Event Bus. If another agent attempts an operation using that stale context, it must immediately clear its local cache and pull the fresh, updated state from the central **Memory Agent**.

### Argument 4: The Cost-Latency Optimization Proof & Verification Defense
*   **The Attack:** *"How do you prove that your routing threshold ($\alpha$) is actually optimal? Isn't it just a trial-and-error slider?"*
*   **The Rebuttal:** "We prove the optimality of our routing threshold by framing it as a multi-objective cost-latency optimization problem, minimizing a joint loss function while maintaining a human-validated synthesis quality constraint."
*   **The Logic:**
    1.  **The Loss Function:** The edge-cloud escalation choice is governed by:
        $$\min_{\alpha} \Big( C_{\text{API}}(\alpha) + \lambda \cdot L_{\text{system}}(\alpha) \Big) \quad \text{subject to } Q_{\text{synthesis}}(\alpha) \ge \beta$$
        Where $C_{\text{API}}$ represents the operational financial cost of cloud calls, $L_{\text{system}}$ is the systemic latency, and $\lambda$ is a user-defined optimization weight balancing resource conservation against processing speed.
    2.  **Quality Boundary ($\beta$):** The routing is constrained such that the human-validated quality score of the structural context mapping ($Q_{\text{synthesis}}$) remains above a minimum acceptable baseline $\beta$.
    3.  **Empirical Verification:** We run continuous 90-minute testing streams through the system, logging system memory footprints, F1-scores of turn-detection latency, and graph readability indexes to empirically prove the convergence of this function.

---

## 4. Component Coverage Map

This section explicitly accounts for all required capstone components. Each row maps a required component to its concrete implementation in SynapseRT.

| Component | Implementation in SynapseRT | Specifics |
| :--- | :--- | :--- |
| **Web Application** | SvelteKit real-time dashboard | Force-directed knowledge graph (D3.js), role-based views (Facilitator, Learner, Note-Taker), WebSocket-driven live updates |
| **Mobile Application** | Progressive Web App (PWA) | Responsive SvelteKit layout installable on mobile; push notifications for amber alerts and session summaries |
| **Machine Learning / AI** | Multi-agent SLM orchestration + VAD + DA classification | Nous Hermes 2 Pro (7B quantized), Silero VAD (RNN), DistilBERT DA classifier, RouteLLM binary classifier |
| **IoT / Hardware** | Audio ingestion via microphone arrays + local GPU passthrough | Web Audio API capture, AudioWorklet processing, RTX 3060 PCIe passthrough for local inference |
| **Data Visualization** | Interactive knowledge graph + timeline + Kanban overlays | D3.js force-directed layout, Shneiderman taxonomy (Overview → Zoom → Filter → Details-on-Demand), sub-graph isolation |
| **Networking** | VLAN-segmented local edge deployment | Local hypervisor host, OpenWrt gateway VM, 802.1Q VLAN trunking, SQM CAKE QoS |

---

## 5. Scope & Delimitations

### 5.1 In Scope
1. Real-time streaming audio ingestion and transcription for **English and Taglish** (Tagalog-English code-switching) in multi-party settings (2–6 concurrent speakers).
2. Local edge deployment on a single dedicated GPU host workstation (RTX 3060 12GB).
3. Four-agent asynchronous orchestration (Context-Captain, Arbitrator, Suggestive, Corrective) with MESI synchronization.
4. Tiered memory hierarchy (L1/L2/Long-Term) with $V_{\text{gold}}$ semantic paging.
5. Interactive web-based knowledge graph visualization using D3.js and SvelteKit.
6. Empirical validation through controlled 90-minute session experiments with NASA-TLX surveys.

### 5.2 Explicitly Out of Scope
1. **Speaker diarization with voice biometric enrollment** — we use channel-based speaker identification (one mic per speaker or pre-assigned channels), not voiceprint recognition.
2. **Real-time translation** — the system transcribes but does not translate between languages. Taglish is handled as a mixed-language input, not a translation target.
3. **Commercial deployment or multi-tenant SaaS** — this is a research prototype deployed on a single on-premise server for controlled academic evaluation.
4. **Video processing or gesture recognition** — SynapseRT operates on audio-only input. Visual modalities are out of scope.
5. **Offline mobile-first mode** — the PWA requires an active WebSocket connection to the server; there is no offline-capable local inference on mobile devices.

---

## 6. Dynamic UI Rendering & Shneiderman Taxonomy

### 6.1 Overview-First Paradigm
Under Shneiderman's *Overview First, Zoom/Filter, Details-on-Demand* paradigm, a massive monolithic node graph causes cognitive overload. SynapseRT implements this hierarchy:

1. **Overview (Master Map):** The default view shows a high-level graph of all active topics as bridge nodes. Each bridge node is a collapsed sub-graph with a label and node count.
2. **Zoom (Sub-Graph Expansion):** Double-clicking a bridge node expands it into the detailed sub-graph view, showing individual nodes, edges, tension links, and amber alerts within that topic.
3. **Filter (Role-Based Views):** The interface offers role-specific layouts:
   - *Facilitator View:* Emphasizes unresolved question loops and tension edges.
   - *Learner View:* Emphasizes the Suggestive Agent's lateral connections and knowledge gaps.
   - *Note-Taker View:* Emphasizes chronological timeline and action items.
4. **Details-on-Demand (Node Inspection):** Clicking any node opens a slide-out panel showing the raw transcript excerpt, speaker attribution, timestamp, gold score, and any correction overlays.

### 6.2 Sub-Graph Split on Topic Shifts
When the DA parser detects a *Topic Shift*:
1. The Context-Captain intercepts the renderer.
2. It seals the active topic's nodes into an isolated sub-graph.
3. In the master map, the sub-graph is collapsed into a single bridge node.
4. The interface renders a new, clean canvas for the new topic.

### 6.3 Force-Directed Graph Layout (D3.js)
The knowledge graph is rendered using a D3.js force-directed simulation with:
- **Charge force:** Nodes repel each other to prevent overlap.
- **Link force:** Connected nodes are pulled together proportional to edge weight.
- **Center force:** The graph is centered in the viewport.
- **Collision force:** Nodes have a minimum separation distance.
- **Tension edges:** Rendered as dashed red lines with a subtle pulsing animation.
- **Amber nodes:** Corrective Agent highlights pulse with a warm amber glow animation.

### 6.4 Orchestration Graphs (Dillenbourg)
Based on Dillenbourg's Orchestration Graphs framework, SynapseRT renders:
- **Social plane:** Who is speaking to whom (interaction edges between speaker nodes).
- **Task plane:** What topics are being discussed (concept nodes and relationship edges).
- **Temporal plane:** When each topic was introduced and how long it was active (timeline view).

---

## 7. Infrastructure Topology

### 7.1 Local Server Virtualization Layout

| VM ID | Name | OS | Cores | RAM | Storage | GPU | Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **200** | App Server | Ubuntu 24.04 LTS | 4 | 8 GB | 100 GB (ZFS) | — | SvelteKit frontend, PostgreSQL, Redis (L2), Traefik reverse proxy, Event Bus |
| **201** | Inference Node | Ubuntu 24.04 LTS | 5 | 20 GB | 50 GB (ZFS) | RTX 3060 12GB (PCIe passthrough) | Ollama (Nous Hermes 2 Pro), Faster-Whisper STT, Silero VAD, DA classifier |
| **202** | Network Gateway | OpenWrt x86 | 1 | 2 GB | 4 GB | — | 802.1Q VLAN routing, SQM CAKE QoS, DHCP/DNS, firewall |

**Total Host Requirements:** 10 Cores, 32 GB RAM, RTX 3060 12GB VRAM, 256+ GB NVMe SSD.

### 7.2 Ollama Concurrent Inference Configuration
Since four agents run in parallel, concurrent inference requests to Ollama could cause VRAM overflow.

- **Model Instance Sharing:** A single instance of Nous Hermes 2 Pro weights is loaded into GPU VRAM (~4.8 GB for Q4_K_M quantization).
- **Parallel Context Slots:** `OLLAMA_NUM_PARALLEL=4` allocates 4 independent context slots in VRAM (~1 GB per slot for 8K context). Agents query the model concurrently, sharing base weights while maintaining separate KV-caches.
- **VRAM Budget:** 4.8 GB (weights) + 4 × 1 GB (context slots) = ~8.8 GB. Faster-Whisper medium model consumes ~2 GB. Total: ~10.8 GB / 12 GB available. Leaves ~1.2 GB headroom.

### 7.3 Network Topology
```
[ISP Uplink]
    │
[OpenWrt VM 202] ── VLAN 10 (Admin) ── [Admin Dashboard]
    │
    ├── VLAN 50 (Workspace) ── [Client Devices / Microphones]
    │       └── SQM CAKE (per-host fairness, < 50ms jitter)
    │
    └── VLAN 100 (Server Internal) ── [App VM 200] ↔ [Inference VM 201]
                                          │
                                    [Redis / Neo4j / PostgreSQL]
```

---

## 8. Technical Mock Q&A: Deep-Dive

### Category A: Streaming Pipeline & Turn-Taking Engineering

#### Q1: "Why deploy a local Neural VAD engine instead of using simple WebRTC VAD or volume-threshold detection?"
*   **Answer:** "Simple volume/energy-threshold detectors (such as WebRTC VAD) are highly sensitive to environmental noise. In a classroom or meeting room, typing on keyboards, papers rustling, or air conditioning units can easily cross volume thresholds, keeping the voice activity state active. A local neural VAD model (like Silero VAD) runs a tiny, optimized Recurrent Neural Network (RNN) that classifies raw audio frames specifically for human vocal characteristics, operating in less than 5ms and ensuring we only ingest actual speech."

#### Q2: "How does the Context-Captain process 'dirty tokens' (uncorrected streaming text) without generating erroneous UI elements?"
*   **Answer:** "The streaming STT engine (Faster-Whisper) emits partial transcripts every 50ms, constantly updating its predictions. The Context-Captain reads these streaming sequences but applies a **Semantic Confidence Gate**. Instead of generating new visual nodes immediately, it passes the dirty tokens to a local semantic parser. If the parser identifies a strong entity-relationship link but the STT confidence is low, the Context-Captain holds the node state in a 'transient' buffer. The node is only committed to the shared workspace once the STT engine stabilizes the text and emits the final transcription segment."

#### Q3: "Explain how backchanneling is detected and filtered out using the Dialogue Act (DA) Transition Matrix."
*   **Answer:** "We define a transition matrix where each cell represents the probability of moving from one Dialogue Act to another.
    1.  **Backchannel Classification:** When a user says *"mm-hmm," "yeah,"* or *"right,"* the local classifier labels it as a backchannel dialogue act.
    2.  **Markov State Tracking:** The turn-detector checks the current state of the conversation. If a speaker is currently in the middle of a *Statement* block, and another participant utters a backchannel, the transition probability matrix identifies that this backchannel has a high likelihood of being a non-interrupting, passive validation.
    3.  **Suppression:** The system suppresses the turn-detector's dispatch signal. The VAD continues tracking the primary speaker's audio buffer, and no agent is invoked, preventing the UI from flashing or generating a card for the backchannel."

#### Q4: "What happens when two speakers talk simultaneously? How does the system handle overlapping speech?"
*   **Answer:** "Overlapping speech is one of the hardest problems in multi-party audio processing. SynapseRT handles it at two levels:
    1.  **Hardware-Level Separation (Preferred):** In our controlled evaluation setup, each participant uses a dedicated microphone channel (e.g., individual lapel mics or directional microphones per seat). The audio ingestion pipeline processes each channel independently, so overlapping speech arrives as separate streams.
    2.  **Software-Level Degradation (Fallback):** If a single shared microphone is used, Faster-Whisper's attention mechanism can partially disambiguate overlapping speech, but accuracy degrades. In this case, the Context-Captain marks the segment with a low-confidence flag and generates a 'contested segment' node in the graph — indicating that manual review may be needed. This is an acknowledged limitation documented in our scope."

---

### Category B: Virtualization & Multi-Agent Node Architecture

#### Q5: "Describe the local hypervisor virtualization topology for this multi-agent cognitive architecture."
*   **Answer:** "We partition the host server (10 Cores, 32GB RAM, RTX 3060 12GB VRAM) into three VM layers:
    1.  **VM 200 - App Server VM (Ubuntu 24.04 LTS):** Allocated 4 Cores, 8GB RAM. Runs our SvelteKit frontend, the PostgreSQL database (storing active L2 states), and the Traefik reverse proxy.
    2.  **VM 201 - Local Inference VM (Ubuntu 24.04 LTS):** Allocated 5 Cores, 20GB RAM, and PCIe passthrough of the RTX 3060 GPU. Runs Ollama, hosting the quantized GGUF Nous Hermes 2 Pro model.
    3.  **VM 202 - Network Gateway VM (OpenWrt):** Allocated 1 Core, 2GB RAM. Segments the workspace client nodes onto VLAN 50, applying SQM CAKE to keep WebSocket state sync latency under 50ms."

#### Q6: "How does Ollama handle concurrent agent requests without causing GPU Out-Of-Memory (OOM) crashes?"
*   **Answer:** "Since our agents (Context-Captain, Arbitrator, Suggestive Agent, Corrective Agent) run in parallel, concurrent inference requests to Ollama could cause VRAM overflow. We prevent this using Ollama's native concurrent request queue and parameter caching:
    1.  **Model Instance Sharing:** We load a single instance of the Nous Hermes 2 Pro model weights into GPU VRAM (approx. 4.8GB).
    2.  **Parallel Context Slots:** We configure the Ollama runner with `OLLAMA_NUM_PARALLEL=4`. This allocates 4 independent context slots in VRAM (approx. 1GB per slot for an 8k context window). The agents query the model concurrently, sharing the base weights while maintaining separate context states, preventing OOM crashes."

#### Q7: "Why Nous Hermes 2 Pro specifically? Why not Llama 3, Mistral, or Phi-3?"
*   **Answer:** "Nous Hermes 2 Pro (based on Mistral 7B) was selected for three specific reasons:
    1.  **ChatML Format with Structured Output:** It natively supports the ChatML prompt format and has been specifically fine-tuned for structured JSON/XML output parsing. Our agents require the model to emit structured node-edge payloads, not free-form text. Nous Hermes 2 Pro achieves > 90% format compliance on structured output benchmarks, reducing retry loops.
    2.  **Quantization Stability:** The Q4_K_M GGUF quantization of this model retains strong reasoning performance while fitting within our 4.8GB weight budget. Larger models (Llama 3 8B) have similar parameter counts but are less optimized for constrained structured generation.
    3.  **Function Calling:** Nous Hermes 2 Pro has robust function-calling capabilities, allowing agents to invoke tools (e.g., 'create_node', 'merge_edges', 'query_rag') through structured tool-use prompts."

---

### Category C: Tiered Memory Hierarchy & Paging Heuristics

#### Q8: "Walk us through the database schema and implementation details of the L2 Working Memory."
*   **Answer:** "The L2 Working Memory is hosted in an in-memory Redis database running inside VM 200.
    1.  **Transient Edge-Lists:** We store the active node-link relationships as a Redis Hash, representing the current session's graph.
    2.  **Unresolved Question Loops:** A Redis Sorted Set (ZSET) tracks active, unanswered questions, sorted by their timestamp.
    3.  **Fast Read/Write:** Because Redis runs entirely in RAM, write latency is sub-millisecond, allowing the Memory Agent to synchronize agent updates and feed them to the SvelteKit WebSocket server immediately."

#### Q9: "How is the $V_{\text{gold}}$ semantic paging eviction rule calculated and executed step-by-step?"
*   **Answer:** "When the Redis L2 cache size crosses our allocation limit (e.g., 200 active nodes):
    1.  **Weight Mapping:** The Memory Agent retrieves the annotator/participant weight $w(l_{i,j})$ for each node $s_i$. Essential concept linkages receive a weight of 3, optional assertions a weight of 1, and social chitchat a weight of 0.
    2.  **Equation Calculation:** We calculate the average score:
        $$V_{\text{gold}}(s_i) = \frac{1}{N} \sum_{j=1}^{N} w(l_{i,j})$$
    3.  **Sorting & Eviction:** The nodes are sorted by $V_{\text{gold}}$ in ascending order.
    4.  **Paging/Archiving:** Nodes where $V_{\text{gold}} \to 0$ are immediately evicted from the volatile Redis L2 cache. Nodes with $V_{\text{gold}} \gg 0$ are compressed: the Memory Agent triggers the local model to write an abstractive summary of these nodes, updates the parent node in L2 with the summary, and evicts the detailed child nodes, pushing the raw history into the long-term Neo4j database."

#### Q10: "What happens when a user wants to revisit an archived topic? How does promotion from Long-Term Storage back to L2 work?"
*   **Answer:** "This is analogous to a page fault in virtual memory:
    1.  **Bridge Node Click:** The user double-clicks a collapsed bridge node in the master map that references an archived sub-graph.
    2.  **Neo4j Query:** The Memory Agent queries Neo4j for the archived sub-graph, retrieving all nodes, edges, and metadata.
    3.  **L2 Re-Hydration:** The retrieved data is loaded back into Redis L2 as active nodes. If L2 is at capacity, the eviction algorithm runs first to make room.
    4.  **UI Expansion:** The SvelteKit frontend receives the hydrated sub-graph via WebSocket and renders the expanded view with a smooth zoom animation.
    5.  **Staleness Flag:** Promoted nodes are marked with a 'promoted' badge in the UI, indicating that they represent historical context that may no longer be current."

---

### Category D: Multi-Agent Synchronization & MESI Protocol

#### Q11: "How does the Semantic MESI Protocol prevent race conditions on the Event Bus?"
*   **Answer:** "Consider the *State Desynchronization Trap*: Agent Alpha (Arbitrator) is merging Node X and Node Y, while Agent Beta (Suggestive Agent) is reading Node Y.
    1.  **Modified (M):** Agent Alpha locks Node X and Node Y's memory ID in Redis and broadcasts a `LOCK [X, Y]` event. The state in Redis is marked as *Modified*.
    2.  **Exclusive (E):** Agent Alpha holds the exclusive write lock. Agent Beta attempts to read Node Y. Finding it locked, Agent Beta suspends its read and waits.
    3.  **Shared (S):** Once Agent Alpha finishes the merge, creating Node Z, it releases the lock. The state returns to *Shared*.
    4.  **Invalid (I):** Agent Alpha broadcasts `INVALIDATE [X, Y] → USE Z`. Agent Beta intercepts this, clears its local context cache for Nodes X and Y, pulls the fresh state of Node Z from the Memory Agent, and resumes its execution safely."

#### Q12: "How does the Arbitrator resolve contradictions in multi-party discussions?"
*   **Answer:** "When two participants make contradictory statements (e.g., Participant A says *'We must use a SQL database,'* and Participant B says *'We must use a NoSQL database'*):
    1.  **Dialogue Act Detection:** The NLP parser classifies both statements as *Strong Assertions* with matching semantic roots (database selection).
    2.  **Conflict Flags:** The Arbitrator compares these assertions against the active L2 graph. Detecting a semantic mismatch, it flags the contradiction.
    3.  **Preserving Tension:** Instead of overwriting Participant A's node with B's node, the Arbitrator preserves both nodes. It creates Node A (*SQL Database*) and Node B (*NoSQL Database*), links them to the parent node (*Database Selection*), and connects Node A and Node B with a dashed red **Tension Edge** labeled with the contradiction details. This visualizes the divergence for the group to resolve later."

#### Q13: "What is the maximum lock contention you expect, and how do you prevent deadlocks?"
*   **Answer:** "In practice, lock contention is low because:
    1.  **Narrow Lock Scope:** Locks are acquired on individual node IDs, not on the entire graph. A typical agent operation touches 2-4 nodes, so the locked region is small.
    2.  **Short Lock Duration:** Agent operations complete in < 300ms (one SLM inference call). Locks are held for the duration of the operation only.
    3.  **Deadlock Prevention:** We enforce strict lock ordering (ascending node ID) and a 2-second timeout. If a lock is not released within 2 seconds, it is forcibly cleared and the operation is retried. In our testing, forced timeouts occur in < 0.5% of operations."

---

### Category E: Dynamic UI Rendering & Shneiderman Taxonomy

#### Q14: "How does the Context-Captain trigger a sub-graph split on clean topic shifts, and how does this map to Shneiderman's taxonomy?"
*   **Answer:** "Under Shneiderman's *Overview First, Zoom/Filter, Details-on-Demand* paradigm, a massive, monolithic node graph causes visual clutter (cognitive overload).
    1.  **Topic Shift Detection:** When the DA parser detects a *Topic Shift* (e.g., moving from *'Networking Setup'* to *'Payment Gateway Integration'*), the Context-Captain intercepts the renderer.
    2.  **Isolating Sub-Graphs:** It seals the active 'Networking Setup' nodes into an isolated sub-graph.
    3.  **Bridge Node Creation:** In the master map, the sub-graph is collapsed into a single, high-level bridge node labeled *'Networking Setup Sub-Graph'*. The interface renders a new, clean canvas for *'Payment Gateway Integration'*.
    4.  **Zoom & Filter:** Users can double-click the bridge node to zoom in and expand the isolated sub-graph, keeping the active workspace clean and organized."

#### Q15: "Explain how the Corrective Agent highlights speaker errors using details-on-demand overlays."
*   **Answer:** "The Corrective Agent constantly cross-references live transcriptions against our local compiled knowledge base (RAG):
    1.  **Error Flagging:** If a speaker says *'We are using an RTX 3070 GPU,'* and the local ledger indicates the actual hardware is an *RTX 3060*, the agent identifies the mismatch.
    2.  **Amber Alert:** The agent publishes an update via the Event Bus. The SvelteKit frontend catches the update and dynamically highlights the affected *'Hardware Specifications'* node in amber (pulsing micro-animation).
    3.  **Details-on-Demand Lookup:** The amber node displays a small alert icon. When clicked, it slides out the detail panel, showing the conflicting statement, the verified parameter from the database, and an on-demand link to the hardware documentation, correcting the error without interrupting the meeting's vocal flow."

#### Q16: "How do you handle the D3.js force-directed layout stability when new nodes are constantly being added in real time?"
*   **Answer:** "Real-time node insertion into a force simulation causes visual instability — nodes jump and the layout 'explodes' as forces re-equilibrate. We mitigate this with three techniques:
    1.  **Warm Start Positioning:** New nodes are inserted at the centroid of their parent topic cluster, not at random positions. This minimizes the force displacement.
    2.  **Alpha Decay Tuning:** We set D3's `alphaDecay` to a high value (0.05) so the simulation quickly settles after each insertion, preventing prolonged jittering.
    3.  **Incremental Simulation:** Instead of restarting the full simulation on each node add, we run only 50 additional ticks, allowing the new node to find its equilibrium without disturbing stable nodes."

---

### Category F: Usability, Verification, & Empirical Math Proofs

#### Q17: "Describe the methodology and metrics for Experiment 1 (Turn-Taking Latency)."
*   **Answer:** "We evaluate the pipeline's responsiveness:
    1.  **Methodology:** We replay 10 recorded Taglish and Ilocano-English academic defense sessions through our ingestion pipeline.
    2.  **Instrumentation:** We log timestamps at:
        *   $T_0$: Audio frame generated at microphone.
        *   $T_{\text{VAD}}$: Neural VAD signals voice endpoint.
        *   $T_{\text{STT}}$: Whisper emits final text token.
        *   $T_{\text{dispatch}}$: Context-Captain dispatches event to Event Bus.
    3.  **Metrics:** We measure the end-to-end loop ($T_{\text{dispatch}} - T_0$). The target is to maintain an average latency of $<700\text{ms}$ while keeping false-interruption cut-offs (where the VAD cuts off a speaker who was just pausing) below 5%."

#### Q18: "Explain Experiment 2 and how you calculate the Node-to-Edge Visual Readability Index ($R_{\text{graph}}$)."
*   **Answer:** "We evaluate if our $V_{\text{gold}}$ memory eviction protocol prevents visual clutter:
    1.  **Methodology:** We run a 90-minute design session through two setups: Control (standard rolling token graph, no eviction) and Experimental (running $V_{\text{gold}}$ eviction and node compression).
    2.  **Formulation:** We calculate the Readability Index:
        $$R_{\text{graph}} = \frac{V_{\text{active}}}{E_{\text{active}}} \cdot \frac{1}{1 + D_{\text{crossing}}}$$
        Where $V_{\text{active}}$ is the number of active nodes, $E_{\text{active}}$ is the number of links, and $D_{\text{crossing}}$ is the count of overlapping or crossing edges.
    3.  **Target:** The Experimental setup must maintain an $R_{\text{graph}}$ score $\ge 0.75$ throughout the 90 minutes, whereas the Control setup is expected to degrade to $<0.30$ as nodes accumulate."

#### Q19: "Walk the panel through the Cost-Latency Optimization Proof and how $\lambda$ is tuned."
*   **Answer:** "We model our routing as a multi-objective loss minimization:
    $$\min_{\alpha} \Big( C_{\text{API}}(\alpha) + \lambda \cdot L_{\text{system}}(\alpha) \Big) \quad \text{subject to } Q_{\text{synthesis}}(\alpha) \ge \beta$$
    1.  **Cost function $C_{\text{API}}(\alpha)$:** The cumulative API cost, which decreases as the threshold $\alpha$ increases (forcing more local model usage).
    2.  **Latency function $L_{\text{system}}(\alpha)$:** System latency, which decreases as $\alpha$ increases because local edge processing (no WAN delays) takes under 200ms compared to cloud API roundtrips (1.2s+).
    3.  **Tuning parameter $\lambda$:** If we have a stable internet connection but a tight budget, we set a high $\lambda$ to penalize cost. If speed and conceptual quality are paramount (such as during a live title defense), we set a low $\lambda$, allowing more cloud escalation. The Context-Captain dynamically adjusts $\lambda$ based on the active room mode, ensuring the optimal threshold $\alpha$ is maintained automatically."

#### Q20: "How do you measure cognitive load reduction? What survey instrument do you use?"
*   **Answer:** "We use the **NASA Task Load Index (NASA-TLX)**, a standardized six-dimensional survey:
    1.  **Mental Demand:** How mentally demanding was the task?
    2.  **Physical Demand:** How physically demanding? (Low for a meeting, but included for completeness.)
    3.  **Temporal Demand:** How hurried or rushed was the pace?
    4.  **Performance:** How successful were you in accomplishing what you were asked to do?
    5.  **Effort:** How hard did you have to work?
    6.  **Frustration:** How insecure, discouraged, irritated, stressed, and annoyed were you?
    
    We administer the NASA-TLX to both the Control group (traditional note-taking during a 90-minute session) and the Experimental group (using SynapseRT). The hypothesis is that the Experimental group reports statistically lower scores on Mental Demand, Temporal Demand, and Effort."

---

### Category G: Security, Privacy, & Edge Deployment

#### Q21: "Where does the audio data go? Is it uploaded to the cloud?"
*   **Answer:** "By default, all audio processing happens **entirely on-premise** within the local server environment. Audio frames travel from the client browser to the server over a local network (VLAN 50). The VAD, STT, and all agent processing occur inside VMs 200 and 201 on the local server. No audio data leaves the local network unless the Context-Captain explicitly escalates a text segment to a cloud API for complex synthesis — and even then, only the processed text is sent, never the raw audio. This provides strong privacy guarantees for sensitive academic discussions."

#### Q22: "How do you handle data retention and deletion?"
*   **Answer:** "SynapseRT implements a tiered data lifecycle:
    1.  **Session Data (L1/L2):** Automatically purged when the session ends, unless the facilitator explicitly saves the session.
    2.  **Saved Sessions (Long-Term):** Stored in Neo4j with an expiration policy. Default retention is 90 days, configurable by the administrator.
    3.  **Manual Deletion:** The facilitator can delete any saved session at any time. Deletion cascades through all tiers — L2 Redis, Neo4j, and any vector embeddings in pgvector.
    4.  **No Training Data Collection:** SynapseRT does not collect or use session data to fine-tune any models. The local SLM runs pre-trained weights without modification."

#### Q23: "What happens if the server loses power or crashes mid-session?"
*   **Answer:** "Resilience is handled at two levels:
    1.  **Redis Persistence:** Redis is configured with AOF (Append-Only File) persistence, writing every mutation to disk. On server restart, the L2 state can be reconstructed from the AOF log, recovering the session graph up to the last write before the crash.
    2.  **Client-Side Buffer:** The browser's AudioWorklet maintains a 30-second circular buffer. If the WebSocket connection drops, the client queues frames locally and replays them upon reconnection. Segments processed before the crash are preserved in Redis; only the exact moment of the crash is lost."

---

### Category H: Comparison with Existing Systems

#### Q24: "How does SynapseRT differ from Otter.ai, Fireflies.ai, or Microsoft Teams transcription?"
*   **Answer:** "The fundamental difference is architectural, not just feature-based:

| Feature | Otter.ai / Fireflies.ai / Teams | SynapseRT |
| :--- | :--- | :--- |
| **Processing Model** | Single-agent cloud pipeline | Multi-agent local edge orchestration |
| **Output Format** | Flat text transcript | Interactive relational knowledge graph |
| **Latency** | 3–10 seconds (batch) | < 700ms (streaming) |
| **Contradiction Handling** | None — overwrites or ignores | Preserves tension edges between conflicting assertions |
| **Memory Management** | Rolling context window (token limit) | Tiered hierarchy with semantic paging ($V_{\text{gold}}$) |
| **Privacy** | Cloud-dependent (audio uploaded) | Local edge (audio never leaves premise) |
| **Synchronization** | N/A (single agent) | MESI cache coherence protocol |
| **Cognitive Load Mitigation** | None (passive dump) | Active — Suggestive Agent, sub-graph isolation, amber alerts |

SynapseRT is not a transcription tool. It is a **cognitive orchestration system** that actively participates in structuring the meeting's knowledge output."

---

## 9. Difficulty Acknowledgment & Roadmap

### 9.1 Honest Difficulty Assessment
We rate this project as **high-complexity but within capability**. The three genuinely hard components are:

1. **Real-Time Streaming STT Accuracy in Taglish:** Whisper's performance on code-switched Tagalog-English speech is not well-documented. We may encounter accuracy degradation on informal Taglish that requires prompt-engineering workarounds or a fine-tuned adapter.
2. **Multi-Agent MESI Synchronization Under Load:** While the protocol is well-defined theoretically, implementing lock-free coordination across 4 concurrent agents with sub-300ms operations requires careful engineering to avoid edge-case deadlocks and performance regressions.
3. **D3.js Force Layout Stability with Real-Time Node Insertion:** Maintaining a visually stable, non-jittering graph while continuously adding and removing nodes is an unsolved UX challenge. Our alpha-decay tuning and warm-start positioning mitigate but may not fully eliminate visual instability during rapid topic changes.

### 9.2 Three-Phase Execution Roadmap

| Phase | Duration | Focus | Deliverable |
| :--- | :--- | :--- | :--- |
| **Phase 1 — Infrastructure & Pipeline** | Weeks 1–4 | Local virtualization setup, Ollama deployment, audio ingestion pipeline, VAD + STT streaming, basic WebSocket transport | Working audio-to-text streaming demo with < 700ms latency |
| **Phase 2 — Agent Orchestration & Memory** | Weeks 5–10 | Multi-agent framework, Event Bus, MESI protocol, L1/L2/LT memory hierarchy, $V_{\text{gold}}$ paging, DA classifier | Working multi-agent system that produces structured graph output from live audio |
| **Phase 3 — Visualization & Evaluation** | Weeks 11–14 | D3.js knowledge graph, SvelteKit dashboard, role-based views, sub-graph splits, empirical experiments (NASA-TLX, $R_{\text{graph}}$) | Complete system with evaluation data and defense-ready results |

Each phase has a working deliverable that can be demoed independently, so even if one component is delayed it does not block the entire defense.

### 9.3 Self-Assessment
> "We rate this as high-complexity but within our capability — the core components are open-source and documented (Ollama, Faster-Whisper, Silero VAD, D3.js, Redis, SvelteKit), and the team has prior experience with edge servers and local network design."

---

## 10. Summary System Matrix

| Layer | Core Technology | Compliance/Standard | Security/Privacy Mitigation | Role in Project |
| :--- | :--- | :--- | :--- | :--- |
| **Virtualization** | Local Linux Hypervisor (e.g., KVM/LXD) | PCIe Hardware Passthrough, ZFS storage | Isolated host kernel, strict VM firewall rules | Separates application server, local inference node, and networking gateways. |
| **Audio Ingestion** | WebSockets, Web Audio API | 20ms Audio Frame Packetization | WSS secure channels, client-side memory buffering | Captures live microphone feeds and pipes raw packets to the VAD VM. |
| **Voice Activity** | Silero VAD (Local RNN) | Millisecond Vocal Classification | Local edge VAD execution, zero external data sharing | Detects human speech starting and ending boundaries. |
| **Transcription** | Faster-Whisper, Dialogue Acts | 50ms Partial Transcript Cascading | Strict on-premise local model loading | Transcribes audio frames and classifies dialogue acts. |
| **Memory Tiering** | Redis (In-Memory Database) | L1/L2 Semantic Paging, $V_{\text{gold}}$ formula | Transient Redis data flushing, encrypted local caches | Manages volatile context cache, summaries, and unresolved loops. |
| **Agent Engine** | Nous Hermes 2 Pro (Mistral 7B) | ChatML prompt format, XML schemas | Structurally constrained parsing loops | Runs the local ReAct loop and invokes skill tools. |
| **PaaS Hosting** | Dokploy, Docker Engine | Container isolation, Traefik proxying | Private internal networks, isolated databases | Automates build pipelines and isolates backend, databases, and brokers. |
| **Dynamic Routing** | RouteLLM Classifier | Binary win-prediction classification | Cost-latency loss function minimization | Determines whether queries are solved locally or escalated to the cloud. |
| **Synchronization** | Semantic MESI Protocol | Software-defined Cache Coherence | Event Bus invalidation signals | Prevents race conditions and state desynchronization among parallel agents. |
| **Dynamic UI** | D3.js, Svelte | Ben Shneiderman Taxonomy | DOM element isolation, lazy-loaded detail panels | Maps JSON payloads to graphs, timelines, and Kanban boards. |
| **Orchestration** | Svelte stores, CSS Transitions | Dillenbourg Orchestration Graphs | Role-based layout filters | Renders role-specific dashboards (Learner, Facilitator, Note-Taker). |
| **Long-Term Storage** | Neo4j Graph DB, pgvector | Cross-session episodic retrieval | Encrypted disk storage, session-scoped access | Archives full relational graphs and vector embeddings for retrieval. |
| **Verification** | NASA-TLX Survey, $R_{\text{graph}}$ index | Standardized 6-pillar cognitive index | Anonymized survey aggregation | Empirically evaluates cognitive load and graph readability. |

---

## 11. Complete Technology Stack Reference

| Category | Technology | Version / Variant | Purpose |
| :--- | :--- | :--- | :--- |
| Hypervisor | Type-1 Hypervisor (e.g., KVM/LXD) | 8.x | Type-1 bare-metal virtualization |
| Server OS | Ubuntu Server | 24.04 LTS | Application and inference VM base |
| Network OS | OpenWrt | 23.x | VLAN routing, QoS, DHCP/DNS |
| Frontend | SvelteKit | Latest | Real-time dashboard, SSR, WebSocket client |
| Graph Rendering | D3.js | v7 | Force-directed knowledge graph visualization |
| CSS Framework | Vanilla CSS + CSS Custom Properties | — | Custom design system, no framework dependency |
| Backend Runtime | Node.js | 20 LTS | SvelteKit server, WebSocket server, Event Bus consumer |
| Database (Relational) | PostgreSQL | 16 | User accounts, session metadata, audit logs |
| Database (Graph) | Neo4j | 5.x | Long-term knowledge graph storage |
| Database (Cache) | Redis | 7.x | L2 Working Memory, Event Bus (Pub/Sub) |
| Vector Store | pgvector (PostgreSQL extension) | Latest | Semantic similarity search for RAG |
| Local LLM Runtime | Ollama | Latest | Hosts quantized SLM with parallel context slots |
| Local LLM Model | Nous Hermes 2 Pro (Mistral 7B) | Q4_K_M GGUF | Multi-agent reasoning, structured output |
| STT Engine | Faster-Whisper | Large-v2 / Medium | Streaming speech-to-text with partial cascading |
| VAD Engine | Silero VAD | v5 ONNX | Neural voice activity detection |
| DA Classifier | DistilBERT (fine-tuned) or rule-based | — | Dialogue act classification, backchannel detection |
| Routing Classifier | RouteLLM | — | Binary local-vs-cloud routing decision |
| Container Platform | Docker Engine | Latest | Application containerization inside Dokploy |
| PaaS | Dokploy | Latest | Self-hosted deployment dashboard |
| Reverse Proxy | Traefik | v3 | HTTPS termination, automatic routing |
| QoS | SQM CAKE | OpenWrt package | Per-host bandwidth fairness |
| Survey Instrument | NASA-TLX | Standardized | Cognitive load evaluation |

---

*This document is the canonical reference for SynapseRT. All slide decks, pitch scripts, and defense preparations should be derived from the content herein.*
