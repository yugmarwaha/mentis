# Learning with Friction — Project Brief

> **Status:** Pre-implementation design and handoff, October 2026  
> **Purpose:** Shared context for the human developer and a local coding agent (Codex / Claude Code).  
> **Important:** This is a record of our current reasoning, not a finalized technical specification. Challenge assumptions and record decisions before adding complexity.

## 1. Why this project exists

The problem is not access to information; LLMs already make answers easy to obtain. The concern is that **getting an answer and understanding it in the moment are different from being able to reason independently and recall it later**.

Before chatbots, a learner might search books or multiple websites, reject unhelpful sources, try several ideas, and eventually reach an understanding. We believe some of that work—generating explanations, exploring approaches, making mistakes, and retrieving ideas—can support learning. The goal is **not to make learning arbitrarily difficult**. It is to preserve **productive struggle** while reducing unproductive frustration.

**Product hypothesis:** A tutor that controls *when and how* it helps, based on the learner's own attempted reasoning, can better support independent problem solving than a tutor that primarily optimizes for immediate correct responses.

**Not yet proven:** The product improves retention, transfer, or understanding. Those are outcomes to test, not claims to make in advance.

## 2. Product in one paragraph

Build a web-based AI tutor with two initial experiences:

- **Learn Mode:** Prioritize independent thought. Ask the learner to try an approach, discuss their reasoning, optionally challenge or encourage further exploration, then provide graduated help or a complete explanation when appropriate. After an explanation, give a *similar but not identical* problem and ask the learner to explain their thinking.
- **Exam Mode:** Prioritize efficient preparation under time pressure. Provide more direct explanations, guided practice, and assessments without unnecessary resistance. This should still encourage recall when useful.

The tutor is a **learning companion, not an anti-cheating system**. People who want to bypass the process can do so; preventing that is not an MVP goal.

## 3. Example interaction and crucial nuance

**Prompt:** “What is essential for life on a planet?”  
**Student:** “Oxygen.”

A weak tutor marks this simply wrong because it expects “water.” A stronger tutor recognizes that oxygen is important to many organisms but **not necessary for all life**; water is important for *life as we know it*. It should clarify the context, credit defensible interpretations, and ask the learner to explore other requirements rather than forcing one anticipated answer.

This example captures a central engineering problem: **evaluate reasoning in context, not keyword overlap with a reference answer**. Some questions have multiple valid answers, hidden assumptions, or no single consensus answer.

## 4. Candidate learner journey (MVP)

1. Learner chooses **Learn** or **Exam** mode and poses a question or chooses a problem.
2. In Learn Mode, the app asks what they've tried or how they're thinking, instead of revealing a complete answer immediately.
3. Learner submits an attempt, partial reasoning, or an honest “I don't know where to start.”
4. A reasoning assessment interprets the attempt, including uncertainty and alternative valid approaches.
5. A **backend intervention policy**, separate from the model's free-form response, selects a permitted next action:
   - invite another attempt / revisit the question;
   - ask a focused, non-leading question;
   - offer a limited hint;
   - explain an error or misconception;
   - give a complete solution when justified.
6. If a solution is shown, generate a related transfer question and ask the student to explain the approach without immediately providing a worked answer.
7. Persist attempts, interventions, and subsequent independent responses for debugging and evaluation.

**Critical nuance:** We do **not** yet know the right thresholds for these transitions. Do not hard-code arbitrary universal rules such as “5 minutes for easy questions” or “exactly two tries for hard questions.” Complexity, previous attempts, quality of reasoning, learner goals, and frustration may matter. Time can be a signal, but not proof of effort.

## 5. Architecture proposal — starting point, not an obligation

```text
React + TypeScript web UI
        |
        v
FastAPI application
        |
        +-- Session + learning-state manager
        +-- Reasoning evaluator (LLM structured assessment)
        +-- Intervention policy (backend state machine/rules)
        +-- Response generator (LLM, constrained by selected action)
        +-- Evaluation/telemetry pipeline
        |
        +-- PostgreSQL (sessions, attempts, interventions, outcomes)
        +-- LLM API (generation/evaluation)
```

