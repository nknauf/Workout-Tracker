from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
from datasets import load_dataset, Dataset
import torch
import json

with open("nlp_engine/intents.json") as f:
    data = json.load(f)

texts = [item['text'] for item in data]
labels = list(set(item["label"] for item in data))
label2id = {label: idx for idx, label in enumerate(labels)}
id2label = {idx: label for label, idx in label2id.items()}

encoded_labels = [label2id[item["label"]] for item in data]

# Tokenize
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
encodings = tokenizer(texts, truncation=True, padding=True)

# Create Hugging Face Dataset
dataset = Dataset.from_dict({
    "input_ids": encodings['input_ids'],
    "attention_mask": encodings['attention_mask'],
    "labels": encoded_labels
})

# Model
model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=len(labels))

# Training
training_args = TrainingArguments(
    output_dir="nlp_engine/model",
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=5,
    logging_dir="./logs",
    evaluation_strategy="no",
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
)

trainer.train()
model.save_pretrained("nlp_engine/model")
tokenizer.save_pretrained("nlp_engine/model")