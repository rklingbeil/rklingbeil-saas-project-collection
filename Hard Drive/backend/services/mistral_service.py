# File: /Users/rick/CaseProject/backend/services/mistral_service.py
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

def load_model():
    # Use the correct repository identifier for Mistral 7B Instruct v0.3
    model_name = "mistralai/Mistral-7B-Instruct-v0.3"
    # Load the tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    # Ensure a pad token is set (use eos_token if pad_token is missing)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        model.resize_token_embeddings(len(tokenizer))
    return tokenizer, model

def analyze_case(case_text):
    tokenizer, model = load_model()
    # Tokenize input with max_length=4096, truncation, and padding
    inputs = tokenizer(
        case_text,
        return_tensors="pt",
        max_length=4096,
        truncation=True,
        padding="max_length"
    )
    # Move model and inputs to GPU if available
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    inputs = {key: val.to(device) for key, val in inputs.items()}
    # Generate predictions using max_new_tokens for new output tokens
    output = model.generate(**inputs, max_new_tokens=128)
    predictions = tokenizer.decode(output[0], skip_special_tokens=True)
    return predictions

if __name__ == "__main__":
    # Sample test case text
    sample_case = "Enter legal case text here for testing."
    result = analyze_case(sample_case)
    print("Prediction:", result)

