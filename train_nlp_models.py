#!/usr/bin/env python3
"""
Training script for custom NLP models for workout and meal tracking
"""

import os
import json
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification,
    AutoModelForTokenClassification,
    TrainingArguments, 
    Trainer,
    DataCollatorWithPadding
)
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import numpy as np
from typing import List, Dict, Tuple

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

class WorkoutMealDataset(Dataset):
    """Custom dataset for workout and meal classification"""
    
    def __init__(self, texts: List[str], labels: List[int], tokenizer, max_length: int = 128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

class EntityDataset(Dataset):
    """Custom dataset for named entity recognition"""
    
    def __init__(self, texts: List[str], labels: List[List[str]], tokenizer, max_length: int = 128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
        
        # Define entity labels
        self.label2id = {
            'O': 0,  # Outside
            'B-EXERCISE': 1,  # Beginning of exercise
            'I-EXERCISE': 2,  # Inside of exercise
            'B-FOOD': 3,      # Beginning of food
            'I-FOOD': 4,      # Inside of food
            'B-NUMBER': 5,    # Beginning of number
            'I-NUMBER': 6,    # Inside of number
            'B-UNIT': 7,      # Beginning of unit
            'I-UNIT': 8       # Inside of unit
        }
        self.id2label = {v: k for k, v in self.label2id.items()}
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = self.texts[idx]
        label_seq = self.labels[idx]
        
        # Tokenize and align labels
        tokenized = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        # Convert labels to IDs
        label_ids = [self.label2id.get(label, 0) for label in label_seq]
        label_ids = label_ids[:self.max_length]
        label_ids += [0] * (self.max_length - len(label_ids))  # Pad
        
        return {
            'input_ids': tokenized['input_ids'].flatten(),
            'attention_mask': tokenized['attention_mask'].flatten(),
            'labels': torch.tensor(label_ids, dtype=torch.long)
        }

def generate_training_data():
    """Generate synthetic training data for workout and meal classification"""
    
    # Workout examples
    workout_examples = [
        "I did 3 sets of 10 reps bench press and 5 sets of 5 deadlifts at 225 lbs",
        "30 minutes of running followed by 20 pushups and 15 pullups",
        "Upper body workout: 4x12 bicep curls, 3x10 shoulder press, 2x8 pullups",
        "Cardio session: 45 minutes cycling, 20 minutes walking",
        "Strength training: 3x8 squats at 185 lbs, 4x10 lunges, 2x15 calf raises",
        "Today's workout: 5x5 bench press at 135 lbs, 3x10 rows, 2x20 pushups",
        "Leg day: 4x12 squats, 3x15 lunges, 2x20 calf raises",
        "HIIT workout: 30 seconds burpees, 30 seconds rest, repeat 10 times",
        "Morning run: 5 miles in 45 minutes",
        "Weight training: deadlifts 3x5 at 225 lbs, overhead press 3x8 at 95 lbs",
        "Circuit training: 10 exercises, 3 rounds, 30 seconds each",
        "Yoga session: 60 minutes of vinyasa flow",
        "Swimming: 20 laps freestyle, 10 laps breaststroke",
        "Boxing workout: 3 rounds of shadow boxing, 3 rounds on heavy bag",
        "CrossFit: AMRAP 20 minutes of thrusters and pullups"
    ]
    
    # Meal examples
    meal_examples = [
        "I ate chicken breast with 250 calories and 35g protein, plus a protein shake",
        "Breakfast: oatmeal with 150 calories, banana with 100 calories, 2g protein",
        "Lunch: salad with 300 calories and 15g protein, apple with 80 calories",
        "Dinner: salmon 400 calories 45g protein, rice 200 calories, vegetables 50 calories",
        "Snack: protein bar 200 calories 20g protein, nuts 150 calories 5g protein",
        "Post-workout meal: grilled chicken 300 calories 40g protein, sweet potato 150 calories",
        "Breakfast bowl: eggs 180 calories 12g protein, avocado 120 calories, toast 80 calories",
        "Protein smoothie: 250 calories 25g protein with banana and berries",
        "Greek yogurt with honey: 150 calories 15g protein",
        "Tuna sandwich: 350 calories 25g protein, chips 150 calories",
        "Steak dinner: 8oz ribeye 500 calories 50g protein, mashed potatoes 200 calories",
        "Vegetarian meal: quinoa bowl 300 calories 12g protein, roasted vegetables 100 calories",
        "Pasta dinner: spaghetti 400 calories 12g protein, meatballs 200 calories 20g protein",
        "Smoothie bowl: 200 calories 8g protein with granola and fruit",
        "Protein pancakes: 300 calories 20g protein with maple syrup"
    ]
    
    # Other examples (not workout or meal)
    other_examples = [
        "What's the weather like today?",
        "I need to buy groceries",
        "Meeting at 3pm tomorrow",
        "The movie was really good",
        "Can you help me with this problem?",
        "I'm going to the store",
        "What time is it?",
        "The book is on the table",
        "I love this song",
        "How are you doing?",
        "The traffic is terrible today",
        "I need to call my mom",
        "What's for dinner tonight?",
        "The game starts at 7pm",
        "I'm tired and want to sleep"
    ]
    
    # Combine all examples
    all_texts = workout_examples + meal_examples + other_examples
    all_labels = [0] * len(workout_examples) + [1] * len(meal_examples) + [2] * len(other_examples)
    
    return all_texts, all_labels

def generate_entity_training_data():
    """Generate training data for named entity recognition"""
    
    # Example texts with entity labels
    training_data = [
        {
            "text": "I did 3 sets of 10 reps bench press",
            "entities": ["O", "O", "B-NUMBER", "O", "B-NUMBER", "O", "B-EXERCISE", "I-EXERCISE"]
        },
        {
            "text": "chicken breast 250 calories 35g protein",
            "entities": ["B-FOOD", "I-FOOD", "B-NUMBER", "O", "B-NUMBER", "B-UNIT", "O"]
        },
        {
            "text": "30 minutes of running",
            "entities": ["B-NUMBER", "B-UNIT", "O", "B-EXERCISE"]
        },
        {
            "text": "protein shake 200 calories",
            "entities": ["B-FOOD", "I-FOOD", "B-NUMBER", "O"]
        }
    ]
    
    texts = [item["text"] for item in training_data]
    labels = [item["entities"] for item in training_data]
    
    return texts, labels

def train_intent_classifier():
    """Train a custom intent classification model"""
    
    print("🔄 Training Intent Classification Model...")
    
    # Generate training data
    texts, labels = generate_training_data()
    
    # Split data
    train_texts, test_texts, train_labels, test_labels = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    # Load tokenizer and model
    model_name = "distilbert-base-uncased"  # Smaller, faster model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name, 
        num_labels=3  # workout, meal, other
    )
    
    # Create datasets
    train_dataset = WorkoutMealDataset(train_texts, train_labels, tokenizer)
    test_dataset = WorkoutMealDataset(test_texts, test_labels, tokenizer)
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir="./models/intent_classifier",
        num_train_epochs=3,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        warmup_steps=100,
        weight_decay=0.01,
        logging_dir="./logs",
        logging_steps=10,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
    )
    
    # Data collator
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
    
    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        data_collator=data_collator,
    )
    
    # Train the model
    trainer.train()
    
    # Evaluate
    results = trainer.evaluate()
    print(f"✅ Intent Classification Model trained successfully!")
    print(f"Test accuracy: {results['eval_accuracy']:.4f}")
    
    # Save the model
    trainer.save_model("./models/intent_classifier")
    tokenizer.save_pretrained("./models/intent_classifier")
    
    return model, tokenizer

