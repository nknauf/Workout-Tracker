# Multi-Turn Slot-Filling Dialogue NLP System Guide

## 🎯 Overview

This guide describes the implementation of a multi-turn slot-filling dialogue NLP system for workout and meal tracking. The system uses state-of-the-art transformer models for intent classification and token classification to provide a conversational interface for logging workouts and meals.

## 🏗️ Architecture

### Core Components

1. **Intent Classification Model** - Determines user intent (workout logging, meal logging, etc.)
2. **Token Classification Model** - Extracts entities (exercises, foods, numbers, etc.)
3. **Dialogue State Manager** - Tracks conversation state and slot filling progress
4. **Slot Validator** - Validates and normalizes extracted slot values
5. **Response Generator** - Generates appropriate system responses

### Model Recommendations

#### Intent Classification Model
**Primary Recommendation: `facebook/bart-large-mnli`**
- **Why**: Excellent zero-shot classification capabilities
- **Alternative**: `google/gemma-2b-it` (as requested, but may be overkill)
- **Fallback**: `distilbert-base-uncased` (faster, smaller)

#### Token Classification Model  
**Primary Recommendation: `FacebookAI/roberta-large`** (as requested)
- **Why**: State-of-the-art performance for NER tasks
- **Alternative**: `dslim/bert-base-NER` (general purpose)
- **Fallback**: `microsoft/DialoGPT-medium` (dialogue-specific)

## 📋 Slot Definitions

### Workout Slots

| Slot | Required | Description | Examples |
|------|----------|-------------|----------|
| `workout_type` | ✅ | Muscle groups worked | "Chest and Tricep Day", "Leg Day" |
| `exercises` | ✅ | Exercises performed | "Barbell Bench Press", "Cable Tricep Extensions" |
| `reps_per_exercise` | ❌ | Number of reps | "10 reps", "8-12 reps" |
| `sets_per_exercise` | ❌ | Number of sets | "3 sets", "4 sets" |
| `max_weight` | ❌ | Maximum weight used | "135 lbs", "225 lbs" |
| `save_option` | ✅ | Save for future or log today | "save for future", "log for today" |

### Meal Slots

| Slot | Required | Description | Examples |
|------|----------|-------------|----------|
| `food_eaten` | ✅ | Food consumed | "chicken and rice", "protein shake" |
| `calories` | ✅ | Total calories | "500 calories", "800 cal" |
| `protein` | ❌ | Protein in grams | "35g protein", "50 grams" |
| `carbs` | ❌ | Carbs in grams | "45g carbs", "60 grams" |
| `fats` | ❌ | Fat in grams | "20g fat", "15 grams" |
| `meal_save_option` | ✅ | Save for future or log today | "save for future", "log for today" |

## 🔄 Dialogue Flow

### Workout Logging Flow

```
User: "I want to log a workout"
System: "Great! What type of workout did you do? (e.g., chest and tricep day, leg day)"

User: "It was chest and tricep day"
System: "Perfect! What exercises did you perform? (e.g., Barbell Bench Press, Cable Tricep Extensions)"

User: "I did barbell bench press and cable tricep extensions"
System: "Great! I've recorded your chest and tricep day workout. Would you like to save this for future use or just log it for today?"

User: "Save it for future use"
System: "Perfect! I've saved your workout for future use."
```

### Meal Logging Flow

```
User: "I want to log a meal"
System: "Great! What food did you eat? (e.g., chicken and rice, protein shake)"

User: "I ate chicken and rice"
System: "Good! How many calories was that? (e.g., 500 calories, 800 cal)"

User: "It was 500 calories"
System: "Perfect! I've recorded your meal. Would you like to save this for future use or just log it for today?"

User: "Just log it for today"
System: "Got it! I've logged your meal for today."
```

## 🎯 Intent Classification

### Intent Types

1. **`workout_logging`** - User wants to log a workout
2. **`meal_logging`** - User wants to log a meal  
3. **`load_saved`** - User wants to load a saved workout/meal
4. **`edit_saved`** - User wants to edit a saved workout/meal
5. **`save_for_future`** - User wants to save current data for future use
6. **`log_for_today`** - User wants to log current data for today only
7. **`other`** - General conversation or unclear intent

### Training Data Examples

```python
# Workout Logging Examples
"I just finished a chest workout" → workout_logging
"I did some exercises today" → workout_logging
"I lifted weights this morning" → workout_logging
"I went to the gym and did bench press" → workout_logging

# Meal Logging Examples  
"I ate chicken and rice for lunch" → meal_logging
"I had a protein shake" → meal_logging
"I consumed 500 calories for breakfast" → meal_logging

# Load Saved Examples
"Load my saved chest workout" → load_saved
"Show me my saved meals" → load_saved

# Edit Saved Examples
"I want to edit my saved workout" → edit_saved
"Change my saved meal" → edit_saved
```