**Why separate evaluator, policy, and generator?** A system prompt requesting “don't reveal the answer” is not reliable enforcement. The backend should govern state and eligible interventions. Where possible, it should limit what the response generator receives or is permitted to reveal. However, with open-ended problems, model-generated hints can still leak solutions; no perfect guarantee is claimed.

**Tech candidates:** Python, FastAPI, React, TypeScript, PostgreSQL, OpenAI API or comparable LLM API. **LangGraph** is optional if the workflow becomes complex enough to justify graph orchestration. **PyTorch** is not part of the initial implementation just to decorate the skills list.

**Agent instruction:** Do not build everything at once. Work in vertical slices with explicit tests. Explain architectural choices and tradeoffs before generating large amounts of code. The developer should understand and own the major decisions and implementation.

## 6. Questions we've discussed and where we landed

| Question | Current answer / position |
|---|---|
| Why can ordinary LLM tutoring be insufficient? | Instant, plausible answers may reduce opportunities for learners to generate and retrieve ideas independently. This is a hypothesis influenced by learning-science research, not a universal claim that AI harms learning. |
| Is friction itself the goal? | No. **Productive cognitive effort** is the goal. Avoid arbitrary delays and pointless frustration. |
| When should a learner receive a hint or solution? | Ask for their approach and consider what they've tried, including being genuinely stuck. Re-invite reasoning when useful; supply a hint or solution when appropriate. Specific thresholds need design and testing. |
| Should every question have one expected answer? | No. Handle multiple defensible interpretations; clarify assumptions and acknowledge valid alternatives. |
| How do we know learners understood? | After assistance, ask them to solve a similar problem independently and explain their thinking. Later, consider delayed tests of recall/transfer. |
| How do we tell genuine thought from convincing text? | A long answer is not proof of effort. Use quality of reasoning and follow-up performance as limited signals; don't claim to detect genuine internal thought or prohibit outside AI. |
| How can we compare this against ChatGPT fairly? | The baseline depends on the prompt. Evaluate against **multiple defined baselines** (ordinary assistant, carefully prompted Socratic tutor, and ideally an ablated version of our own system) across a fixed task set. Keep models, temperature/settings where practical, questions, and scoring rules consistent. |
| How can we test without many users? | Start with automated scenario evaluation and manual dogfooding, then seek a modest voluntary student pilot. Automated scores measure system behavior; **only learner studies can begin to support learning-outcome claims**. |
| Is training our own model required? | No for MVP. A small embedding-based classifier or LoRA/QLoRA fine-tune could be explored later if data and evaluation support it. |
| Does a large model need an expensive local GPU? | Not necessarily: small-model training, LoRA/QLoRA, free/limited hosted GPUs, and rented GPUs exist; available compute is not the biggest risk. **Reliable training labels are harder.** |
| Do we need to stop students cheating? | No for MVP. This is a self-directed learning tool, not an exam proctor. |
| How to prevent a merely prompted chatbot? | Enforce a separate, testable intervention policy, track state, check output behavior, benchmark against prompt-only implementations, and document measurable engineering improvements. |
| What is the role of Matt Pocock's `grill-with-docs`? | **Use its relentless-questioning approach to interrogate *our project design and decisions*** and produce documentation (e.g., ADRs/glossary). It is **not** an MVP runtime feature or a student-facing tutoring skill. |

## 7. Alternatives considered

| Alternative | Decision | Reason |
|---|---|---|
| Generic chat UI plus a “be Socratic” system prompt | **Reject as the whole product; keep as baseline** | Too easy to prompt away, difficult to enforce policy or demonstrate engineering differentiation. |
| Always refuse to provide complete solutions | **Reject** | Can convert learning into frustration; some explanations are necessary and useful. |
| Fixed wait times or rigid attempt counts for all problems | **Defer / reject as universal rule** | Doesn't account for problem difficulty or quality of attempt and can reward waiting/meaningless submissions. |
| Give a hint every time a learner gets stuck | **Reject as default** | Hints can do the reasoning for students; sometimes another independent attempt is better. |
| Score attempts solely against one reference answer | **Reject** | Punishes valid alternatives and ambiguous questions. |
| Train/fine-tune a dedicated model before building the app | **Defer** | Adds GPU/data/labeling complexity before we know the core requirements; compare simpler designs first. |
| Build an anti-cheating / external-AI detection system | **Out of scope** | Adversarial enforcement isn't central to voluntary learning. |
| Recruit a large research study before writing code | **Reject as blocker** | Not practical initially; test reliability first and recruit users later. |
| Require LangGraph / microservices for resume keywords | **Reject as requirement** | Choose architecture because it solves observed complexity, not because it sounds impressive. |

