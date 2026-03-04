from datasets import load_dataset

# Load a small subset of SQuAD validation set
dataset = load_dataset("squad", split="validation[:2]") 

print(">> Exploring SQuAD Dataset - Questions and Answers\n")

for i, item in enumerate(dataset):
    print(f"Example {i+1}:")
    print(f"Question: {item['question']}")
    
    # FIX: item['answers'] is a dict, item['answers']['text'] is the list of answers
    gold_answers = item['answers']['text'] 
    
    print(f"Gold Answers: {gold_answers}")
    print(f"Passage (first 300 chars): {item['context'][:3000]}...")
    print("-" * 50)