## 🏷️ Token Classification (NER)

### Entity Types

1. **`EXERCISE`** - Exercise names (bench press, squat, deadlift)
2. **`FOOD`** - Food names (chicken, rice, protein shake)
3. **`NUMBER`** - Numeric values (reps, sets, calories, protein grams)
4. **`WEIGHT`** - Weight units (lbs, kg, pounds)
5. **`WORKOUT_TYPE`** - Workout categories (chest day, leg day, upper body)
6. **`MEAL_TYPE`** - Meal categories (breakfast, lunch, dinner)

### Training Data Examples

```python
# Workout Examples
"I did chest and tricep day with barbell bench press"
# Tokens: ["I", "did", "chest", "and", "tricep", "day", "with", "barbell", "bench", "press"]
# Labels: ["O", "O", "B-WORKOUT_TYPE", "I-WORKOUT_TYPE", "I-WORKOUT_TYPE", "I-WORKOUT_TYPE", "O", "B-EXERCISE", "I-EXERCISE", "I-EXERCISE"]

"I did 3 sets of 10 reps bench press with 135 lbs"
# Tokens: ["I", "did", "3", "sets", "of", "10", "reps", "bench", "press", "with", "135", "lbs"]
# Labels: ["O", "O", "B-NUMBER", "O", "O", "B-NUMBER", "O", "B-EXERCISE", "I-EXERCISE", "O", "B-WEIGHT", "I-WEIGHT"]

# Meal Examples
"I ate chicken and rice with 500 calories"
# Tokens: ["I", "ate", "chicken", "and", "rice", "with", "500", "calories"]
# Labels: ["O", "O", "B-FOOD", "I-FOOD", "I-FOOD", "O", "B-NUMBER", "O"]
```

## 🚀 Implementation Steps

### Step 1: Model Setup

```python
# Install required packages
pip install transformers torch numpy scikit-learn

# Initialize models
from transformers import pipeline

# Intent Classification
intent_classifier = pipeline(
    "text-classification",
    model="facebook/bart-large-mnli",
    device="cuda" if torch.cuda.is_available() else "cpu"
)

# Token Classification  
token_classifier = pipeline(
    "token-classification", 
    model="FacebookAI/roberta-large",
    device="cuda" if torch.cuda.is_available() else "cpu"
)
```

### Step 2: Training Data Generation

You need to create thousands of training examples:

**Intent Classification: 5,000-10,000 examples**
- Various ways to express each intent
- Different user speaking styles
- Edge cases and ambiguous inputs

**Token Classification: 10,000-20,000 examples**
- Different exercise and food names
- Various number formats and units
- Mixed entity types in single sentences

**Multi-turn Dialogues: 1,000-2,000 complete dialogues**
- Different dialogue flows
- Error corrections and clarifications
- Various slot filling orders

### Step 3: Model Training

```python
# Intent Classification Training
from transformers import TrainingArguments, Trainer

training_args = TrainingArguments(
    output_dir="./models/intent_classifier",
    num_train_epochs=3,
    per_device_train_batch_size=8,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
)

trainer.train()
```

### Step 4: Integration

```python
# Initialize the multi-turn processor
nlp_processor = MultiTurnNLPProcessor(use_gpu=True)

# Process a dialogue turn
result = nlp_processor.process_dialogue_turn(
    user_id="user123",
    text="I want to log a chest workout"
)

print(result['response'])
# Output: "Great! I can help you log a workout. What type of workout did you do?"
```

## 📊 Training Data Requirements

### Intent Classification Data (5,000-10,000 examples)

**Workout Logging Examples:**
- "I just finished a chest workout"
- "I did some exercises today"
- "I lifted weights this morning"
- "I went to the gym and did bench press"
- "I completed my leg day routine"
- "I did upper body workout with pullups"
- "I trained chest and triceps today"
- "I worked out my back and biceps"
- "I did a full body workout"
- "I completed my shoulder routine"

**Meal Logging Examples:**
- "I ate chicken and rice for lunch"
- "I had a protein shake"
- "I consumed 500 calories for breakfast"
- "I had a salad with 200 calories"
- "I ate oatmeal with 150 calories"
- "I had beef and vegetables for dinner"
- "I consumed a smoothie with 300 calories"
- "I ate eggs and toast for breakfast"
- "I had yogurt with berries"
- "I consumed steak and broccoli"

