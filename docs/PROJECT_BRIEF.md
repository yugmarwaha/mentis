# Mentis — Project Brief

> **Status:** Pre-implementation design and handoff, October 2026  
> **Purpose:** Shared context for the human developer and a local coding agent (Codex / Claude Code).  
> **Important:** This brief records our current reasoning. It is not a final technical specification. Challenge assumptions and record decisions before you add complexity.

## 1. Why this project exists

Access to information is not the problem. LLMs already make answers easy to get. The concern is that **getting an answer and understanding it in the moment are different from being able to reason independently and recall it later**.

Before chatbots, a learner might search books or many websites. The learner would reject unhelpful sources, try several ideas, and eventually reach an understanding. We believe some of that work can support learning. This work includes generating explanations, exploring approaches, making mistakes, and retrieving ideas. The goal is **not to make learning arbitrarily difficult**. The goal is to keep **productive struggle** and reduce unproductive frustration.

**Product hypothesis:** A tutor that controls *when and how* it helps can better support independent problem solving. The tutor bases its help on the learner's own attempted reasoning. The comparison is with a tutor that mainly optimizes for immediate correct responses.

**Not yet proven:** The product improves retention, transfer, or understanding. These are outcomes to test. Do not claim them in advance.

## 2. Product in one paragraph

Build a web-based AI tutor with two initial experiences:

- **Learn Mode:** Put independent thought first. Ask the learner to try an approach and discuss their reasoning. Optionally challenge the learner or encourage more exploration. Then give graduated help, or a complete explanation when appropriate. After an explanation, give a *similar but not identical* problem. Ask the learner to explain their thinking.
- **Exam Mode:** Put efficient preparation under time pressure first. Give more direct explanations, guided practice, and assessments without unnecessary resistance. This mode should still encourage recall when useful.

The tutor is a **learning companion, not an anti-cheating system**. People who want to bypass the process can do so. Preventing this is not an MVP goal.

## 3. Example interaction and crucial nuance

**Prompt:** “What is essential for life on a planet?”  
**Student:** “Oxygen.”

A weak tutor marks this answer wrong because it expects “water.” A stronger tutor sees that oxygen is important to many organisms but **not necessary for all life**. Water is important for *life as we know it*. The stronger tutor clarifies the context and credits defensible interpretations. It asks the learner to explore other requirements. It does not force one expected answer.

This example shows a central engineering problem: **evaluate reasoning in context, not keyword overlap with a reference answer**. Some questions have many valid answers, hidden assumptions, or no single consensus answer.

## 4. Candidate learner journey (MVP)

1. The learner chooses **Learn** or **Exam** mode. The learner poses a question or chooses a problem.
2. In Learn Mode, the app asks what the learner has tried or how the learner is thinking. It does not reveal a complete answer immediately.
3. The learner submits an attempt, partial reasoning, or an honest “I don't know where to start.”
4. A reasoning assessment interprets the attempt. It includes uncertainty and alternative valid approaches.
5. A **backend intervention policy** selects a permitted next action. This policy is separate from the free-form response of the model. The actions are:
   - invite another attempt / revisit the question;
   - ask a focused, non-leading question;
   - offer a limited hint;
   - explain an error or misconception;
   - give a complete solution when justified.
6. If the app shows a solution, it generates a related transfer question. It asks the student to explain the approach. It does not immediately give a worked answer.
7. The app persists attempts, interventions, and later independent responses. The team uses them for debugging and evaluation.

**Critical nuance:** We do **not** yet know the right thresholds for these transitions. Do not hard-code arbitrary universal rules such as “5 minutes for easy questions” or “exactly two tries for hard questions.” These factors may matter: complexity, previous attempts, quality of reasoning, learner goals, and frustration. Time can be a signal, but it is not proof of effort.

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

**Why separate the evaluator, policy, and generator?** A system prompt that says “don't reveal the answer” is not reliable enforcement. The backend should govern state and eligible interventions. Where possible, the backend should limit what the response generator receives or may reveal. With open-ended problems, hints from the model can still leak solutions. We claim no perfect guarantee.

