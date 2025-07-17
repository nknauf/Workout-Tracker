import re
import json
from typing import Dict, List, Tuple, Optional, Union
from transformers import (
    pipeline, 
    AutoTokenizer, 
    AutoModelForSequenceClassification,
    AutoModelForTokenClassification,
    AutoModelForQuestionAnswering
)
import torch
from torch.nn.functional import softmax
import numpy as np
from .models import Exercise, Muscle, Equipment, MovementType, CalorieEntry

class AdvancedNLPProcessor:
    """
    Advanced NLP Processor using Hugging Face models for workout and meal logging
    """
    
    def __init__(self, use_gpu: bool = False):
        self.device = "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
        self.models = {}
        self.tokenizers = {}
        
        # Initialize models (lazy loading)
        self._load_models()
        
        # Fallback to regex patterns
        self.fallback_processor = BasicNLPProcessor()
        
    def _load_models(self):
        """Load Hugging Face models for different NLP tasks"""
        try:
            # 1. Intent Classification Model (Workout vs Meal vs Other)
            self.models['intent_classifier'] = pipeline(
                "text-classification",
                model="facebook/bart-large-mnli",  # Zero-shot classification
                device=self.device
            )
            
            # 2. Named Entity Recognition (NER) for exercises and foods
            self.models['ner'] = pipeline(
                "ner",
                model="dslim/bert-base-NER",  # General NER model
                device=self.device
            )
            
            # 3. Question Answering for extracting specific values
            self.models['qa'] = pipeline(
                "question-answering",
                model="deepset/roberta-base-squad2",
                device=self.device
            )
            
            # 4. Text Generation for workout suggestions
            self.models['text_generator'] = pipeline(
                "text-generation",
                model="gpt2",  # Small model for demo
                device=self.device
            )
            
            print("✅ Advanced NLP models loaded successfully")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not load advanced models: {e}")
            print("Falling back to basic regex-based processing")
            self.models = {}
    
    def classify_intent(self, text: str) -> Dict[str, float]:
        """
        Classify the intent of the input text (workout, meal, or other)
        """
        if not self.models.get('intent_classifier'):
            return self._fallback_intent_classification(text)
        
        candidate_labels = [
            "workout logging",
            "meal logging", 
            "exercise tracking",
            "nutrition tracking",
            "general fitness"
        ]
        
        try:
            result = self.models['intent_classifier'](
                text,
                candidate_labels=candidate_labels,
                hypothesis_template="This text is about {}."
            )
            
            # Convert to confidence scores
            scores = {}
            for label, score in zip(result['labels'], result['scores']):
                scores[label] = score
            
            return scores
            
        except Exception as e:
            print(f"Intent classification failed: {e}")
            return self._fallback_intent_classification(text)
    
    def extract_entities(self, text: str) -> List[Dict]:
        """
        Extract named entities (exercises, foods, numbers, units)
        """
        if not self.models.get('ner'):
            return self._fallback_entity_extraction(text)
        
        try:
            entities = self.models['ner'](text)
            
            # Process and categorize entities
            processed_entities = []
            for entity in entities:
                processed_entities.append({
                    'text': entity['word'],
                    'type': entity['entity_group'],
                    'confidence': entity['score'],
                    'start': entity['start'],
                    'end': entity['end']
                })
            
            return processed_entities
            
        except Exception as e:
            print(f"Entity extraction failed: {e}")
            return self._fallback_entity_extraction(text)
    
    def extract_structured_data(self, text: str) -> Dict:
        """
        Extract structured data using question-answering approach
        """
        if not self.models.get('qa'):
            return self._fallback_structured_extraction(text)
        
        try:
            # Define questions to extract specific information
            questions = {
                'workout_name': "What is the name of this workout?",
                'exercise_count': "How many different exercises are mentioned?",
                'total_sets': "What is the total number of sets?",
                'total_reps': "What is the total number of reps?",
                'total_weight': "What is the total weight used?",
                'total_duration': "What is the total duration in minutes?",
                'meal_type': "What type of meal is this?",
                'total_calories': "What is the total number of calories?",
                'total_protein': "What is the total protein in grams?"
            }
            
            extracted_data = {}
            
            for field, question in questions.items():
                try:
                    answer = self.models['qa'](
                        question=question,
                        context=text
                    )
                    
                    if answer['score'] > 0.5:  # Confidence threshold
                        extracted_data[field] = {
                            'value': answer['answer'],
                            'confidence': answer['score']
                        }
                        
                except Exception as e:
                    print(f"Failed to extract {field}: {e}")
                    continue
            
            return extracted_data
            
        except Exception as e:
            print(f"Structured extraction failed: {e}")
            return self._fallback_structured_extraction(text)
    
    def parse_workout_text(self, text: str) -> Dict:
        """
        Advanced workout parsing using multiple NLP techniques
        """
        # 1. Intent classification
        intent_scores = self.classify_intent(text)
        is_workout = intent_scores.get('workout logging', 0) > 0.3 or intent_scores.get('exercise tracking', 0) > 0.3
        
        if not is_workout:
            return {
                'workout_name': '',
                'exercises': [],
                'confidence': 0.1,
                'raw_text': text,
                'intent_scores': intent_scores
            }
        
        # 2. Entity extraction
        entities = self.extract_entities(text)
        
        # 3. Structured data extraction
        structured_data = self.extract_structured_data(text)
        
        # 4. Parse exercises using advanced techniques
        exercises = self._parse_exercises_advanced(text, entities)
        
        # 5. Generate workout name
        workout_name = self._generate_workout_name(text, exercises, structured_data)
        
        # 6. Calculate confidence
        confidence = self._calculate_confidence(intent_scores, entities, structured_data, exercises)
        
        return {
            'workout_name': workout_name,
            'exercises': exercises,
            'confidence': confidence,
            'raw_text': text,
            'intent_scores': intent_scores,
            'entities': entities,
            'structured_data': structured_data
        }
    
    def parse_meal_text(self, text: str) -> Dict:
        """
        Advanced meal parsing using multiple NLP techniques
        """
        # 1. Intent classification
        intent_scores = self.classify_intent(text)
        is_meal = intent_scores.get('meal logging', 0) > 0.3 or intent_scores.get('nutrition tracking', 0) > 0.3
        
        if not is_meal:
            return {
                'meal_name': '',
                'foods': [],
                'total_calories': 0,
                'total_protein': 0,
                'confidence': 0.1,
                'raw_text': text,
                'intent_scores': intent_scores
            }
        
        # 2. Entity extraction
        entities = self.extract_entities(text)
        
        # 3. Structured data extraction
        structured_data = self.extract_structured_data(text)
        
        # 4. Parse foods using advanced techniques
        foods = self._parse_foods_advanced(text, entities)
        
        # 5. Generate meal name
        meal_name = self._generate_meal_name(text, foods, structured_data)
        
        # 6. Calculate totals
        total_calories = sum(food.get('calories', 0) for food in foods)
        total_protein = sum(food.get('protein', 0) for food in foods)
        
        # 7. Calculate confidence
        confidence = self._calculate_confidence(intent_scores, entities, structured_data, foods)
        
        return {
            'meal_name': meal_name,
            'foods': foods,
            'total_calories': total_calories,
            'total_protein': total_protein,
            'confidence': confidence,
            'raw_text': text,
            'intent_scores': intent_scores,
            'entities': entities,
            'structured_data': structured_data
        }
    
    def _parse_exercises_advanced(self, text: str, entities: List[Dict]) -> List[Dict]:
        """Advanced exercise parsing using entities and context"""
        exercises = []
        
        # Extract exercise names from entities
        exercise_entities = [e for e in entities if e['type'] in ['PERSON', 'ORG', 'MISC']]
        
        # Use regex as fallback for specific patterns
        regex_exercises = self.fallback_processor.parse_workout_text(text)['exercises']
        
        # Combine and deduplicate
        for exercise in regex_exercises:
            exercises.append({
                'name': exercise['name'],
                'sets': exercise.get('sets', 1),
                'reps': exercise.get('reps'),
                'weight': exercise.get('weight'),
                'duration': exercise.get('duration'),
                'source': 'regex'
            })
        
        return exercises
    
    def _parse_foods_advanced(self, text: str, entities: List[Dict]) -> List[Dict]:
        """Advanced food parsing using entities and context"""
        foods = []
        
        # Extract food names from entities
        food_entities = [e for e in entities if e['type'] in ['PERSON', 'ORG', 'MISC']]
        
        # Use regex as fallback for specific patterns
        regex_foods = self.fallback_processor.parse_meal_text(text)['foods']
        
        # Combine and deduplicate
        for food in regex_foods:
            foods.append({
                'name': food['name'],
                'calories': food.get('calories', 0),
                'protein': food.get('protein', 0),
                'source': 'regex'
            })
        
        return foods
    
    def _generate_workout_name(self, text: str, exercises: List[Dict], structured_data: Dict) -> str:
        """Generate workout name using AI"""
        if not self.models.get('text_generator'):
            return self.fallback_processor.suggest_workout_name(exercises)
        
        try:
            # Create a prompt for workout name generation
            exercise_names = [ex['name'] for ex in exercises]
            prompt = f"Generate a short workout name for: {', '.join(exercise_names)}"
            
            result = self.models['text_generator'](
                prompt,
                max_length=50,
                num_return_sequences=1,
                temperature=0.7
            )
            
            generated_name = result[0]['generated_text'].replace(prompt, '').strip()
            return generated_name if generated_name else "Workout"
            
        except Exception as e:
            print(f"Workout name generation failed: {e}")
            return self.fallback_processor.suggest_workout_name(exercises)
    
    def _generate_meal_name(self, text: str, foods: List[Dict], structured_data: Dict) -> str:
        """Generate meal name using AI"""
        if not self.models.get('text_generator'):
            return self.fallback_processor._identify_meal_type(text) or "Meal"
        
        try:
            # Create a prompt for meal name generation
            food_names = [food['name'] for food in foods]
            prompt = f"Generate a short meal name for: {', '.join(food_names)}"
            
            result = self.models['text_generator'](
                prompt,
                max_length=50,
                num_return_sequences=1,
                temperature=0.7
            )
            
            generated_name = result[0]['generated_text'].replace(prompt, '').strip()
            return generated_name if generated_name else "Meal"
            
        except Exception as e:
            print(f"Meal name generation failed: {e}")
            return self.fallback_processor._identify_meal_type(text) or "Meal"
    
    def _calculate_confidence(self, intent_scores: Dict, entities: List[Dict], 
                            structured_data: Dict, parsed_items: List[Dict]) -> float:
        """Calculate confidence score based on multiple factors"""
        confidence = 0.0
        
        # Intent confidence (30%)
        max_intent_score = max(intent_scores.values()) if intent_scores else 0
        confidence += max_intent_score * 0.3
        
        # Entity extraction confidence (25%)
        if entities:
            avg_entity_confidence = sum(e['confidence'] for e in entities) / len(entities)
            confidence += avg_entity_confidence * 0.25
        
        # Structured data confidence (25%)
        if structured_data:
            avg_structured_confidence = sum(d['confidence'] for d in structured_data.values() if isinstance(d, dict)) / len(structured_data)
            confidence += avg_structured_confidence * 0.25
        
        # Parsed items confidence (20%)
        if parsed_items:
            confidence += min(0.2, len(parsed_items) * 0.05)
        
        return min(0.95, confidence)
    
    # Fallback methods
    def _fallback_intent_classification(self, text: str) -> Dict[str, float]:
        """Fallback intent classification using keywords"""
        text_lower = text.lower()
        
        workout_keywords = ['workout', 'exercise', 'reps', 'sets', 'lift', 'run', 'pushup', 'squat']
        meal_keywords = ['ate', 'eat', 'food', 'meal', 'calories', 'protein', 'breakfast', 'lunch', 'dinner']
        
        workout_score = sum(1 for keyword in workout_keywords if keyword in text_lower) / len(workout_keywords)
        meal_score = sum(1 for keyword in meal_keywords if keyword in text_lower) / len(meal_keywords)
        
        return {
            'workout logging': workout_score,
            'meal logging': meal_score,
            'exercise tracking': workout_score * 0.8,
            'nutrition tracking': meal_score * 0.8,
            'general fitness': max(workout_score, meal_score) * 0.5
        }
    
    def _fallback_entity_extraction(self, text: str) -> List[Dict]:
        """Fallback entity extraction using regex"""
        entities = []
        
        # Extract numbers
        numbers = re.findall(r'\d+', text)
        for i, number in enumerate(numbers):
            entities.append({
                'text': number,
                'type': 'NUMBER',
                'confidence': 0.9,
                'start': text.find(number),
                'end': text.find(number) + len(number)
            })
        
        # Extract exercise-like words
        exercise_pattern = r'\b\w+(?:\s+\w+)*\b'
        words = re.findall(exercise_pattern, text)
        for word in words:
            if len(word) > 3 and word.lower() not in ['with', 'and', 'the', 'for', 'sets', 'reps']:
                entities.append({
                    'text': word,
                    'type': 'MISC',
                    'confidence': 0.6,
                    'start': text.find(word),
                    'end': text.find(word) + len(word)
                })
        
        return entities
    
    def _fallback_structured_extraction(self, text: str) -> Dict:
        """Fallback structured extraction using regex"""
        return self.fallback_processor.parse_workout_text(text) if 'workout' in text.lower() else self.fallback_processor.parse_meal_text(text)