## 8. Evaluation plan and metrics

**A. Engineering/evaluation metrics (possible without recruiting many users)**

- **Premature answer disclosure rate:** Percentage of cases in which a response reveals the answer when policy forbids it. Define exact rubrics and include cases where hints indirectly give away the solution.
- **Intervention-policy adherence:** Percentage of model turns that follow the backend-selected intervention type.
- **Reasoning assessment agreement:** Compare model judgments (e.g., meaningful attempt, misconception, valid alternative, stuck) with a manually labeled, adjudicated evaluation set. Report agreement and failure categories, not just a single accuracy number.
- **Robustness to prompt paraphrases:** Test semantically equivalent questions and differently worded learner requests, including requests to “just tell me.”
- **Cost and latency:** Median/p95 end-to-end response latency and estimated API cost per learning session.
- **Ablations:** Same LLM with prompt only vs prompt plus state/policy vs full evaluator/policy/generator. Keep scenario sets held out where possible.

**B. Educational outcomes (later, require real learners)**

- Independent performance on matched transfer questions after tutoring.
- Delayed retention/transfer (e.g., after a week), when feasible.
- Learner frustration, perceived helpfulness, time on task, and dropout.
- Compare against a **strong** carefully prompted ChatGPT baseline, not just a deliberately weak one; randomize or counterbalance topics and conditions where possible.

**Warnings:** Simulated learner responses are useful for debugging but are not evidence that real students learned more. LLM-as-judge outputs need calibration and human review; no metric should be advertised as proof of educational improvement without suitable data.

## 9. Research and inspiration

Three research themes from our discussion:

1. **Generative AI and learning:** Short-term education studies suggest that unrestricted assistance may improve immediate performance while undermining later independent performance in some contexts. **Do not generalize from a single high-school mathematics study to all subjects, all learners, or long-term outcomes.**
2. **Retrieval practice / test-enhanced learning:** Retrieving knowledge can strengthen retention more than merely re-reading it.
3. **Productive failure:** Attempting and exploring a problem before instruction can prepare students to learn from a subsequent explanation.

Research **informs hypotheses**; it does not dictate universal intervention rules. Before implementation, identify and read the actual papers/methods and record bibliographic details and limitations accurately in `docs/research.md`.

Design-process inspiration: Matt Pocock's **`grill-with-docs`** skill — relentless interview/questions plus architecture decisions and glossary. Use it during planning, not as a requirement for the student-facing product.

## 10. Scope and sequencing

### Phase 0 — Decisions before coding

- Write 5–10 realistic example learning conversations, including valid alternatives, novice stuck cases, persistent incorrect beliefs, solution demands, and subjective/ambiguous questions.
- Decide exactly what counts as a “premature disclosure,” “meaningful attempt,” and “good intervention” for a narrow initial subject domain.
- Choose the first domain intentionally (e.g., introductory CS concepts or mathematics). **Undecided.** Broad arbitrary-topic tutoring makes evaluation much harder.
- Record initial architecture decisions in brief ADRs. Define a minimal intervention state machine.

### Phase 1 — Small working end-to-end slice

- Learn Mode, one problem at a time; learner attempt captured; structured reasoning assessment; backend action selection; response generated; session persisted.
- One follow-up/transfer problem after explanation.
- Minimal React interface + FastAPI + database; no elaborate analytics dashboard yet.
- Test the state transitions and include curated adversarial conversations.

### Phase 2 — Reliability and comparisons