**Tech candidates:** Python, FastAPI, React, TypeScript, PostgreSQL, OpenAI API or a comparable LLM API. **LangGraph** is optional. Use it only if the workflow becomes complex enough to justify graph orchestration. **PyTorch** is not part of the initial implementation. Do not add it only to decorate the skills list.

**Agent instruction:** Do not build everything at once. Work in vertical slices with explicit tests. Explain architectural choices and tradeoffs before you generate large amounts of code. The developer should understand and own the major decisions and the implementation.

## 6. Questions we've discussed and where we landed

| Question | Current answer / position |
|---|---|
| Why can ordinary LLM tutoring be insufficient? | Instant, plausible answers may reduce chances for learners to generate and retrieve ideas independently. This is a hypothesis from learning-science research. It is not a universal claim that AI harms learning. |
| Is friction itself the goal? | No. **Productive cognitive effort** is the goal. Avoid arbitrary delays and pointless frustration. |
| When should a learner receive a hint or solution? | Ask for the learner's approach. Consider what the learner has tried, including being genuinely stuck. Re-invite reasoning when useful. Give a hint or solution when appropriate. Specific thresholds need design and testing. |
| Should every question have one expected answer? | No. Handle many defensible interpretations. Clarify assumptions and acknowledge valid alternatives. |
| How do we know learners understood? | After assistance, ask them to solve a similar problem independently and explain their thinking. Later, consider delayed tests of recall/transfer. |
| How do we tell genuine thought from convincing text? | A long answer is not proof of effort. Use quality of reasoning and follow-up performance as limited signals. Do not claim to detect genuine internal thought. Do not prohibit outside AI. |
| How can we compare this against ChatGPT fairly? | The baseline depends on the prompt. Evaluate against **multiple defined baselines** across a fixed task set. The baselines are an ordinary assistant, a carefully prompted Socratic tutor, and ideally an ablated version of our own system. Keep the models, questions, and scoring rules consistent. Keep temperature/settings consistent where practical. |
| How can we test without many users? | Start with automated scenario evaluation and manual dogfooding. Then seek a modest voluntary student pilot. Automated scores measure system behavior. **Only learner studies can begin to support learning-outcome claims.** |
| Is training our own model required? | No for MVP. We could explore a small embedding-based classifier or a LoRA/QLoRA fine-tune later, if data and evaluation support it. |
| Does a large model need an expensive local GPU? | Not necessarily. Small-model training, LoRA/QLoRA, free/limited hosted GPUs, and rented GPUs exist. Available compute is not the biggest risk. **Reliable training labels are harder.** |
| Do we need to stop students cheating? | No for MVP. This is a self-directed learning tool, not an exam proctor. |
| How to prevent a merely prompted chatbot? | Enforce a separate, testable intervention policy. Track state and check output behavior. Benchmark against prompt-only implementations. Document measurable engineering improvements. |
| What is the role of Matt Pocock's `grill-with-docs`? | **Use its relentless-questioning approach to interrogate *our project design and decisions*.** Use it to produce documentation (for example, ADRs/glossary). It is **not** an MVP runtime feature. It is not a student-facing tutoring skill. |

## 7. Alternatives considered

| Alternative | Decision | Reason |
|---|---|---|
| Generic chat UI plus a “be Socratic” system prompt | **Reject as the whole product; keep as baseline** | A prompt can easily override it. It is hard to enforce policy or show engineering differentiation. |
| Always refuse to provide complete solutions | **Reject** | It can turn learning into frustration. Some explanations are necessary and useful. |
| Fixed wait times or rigid attempt counts for all problems | **Defer / reject as universal rule** | It ignores problem difficulty and quality of attempt. It can reward waiting or meaningless submissions. |
| Give a hint every time a learner gets stuck | **Reject as default** | Hints can do the reasoning for students. Sometimes another independent attempt is better. |
| Score attempts solely against one reference answer | **Reject** | It punishes valid alternatives and ambiguous questions. |
| Train/fine-tune a dedicated model before building the app | **Defer** | It adds GPU, data, and labeling complexity before we know the core requirements. Compare simpler designs first. |
| Build an anti-cheating / external-AI detection system | **Out of scope** | Adversarial enforcement is not central to voluntary learning. |
| Recruit a large research study before writing code | **Reject as blocker** | It is not practical at first. Test reliability first and recruit users later. |
| Require LangGraph / microservices for resume keywords | **Reject as requirement** | Choose an architecture because it solves observed complexity. Do not choose it because it sounds impressive. |

