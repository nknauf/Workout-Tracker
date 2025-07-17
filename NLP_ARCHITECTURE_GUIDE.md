# NLP Architecture Guide for Workout & Meal Tracker

## 🏗️ Current Architecture Overview

### **Current Implementation (Rule-Based)**
```
User Input → Regex Patterns → Structured Data → Database
```

### **Enhanced Implementation (ML-Based)**
```
User Input → Intent Classification → Entity Recognition → Structured Data → Database
                ↓                        ↓
            Workout/Meal/Other      Exercises/Foods/Numbers
```

---

## 🔍 Current NLP Logic Explained

### **1. Pattern Matching (Regex-Based)**

The current system uses **regular expressions** to extract structured data:

```python
# Workout Patterns
'exercise_with_reps': r'(\d+)\s*(?:x|sets?|reps?)\s*(\d+)\s*(?:reps?|times?)?\s*(?:of\s+)?([^,\n]+)'
# Matches: "3 sets of 10 reps bench press"

'exercise_with_weight': r'(\d+)\s*(?:lbs?|kg|pounds?)\s*(?:x|for)\s*(\d+)\s*(?:reps?|times?)?\s*(?:of\s+)?([^,\n]+)'
# Matches: "135 lbs x 5 reps deadlift"

# Meal Patterns  
'food_with_calories': r'([^,\n]+?)\s*(\d+)\s*(?:calories?|cal)'
# Matches: "chicken breast 250 calories"
```

### **2. Keyword Classification**

Uses predefined keyword lists to classify input type:

```python
workout_keywords = ['workout', 'exercise', 'reps', 'sets', 'lift', 'run', 'pushup', 'squat']
meal_keywords = ['ate', 'eat', 'food', 'meal', 'calories', 'protein', 'breakfast', 'lunch', 'dinner']
```

### **3. Confidence Scoring**

Calculates confidence based on pattern matches:

```python
confidence = min(0.9, 0.3 + len(exercises_found) * 0.2)
```

---

## 🚀 Enhanced NLP with Hugging Face Models

### **Model Architecture**

#### **1. Intent Classification Model**
- **Purpose**: Classify input as workout, meal, or other
- **Model**: `facebook/bart-large-mnli` (Zero-shot classification)
- **Alternative**: Custom fine-tuned DistilBERT
- **Output**: Confidence scores for each intent

#### **2. Named Entity Recognition (NER)**
- **Purpose**: Extract exercises, foods, numbers, units
- **Model**: `dslim/bert-base-NER` (General NER)
- **Alternative**: Custom fine-tuned model
- **Output**: Tagged entities with confidence scores

#### **3. Question Answering (QA)**
- **Purpose**: Extract specific values (sets, reps, calories, protein)
- **Model**: `deepset/roberta-base-squad2`
- **Output**: Structured data extraction

#### **4. Text Generation**
- **Purpose**: Generate workout/meal names
- **Model**: `gpt2` (Small model for demo)
- **Output**: Natural language generation

### **Advanced Processing Pipeline**

```python
def parse_workout_text(self, text: str) -> Dict:
    # 1. Intent Classification
    intent_scores = self.classify_intent(text)
    is_workout = intent_scores.get('workout logging', 0) > 0.3
    
    # 2. Entity Extraction
    entities = self.extract_entities(text)
    
    # 3. Structured Data Extraction
    structured_data = self.extract_structured_data(text)
    
    # 4. Advanced Exercise Parsing
    exercises = self._parse_exercises_advanced(text, entities)
    
    # 5. AI-Generated Workout Name
    workout_name = self._generate_workout_name(text, exercises, structured_data)
    
    # 6. Multi-factor Confidence
    confidence = self._calculate_confidence(intent_scores, entities, structured_data, exercises)
    
    return {
        'workout_name': workout_name,
        'exercises': exercises,
        'confidence': confidence,
        'intent_scores': intent_scores,
        'entities': entities,
        'structured_data': structured_data
    }
```

---

## 🎯 Model Training Strategy

### **1. Custom Model Training**

#### **Intent Classification Training**
```python
# Training Data Structure
workout_examples = [
    "I did 3 sets of 10 reps bench press",
    "30 minutes of running followed by pushups",
    "Upper body workout: 4x12 bicep curls"
]

meal_examples = [
    "I ate chicken breast with 250 calories",
    "Breakfast: oatmeal with 150 calories",
    "Protein shake with 200 calories"
]

other_examples = [
    "What's the weather like today?",
    "I need to buy groceries"
]

# Labels: 0=workout, 1=meal, 2=other
```

