import re
import json
from typing import Dict, List, Tuple, Optional, Union
from datetime import date
from django.db import transaction
from .models import (
    Exercise, Muscle, Equipment, Workout, DailyLog, 
    WorkoutExerciseItem, BaseExercise
)
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

class ImprovedNLPEngine:
    """
    Improved NLP Engine with better pattern matching and accuracy
    """
    
    def __init__(self):
        # Enhanced workout patterns with better regex
        self.workout_patterns = {
            # "3 sets of 10 reps bench press" or "3x10 bench press"
            'sets_reps_exercise': r'(\d+)\s*(?:sets?\s+of\s+|x|X)\s*(\d+)\s*(?:reps?\s+)?(.+?)(?=\s+and\s+|\s*,|$)',
            
            # "bench press 3x10" or "bench press 3 sets of 10"
            'exercise_sets_reps': r'([a-zA-Z\s]+?)\s+(\d+)\s*(?:x|X|sets?\s+of)\s*(\d+)',
            
            # "10 reps bench press" or "10 bench press"
            'reps_exercise': r'(\d+)\s*(?:reps?\s+)?([a-zA-Z\s]+?)(?=\s+and\s+|\s*,|$)',
            
            # "bench press at 135 lbs" or "135 lb bench press"
            'exercise_weight': r'([a-zA-Z\s]+?)\s+(?:at\s+)?(\d+)\s*(?:lbs?|kg|pounds?)',
            'weight_exercise': r'(\d+)\s*(?:lbs?|kg|pounds?)\s+([a-zA-Z\s]+)',
            
            # "30 minutes running" or "30 min cardio"
            'duration_exercise': r'(\d+)\s*(?:minutes?|mins?|hours?|hrs?)\s+(?:of\s+)?([a-zA-Z\s]+)',
            
            # Simple mentions: "did bench press", "completed squats"
            'simple_mentions': r'(?:did|completed|performed|finished)\s+([a-zA-Z\s]+?)(?=\s+and\s+|\s*,|$)',
            
            # List format: "bench press, squats, deadlifts"
            'exercise_list': r'\b([a-zA-Z\s]{3,}?)(?:,|\s+and\s+|$)',
        }
        
        # Enhanced exercise name mappings
        self.exercise_mappings = {
            # Common abbreviations
            'bench': 'bench press',
            'bp': 'bench press',
            'squats': 'squat',
            'deadlifts': 'deadlift',
            'dl': 'deadlift',
            'pullups': 'pullup',
            'pull ups': 'pullup',
            'pull-ups': 'pullup',
            'pushups': 'pushup',
            'push ups': 'pushup',
            'push-ups': 'pushup',
            'curls': 'bicep curl',
            'bicep curls': 'bicep curl',
            'ohp': 'overhead press',
            'rows': 'barbell row',
            'running': 'treadmill',
            'cardio': 'treadmill',
            
            # Plural to singular
            'presses': 'press',
            'raises': 'raise',
            'extensions': 'extension',
            'flyes': 'fly',
            'flies': 'fly',
        }
        
        # Stop words to remove from exercise names
        self.stop_words = {
            'i', 'did', 'completed', 'performed', 'finished', 'some', 'the', 'a', 'an',
            'with', 'and', 'or', 'at', 'for', 'sets', 'set', 'reps', 'rep', 'of',
            'x', 'times', 'time', 'lbs', 'lb', 'kg', 'pounds', 'minutes', 'mins',
            'hours', 'hrs', 'today', 'yesterday', 'workout', 'exercise', 'training'
        }
        
        # Workout type keywords for better naming
        self.workout_types = {
            'chest': ['chest', 'pecs', 'bench'],
            'back': ['back', 'lats', 'rows', 'pullup', 'pulldown'],
            'legs': ['legs', 'quads', 'squat', 'deadlift', 'lunge'],
            'arms': ['arms', 'bicep', 'tricep', 'curl'],
            'shoulders': ['shoulders', 'delts', 'press', 'raise'],
            'cardio': ['running', 'cardio', 'bike', 'treadmill', 'elliptical'],
            'core': ['abs', 'core', 'plank', 'crunch']
        }
    
    def process_workout_input(self, text: str, user) -> Dict:
        """
        Enhanced workout processing with better accuracy
        """
        logger.info(f"Processing workout input: {text}")
        
        # Step 1: Clean and preprocess text
        cleaned_text = self._preprocess_text(text)
        
        # Step 2: Classify if this is a workout
        is_workout = self._classify_as_workout(cleaned_text)
        if not is_workout:
            return {
                'success': False,
                'message': 'Input does not appear to be workout-related',
                'confidence': 0.1
            }
        
        # Step 3: Enhanced exercise parsing
        exercises = self._enhanced_parse_exercises(cleaned_text)
        
        # Step 4: Match exercises to database with fuzzy matching
        matched_exercises = self._enhanced_match_exercises(exercises, user)
        
        # Step 5: Generate better workout name
        workout_name = self._enhanced_generate_workout_name(cleaned_text, matched_exercises)
        
        # Step 6: Calculate improved confidence
        confidence = self._enhanced_calculate_confidence(exercises, matched_exercises, cleaned_text)
        
        return {
            'success': True,
            'workout_name': workout_name,
            'exercises': matched_exercises,
            'confidence': confidence,
            'raw_text': text,
            'cleaned_text': cleaned_text,
            'parsed_exercises': exercises
        }
    
    def _preprocess_text(self, text: str) -> str:
        """
        Clean and preprocess the input text
        """
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Normalize common patterns
        text = re.sub(r'\bx\b', ' x ', text)  # Ensure space around 'x'
        text = re.sub(r'(\d+)\s*x\s*(\d+)', r'\1 x \2', text)  # "3x10" -> "3 x 10"
        
        # Handle common separators
        text = re.sub(r'\s*[,;]\s*', ' and ', text)  # Replace commas with 'and'
        text = re.sub(r'\s+and\s+and\s+', ' and ', text)  # Remove duplicate 'and'
        
        return text
    
    def _enhanced_parse_exercises(self, text: str) -> List[Dict]:
        """
        Enhanced exercise parsing with better pattern matching
        """
        exercises = []
        
        # Pattern 1: "3 sets of 10 reps bench press" or "3x10 bench press"
        matches = re.finditer(self.workout_patterns['sets_reps_exercise'], text)
        for match in matches:
            sets = int(match.group(1))
            reps = int(match.group(2))
            exercise_name = match.group(3).strip()
            
            if self._is_valid_exercise_name(exercise_name):
                exercises.append({
                    'name': self._clean_exercise_name(exercise_name),
                    'sets': sets,
                    'reps': reps,
                    'weight': None,
                    'duration': None,
                    'source': 'sets_reps_exercise'
                })
        
        # Pattern 2: "bench press 3x10"
        matches = re.finditer(self.workout_patterns['exercise_sets_reps'], text)
        for match in matches:
            exercise_name = match.group(1).strip()
            sets = int(match.group(2))
            reps = int(match.group(3))
            
            if self._is_valid_exercise_name(exercise_name):
                exercises.append({
                    'name': self._clean_exercise_name(exercise_name),
                    'sets': sets,
                    'reps': reps,
                    'weight': None,
                    'duration': None,
                    'source': 'exercise_sets_reps'
                })
        
        # Pattern 3: Weight-based exercises
        for pattern_name in ['exercise_weight', 'weight_exercise']:
            matches = re.finditer(self.workout_patterns[pattern_name], text)
            for match in matches:
                if pattern_name == 'exercise_weight':
                    exercise_name = match.group(1).strip()
                    weight = int(match.group(2))
                else:  # weight_exercise
                    weight = int(match.group(1))
                    exercise_name = match.group(2).strip()
                
                if self._is_valid_exercise_name(exercise_name):
                    exercises.append({
                        'name': self._clean_exercise_name(exercise_name),
                        'sets': 1,  # Default
                        'reps': None,
                        'weight': weight,
                        'duration': None,
                        'source': pattern_name
                    })
        
        # Pattern 4: Duration exercises
        matches = re.finditer(self.workout_patterns['duration_exercise'], text)
        for match in matches:
            duration = int(match.group(1))
            exercise_name = match.group(2).strip()
            
            if self._is_valid_exercise_name(exercise_name):
                exercises.append({
                    'name': self._clean_exercise_name(exercise_name),
                    'sets': 1,
                    'reps': None,
                    'weight': None,
                    'duration': duration,
                    'source': 'duration_exercise'
                })
        
        # Pattern 5: Simple mentions
        if not exercises:  # Only if no other patterns matched
            matches = re.finditer(self.workout_patterns['simple_mentions'], text)
            for match in matches:
                exercise_name = match.group(1).strip()
                if self._is_valid_exercise_name(exercise_name):
                    exercises.append({
                        'name': self._clean_exercise_name(exercise_name),
                        'sets': 1,
                        'reps': None,
                        'weight': None,
                        'duration': None,
                        'source': 'simple_mentions'
                    })
        
        # Remove duplicates and clean up
        exercises = self._remove_duplicate_exercises(exercises)
        
        return exercises
    
    def _is_valid_exercise_name(self, name: str) -> bool:
        """
        Check if a name looks like a valid exercise
        """
        if not name or len(name.strip()) < 3:
            return False
        
        # Remove stop words and check if anything meaningful remains
        words = name.split()
        meaningful_words = [w for w in words if w not in self.stop_words]
        
        return len(meaningful_words) >= 1 and len(' '.join(meaningful_words)) >= 3
    
    def _clean_exercise_name(self, name: str) -> str:
        """
        Clean and normalize exercise name
        """
        # Remove stop words
        words = name.split()
        clean_words = [w for w in words if w not in self.stop_words]
        name = ' '.join(clean_words)
        
        # Apply mappings
        name_lower = name.lower()
        if name_lower in self.exercise_mappings:
            name = self.exercise_mappings[name_lower]
        
        # Handle plurals
        if name.endswith('s') and name[:-1] in self.exercise_mappings:
            name = self.exercise_mappings[name[:-1]]
        
        # Title case
        return name.title()
    
    def _remove_duplicate_exercises(self, exercises: List[Dict]) -> List[Dict]:
        """
        Remove duplicate exercises, keeping the one with most information
        """
        unique_exercises = {}
        
        for exercise in exercises:
            name = exercise['name']
            
            if name not in unique_exercises:
                unique_exercises[name] = exercise
            else:
                # Keep the one with more information
                existing = unique_exercises[name]
                current = exercise
                
                # Score based on available information
                existing_score = sum([
                    1 if existing.get('sets') else 0,
                    1 if existing.get('reps') else 0,
                    1 if existing.get('weight') else 0,
                    1 if existing.get('duration') else 0
                ])
                
                current_score = sum([
                    1 if current.get('sets') else 0,
                    1 if current.get('reps') else 0,
                    1 if current.get('weight') else 0,
                    1 if current.get('duration') else 0
                ])
                
                if current_score > existing_score:
                    unique_exercises[name] = current
        
        return list(unique_exercises.values())
    
    def _enhanced_match_exercises(self, exercises: List[Dict], user) -> List[Dict]:
        """
        Enhanced exercise matching with fuzzy search
        """
        matched_exercises = []
        
        for exercise_data in exercises:
            exercise_name = exercise_data['name']
            
            # Try exact match first
            db_exercise = Exercise.objects.filter(name__iexact=exercise_name).first()
            
            if not db_exercise:
                # Try fuzzy matching with contains
                db_exercise = Exercise.objects.filter(name__icontains=exercise_name).first()
            
            if not db_exercise:
                # Try matching individual words
                words = exercise_name.split()
                for word in words:
                    if len(word) > 3:  # Only try meaningful words
                        db_exercise = Exercise.objects.filter(name__icontains=word).first()
                        if db_exercise:
                            break
            
            if not db_exercise:
                # Try base exercise match
                base_exercise = BaseExercise.objects.filter(name__icontains=exercise_name).first()
                if base_exercise:
                    db_exercise = Exercise.objects.filter(base_exercise=base_exercise).first()
            
            # Calculate match confidence
            match_confidence = 0.0
            if db_exercise:
                # Perfect match
                if db_exercise.name.lower() == exercise_name.lower():
                    match_confidence = 1.0
                # Contains match
                elif exercise_name.lower() in db_exercise.name.lower():
                    match_confidence = 0.8
                # Partial match
                else:
                    match_confidence = 0.6
            
            # Get suggestions
            suggestions = self._get_exercise_suggestions(exercise_name)
            
            # Add to results
            exercise_data['db_match'] = db_exercise
            exercise_data['match_confidence'] = match_confidence
            exercise_data['suggested_exercises'] = suggestions
            
            matched_exercises.append(exercise_data)
        
        return matched_exercises
    
    def _enhanced_generate_workout_name(self, text: str, exercises: List[Dict]) -> str:
        """
        Generate better workout names
        """
        # Try to extract explicit workout name
        name_patterns = [
            r'(?:workout|training|session):\s*([^,\n.]+)',
            r'(?:did|completed)\s+(?:a\s+)?([^,\n.]+?)\s+(?:workout|training)',
            r'^([^,\n.]+?)\s+(?:workout|training|session)',
            r'(?:today|yesterday)(?:\s+i)?\s+(?:did|had)\s+([^,\n.]+?)(?:\s+with|\s+including|$)',
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text.lower())
            if match:
                name = match.group(1).strip()
                if len(name) > 2 and not any(word in name for word in ['sets', 'reps', 'lbs']):
                    return name.title()
        
        # Generate name based on workout type
        workout_type = self._detect_workout_type(text, exercises)
        if workout_type:
            return f"{workout_type.title()} Workout"
        
        # Generate name based on exercises
        if exercises:
            exercise_names = [ex['name'] for ex in exercises if ex.get('db_match')]
            if exercise_names:
                if len(exercise_names) == 1:
                    return f"{exercise_names[0]} Workout"
                elif len(exercise_names) <= 3:
                    return f"{', '.join(exercise_names)} Workout"
                else:
                    return f"{len(exercise_names)} Exercise Workout"
        
        # Default name
        return f"Workout - {date.today().strftime('%m/%d/%Y')}"
    
    def _detect_workout_type(self, text: str, exercises: List[Dict]) -> Optional[str]:
        """
        Detect the type of workout based on keywords and exercises
        """
        text_lower = text.lower()
        
        # Check for explicit workout type mentions
        for workout_type, keywords in self.workout_types.items():
            if any(keyword in text_lower for keyword in keywords):
                return workout_type
        
        # Check based on exercises
        if exercises:
            exercise_names = ' '.join([ex['name'].lower() for ex in exercises])
            for workout_type, keywords in self.workout_types.items():
                if any(keyword in exercise_names for keyword in keywords):
                    return workout_type
        
        return None
    
    def _enhanced_calculate_confidence(self, parsed_exercises: List[Dict], 
                                     matched_exercises: List[Dict], text: str) -> float:
        """
        Enhanced confidence calculation
        """
        if not parsed_exercises:
            return 0.1
        
        confidence = 0.0
        
        # Base confidence for finding exercises
        confidence += min(0.3, len(parsed_exercises) * 0.1)
        
        # Confidence for database matches
        total_matches = sum(1 for ex in matched_exercises if ex.get('db_match'))
        if parsed_exercises:
            match_ratio = total_matches / len(parsed_exercises)
            confidence += match_ratio * 0.4
        
        # Confidence for detailed information
        detailed_exercises = sum(1 for ex in parsed_exercises 
                               if ex.get('sets') or ex.get('reps') or ex.get('weight') or ex.get('duration'))
        if parsed_exercises:
            detail_ratio = detailed_exercises / len(parsed_exercises)
            confidence += detail_ratio * 0.2
        
        # Confidence for workout keywords
        workout_keywords = ['workout', 'exercise', 'training', 'sets', 'reps', 'lbs', 'kg']
        keyword_count = sum(1 for keyword in workout_keywords if keyword in text.lower())
        confidence += min(0.1, keyword_count * 0.02)
        
        return min(0.95, confidence)
    
    def create_workout_from_nlp(self, nlp_result: Dict, user) -> Dict:
        """
        Create a workout from NLP parsing results with proper user handling
        """
        if not nlp_result.get('success'):
            return {
                'success': False,
                'message': 'Invalid NLP result'
            }
        
        try:
            # Ensure user is a proper User instance
            if not isinstance(user, User):
                return {
                    'success': False,
                    'message': 'Invalid user object'
                }
            
            with transaction.atomic():
                # Create the workout
                workout = Workout.objects.create(
                    user=user,
                    name=nlp_result['workout_name']
                )
                
                # Add exercises to workout
                order = 0
                for exercise_data in nlp_result['exercises']:
                    if exercise_data.get('db_match'):
                        exercise = exercise_data['db_match']
                        WorkoutExerciseItem.objects.create(
                            workout=workout,
                            content_type=ContentType.objects.get_for_model(Exercise),
                            object_id=exercise.id,
                            order=order
                        )
                        order += 1
                
                # Add to today's daily log
                daily_log, created = DailyLog.objects.get_or_create(
                    user=user,
                    date=date.today()
                )
                daily_log.workouts.add(workout)
                
                logger.info(f"Created workout: {workout.name} with {order} exercises")
                
                return {
                    'success': True,
                    'workout': workout,
                    'message': f'Successfully created workout "{workout.name}" with {order} exercises'
                }
        
        except Exception as e:
            logger.error(f"Error creating workout: {str(e)}")
            return {
                'success': False,
                'message': f'Error creating workout: {str(e)}'
            }
    
    # Keep all the other methods from the original NLPEngine
    def _classify_as_workout(self, text: str) -> bool:
        """Classify if the input text is workout-related"""
        workout_keywords = [
            'workout', 'exercise', 'training', 'gym', 'lift', 'run', 'pushup', 
            'pullup', 'squat', 'bench', 'deadlift', 'curl', 'press', 'row',
            'sets', 'reps', 'lbs', 'kg', 'pounds', 'minutes', 'cardio'
        ]
        text_lower = text.lower()
        workout_score = sum(1 for keyword in workout_keywords if keyword in text_lower)
        return workout_score >= 1
    
    def _get_exercise_suggestions(self, exercise_name: str) -> List:
        """Get exercise suggestions for unmatched exercises"""
        words = exercise_name.split()
        suggestions = []
        
        for word in words:
            if len(word) > 3:
                matches = Exercise.objects.filter(name__icontains=word)[:3]
                suggestions.extend(matches)
        
        # Remove duplicates and limit to 5
        seen_ids = set()
        unique_suggestions = []
        for suggestion in suggestions:
            if suggestion.id not in seen_ids:
                unique_suggestions.append(suggestion)
                seen_ids.add(suggestion.id)
                if len(unique_suggestions) >= 5:
                    break
        
        return unique_suggestions
    
    def create_missing_exercises(self, nlp_result: Dict, user) -> Dict:
        """Create missing exercises that weren't found in the database"""
        created_exercises = []
        
        for exercise_data in nlp_result.get('exercises', []):
            if not exercise_data.get('db_match'):
                try:
                    # Create a basic exercise
                    exercise = Exercise.objects.create(
                        name=exercise_data['name'],
                        notes=f"Auto-created from NLP input"
                    )
                    
                    # Update the exercise data
                    exercise_data['db_match'] = exercise
                    exercise_data['match_confidence'] = 0.8  # Lower confidence for auto-created
                    
                    created_exercises.append(exercise)
                    
                except Exception as e:
                    logger.error(f"Error creating exercise {exercise_data['name']}: {e}")
        
        return {
            'created_exercises': created_exercises,
            'count': len(created_exercises)
        }
    
    def get_workout_summary(self, nlp_result: Dict) -> str:
        """Generate a human-readable summary of the parsed workout"""
        if not nlp_result.get('success'):
            return "Unable to parse workout"
        
        summary_parts = [f"Workout: {nlp_result['workout_name']}"]
        
        exercises = nlp_result.get('exercises', [])
        for exercise in exercises:
            parts = [exercise['name']]
            
            if exercise.get('sets') and exercise.get('reps'):
                parts.append(f"{exercise['sets']}x{exercise['reps']}")
            elif exercise.get('reps'):
                parts.append(f"{exercise['reps']} reps")
            
            if exercise.get('weight'):
                parts.append(f"{exercise['weight']} lbs")
            
            if exercise.get('duration'):
                parts.append(f"{exercise['duration']} minutes")
            
            if not exercise.get('db_match'):
                parts.append("(not found in database)")
            
            summary_parts.append("  • " + " - ".join(parts))
        
        summary_parts.append(f"Confidence: {nlp_result['confidence']:.1%}")
        
        return "\n".join(summary_parts)