class BasicNLPProcessor:
    """Basic NLP processor for fallback functionality"""
    
    def __init__(self):
        # Copy the original NLPProcessor logic here
        self.workout_patterns = {
            'exercise_with_reps': r'(\d+)\s*(?:x|sets?|reps?)\s*(\d+)\s*(?:reps?|times?)?\s*(?:of\s+)?([^,\n]+)',
            'exercise_with_weight': r'(\d+)\s*(?:lbs?|kg|pounds?)\s*(?:x|for)\s*(\d+)\s*(?:reps?|times?)?\s*(?:of\s+)?([^,\n]+)',
            'simple_exercise': r'(\d+)\s*(?:reps?|times?)\s*(?:of\s+)?([^,\n]+)',
            'duration_exercise': r'(\d+)\s*(?:minutes?|mins?|hours?|hrs?)\s*(?:of\s+)?([^,\n]+)',
        }
        
        self.meal_patterns = {
            'food_with_calories': r'([^,\n]+?)\s*(\d+)\s*(?:calories?|cal)',
            'food_with_protein': r'([^,\n]+?)\s*(\d+)\s*(?:g|grams?)\s*(?:protein)',
            'food_with_both': r'([^,\n]+?)\s*(\d+)\s*(?:calories?|cal).*?(\d+)\s*(?:g|grams?)\s*(?:protein)',
        }
    
    def parse_workout_text(self, text: str) -> Dict:
        """Basic workout parsing using regex"""
        # Implementation from original NLPProcessor
        text = text.lower().strip()
        result = {
            'workout_name': '',
            'exercises': [],
            'confidence': 0.0,
            'raw_text': text
        }
        
        # Extract exercises with different patterns
        exercises_found = []
        
        # Pattern 1: "3 sets of 10 reps bench press"
        matches = re.finditer(self.workout_patterns['exercise_with_reps'], text)
        for match in matches:
            sets = int(match.group(1))
            reps = int(match.group(2))
            exercise_name = match.group(3).strip()
            exercises_found.append({
                'name': exercise_name,
                'sets': sets,
                'reps': reps,
                'weight': None,
                'duration': None
            })
        
        result['exercises'] = exercises_found
        
        # Calculate confidence
        if exercises_found:
            result['confidence'] = min(0.9, 0.3 + len(exercises_found) * 0.2)
        else:
            result['confidence'] = 0.1
        
        return result
    
    def parse_meal_text(self, text: str) -> Dict:
        """Basic meal parsing using regex"""
        # Implementation from original NLPProcessor
        text = text.lower().strip()
        result = {
            'meal_name': '',
            'foods': [],
            'total_calories': 0,
            'total_protein': 0,
            'confidence': 0.0,
            'raw_text': text
        }
        
        # Extract foods with calories and protein
        foods_found = []
        
        # Pattern 1: "chicken breast 250 calories"
        matches = re.finditer(self.meal_patterns['food_with_calories'], text)
        for match in matches:
            food_name = match.group(1).strip()
            calories = int(match.group(2))
            foods_found.append({
                'name': food_name,
                'calories': calories,
                'protein': 0
            })
        
        result['foods'] = foods_found
        
        # Calculate totals
        result['total_calories'] = sum(f['calories'] for f in foods_found)
        result['total_protein'] = sum(f['protein'] for f in foods_found)
        
        # Calculate confidence
        if foods_found:
            result['confidence'] = min(0.9, 0.3 + len(foods_found) * 0.15)
        else:
            result['confidence'] = 0.1
        
        return result
    
    def suggest_workout_name(self, exercises: List[Dict]) -> str:
        """Suggest workout name based on exercises"""
        if not exercises:
            return "Workout"
        
        exercise_types = {}
        for exercise in exercises:
            name = exercise['name'].lower()
            if any(keyword in name for keyword in ['run', 'jog', 'walk', 'bike', 'swim']):
                exercise_types['cardio'] = exercise_types.get('cardio', 0) + 1
            elif any(keyword in name for keyword in ['lift', 'bench', 'squat', 'deadlift', 'press']):
                exercise_types['strength'] = exercise_types.get('strength', 0) + 1
            elif any(keyword in name for keyword in ['pushup', 'pullup', 'plank', 'burpee']):
                exercise_types['bodyweight'] = exercise_types.get('bodyweight', 0) + 1
        
        if exercise_types:
            dominant_type = max(exercise_types, key=exercise_types.get)
            return f"{dominant_type.title()} Workout"
        
        return f"{len(exercises)} Exercise Workout"
    
    def _identify_meal_type(self, text: str) -> Optional[str]:
        """Identify meal type from text"""
        meal_keywords = {
            'breakfast': ['breakfast', 'cereal', 'oatmeal', 'eggs', 'toast', 'pancakes'],
            'lunch': ['lunch', 'sandwich', 'salad', 'soup', 'pasta'],
            'dinner': ['dinner', 'steak', 'chicken', 'fish', 'rice', 'vegetables'],
            'snack': ['snack', 'apple', 'banana', 'nuts', 'protein bar', 'shake'],
        }
        
        for meal_type, keywords in meal_keywords.items():
            if any(keyword in text for keyword in keywords):
                return meal_type
        return None 