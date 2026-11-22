# Teaching guidelines

These guidelines are required for every new or revised TestNeural LLM Academy lesson. Read them before drafting and use them during review. Keep the topic's official objectives, prerequisites, and scope in [MASTER_CURRICULUM.md](MASTER_CURRICULUM.md).

Follow this sequence for each new idea.

**Everyday example → Simple explanation → Technical name → Practical demonstration → Learner tries it**

## Write like you're teaching someone in front of you

1. **Start with something familiar.** Open with an everyday question, object, or decision the learner can picture without knowing the subject. Then carry that idea into the lesson's example.
2. **Explain why before how.** Show what goes wrong or what decision is hard before giving the method.
3. **Speak directly to the learner.** Use conversational, plain English and concrete examples. Give directions a beginner can act on.
4. **Introduce one idea at a time.** Build on what the learner has already seen. State any prerequisite the example actually needs.
5. **Name and explain technical terms when they first matter.** For example, show why a long request might not fit, then name the model's information capacity the *context window*. Keep the precise term so the learner can recognize it later.
6. **Show what happens in order.** Give the situation, identify the problem, explain why it happens, and show how to act. In a worked example, give the learner a moment to predict the result.
7. **Use short paragraphs and natural questions.** Let a paragraph carry one thought. Ask questions the learner can answer from what is on the page.
8. **Connect learning to a decision.** Explain who would use the result and what it would change. Show when the method is useful and where it can mislead.
9. **Keep the technical details accurate.** State what an analogy leaves out. Separate observations from guesses, real measurements from simulations, and evidence for one example from evidence for a broader claim.
10. **Teach Python from zero.** Introduce each new symbol, operation, or structure before the learner needs it. Explain familiar syntax briefly when it does something new in the example.

Review the order of ideas as well as the language. For each new term, identify the concrete thing the learner has already seen that gives it meaning. If the reader needs to understand several unfamiliar terms to follow a paragraph, split the demonstration and teach the missing idea first. Start the first Python program with the smallest operation that illustrates the lesson. Add another operation only after the learner knows what the first one does and can change its result.

## Beginner Python Execution Standard

Use an online Python editor as the default in every beginner lesson. Put the **Open Python Editor** link next to the practice instructions or the code. Use [Online Python](https://www.online-python.com/) as the recommended editor. Open it in a new tab with `rel="noopener noreferrer"`. Explain that learners paste the copied code themselves.

Teach the workflow in this order. **Copy Code → Paste → Run → Observe → Understand → Experiment.** Before the code, say what the learner is trying to find out and why. Give the exact expected output. After the run, explain why it happened, then ask the learner to predict and verify one small change and answer a checkpoint.

- Make every block runnable from an empty editor with Python 3.10+ and the standard library. Include its starting values, sample data, and any functions it calls. A previous step should never have to run first.
- Keep file creation, repository checkout, directory navigation, encoding, and terminal commands out of the main beginner workflow. Local execution is optional and clearly separated when it is documented.
- Give learners every file you ask them to open, edit, or run. Keep sample data inside beginner blocks. When a later lesson genuinely needs a file, link to the exact download and explain how to use it. Explain every dependency where it is introduced.
- Keep the Academy's code and expected output available without the editor. Link to the editor as a separate site and leave the choice to open it with the learner.

## Lead the learner through the lab

For each step, explain the goal and why it matters. Walk through the important lines in the order Python runs them, including what the names stand for, what changes, and why a branch is taken. Give the learner a complete snippet, clear instructions to run it, and the exact expected output. Read that output with them, then give them one change to predict, try, and explain. Finish with a checkpoint and its reasoning.

Keep worked examples, code, outputs, experiments, checkpoints, practice, solutions, knowledge checks, and assignments. Give the learner enough evidence to attempt each activity before showing its answer. Exercise prompts should say what to produce and what a sound answer would need to explain. Treat shorter sentences as a way to improve access to the same ideas, including their nuance and limitations.

## Review before publishing

Read the lesson as a first-time learner. Check each term at its first use. Check each example and exercise for missing assumptions, each code block for unexplained syntax, and each result for what it actually establishes. Keep author-only notes in the curriculum or audit sources. Run any changed examples and experiments and check their transcripts. Regenerate the course and run the synchronization and static-site checks described in [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md).

Have a person review the actual learning experience. Ask them to follow the link, paste code into an empty editor, predict a change, and explain one result in their own words. Record where they get stuck or need a term explained. Automated checks verify the examples and site wiring. Human review decides whether the sequence teaches the lesson.