## 8. Evaluation plan and metrics

**A. Engineering/evaluation metrics (possible without recruiting many users)**

- **Premature answer disclosure rate:** The percentage of cases where a response reveals the answer when policy forbids it. Define exact rubrics. Include cases where hints indirectly give away the solution.
- **Intervention-policy adherence:** The percentage of model turns that follow the intervention type selected by the backend.
- **Reasoning assessment agreement:** Compare model judgments with a manually labeled, adjudicated evaluation set. Example judgments: meaningful attempt, misconception, valid alternative, stuck. Report agreement and failure categories. Do not report only a single accuracy number.
- **Robustness to prompt paraphrases:** Test semantically equivalent questions. Test learner requests with different wording, including requests to “just tell me.”
- **Cost and latency:** Median/p95 end-to-end response latency. Estimated API cost per learning session.
- **Ablations:** Compare three setups with the same LLM: prompt only, prompt plus state/policy, and full evaluator/policy/generator. Keep scenario sets held out where possible.

**B. Educational outcomes (later, require real learners)**

- Independent performance on matched transfer questions after tutoring.
- Delayed retention/transfer (for example, after a week), when feasible.
- Learner frustration, perceived helpfulness, time on task, and dropout.
- Compare against a **strong**, carefully prompted ChatGPT baseline. Do not compare only against a deliberately weak one. Randomize or counterbalance topics and conditions where possible.

**Warnings:** Simulated learner responses are useful for debugging. They are not evidence that real students learned more. LLM-as-judge outputs need calibration and human review. Do not advertise any metric as proof of educational improvement without suitable data.

## 9. Research and inspiration

Our discussion produced three research themes:

1. **Generative AI and learning:** Short-term education studies suggest that unrestricted assistance may improve immediate performance. In some contexts it may weaken later independent performance. **Do not generalize from a single high-school mathematics study to all subjects, all learners, or long-term outcomes.**
2. **Retrieval practice / test-enhanced learning:** Retrieving knowledge can strengthen retention more than re-reading it.
3. **Productive failure:** Students who attempt and explore a problem before instruction can be better prepared to learn from a later explanation.

Research **informs hypotheses**. It does not dictate universal intervention rules. [research.md](research.md) lists the three papers and their main conclusions.

Design-process inspiration: Matt Pocock's **`grill-with-docs`** skill. It gives relentless interview questions, plus architecture decisions and a glossary. Use it during planning. It is not a requirement for the student-facing product.

## 10. Scope and sequencing

### Phase 0 — Decisions before coding

- Write 5–10 realistic example learning conversations. Include valid alternatives, novice stuck cases, persistent incorrect beliefs, solution demands, and subjective/ambiguous questions.
- Decide exactly what counts as a “premature disclosure,” a “meaningful attempt,” and a “good intervention.” Do this for a narrow initial subject domain.
- Choose the first domain intentionally (for example, introductory CS concepts or mathematics). **Undecided.** Tutoring on broad, arbitrary topics makes evaluation much harder.
- Record initial architecture decisions in brief ADRs. Define a minimal intervention state machine.

### Phase 1 — Small working end-to-end slice

- Learn Mode, one problem at a time. Capture the learner attempt. Run a structured reasoning assessment. Select the action in the backend. Generate a response. Persist the session.
- One follow-up/transfer problem after the explanation.
- Minimal React interface + FastAPI + database. No elaborate analytics dashboard yet.
- Test the state transitions. Include curated adversarial conversations.

### Phase 2 — Reliability and comparisons