def train_entity_recognizer():
    """Train a custom named entity recognition model"""
    
    print("🔄 Training Named Entity Recognition Model...")
    
    # Generate training data
    texts, labels = generate_entity_training_data()
    
    # Split data
    train_texts, test_texts, train_labels, test_labels = train_test_split(
        texts, labels, test_size=0.2, random_state=42
    )
    
    # Load tokenizer and model
    model_name = "distilbert-base-uncased"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForTokenClassification.from_pretrained(
        model_name,
        num_labels=9  # Number of entity types
    )
    
    # Create datasets
    train_dataset = EntityDataset(train_texts, train_labels, tokenizer)
    test_dataset = EntityDataset(test_texts, test_labels, tokenizer)
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir="./models/entity_recognizer",
        num_train_epochs=5,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        warmup_steps=100,
        weight_decay=0.01,
        logging_dir="./logs",
        logging_steps=10,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
    )
    
    # Data collator
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
    
    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        data_collator=data_collator,
    )
    
    # Train the model
    trainer.train()
    
    # Evaluate
    results = trainer.evaluate()
    print(f"✅ Named Entity Recognition Model trained successfully!")
    print(f"Test loss: {results['eval_loss']:.4f}")
    
    # Save the model
    trainer.save_model("./models/entity_recognizer")
    tokenizer.save_pretrained("./models/entity_recognizer")
    
    return model, tokenizer