**Load Saved Examples:**
- "Load my saved chest workout"
- "Show me my saved meals"
- "I want to use my previous workout template"
- "Load the meal I saved yesterday"
- "Get my saved workout routine"
- "Retrieve my meal template"

**Edit Saved Examples:**
- "I want to edit my saved workout"
- "Change my saved meal"
- "Modify my previous workout"
- "Update my saved meal template"
- "Edit the workout I saved"
- "I need to change my meal plan"

### Token Classification Data (10,000-20,000 examples)

**Exercise Entities:**
- bench press, squat, deadlift, pullup, pushup
- bicep curl, shoulder press, leg press, lat pulldown
- row, lunge, calf raise, plank, dip
- cable tricep extension, plate-loaded dip
- barbell curl, dumbbell press, machine row

**Food Entities:**
- chicken, rice, beef, fish, salad
- protein shake, oatmeal, pasta, sandwich
- smoothie, eggs, toast, yogurt, berries
- steak, broccoli, vegetables, potatoes
- sauce, dressing, seasoning, marinade

**Number and Unit Variations:**
- 10 reps, 8-12 reps, 5 reps, 15 reps
- 3 sets, 4 sets, 5 sets, 2 sets
- 135 lbs, 225 lbs, 100 kg, 185 pounds
- 500 calories, 800 cal, 1200 calories
- 35g protein, 50 grams protein, 25g
- 45g carbs, 60 grams carbs, 30g
- 20g fat, 15 grams fat, 10g

### Multi-turn Dialogue Data (1,000-2,000 dialogues)

**Sample Dialogue Patterns:**

1. **Complete Workout Logging:**
   ```
   User: "I want to log a workout"
   System: "What type of workout?"
   User: "Chest and tricep day"
   System: "What exercises?"
   User: "Bench press and cable extensions"
   System: "Save for future or log today?"
   User: "Save for future"
   ```

2. **Complete Meal Logging:**
   ```
   User: "I want to log a meal"
   System: "What food did you eat?"
   User: "Chicken and rice"
   System: "How many calories?"
   User: "500 calories"
   System: "Save for future or log today?"
   User: "Just log today"
   ```

3. **Load and Edit:**
   ```
   User: "Load my saved workout"
   System: "Here's your saved workout. Edit it?"
   User: "Yes, change exercises"
   System: "What exercises?"
   User: "Add dips"
   System: "Updated. Save or log?"
   User: "Save"
   ```

## 🔧 Model Configuration

### Recommended Model Settings

```python
# Intent Classification Model
intent_model_config = {
    "model_name": "facebook/bart-large-mnli",
    "max_length": 512,
    "batch_size": 8,
    "learning_rate": 2e-5,
    "num_epochs": 3,
    "warmup_steps": 100,
    "weight_decay": 0.01
}

# Token Classification Model
token_model_config = {
    "model_name": "FacebookAI/roberta-large", 
    "max_length": 512,
    "batch_size": 16,
    "learning_rate": 3e-5,
    "num_epochs": 4,
    "warmup_steps": 200,
    "weight_decay": 0.01
}
```

### Performance Metrics

**Target Performance:**
- Intent Classification Accuracy: >95%
- Token Classification F1-Score: >90%
- Slot Filling Accuracy: >85%
- Dialogue Completion Rate: >90%

## 🎯 Next Steps

1. **Generate Training Data**: Create thousands of examples using the patterns above
2. **Train Models**: Fine-tune the recommended models on your data
3. **Integrate**: Connect the NLP system to your Django application
4. **Test**: Evaluate performance on real user interactions
5. **Iterate**: Improve based on user feedback and usage patterns

## 📝 Training Data Generation Tips

1. **Use Templates**: Create sentence templates and fill with variations
2. **Include Edge Cases**: Add ambiguous, incomplete, and error cases
3. **Vary Language**: Include formal, casual, and technical speaking styles
4. **Add Noise**: Include typos, abbreviations, and informal language
5. **Balance Classes**: Ensure equal representation of all intents
6. **Context Matters**: Include context-dependent examples
7. **Realistic Flows**: Create natural dialogue progression patterns

## 🔍 Evaluation Strategy

1. **Holdout Test Set**: Reserve 20% of data for final evaluation
2. **Cross-Validation**: Use 5-fold cross-validation during training
3. **A/B Testing**: Compare with baseline regex-based system
4. **User Testing**: Collect feedback from real users
5. **Error Analysis**: Analyze failure cases to improve training data

This comprehensive system will provide a natural, conversational interface for your workout and meal tracking application! 