- Build a scenario dataset. Start small and grow it as failures appear. Add explicit grading rubrics and repeatable evaluations.
- Compare prompt-only, carefully prompted, and orchestrated system variants.
- Improve answer-leak controls, ambiguity handling, state transitions, and instrumentation.
- Add Exam Mode with distinct goals and measurable behavior.

### Phase 3 — Ship and validate

- Deploy the app. Add essential reliability/privacy safeguards. Measure latency and costs.
- Invite a small number of voluntary users. Collect feedback responsibly and with clear consent.
- If feasible, compare unaided transfer/retention on matched topics. Be transparent about the limited sample size.

### Later / not MVP

- Train or fine-tune an intervention classifier (PyTorch, scikit-learn, LoRA/QLoRA) **only after** two conditions are met. First, collect defensible labels. Second, define what improves over a rule-based or LLM baseline.
- Personalized intervention policies trained on learner history; spaced review; multi-session knowledge tracking.
- Sophisticated difficulty estimation, adaptive problem selection, curriculum integrations, instructor dashboards.
- Anti-gaming/cheating defenses beyond basic abuse protection.
- Large-scale randomized educational study; user growth beyond a realistic early pilot.

## 11. Resume target — aspirational, not achieved

**Mentis | Python, FastAPI, React, TypeScript, PostgreSQL, LLM API**  
*Optional later: LangGraph if justified; PyTorch only if a model is actually trained.*

These are **target formulations**. Replace placeholders only with defensible measured values. Do not claim 3 modes when only 2 are built. Do not claim trained models without training them. Do not fabricate users.

- **Engineered** a full-stack adaptive AI tutoring platform using React, TypeScript, and FastAPI, orchestrating state-aware reasoning assessment and graduated interventions across **Learn and Exam** modes.
- **Architected** a backend-controlled intervention engine combining structured LLM evaluations and rule-based policy decisions, reducing premature answer disclosures by **[X]%** versus a carefully prompted baseline across **[N]** held-out learning scenarios.
- **Deployed** the platform with PostgreSQL-backed learning histories and a reproducible evaluation pipeline, achieving **[Y]%** intervention-policy adherence and **[Z] ms** p95 response latency across **[N]** test sessions.

**If real-user testing happens**, the third bullet can instead emphasize **[N] voluntary users** and independently measured follow-up performance, with honest caveats. Do not state “improved learning by X%” unless a study supports it.

**Resume-worthiness bar:** A narrowly scoped problem. Substantive, independently implemented engineering (not just API prompts). Repeatable, honest comparisons. A usable deployed app. Training a model is optional. No project or resume bullet can guarantee a particular hiring outcome.

## 12. Open questions for our next design session

1. What is our **first subject domain**, and why? Should we restrict v1 to objectively assessable questions?
2. What does the intervention evaluator output? Which criteria are reliable enough to use in policy decisions?
3. What is the first version of the **state machine**? When should a stuck learner get a clue or an explanation?
4. How can we keep a hint from unintentionally disclosing a full solution? What are the realistic limits?
5. Who produces and checks transfer questions? How do we avoid a follow-up that is too similar to the original?
6. What data do we store, and for how long? How do we protect learner privacy?
7. What baseline prompts and evaluation dataset would make a fair comparison?
8. Which technical choices are necessary on day one? Which are justified only after evidence?

## 13. Working agreement with the coding agent

- **Do not begin by scaffolding the whole app.** Do not implement features from this document blindly.
- First, summarize the intended MVP and challenge unresolved design choices. Ask **one focused question at a time**.
- Keep discussion conversational and short (normally 3–4 lines, unless the developer explicitly asks for detailed work).
- Use small vertical slices. Have the developer reason about data flow and states before you write implementations.
- Prefer tests and a documented hypothesis over adding technology for the resume.
- Write short architecture decision records in `docs/adr/` when the team makes choices. Include options, tradeoffs, and what evidence would change the decision.
- Record failures found in evaluation, not only passing examples.
- Keep *proposed*, *implemented*, and *measured* features clearly distinct.

---

**Immediate next action:** Decide a narrow initial learning domain. Draft several real example learner–tutor transcripts. Then design the smallest intervention policy that handles those cases. Only then start the first vertical slice.
