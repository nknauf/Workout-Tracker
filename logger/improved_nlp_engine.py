import re
import json
from typing import Dict, List, Optional, Tuple
from datetime import date
from django.db import transaction
from .models import (
    Exercise, Muscle, Equipment, Workout, DailyLog, 
    WorkoutExerciseItem, BaseExercise
)
from django.contrib.contenttypes.models import ContentType
import logging

logger = logging.getLogger(__name__)

class MultiTurnNLPEngine:
    """
    Multi-turn conversational NLP engine for workout creation
    """
    
    def __init__(self):
        # Conversation states
        self.STATES = {
            'INITIAL': 'initial',
            'WORKOUT_TYPE': 'workout_type',
            'COLLECTING_EXERCISES': 'collecting_exercises',
            'CONFIRM_WORKOUT': 'confirm_workout',
            'COMPLETED': 'completed'
        }
        
        # Exercise detail patterns
        self.exercise_patterns = {
            # Main exercise pattern: "Exercise name: details"
            'detailed_exercise': r'^([^:]+):\s*(.+)$',
            
            # Working sets patterns - more flexible to handle typos and variations
            'working_sets': r'(\d+)\s*(?:working\s+)?(?:workings\s+)?sets?',
            
            # Max weight patterns - improved to handle different formats
            # "3 plates max", "5 plates max"
            'max_weight_plates': r'(\d+)\s*(?:plates?|plate)\s*(?:max|maximum)?',
            
            # "45 lb max", "95 lb max", "260 max"
            'max_weight_lbs': r'(\d+)\s*(?:lb|lbs|pounds?)\s*(?:max|maximum)?',
            
            # Simple number max: "260 max", "75 max" (when no unit specified)
            'max_weight_simple': r'(\d+)\s*(?:max|maximum)(?!\s*(?:reps?|rep))',
            
            # Max reps pattern: "4 reps max", "6 max reps"
            'max_reps': r'(\d+)\s*(?:reps?\s*)?(?:max|maximum)(?:\s*reps?)?',
            
            # Exercise variations - case insensitive
            'single_arm': r'\bsingle\s+arm\b',
            'alternating': r'\balternating\b',
            'seated': r'\bseated\b',
            'standing': r'\bstanding\b',
            'lying': r'\blying\b',
            'incline': r'\bincline\b',
            'decline': r'\bdecline\b',
            
            # Grip and bar variations
            'flat_bar': r'\bflat\s+bar\b',
            'ez_bar': r'\bez\s+bar\b',
            'neutral_grip': r'\bneutral\s+grip\b',
            'wide_grip': r'\bwide\s+grip\b',
            'close_grip': r'\bclose\s+grip\b',
            'overhand': r'\boverhand\b',
            'underhand': r'\bunderhand\b',
            
            # Equipment specifications
            'plate_loaded': r'\bplate\s*loaded\b',
            'pin_loaded': r'\bpin\s*loaded\b',
            'machine': r'\bmachine\b',
            'cable': r'\bcable\b',
            'dumbbell': r'\bdumbbell\b',
            'barbell': r'\bbarbell\b',
            
            # Additional modifiers
            'unilateral': r'\bunilateral\b',
            'bilateral': r'\bbilateral\b',
            'partial_rep': r'\bpartial\s+rep\b',
            'pause_rep': r'\bpause\s+rep\b',
            'tempo': r'\btempo\b',
            }
        
        # Workout type keywords
        self.workout_types = {
            'chest': ['chest', 'pecs'],
            'back': ['back', 'back day', 'lats', 'latissimus', 'traps'],
            'shoulders': ['shoulders', 'shoulder', 'delts', 'delt'],
            'front_delts': ['front delts', 'anterior deltoids', 'front delt'],
            'side_delts': ['side delts', 'lateral deltoids', 'side delt'],
            'rear_delts': ['rear delts', 'posterior deltoids', 'rear delt'],
            'arms': ['arms', 'arm', 'arm day', 'arm workout'],
            'biceps': ['biceps', 'bicep', 'bi', 'bis'],
            'triceps': ['triceps', 'tricep', 'tri', 'tris'],
            'forearms': ['forearms', 'forearm', 'wrist'],
            'legs': ['legs', 'leg', 'leg day'],
            'quads': ['quads', 'quadriceps', 'quad day'],
            'hamstrings': ['hamstrings', 'hamstring', 'hams'],
            'glutes': ['glutes', 'glute', 'butt'],
            'calves': ['calves', 'calf', 'calf raise'],
            'core': ['core', 'abdominals', 'abs', 'ab workout', 'ab', 'abdominal', 'obliques'],

            'push': ['push', 'push day', 'push workout'],
            'pull': ['pull', 'pull day', 'pull workout'],
            'upper': ['upper', 'upper body', 'upper day', 'upper body workout', 'upper workout'],
            'lower': ['lower', 'lower body', 'lower day', 'lower body workout', 'lower workout'],
            'full': ['full', 'full body', 'full day', 'full body workout', 'full workout'],

            'chest_triceps': ['chest and triceps', 'chest & triceps', 'chest/triceps', 'chest tri', 'chest tris', 'chest and tris', 'chest and tricep', 'chest tri day'],
            'back_biceps': ['back and biceps', 'back & biceps', 'back/biceps', 'back bi', 'back bis', 'back and bis', 'back and bicep', 'back bi day'],
            'chest_shoulder_triceps': ['chest shoulder triceps', 'chest & shoulder & triceps', 'chest/shoulder/triceps', 'chest shoulder tri', 'chest shoulder tris', 'chest shoulder and triceps', 'chest shoulder and tris'],
            'chest_back': ['chest and back', 'chest & back', 'chest/back', 'chest bi tri', 'chest bis tris', 'chest and bis tris', 'chest and back day'],
            'back_shoulders': ['back and shoulders', 'back & shoulders', 'back/shoulders', 'back shoulder', 'back and shoulder', 'back and shoulders day', 'back shoulders', 'back and shoulder day'],
            'shoulder_arms': ['shoulder and arms', 'shoulder & arms', 'shoulder/arms', 'shoulder arm', 'shoulder and arm', 'shoulder arms day', 'sarms', 'sharms', 'shoulder and arms day', 'sarm day', 'sharm day'],  
        }

        self.workout_type_priority = [
            # Compound types first (most specific)
            'chest_triceps', 'back_biceps', 'chest_shoulder_triceps', 
            'chest_back', 'back_shoulders', 'shoulder_arms',
            
            # Movement patterns
            'push', 'pull', 'upper', 'lower', 'full',
            
            # Individual muscles last
            'chest', 'back', 'shoulders', 'arms', 'legs', 'biceps', 'triceps',
            'front_delts', 'side_delts', 'rear_delts', 'forearms', 'quads', 
            'hamstrings', 'glutes', 'calves', 'core'
        ]
    
    def start_conversation(self, initial_input: str, user) -> Dict:
        """
        Start a new workout conversation
        """
        session_data = {
            'state': self.STATES['INITIAL'],
            'user_id': user.id,
            'workout_type': None,
            'exercises': [],
            'raw_inputs': [initial_input],
            'conversation_history': []
        }
        
        # Process the initial input
        return self.process_input(initial_input, session_data)
    
    def continue_conversation(self, user_input: str, session_data: Dict) -> Dict:
        """
        Continue an existing conversation
        """
        session_data['raw_inputs'].append(user_input)
        return self.process_input(user_input, session_data)
    
    def process_input(self, user_input: str, session_data: Dict) -> Dict:
        """
        Process user input based on current conversation state
        """
        current_state = session_data['state']
        
        if current_state == self.STATES['INITIAL']:
            return self._handle_initial_input(user_input, session_data)
        elif current_state == self.STATES['WORKOUT_TYPE']:
            return self._handle_workout_type(user_input, session_data)
        elif current_state == self.STATES['COLLECTING_EXERCISES']:
            return self._handle_exercise_input(user_input, session_data)
        elif current_state == self.STATES['CONFIRM_WORKOUT']:
            return self._handle_confirmation(user_input, session_data)
        else:
            return self._create_response("I'm not sure what to do next. Let's start over.", session_data)
    
    def _handle_initial_input(self, user_input: str, session_data: Dict) -> Dict:
        """
        Handle the initial input to determine workout type
        """
        workout_type = self._extract_workout_type(user_input)
        
        if workout_type:
            session_data['workout_type'] = workout_type
            session_data['state'] = self.STATES['COLLECTING_EXERCISES']
            
            response = f"Great! I'll help you create a {workout_type} workout. Please tell me what exercises you did. You can list them one by one with details like:\n\n"
            response += "• Exercise name: working sets, max weight/reps\n"
            response += "• Example: 'Bench press: 3 working sets, 225 max 4 reps'\n\n"
            response += "Go ahead and tell me your first exercise:"
            
            return self._create_response(response, session_data, needs_input=True)
        else:
            # Ask for clarification
            session_data['state'] = self.STATES['WORKOUT_TYPE']
            response = "I'd love to help you create a workout! What type of workout did you do? (e.g., chest and triceps, back and biceps, legs, push, pull, etc.)"
            return self._create_response(response, session_data, needs_input=True)
    
    def _handle_workout_type(self, user_input: str, session_data: Dict) -> Dict:
        """
        Handle workout type specification
        """
        workout_type = self._extract_workout_type(user_input)
        
        if workout_type:
            session_data['workout_type'] = workout_type
            session_data['state'] = self.STATES['COLLECTING_EXERCISES']
            
            response = f"Perfect! {workout_type.title()} workout it is. Now tell me what exercises you did with details like working sets and max weights:"
            return self._create_response(response, session_data, needs_input=True)
        else:
            response = "I didn't catch the workout type. Could you specify what muscle groups or workout type? (chest, back, legs, push, pull, etc.)"
            return self._create_response(response, session_data, needs_input=True)
    
    def _handle_exercise_input(self, user_input: str, session_data: Dict) -> Dict:
        """
        Handle exercise input and details
        """
        # Check for completion signals
        completion_signals = ['done', 'finished', 'that\'s it', 'complete', 'save', 'end']
        if any(signal in user_input.lower() for signal in completion_signals):
            if session_data['exercises']:
                return self._move_to_confirmation(session_data)
            else:
                response = "You haven't added any exercises yet. Please tell me about your exercises first."
                return self._create_response(response, session_data, needs_input=True)
        
        # Parse exercises from input
        exercises = self._parse_exercise_details(user_input)
        
        if exercises:
            # Add to session
            session_data['exercises'].extend(exercises)
            
            # Create response
            response = f"Got it! Added {len(exercises)} exercise(s):\n"
            for ex in exercises:
                response += f"• {ex['name']}"
                if ex.get('working_sets'):
                    response += f" - {ex['working_sets']} working sets"
                if ex.get('max_weight'):
                    response += f" - {ex['max_weight']} max"
                if ex.get('max_weight_reps'):
                    response += f" ({ex['max_weight_reps']} reps)"
                response += "\n"
            
            response += "\nTell me about your next exercise, or say 'done' when you're finished:"
            return self._create_response(response, session_data, needs_input=True)
        else:
            response = "I couldn't parse that exercise. Try this format:\n"
            response += "'Exercise name: X working sets, Y lbs/plates max'\n"
            response += "Example: 'Bench press: 3 working sets, 225 max 4 reps'"
            return self._create_response(response, session_data, needs_input=True)
    
    def _handle_confirmation(self, user_input: str, session_data: Dict) -> Dict:
        """
        Handle workout confirmation
        """
        user_input_lower = user_input.lower().strip()
        
        if any(word in user_input_lower for word in ['yes', 'y', 'correct', 'good', 'save', 'confirm']):
            # Create the workout
            result = self._create_workout_from_session(session_data)
            session_data['state'] = self.STATES['COMPLETED']
            
            if result['success']:
                response = f"✅ Great! Your {session_data['workout_type']} workout has been saved successfully with {len(session_data['exercises'])} exercises!"
                return self._create_response(response, session_data, completed=True, workout=result['workout'])
            else:
                response = f"❌ Sorry, there was an error saving your workout: {result['message']}"
                return self._create_response(response, session_data, error=True)
        
        elif any(word in user_input_lower for word in ['no', 'n', 'wrong', 'edit', 'change']):
            # Go back to exercise collection
            session_data['state'] = self.STATES['COLLECTING_EXERCISES']
            response = "No problem! Tell me what you'd like to change or add more exercises:"
            return self._create_response(response, session_data, needs_input=True)
        
        else:
            response = "Please respond with 'yes' to save the workout or 'no' to make changes."
            return self._create_response(response, session_data, needs_input=True)
    
    def _extract_workout_type(self, text: str) -> Optional[str]:
        """
        Extract workout type from text
        """
        text_lower = text.lower()
        
        # Look for explicit workout type mentions
        for workout_type in self.workout_type_priority:
            if workout_type in self.workout_types:
                keywords = self.workout_types[workout_type]
                for keyword in keywords:
                    if keyword in text_lower:
                        return self._format_workout_name(workout_type)
                        
        return None

    def _format_workout_name(self, workout_type: str) -> str:
        """
        Format workout type into a proper workout name
        """

        formatting_map = {
            'chest_triceps': 'chest and triceps',
            'back_biceps': 'back and biceps',
            'chest_shoulder_triceps': 'chest, shoulders and triceps',
            'chest_back': 'chest and back',
            'back_shoulders': 'back and shoulders',
            'shoulder_arms': 'shoulders and arms',
            # Individual muscles and others stay as-is
            'chest': 'chest',
            'upperchest': 'upper chest',
            'midchest': 'mid chest',
            'lowerchest': 'lower chest',
            'back': 'back',
            'upperback': 'upper back',
            'midback': 'mid back',
            'lowerback': 'lower back',
            'lats': 'lats',
            'traps': 'traps',
            'shoulders': 'shoulders',
            'frontdelt': 'front delts',
            'sidedelt': 'side delts',
            'reardelt': 'rear delts',
            'arms': 'arms',
            'biceps': 'biceps',
            'triceps': 'triceps',
            'forearms': 'forearms',
            'legs': 'legs',
            'quads': 'quads',
            'hamstrings': 'hamstrings',
            'glutes': 'glutes', 
            'calves': 'calves',
            'abductors': 'abductors',
            'adductors': 'adductors',
            'abs': 'abs',
            'obliques': 'obliques',
        }

        # Replace underscores with spaces and capitalize
        return formatting_map.get(workout_type, workout_type.replace('_', ' '))
    
    def _parse_exercise_details(self, text: str) -> List[Dict]:
        """
        Parse exercise details from text
        """
        exercises = []
        
        # Split by common separators and process each line
        lines = re.split(r'\n|;', text.strip())
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            exercise_data = self._parse_single_exercise(line)
            if exercise_data:
                exercises.append(exercise_data)
        
        return exercises
    
    def _parse_single_exercise(self, text: str) -> Optional[Dict]:
        """
        Fixed version - Parse a single exercise with details
        """
        # Check for detailed exercise pattern: "Exercise: details"
        text = text.strip()
        if not text:
            return None
        
        detailed_match = re.search(self.exercise_patterns['detailed_exercise'], text, re.IGNORECASE)
        
        if not detailed_match:
            words = text.split()
            if len(words) >= 2:
                # Assume first word is exercise name, rest is details
                exercise_name = ' '.join(words[:3])
                details_text = ' '.join(words[3:])
            else:
                return None
        else:
            exercise_name = detailed_match.group(1).strip()
            details_text = detailed_match.group(2).strip()
        
        # Parse details
        exercise_data = {
            'name': self._normalize_exercise_name(exercise_name),
            'working_sets': None,
            'max_weight': None,
            'max_weight_reps': None,
            'weight_type': 'lbs',  # 'lbs' or 'plates'
            'variations': [],
            'raw_details': details_text,
            'plates': None
        }
        
        # 🔧 FIX 1: Check for variations in BOTH exercise name AND details
        full_text_for_variations = f"{exercise_name} {details_text}".lower()
        
        # Split details by commas and semicolons for processing
        detail_parts = re.split(r'[,;]', details_text)
        
        # Process each part separately for sets/weights/reps
        for part in detail_parts:
            part = part.strip()
            if not part:
                continue
            
            # Check for working sets (with typo tolerance)
            if not exercise_data['working_sets']:
                sets_match = re.search(self.exercise_patterns['working_sets'], part, re.IGNORECASE)
                if sets_match:
                    exercise_data['working_sets'] = int(sets_match.group(1))
                    continue
            
            # Check for max weight - order matters (plates first, then lbs, then simple)
            if not exercise_data['max_weight']:
                # Try plates pattern first (highest priority)
                plates_match = re.search(self.exercise_patterns['max_weight_plates'], part, re.IGNORECASE)
                if plates_match:
                    plates = int(plates_match.group(1))
                    exercise_data['max_weight'] = plates * 45  # Convert to lbs
                    exercise_data['weight_type'] = 'plates'
                    exercise_data['plates'] = plates
                    continue
                
                # Try explicit lbs pattern
                lbs_match = re.search(self.exercise_patterns['max_weight_lbs'], part, re.IGNORECASE)
                if lbs_match:
                    exercise_data['max_weight'] = int(lbs_match.group(1))
                    exercise_data['weight_type'] = 'lbs'
                    continue
                
                # Try simple max pattern (assume lbs if no unit specified)
                simple_match = re.search(self.exercise_patterns['max_weight_simple'], part, re.IGNORECASE)
                if simple_match:
                    exercise_data['max_weight'] = int(simple_match.group(1))
                    exercise_data['weight_type'] = 'lbs'
                    continue
            
            # Check for max reps
            if not exercise_data['max_weight_reps']:
                reps_match = re.search(self.exercise_patterns['max_reps'], part, re.IGNORECASE)
                if reps_match:
                    exercise_data['max_weight_reps'] = int(reps_match.group(1))
                    continue
        
        # 🔧 FIX 2: Check for variations in the FULL TEXT (name + details)
        for variation_name, pattern in self.exercise_patterns.items():
            if variation_name.startswith(('max_', 'working_', 'detailed_')):
                continue
            
            # Search in the full text (exercise name + details)
            if re.search(pattern, full_text_for_variations, re.IGNORECASE):
                variation_display = variation_name.replace('_', ' ').title()
                if variation_display not in exercise_data['variations']:
                    exercise_data['variations'].append(variation_display)
        
        return exercise_data
    
    def _normalize_exercise_name(self, name: str) -> str:
        """
        Normalize exercise name
        """
        # Clean up the name
        name = name.strip().title()
        
        # Common mappings
        mappings = {
            'T Bar Row': 'T-Bar Row',
            'Lat Pulldown': 'Lat Pulldown',
            'Pec Deck': 'Pec Deck',
            'Preacher Curl': 'Preacher Curl',
        }
        
        return mappings.get(name, name)
    
    def _move_to_confirmation(self, session_data: Dict) -> Dict:
        """
        Move to confirmation state and show workout summary
        """
        session_data['state'] = self.STATES['CONFIRM_WORKOUT']
        
        response = f"Here's your {session_data['workout_type']} workout:\n\n"
        response += f"**Workout Name:** {session_data['workout_type'].title()} Day\n\n"
        
        for i, exercise in enumerate(session_data['exercises'], 1):
            response += f"**Exercise {i}:** {exercise['name']}\n"
            
            if exercise.get('variations'):
                response += f"Notes: {', '.join(exercise['variations'])}\n"
            
            if exercise.get('working_sets'):
                response += f"Working sets: {exercise['working_sets']}\n"
            
            if exercise.get('max_weight'):
                response += f"Max weight: {exercise['max_weight']}"
                if exercise.get('weight_type') == 'plates':
                    response += " lbs"
                else:
                    response += " lbs"
                response += "\n"
            
            if exercise.get('max_weight_reps'):
                response += f"Max weight reps: {exercise['max_weight_reps']}\n"
            
            response += "\n"
        
        response += "Does everything look correct? (yes/no)"
        
        return self._create_response(response, session_data, needs_input=True)
    
    def _create_workout_from_session(self, session_data: Dict) -> Dict:
        """
        Create workout from session data
        """
        try:
            from django.contrib.auth.models import User
            user = User.objects.get(id=session_data['user_id'])
            
            with transaction.atomic():
                # Create workout
                workout_name = f"{session_data['workout_type'].title()} Day"
                workout = Workout.objects.create(
                    user=user,
                    name=workout_name
                )
                
                # Add exercises
                for order, exercise_data in enumerate(session_data['exercises']):
                    # Find or create exercise
                    exercise = self._find_or_create_exercise(exercise_data, user)
                    
                    # Create workout item
                    WorkoutExerciseItem.objects.create(
                        workout=workout,
                        content_type=ContentType.objects.get_for_model(Exercise),
                        object_id=exercise.id,
                        order=order,
                        working_sets=exercise_data.get('working_sets', 0),
                        max_weight=exercise_data.get('max_weight', 0),
                        max_weight_reps=exercise_data.get('max_weight_reps', 0),
                        notes=', '.join(exercise_data.get('variations', []))
                    )
                
                # Add to daily log
                daily_log, created = DailyLog.objects.get_or_create(
                    user=user,
                    date=date.today()
                )
                daily_log.workouts.add(workout)
                
                return {
                    'success': True,
                    'workout': workout,
                    'message': 'Workout created successfully'
                }
        
        except Exception as e:
            logger.error(f"Error creating workout: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }
        
    def get_improved_exercise_patterns():
        """
        Return improved exercise patterns that are more flexible
        """
        return {
            # Main exercise pattern: "Exercise name: details"
            'detailed_exercise': r'^([^:]+):\s*(.+)$',
            
            # Working sets patterns - more flexible to handle typos and variations
            'working_sets': r'(\d+)\s*(?:working\s+)?(?:workings\s+)?sets?',
            
            # Max weight patterns - improved to handle different formats
            'max_weight_plates': r'(\d+)\s*(?:plates?|plate)\s*(?:max|maximum)?',
            'max_weight_lbs': r'(\d+)\s*(?:lb|lbs|pounds?)\s*(?:max|maximum)?',
            'max_weight_simple': r'(\d+)\s*(?:max|maximum)(?!\s*(?:reps?|rep))',
            'max_reps': r'(\d+)\s*(?:reps?\s*)?(?:max|maximum)(?:\s*reps?)?',
            
            # 🔧 IMPROVED: More flexible variation patterns
            'single_arm': r'\bsingle\s+arm\b',
            'alternating': r'\balternating\b',
            'seated': r'\bseated\b',
            'standing': r'\bstanding\b',
            'lying': r'\blying\b',
            'incline': r'\bincline\b',
            'decline': r'\bdecline\b',
            
            # Equipment patterns - made more flexible
            'plate_loaded': r'\bplate\s*loaded\b',
            'pin_loaded': r'\bpin\s*loaded\b',
            'machine': r'\bmachine\b',
            'cable': r'\bcable\b',
            'dumbbell': r'\bdumbbell\b',
            'barbell': r'\bbarbell\b',
            
            # Grip and bar variations
            'flat_bar': r'\bflat\s+bar\b',
            'ez_bar': r'\bez\s+bar\b',
            'neutral_grip': r'\bneutral\s+grip\b',
            'wide_grip': r'\bwide\s+grip\b',
            'close_grip': r'\bclose\s+grip\b',
            'overhand': r'\boverhand\b',
            'underhand': r'\bunderhand\b',
            
            # Additional modifiers
            'unilateral': r'\bunilateral\b',
            'bilateral': r'\bbilateral\b',
            'partial_rep': r'\bpartial\s+rep\b',
            'pause_rep': r'\bpause\s+rep\b',
            'tempo': r'\btempo\b',
        }
    
    def _find_or_create_exercise(self, exercise_data: Dict, user) -> Exercise:
        """
        Find existing exercise or create new one
        """
        exercise_name = exercise_data['name']
        
        # Try to find existing exercise
        exercise = Exercise.objects.filter(name__icontains=exercise_name).first()
        
        if not exercise:
            # Create new exercise
            exercise = Exercise.objects.create(
                name=exercise_name,
                notes=f"Auto-created from conversational input"
            )
        
        return exercise
    
    def _create_response(self, message: str, session_data: Dict, 
                        needs_input: bool = False, completed: bool = False, 
                        error: bool = False, workout=None) -> Dict:
        """
        Create a standardized response
        """
        return {
            'message': message,
            'session_data': session_data,
            'needs_input': needs_input,
            'completed': completed,
            'error': error,
            'workout': workout,
            'state': session_data['state']
        }