# Multi-Turn Slot-Filling Dialogue NLP System

## 🎯 Overview

This implementation provides a comprehensive multi-turn slot-filling dialogue NLP system for your workout and meal tracking application. The system uses state-of-the-art transformer models to provide a natural, conversational interface for logging workouts and meals.

## 🏗️ Architecture

### Core Components

1. **Intent Classification** - Determines user intent (workout logging, meal logging, etc.)
2. **Token Classification** - Extracts entities (exercises, foods, numbers, etc.)
3. **Dialogue State Management** - Tracks conversation state and slot filling progress
4. **Slot Validation** - Validates and normalizes extracted slot values
5. **Response Generation** - Generates appropriate system responses

### Model Recommendations

#### Intent Classification Model
- **Primary**: `facebook/bart-large-mnli` (excellent zero-shot classification)
- **Alternative**: `google/gemma-2b-it` (as requested, but may be overkill)
- **Fallback**: `distilbert-base-uncased` (faster, smaller)

#### Token Classification Model
- **Primary**: `FacebookAI/roberta-large` (as requested, state-of-the-art NER)
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

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install the required packages
pip install -r requirements_multi_turn_nlp.txt

# For GPU support (recommended)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 2. Use the Simple Implementation (Immediate)

The `logger/simple_multi_turn_nlp.py` provides a working implementation using rule-based methods:

```python
from logger.simple_multi_turn_nlp import SimpleMultiTurnNLPProcessor

# Initialize the processor
nlp_processor = SimpleMultiTurnNLPProcessor()

# Process a dialogue turn
result = nlp_processor.process_dialogue_turn(
    user_id="user123",
    text="I want to log a chest workout"
)

print(result['response'])
# Output: "Great! I can help you log a workout. What type of workout did you do?"
```

### 3. Train Your Own Models (Recommended)

```bash
# Train intent classification model
python train_multi_turn_nlp.py --task intent --epochs 3

# Train token classification model
python train_multi_turn_nlp.py --task token --epochs 4
```

### 4. Use the Full Implementation

Once you have trained models, use the full implementation:

```python
from logger.multi_turn_nlp_processor import MultiTurnNLPProcessor

# Initialize with trained models
nlp_processor = MultiTurnNLPProcessor(use_gpu=True)

# Process dialogue turns
result = nlp_processor.process_dialogue_turn(
    user_id="user123",
    text="I want to log a chest workout"
)
```

## 🔄 Dialogue Flow Examples

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

## 📊 Training Data Requirements

### Intent Classification Data (5,000-10,000 examples)

**Workout Logging Examples:**
- "I just finished a chest workout"
- "I did some exercises today"
- "I lifted weights this morning"
- "I went to the gym and did bench press"
- "I completed my leg day routine"

**Meal Logging Examples:**
- "I ate chicken and rice for lunch"
- "I had a protein shake"
- "I consumed 500 calories for breakfast"
- "I had a salad with 200 calories"

**Load Saved Examples:**
- "Load my saved chest workout"
- "Show me my saved meals"
- "I want to use my previous workout template"

**Edit Saved Examples:**
- "I want to edit my saved workout"
- "Change my saved meal"
- "Modify my previous workout"

### Token Classification Data (10,000-20,000 examples)

**Exercise Entities:**
- bench press, squat, deadlift, pullup, pushup
- bicep curl, shoulder press, leg press, lat pulldown
- row, lunge, calf raise, plank, dip

**Food Entities:**
- chicken, rice, beef, fish, salad
- protein shake, oatmeal, pasta, sandwich
- smoothie, eggs, toast, yogurt, berries

**Number and Unit Variations:**
- 10 reps, 8-12 reps, 5 reps, 15 reps
- 3 sets, 4 sets, 5 sets, 2 sets
- 135 lbs, 225 lbs, 100 kg, 185 pounds
- 500 calories, 800 cal, 1200 calories
- 35g protein, 50 grams protein, 25g

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

