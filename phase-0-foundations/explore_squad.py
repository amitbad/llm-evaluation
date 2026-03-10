from datasets import load_dataset

# ── ANSI colour helpers ──────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
CYAN   = "\033[36m"
YELLOW = "\033[33m"
GREEN  = "\033[32m"
PURPLE = "\033[35m"
WHITE  = "\033[97m"

def c(color, text):
    return f"{color}{text}{RESET}"

# Load a small subset of SQuAD validation set
dataset = load_dataset("squad", split="validation[:2]")

print()
print(c(CYAN, "=" * 64))
print(c(BOLD + WHITE, "  Phase 0 — Exploration: What Does Eval Data Look Like?"))
print(c(CYAN, "=" * 64))
print(f"""
  {c(YELLOW, 'This is NOT a test.')} No model is called. Nothing is evaluated.

  This is a {c(BOLD, 'reading exercise')}. Before you write your first eval,
  you need to understand what structured evaluation data looks like.
  Real benchmarks like SQuAD define exactly what we mean by
  'a question, a context, and a correct answer' — the same
  structure you will build yourself from Phase 1 onward.

  {c(BOLD + CYAN, 'What is SQuAD?')}
  Stanford Question Answering Dataset — a widely used benchmark
  where each example gives a model a passage and asks it a question.
  The {c(GREEN, 'gold answers')} are the known-correct answers a human provided.

  {c(BOLD, 'What to notice as you read:')}
    {c(YELLOW, '1.')} The gold answer is a short phrase extracted from the passage.
    {c(YELLOW, '2.')} There can be multiple valid phrasings of the same answer.
    {c(YELLOW, '3.')} The passage is the only source of truth — the model should
       not need to know anything outside it to answer correctly.

  This is the foundation of {c(CYAN, 'RAG evaluation (Test 9)')} and
  {c(CYAN, 'groundedness scoring (Test 7)')} — you will build this structure.
""")

for i, item in enumerate(dataset):
    print(c(YELLOW, "-" * 64))
    print(f"  {c(BOLD + WHITE, f'Example {i + 1}')}")
    print(f"  {c(DIM, 'Question    :')} {item['question']}")
    gold_answers = item['answers']['text']
    print(f"  {c(DIM, 'Gold Answers:')} {c(GREEN, str(gold_answers))}")
    print(f"  {c(DIM, 'Passage     :')}\n{item['context'][:300]}...")
print(c(YELLOW, "-" * 64))

print()
print(c(CYAN, "=" * 64))
print(c(BOLD + PURPLE, "  WHAT YOU JUST SAW"))
print(c(CYAN, "=" * 64))
print(f"""
  Every evaluation dataset follows this same pattern:
    {c(YELLOW, '-')} An {c(BOLD, 'input')}       (the question or prompt)
    {c(YELLOW, '-')} A {c(BOLD, 'context')}      (the source material, if any)
    {c(YELLOW, '-')} A {c(BOLD, 'gold answer')}  (what correct looks like)

  Your test cases in Excel from Phase 1 onward are exactly this —
  just expressed in a spreadsheet instead of a JSON dataset.

  {c(BOLD, 'The difference between SQuAD and what you will build:')}
    SQuAD uses {c(CYAN, 'extraction')}  — answer is a span in the passage
    Your tests use {c(CYAN, 'keyword checks')}, {c(CYAN, 'judge scoring')}, or
    {c(CYAN, 'semantic similarity')} to decide if the answer is good enough

  {c(BOLD + PURPLE, 'KEY LEARNING')}
  A {c(GREEN, 'gold answer')} is only as reliable as the human who wrote it.
  In production eval you decide what 'correct' means — and that
  decision is as important as the evaluation method itself.
""")
print(c(DIM, "  ─" * 32))
print(f"  {c(BOLD, '📖 Read the full details about SQuAD and benchmark datasets:')}")
print(f"     {c(CYAN, 'docs/test0.html')}  (open docs/index.html in a browser)")
print()
print(c(CYAN, "=" * 64))