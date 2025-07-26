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
import logging

logger = logging.getLogger(__name__)

class NLPEngine:
    """
    Enhanced NLP Engine for workout and meal logging with structured workflow
    """
    
    def __init__(self):
        
        # Workout patterns for parsing, kind of like templates to help identify exercises
        self.workout_patterns = {
            # "3 sets of 10 reps bench press"
            'sets_reps_exercise': r'(\d+)\s*(?:x|sets?)\s*(?:of\s+)?(\d+)\s*(?:reps?|times?)\s*(?:of\s+)?([^,\n.]+)',
            # "10 reps bench press"
            'reps_exercise': r'(\d+)\s*(?:reps?|times?)\s*(?:of\s+)?([^,\n.]+)',
            # "bench press 3x10"
            'exercise_sets_reps': r'([^,\n.]+?)\s*(\d+)\s*x\s*(\d+)',
            # "bench press at 135 lbs"
            'exercise_weight': r'([^,\n.]+?)\s*(?:at|with|@)\s*(\d+)\s*(?:lbs?|kg|pounds?)',
            # "30 minutes running"
            'duration_exercise': r'(\d+)\s*(?:minutes?|mins?|hours?|hrs?)\s*(?:of\s+)?([^,\n.]+)',
            # Simple exercise mention
            'simple_exercise': r'(?:did|performed|completed)\s+([^,\n.]+?)(?:\s*,|\s*and|\s*$)',
        }
        
        # Workout keywords for classification
        self.workout_keywords = [
            'workout', 'exercise', 'training', 'gym', 'lift', 'run', 'pushup', 
            'pullup', 'squat', 'bench', 'deadlift', 'curl', 'press', 'row', 'extension','sets', 'reps', 'weight',
              'duration', 'cardio', 'push', 'pull', 'legs', 'upper body', 'lower body', 'core'
        ]
        
        # Common exercise name mappings
        self.exercise_mappings = {
            'bench': 'bench press',
            'bp': 'bench press',
            'squat': 'squat',
            'dl': 'deadlift',
            'deadlift': 'deadlift',
            'pullup': 'pullup',
            'pullups': 'pullup',
            'pushup': 'pushup',
            'pushups': 'pushup',
            'curl': 'bicep curl',
            'curls': 'bicep curl',
            'ohp': 'overhead press',
            'overhead press': 'overhead press',
            'row': 'barbell row',
            'rows': 'barbell row',
        }
    
    def process_workout_input(self, text: str, user) -> Dict:
        """
        Main method to process workout input and return structured data
        """
        logger.info(f"Processing workout input: {text}")
        
        # Step 1: Classify if this is a workout
        is_workout = self._classify_as_workout(text)
        if not is_workout:
            return {
                'success': False,
                'message': 'Input does not appear to be workout-related',
                'confidence': 0.1
            }
        
        # Step 2: Parse exercises from text
        exercises = self._parse_exercises(text)
        
        # Step 3: Match exercises to database
        matched_exercises = self._match_exercises_to_db(exercises, user)
        
        # Step 4: Generate workout name
        workout_name = self._generate_workout_name(text, matched_exercises)
        
        # Step 5: Calculate confidence
        confidence = self._calculate_confidence(exercises, matched_exercises)
        
        return {
            'success': True,
            'workout_name': workout_name,
            'exercises': matched_exercises,
            'confidence': confidence,
            'raw_text': text,
            'parsed_exercises': exercises
        }
    
    def create_workout_from_nlp(self, nlp_result: Dict, user) -> Dict:
        """
        Create a workout from NLP parsing results
        """
        if not nlp_result.get('success'):
            return {
                'success': False,
                'message': 'Invalid NLP result'
            }
        
        try:
            with transaction.atomic(): # Wraps everything in a transaction
                # Create the workout
                workout = Workout.objects.create(
                    user=user,
                    name=nlp_result['workout_name']
                )
                
                # Add exercises to workout
                order = 0
                for exercise_data in nlp_result['exercises']:
                    if exercise_data['db_match']:
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
    
    def _classify_as_workout(self, text: str) -> bool:
        """
        Classify if the input text is workout-related
        """
        text_lower = text.lower()
        workout_score = sum(1 for keyword in self.workout_keywords if keyword in text_lower)
        return workout_score >= 1
    
    def _parse_exercises(self, text: str) -> List[Dict]:
        """
        Parse exercises from text using regex patterns
        """
        exercises = []
        text_lower = text.lower()
        
        # Try each pattern
        for pattern_name, pattern in self.workout_patterns.items():
            matches = re.finditer(pattern, text_lower)
            
            for match in matches:
                exercise_data = self._extract_exercise_data(match, pattern_name)
                if exercise_data:
                    exercises.append(exercise_data)
        
        # Remove duplicates based on exercise name
        unique_exercises = []
        seen_names = set()
        for exercise in exercises:
            name = exercise['name'].strip()
            if name not in seen_names:
                unique_exercises.append(exercise)
                seen_names.add(name)
        
        return unique_exercises
    
    def _extract_exercise_data(self, match, pattern_name: str) -> Optional[Dict]:
        """
        Extract exercise data from regex match based on pattern type
        """
        try:
            if pattern_name == 'sets_reps_exercise':
                # "3 sets of 10 reps bench press"
                sets = int(match.group(1))
                reps = int(match.group(2))
                name = match.group(3).strip()
                return {
                    'name': self._normalize_exercise_name(name),
                    'sets': sets,
                    'reps': reps,
                    'weight': None,
                    'duration': None
                }
            
            elif pattern_name == 'reps_exercise':
                # "10 reps bench press"
                reps = int(match.group(1))
                name = match.group(2).strip()
                return {
                    'name': self._normalize_exercise_name(name),
                    'sets': 1,  # Default
                    'reps': reps,
                    'weight': None,
                    'duration': None
                }
            
            elif pattern_name == 'exercise_sets_reps':
                # "bench press 3x10"
                name = match.group(1).strip()
                sets = int(match.group(2))
                reps = int(match.group(3))
                return {
                    'name': self._normalize_exercise_name(name),
                    'sets': sets,
                    'reps': reps,
                    'weight': None,
                    'duration': None
                }
            
            elif pattern_name == 'exercise_weight':
                # "bench press at 135 lbs"
                name = match.group(1).strip()
                weight = int(match.group(2))
                return {
                    'name': self._normalize_exercise_name(name),
                    'sets': 1,  # Default
                    'reps': None,
                    'weight': weight,
                    'duration': None
                }
            
            elif pattern_name == 'duration_exercise':
                # "30 minutes running"
                duration = int(match.group(1))
                name = match.group(2).strip()
                return {
                    'name': self._normalize_exercise_name(name),
                    'sets': 1,
                    'reps': None,
                    'weight': None,
                    'duration': duration
                }
            
            elif pattern_name == 'simple_exercise':
                # "did bench press"
                name = match.group(1).strip()
                return {
                    'name': self._normalize_exercise_name(name),
                    'sets': 1,  # Default
                    'reps': None,
                    'weight': None,
                    'duration': None
                }
        
        except (ValueError, IndexError) as e:
            logger.warning(f"Error extracting exercise data: {e}")
            return None
        
        return None
    
    def _normalize_exercise_name(self, name: str) -> str:
        """
        Normalize exercise name using mappings
        """
        name = name.strip().lower()
        
        # Remove common words
        name = re.sub(r'\b(the|a|an|with|and|or)\b', '', name).strip()
        
        # Check mappings
        if name in self.exercise_mappings:
            return self.exercise_mappings[name]
        
        # Clean up the name
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name.title()
    
    def _match_exercises_to_db(self, exercises: List[Dict], user) -> List[Dict]:
        """
        Match parsed exercises to database exercises
        """
        matched_exercises = []
        
        for exercise_data in exercises:
            exercise_name = exercise_data['name']
            
            # Try exact match first
            db_exercise = Exercise.objects.filter(
                name__iexact=exercise_name
            ).first()
            
            if not db_exercise:
                # Try partial match
                db_exercise = Exercise.objects.filter(
                    name__icontains=exercise_name
                ).first()
            
            if not db_exercise:
                # Try base exercise match
                base_exercise = BaseExercise.objects.filter(
                    name__icontains=exercise_name
                ).first()
                
                if base_exercise:
                    # Get first exercise instance of this base exercise
                    db_exercise = Exercise.objects.filter(
                        base_exercise=base_exercise
                    ).first()
            
            # Add match info to exercise data
            exercise_data['db_match'] = db_exercise
            exercise_data['match_confidence'] = 1.0 if db_exercise else 0.0
            exercise_data['suggested_exercises'] = self._get_exercise_suggestions(exercise_name)
            
            matched_exercises.append(exercise_data)
        
        return matched_exercises
    
    def _get_exercise_suggestions(self, exercise_name: str) -> List[Exercise]:
        """
        Get exercise suggestions for unmatched exercises
        """
        # Get top 3 similar exercises
        suggestions = Exercise.objects.filter(
            name__icontains=exercise_name.split()[0]  # Match first word
        )[:3]
        
        return list(suggestions)
    
    def _generate_workout_name(self, text: str, exercises: List[Dict]) -> str:
        """
        Generate a workout name based on input and exercises
        """
        # Try to extract explicit workout name
        name_patterns = [
            r'(?:workout|training|session):\s*([^,\n.]+)',
            r'(?:did|completed)\s+(?:a\s+)?([^,\n.]+?)\s+(?:workout|training)',
            r'^([^,\n.]+?)\s+(?:workout|training|session)',
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(1).strip().title()
        
        # Generate name based on exercises
        if exercises:
            exercise_names = [ex['name'] for ex in exercises if ex.get('db_match')]
            if len(exercise_names) == 1:
                return f"{exercise_names[0]} Workout"
            elif len(exercise_names) <= 3:
                return f"{', '.join(exercise_names)} Workout"
            else:
                return f"{len(exercise_names)} Exercise Workout"
        
        # Default name
        return f"Workout - {date.today().strftime('%m/%d/%Y')}"
    
    def _calculate_confidence(self, parsed_exercises: List[Dict], matched_exercises: List[Dict]) -> float:
        """
        Calculate confidence score for the parsing
        """
        if not parsed_exercises:
            return 0.0
        
        # Base confidence for parsing exercises
        parsing_confidence = min(0.4, len(parsed_exercises) * 0.1)
        
        # Confidence for database matches
        total_matches = sum(1 for ex in matched_exercises if ex.get('db_match'))
        match_confidence = (total_matches / len(matched_exercises)) * 0.6
        
        return min(0.95, parsing_confidence + match_confidence)
    
    def get_workout_summary(self, nlp_result: Dict) -> str:
        """
        Generate a human-readable summary of the parsed workout
        """
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
    
    def create_missing_exercises(self, nlp_result: Dict, user) -> Dict:
        """
        Create missing exercises that weren't found in the database
        """
        created_exercises = []
        
        for exercise_data in nlp_result.get('exercises', []):
            if not exercise_data.get('db_match'):
                try:
                    # Create a basic exercise
                    exercise = Exercise.objects.create(
                        name=exercise_data['name'],
                        notes=f"Auto-created from NLP input: {nlp_result.get('raw_text', '')[:100]}"
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

# Test function for the NLP Engine
def test_nlp_engine():
    """
    Test function for the NLP Engine
    """
    nlp = NLPEngine()
    
    test_cases = [
        "I did 3 sets of 10 reps bench press and 5 sets of 5 deadlifts",
        "30 minutes of running followed by 20 pushups",
        "Upper body workout: 4x12 bicep curls, 3x10 shoulder press",
        "I completed bench press at 135 lbs and did some squats",
        "Did pullups and pushups today",
    ]
    
    print("Testing NLP Engine:")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case}")
        
        # Mock user object
        class MockUser:
            id = 1
        
        result = nlp.process_workout_input(test_case, MockUser())
        
        if result['success']:
            print(f"✅ Parsed successfully (confidence: {result['confidence']:.1%})")
            print(f"Workout: {result['workout_name']}")
            for exercise in result['exercises']:
                print(f"  • {exercise['name']}")
                if exercise.get('sets') and exercise.get('reps'):
                    print(f"    {exercise['sets']}x{exercise['reps']}")
                if exercise.get('weight'):
                    print(f"    {exercise['weight']} lbs")
        else:
            print(f"❌ Failed: {result['message']}")

if __name__ == "__main__":
    test_nlp_engine()