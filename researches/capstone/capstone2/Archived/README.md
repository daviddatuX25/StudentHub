# Capstone 2 Proposal — SynapseRT

This directory contains the proposal resources, engineering specifications, and title defense preparation guides for **SynapseRT (Context-Aware Real-Time Salience Pipeline, Offline Agent Harness Engine, and Multi-View Visual Orchestration Framework for Collaborative Environments)**.

## Project Thesis
SynapseRT investigates a context-aware real-time salience pipeline that classifies live meeting speech by session mode and audience role, orchestrates an offline LLM agent with selective online tool access, and renders the appropriate information artifact dynamically into a collaborative visual workspace.

## Contents
- `synapsert_defense_guide.md` — The comprehensive title defense guide containing:
  - Slide pacing, verbal hooks, and panel defense strategy.
  - Core component coverage map (Web, Mobile, Agent Architecture, Dynamic UI Rendering).
  - Mathematical and algorithmic specifications for Session Classification and Visual Form Selection.
  - The Agent Harness escalation layer logic and function-calling schemas.
  - Detailed panel Q&A strategies tackling the "Salience vs. Noise" problem.

## System Target Metrics
- **Context Classification Accuracy (Session Mode)**: $>90\%$ precision on live stream windows
- **Visual Form Alignment Score**: $>85\%$ F1-Score compared to expert human facilitators
- **Harness Escalation Latency**: $<1.5$ seconds for local-to-online tool execution loops
- **State Synchronization Latency**: $<100\text{ms}$ delta between agent synthesis payload and SvelteKit View updates
- **Deployment Mode**: Hybrid Local Orchestration (Edge-deployed local model reasoning + selective WAN tool calling)