- Build a scenario dataset (start small, grow as failures appear), explicit grading rubrics, and repeatable evaluations.
- Compare prompt-only, carefully prompted, and orchestrated system variants.
- Improve answer-leak controls, ambiguity handling, state transitions, and instrumentation.
- Add Exam Mode with distinct goals and measurable behavior.

### Phase 3 — Ship and validate

- Deploy the app, add essential reliability/privacy safeguards, measure latency and costs.
- Invite a small number of voluntary users; collect feedback responsibly and with clear consent.
- If feasible, compare unaided transfer/retention on matched topics. Be transparent about limited sample size.

### Later / not MVP

- Train or fine-tune an intervention classifier (PyTorch, scikit-learn, LoRA/QLoRA) **only after** collecting defensible labels and defining what improves over a rule-based or LLM baseline.
- Personalized intervention policies trained on learner history; spaced review; multi-session knowledge tracking.
- Sophisticated difficulty estimation, adaptive problem selection, curriculum integrations, instructor dashboards.
- Anti-gaming/cheating defenses beyond basic abuse protection.
- Large-scale randomized educational study; user growth beyond a realistic early pilot.

## 11. Resume target — aspirational, not achieved

**Learning with Friction | Python, FastAPI, React, TypeScript, PostgreSQL, LLM API**  
*Optional later: LangGraph if justified; PyTorch only if a model is actually trained.*

These are **target formulations**. Replace placeholders only with defensible measured values; don't claim 3 modes when only 2 are built, don't claim trained models without training them, and don't fabricate users.

- **Engineered** a full-stack adaptive AI tutoring platform using React, TypeScript, and FastAPI, orchestrating state-aware reasoning assessment and graduated interventions across **Learn and Exam** modes.
- **Architected** a backend-controlled intervention engine combining structured LLM evaluations and rule-based policy decisions, reducing premature answer disclosures by **[X]%** versus a carefully prompted baseline across **[N]** held-out learning scenarios.
- **Deployed** the platform with PostgreSQL-backed learning histories and a reproducible evaluation pipeline, achieving **[Y]%** intervention-policy adherence and **[Z] ms** p95 response latency across **[N]** test sessions.

**If real-user testing happens**, the third bullet can instead emphasize **[N] voluntary users** and independently measured follow-up performance, with honest caveats. Avoid stating “improved learning by X%” unless a study supports it.

**Resume-worthiness bar:** A narrowly scoped problem; substantive independently implemented engineering (not just API prompts); repeatable, honest comparisons; a usable deployed app. Training a model is optional. No project or resume bullet can guarantee a particular hiring outcome.

## 12. Open questions for our next design session

1. What is our **first subject domain**, and why? Should we restrict to objectively assessable questions in v1?
2. What does the intervention evaluator output? Which criteria are sufficiently reliable to use in policy decisions?
3. What is the first version of the **state machine**? When should a stuck learner get a clue or an explanation?
4. How can we keep a hint from unintentionally disclosing a full solution? What are realistic limits?
5. Who produces and checks transfer questions? How do we avoid a follow-up too similar to the original?
6. What data do we store, and for how long? How do we protect learner privacy?
7. What baseline prompts and evaluation dataset would constitute a fair comparison?
8. Which technical choices are necessary on day one versus justified only after evidence?

## 13. Working agreement with the coding agent

- **Do not begin by scaffolding the whole app** or implementing features from this document blindly.
- First summarize the intended MVP, challenge unresolved design choices, and ask **one focused question at a time**.
- Keep discussion conversational and short (normally 3–4 lines unless detailed work is explicitly requested).
- Use small vertical slices. Have the developer reason about data flow and states before writing implementations.
- Prefer tests and a documented hypothesis over adding technology for the resume.
- Write short architecture decision records in `docs/adr/` when choices are made; include options, tradeoffs, and what evidence would change the decision.
- Record failures discovered in evaluation, not only passing examples.
- Keep *proposed*, *implemented*, and *measured* features clearly distinct.

---

**Immediate next action:** Decide a narrow initial learning domain and draft several real example learner–tutor transcripts. Then design the smallest intervention policy that handles those cases. Only then start the first vertical slice.