#### **Entity Recognition Training**
```python
# Training Data with BIO Tags
training_data = [
    {
        "text": "I did 3 sets of 10 reps bench press",
        "entities": ["O", "O", "B-NUMBER", "O", "B-NUMBER", "O", "B-EXERCISE", "I-EXERCISE"]
    },
    {
        "text": "chicken breast 250 calories 35g protein", 
        "entities": ["B-FOOD", "I-FOOD", "B-NUMBER", "O", "B-NUMBER", "B-UNIT", "O"]
    }
]
```

### **2. Training Process**

#### **Step 1: Data Preparation**
```python
# Generate synthetic training data
texts, labels = generate_training_data()

# Split into train/test
train_texts, test_texts, train_labels, test_labels = train_test_split(
    texts, labels, test_size=0.2, random_state=42, stratify=labels
)
```

#### **Step 2: Model Initialization**
```python
# Load pre-trained model
model_name = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(
    model_name, 
    num_labels=3  # workout, meal, other
)
```

#### **Step 3: Training Configuration**
```python
training_args = TrainingArguments(
    output_dir="./models/intent_classifier",
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    warmup_steps=100,
    weight_decay=0.01,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
)
```

#### **Step 4: Training Execution**
```python
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    data_collator=data_collator,
)

trainer.train()
```

---

## 🔧 Implementation Guide

### **1. Install Dependencies**

```bash
# Install basic requirements
pip install -r requirements_nlp.txt

# Or install individually
pip install torch transformers datasets tokenizers
pip install scikit-learn numpy pandas
```

### **2. Train Custom Models**

```bash
# Run the training script
python train_nlp_models.py
```

This will:
- Generate synthetic training data
- Train intent classification model
- Train entity recognition model
- Save models to `./models/` directory
- Test the models with sample inputs

### **3. Integrate with Django**

```python
# In your views.py
from .advanced_nlp_processor import AdvancedNLPProcessor

# Initialize the processor
nlp = AdvancedNLPProcessor(use_gpu=False)  # Set to True if GPU available

# Use in your views
def conversational_input(request):
    if request.method == 'POST':
        text = request.POST.get('input_text')
        
        # Parse with advanced NLP
        if 'workout' in text.lower():
            result = nlp.parse_workout_text(text)
        else:
            result = nlp.parse_meal_text(text)
        
        return render(request, 'confirm.html', {'result': result})
```

### **4. Model Performance Monitoring**

```python
# Add logging and metrics
import logging
from sklearn.metrics import classification_report

def evaluate_model_performance():
    # Test on real user data
    test_cases = [
        "I did 3 sets of 10 reps bench press",
        "I ate chicken breast with 250 calories",
        "What's the weather like?"
    ]
    
    predictions = []
    true_labels = []
    
    for text in test_cases:
        result = nlp.parse_workout_text(text)
        predictions.append(result['intent_scores'])
        # Compare with expected results
    
    # Generate performance report
    report = classification_report(true_labels, predictions)
    logging.info(f"Model Performance:\n{report}")
```

---

## 📊 Model Performance Metrics

### **Expected Performance**

#### **Intent Classification**
- **Accuracy**: 90-95% for well-formatted input
- **Precision**: 85-90% for workout/meal classification
- **Recall**: 80-85% for edge cases
- **F1-Score**: 85-90% overall

#### **Entity Recognition**
- **NER Accuracy**: 85-90% for exercises and foods
- **Number Extraction**: 95%+ for explicit numbers
- **Unit Recognition**: 90%+ for common units

#### **Structured Data Extraction**
- **Sets/Reps**: 90%+ accuracy
- **Weights**: 85%+ accuracy
- **Calories/Protein**: 90%+ accuracy

### **Performance Optimization**

#### **1. Model Optimization**
```python
# Use smaller, faster models for production
model_name = "distilbert-base-uncased"  # Instead of bert-large
model_name = "microsoft/DialoGPT-small"  # For text generation
```

#### **2. Caching**
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_intent_classification(text: str):
    return nlp.classify_intent(text)