def create_custom_models():
    """Create custom models for specific workout and meal patterns"""
    
    print("🚀 Creating Custom NLP Models...")
    
    # Create models directory
    os.makedirs("./models", exist_ok=True)
    os.makedirs("./logs", exist_ok=True)
    
    # Train intent classifier
    intent_model, intent_tokenizer = train_intent_classifier()
    
    # Train entity recognizer
    entity_model, entity_tokenizer = train_entity_recognizer()
    
    # Save model metadata
    metadata = {
        "intent_classifier": {
            "model_path": "./models/intent_classifier",
            "num_labels": 3,
            "label_map": {
                0: "workout",
                1: "meal", 
                2: "other"
            }
        },
        "entity_recognizer": {
            "model_path": "./models/entity_recognizer",
            "num_labels": 9,
            "label_map": {
                0: "O",
                1: "B-EXERCISE",
                2: "I-EXERCISE", 
                3: "B-FOOD",
                4: "I-FOOD",
                5: "B-NUMBER",
                6: "I-NUMBER",
                7: "B-UNIT",
                8: "I-UNIT"
            }
        }
    }
    
    with open("./models/metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    print("✅ Custom models created and saved successfully!")
    print("📁 Models saved in ./models/ directory")
    
    return metadata

def test_custom_models():
    """Test the trained custom models"""
    
    print("🧪 Testing Custom Models...")
    
    # Load models
    intent_model = AutoModelForSequenceClassification.from_pretrained("./models/intent_classifier")
    intent_tokenizer = AutoTokenizer.from_pretrained("./models/intent_classifier")
    
    entity_model = AutoModelForTokenClassification.from_pretrained("./models/entity_recognizer")
    entity_tokenizer = AutoTokenizer.from_pretrained("./models/entity_recognizer")
    
    # Test cases
    test_cases = [
        "I did 3 sets of 10 reps bench press",
        "I ate chicken breast with 250 calories",
        "What's the weather like today?",
        "30 minutes of running followed by pushups",
        "Protein shake with 200 calories and 25g protein"
    ]
    
    label_map = {0: "workout", 1: "meal", 2: "other"}
    
    for text in test_cases:
        # Intent classification
        inputs = intent_tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        outputs = intent_model(**inputs)
        predictions = torch.softmax(outputs.logits, dim=-1)
        predicted_label = torch.argmax(predictions, dim=-1).item()
        confidence = predictions[0][predicted_label].item()
        
        print(f"\nText: {text}")
        print(f"Intent: {label_map[predicted_label]} (confidence: {confidence:.3f})")
        
        # Entity recognition
        inputs = entity_tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        outputs = entity_model(**inputs)
        predictions = torch.argmax(outputs.logits, dim=-1)
        
        tokens = entity_tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
        entities = []
        
        for token, pred in zip(tokens, predictions[0]):
            if pred > 0:  # Not 'O' label
                entities.append(f"{token}: {pred.item()}")
        
        if entities:
            print(f"Entities: {entities}")

if __name__ == "__main__":
    print("🚀 Starting Custom NLP Model Training...")
    
    try:
        # Create custom models
        metadata = create_custom_models()
        
        # Test the models
        test_custom_models()
        
        print("\n🎉 Training completed successfully!")
        print("\nTo use the custom models:")
        print("1. Update the AdvancedNLPProcessor to load custom models")
        print("2. Replace the model paths in the processor")
        print("3. Test with real workout and meal data")
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        import traceback
        traceback.print_exc() 