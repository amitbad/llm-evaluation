import ollama
import time
import sacrebleu
from rouge_score import rouge_scorer

# Change your models here
models = ['deepseek-r1:7b', 'mistral', 'llama3.1:8b', 'gemma2:9b']

# A sample paragraph about AI (what we want the models to summarize).
text = """Artificial intelligence (AI) is a field of computer science that aims to create machines capable of intelligent behavior. It has applications in various domains, including healthcare, finance, and transportation. AI systems can learn from data, make predictions, and automate tasks."""

# A "gold standard" summary of that paragraph (what a perfect summary might look like).
reference = "AI is a computer science field focused on creating intelligent machines with applications in healthcare, finance, and transportation. These systems learn from data, predict outcomes, and automate tasks."

def query_model(model, prompt):
    start_time = time.time()
    response = ollama.chat(model=model, messages=[{'role': 'user', 'content': prompt}])
    end_time = time.time()
    return response['message']['content'], end_time - start_time

if __name__ == "__main__":
    prompt = f"Summarize the following text in 2-3 sentences: {text}"
    for model in models:
        try:
            output, duration = query_model(model, prompt)
            print(f">> Model: {model}")
            print(f"Response: {output}")
            print(f"Time: {duration:.2f}s\n")
            
            # Compute BLEU
            bleu_score = sacrebleu.sentence_bleu(output, [reference])
            print(f"BLEU Score: {bleu_score.score:.2f}")
            # Compute ROUGE
            scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
            scores = scorer.score(reference, output)
            print(f"ROUGE-1 F1: {scores['rouge1'].fmeasure:.4f}")
            print(f"ROUGE-2 F1: {scores['rouge2'].fmeasure:.4f}")
            print(f"ROUGE-L F1: {scores['rougeL'].fmeasure:.4f}")
            print("=" * 50)
        except Exception as e:
            print(f"Error with {model}: {e}")