## 🎯 Integration with Django

### 1. Add to Your Django Views

```python
# views.py
from logger.simple_multi_turn_nlp import SimpleMultiTurnNLPProcessor
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

nlp_processor = SimpleMultiTurnNLPProcessor()

@csrf_exempt
def process_nlp_dialogue(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_id = data.get('user_id')
        text = data.get('text')
        
        result = nlp_processor.process_dialogue_turn(user_id, text)
        
        return JsonResponse({
            'response': result['response'],
            'is_complete': result['is_complete'],
            'extracted_slots': result['extracted_slots']
        })
    
    return JsonResponse({'error': 'Invalid request method'})
```

### 2. Add URL Pattern

```python
# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('api/nlp/dialogue/', views.process_nlp_dialogue, name='nlp_dialogue'),
]
```

### 3. Frontend Integration

```javascript
// JavaScript for frontend integration
async function sendNLPMessage(userId, text) {
    const response = await fetch('/api/nlp/dialogue/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            user_id: userId,
            text: text
        })
    });
    
    const result = await response.json();
    return result;
}

// Example usage
sendNLPMessage('user123', 'I want to log a workout')
    .then(result => {
        console.log('System response:', result.response);
        if (result.is_complete) {
            console.log('Dialogue complete!');
            console.log('Extracted slots:', result.extracted_slots);
        }
    });
```

## 🔧 Configuration

### Model Settings

```python
# Recommended configuration
config = {
    "intent_model": "facebook/bart-large-mnli",
    "token_model": "FacebookAI/roberta-large",
    "max_length": 512,
    "batch_size": 8,
    "learning_rate": 2e-5,
    "num_epochs": 3,
    "warmup_steps": 100,
    "weight_decay": 0.01
}
```

### Performance Metrics

**Target Performance:**
- Intent Classification Accuracy: >95%
- Token Classification F1-Score: >90%
- Slot Filling Accuracy: >85%
- Dialogue Completion Rate: >90%

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

## 🚀 Next Steps

1. **Start with Simple Implementation**: Use `SimpleMultiTurnNLPProcessor` immediately
2. **Generate Training Data**: Create thousands of examples using the patterns in `MULTI_TURN_NLP_GUIDE.md`
3. **Train Models**: Use the training script to create custom models
4. **Integrate**: Connect to your Django application
5. **Test**: Evaluate performance on real user interactions
6. **Iterate**: Improve based on user feedback and usage patterns

## 📁 File Structure

```
Workout Tracker/
├── logger/
│   ├── simple_multi_turn_nlp.py      # Immediate working implementation
│   ├── multi_turn_nlp_processor.py   # Full ML-based implementation
│   └── nlp_training_data.py          # Training data examples
├── train_multi_turn_nlp.py           # Training script
├── requirements_multi_turn_nlp.txt    # Dependencies
├── MULTI_TURN_NLP_GUIDE.md           # Comprehensive guide
└── MULTI_TURN_NLP_README.md          # This file
```

## 🆘 Troubleshooting

### Common Issues

1. **Model Loading Errors**: Ensure you have enough disk space (~3.6GB for models)
2. **Memory Issues**: Use smaller batch sizes or enable gradient accumulation
3. **Slow Performance**: Enable GPU acceleration if available
4. **Poor Accuracy**: Increase training data size and diversity

### Performance Optimization

1. **GPU Acceleration**: Install CUDA-compatible PyTorch
2. **Model Quantization**: Use smaller models for faster inference
3. **Caching**: Cache model outputs for repeated inputs
4. **Batch Processing**: Process multiple requests together

## 📞 Support

For questions or issues:
1. Check the `MULTI_TURN_NLP_GUIDE.md` for detailed implementation
2. Review the training data examples in `logger/nlp_training_data.py`
3. Test with the simple implementation first
4. Generate comprehensive training data before training models

This system will provide a natural, conversational interface for your workout and meal tracking application! 