```

#### **3. Batch Processing**
```python
# Process multiple inputs at once
def batch_parse_texts(texts: List[str]):
    return [nlp.parse_workout_text(text) for text in texts]
```

---

## 🚀 Advanced Features

### **1. Context Awareness**

```python
class ContextAwareNLPProcessor:
    def __init__(self):
        self.user_history = {}
        self.preferences = {}
    
    def parse_with_context(self, text: str, user_id: int):
        # Load user history
        user_history = self.user_history.get(user_id, [])
        
        # Use context to improve parsing
        if "same as yesterday" in text:
            return self._parse_from_history(user_history)
        
        # Normal parsing with context
        result = self.parse_workout_text(text)
        result['context_suggestions'] = self._generate_suggestions(user_history)
        
        return result
```

### **2. Multi-language Support**

```python
# Use multilingual models
model_name = "xlm-roberta-base"  # Multilingual model

# Or train separate models for each language
models = {
    'en': 'english_model',
    'es': 'spanish_model', 
    'fr': 'french_model'
}
```

### **3. Real-time Learning**

```python
class AdaptiveNLPProcessor:
    def __init__(self):
        self.feedback_data = []
    
    def update_from_feedback(self, text: str, user_correction: Dict):
        # Store feedback for retraining
        self.feedback_data.append({
            'text': text,
            'prediction': self.last_prediction,
            'correction': user_correction
        })
        
        # Retrain model periodically
        if len(self.feedback_data) > 100:
            self.retrain_model()
```

---

## 🔒 Security and Validation

### **1. Input Sanitization**
```python
import re
from html import escape

def sanitize_input(text: str) -> str:
    # Remove potentially harmful content
    text = escape(text)
    text = re.sub(r'<script.*?</script>', '', text, flags=re.IGNORECASE)
    return text[:1000]  # Limit length
```

### **2. Model Validation**
```python
def validate_model_output(result: Dict) -> bool:
    # Check for reasonable values
    if result.get('confidence', 0) > 1.0:
        return False
    
    # Validate exercise data
    for exercise in result.get('exercises', []):
        if exercise.get('reps', 0) > 10000:
            return False
    
    return True
```

### **3. Rate Limiting**
```python
from django.core.cache import cache

def rate_limited_nlp_processing(user_id: int, text: str):
    cache_key = f"nlp_requests_{user_id}"
    requests = cache.get(cache_key, 0)
    
    if requests > 100:  # Max 100 requests per hour
        raise Exception("Rate limit exceeded")
    
    cache.set(cache_key, requests + 1, 3600)  # 1 hour expiry
    return nlp.parse_workout_text(text)
```

---

## 📈 Future Enhancements

### **1. Voice Input Integration**
```python
# Speech-to-text processing
import speech_recognition as sr

def process_voice_input(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
        text = recognizer.recognize_google(audio)
        return nlp.parse_workout_text(text)
```

### **2. Image Recognition**
```python
# OCR for handwritten workout logs
import pytesseract
from PIL import Image

def process_image_input(image_file):
    image = Image.open(image_file)
    text = pytesseract.image_to_string(image)
    return nlp.parse_workout_text(text)
```

### **3. Predictive Analytics**
```python
# Suggest workouts based on user patterns
def suggest_workout(user_id: int, date: date):
    user_history = get_user_workout_history(user_id)
    patterns = analyze_workout_patterns(user_history)
    suggested_workout = generate_workout_suggestion(patterns)
    return suggested_workout
```

---

## 🎯 Best Practices

### **1. Model Selection**
- Use **DistilBERT** for fast inference
- Use **BERT-large** for maximum accuracy
- Use **GPT-2** for text generation
- Consider **domain-specific models** for fitness

### **2. Data Quality**
- Collect diverse training data
- Include edge cases and variations
- Regular data validation and cleaning
- User feedback integration

### **3. Performance Monitoring**
- Track accuracy metrics over time
- Monitor inference latency
- Log user corrections and feedback
- A/B test different model versions

### **4. Deployment Strategy**
- Use **model versioning**
- Implement **gradual rollouts**
- Monitor **model drift**
- Plan **fallback strategies**

---

This architecture provides a solid foundation for advanced NLP capabilities while maintaining the reliability of rule-based fallbacks. The modular design allows for easy upgrades and improvements as the system evolves. 