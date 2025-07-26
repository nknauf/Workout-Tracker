#!/usr/bin/env python3
"""
Test script for the NLP Engine
Run this script to test the NLP engine functionality
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from logger.nlp_engine import NLPEngine
from logger.models import Exercise, BaseExercise, Muscle, Equipment

def setup_test_data():
    """Create some test exercises if they don't exist"""
    print("Setting up test data...")
    
    # Create some basic exercises for testing
    test_exercises = [
        'Bench Press',
        'Squat', 
        'Deadlift',
        'Pullup',
        'Pushup',
        'Bicep Curl',
        'Overhead Press',
        'Barbell Row'
    ]
    
    created_count = 0
    for exercise_name in test_exercises:
        exercise, created = Exercise.objects.get_or_create(
            name=exercise_name,
            defaults={'notes': 'Test exercise for NLP'}
        )
        if created:
            created_count += 1
    
    print(f"Created {created_count} test exercises")

def test_nlp_parsing():
    """Test the NLP parsing functionality"""
    print("\n🧪 Testing NLP Parsing...")
    print("=" * 50)
    
    nlp = NLPEngine()
    
    # Mock user class for testing
    class MockUser:
        id = 1
    
    test_cases = [
        "I did 3 sets of 10 reps bench press and 5 sets of 5 deadlifts",
        "30 minutes of running followed by 20 pushups",
        "Upper body workout: 4x12 bicep curls, 3x10 overhead press",
        "I completed bench press at 135 lbs and did some squats",
        "Did pullups and pushups today",
        "Chest and tricep workout with bench press 3x10 and overhead press",
        "I trained legs with squat 4x8 and deadlift 3x5",
    ]
    
    user = MockUser()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Input: '{test_case}'")
        
        # Process the input
        result = nlp.process_workout_input(test_case, user)
        
        if result['success']:
            print(f"✅ SUCCESS (confidence: {result['confidence']:.1%})")
            print(f"Workout Name: {result['workout_name']}")
            print(f"Exercises Found: {len(result['exercises'])}")
            
            for j, exercise in enumerate(result['exercises'], 1):
                print(f"  {j}. {exercise['name']}")
                details = []
                if exercise.get('sets'):
                    details.append(f"{exercise['sets']} sets")
                if exercise.get('reps'):
                    details.append(f"{exercise['reps']} reps")
                if exercise.get('weight'):
                    details.append(f"{exercise['weight']} lbs")
                if exercise.get('duration'):
                    details.append(f"{exercise['duration']} min")
                
                if details:
                    print(f"     Details: {', '.join(details)}")
                
                # Show database match status
                if exercise.get('db_match'):
                    print(f"     ✅ Matched to: {exercise['db_match'].name}")
                else:
                    print(f"     ❌ Not found in database")
                    if exercise.get('suggested_exercises'):
                        suggestions = [ex.name for ex in exercise['suggested_exercises']]
                        print(f"     💡 Suggestions: {', '.join(suggestions)}")
        else:
            print(f"❌ FAILED: {result['message']}")
        
        print("-" * 30)

def test_workout_creation():
    """Test creating workouts from NLP results"""
    print("\n🏗️ Testing Workout Creation...")
    print("=" * 50)
    
    nlp = NLPEngine()
    
    class MockUser:
        id = 1
        username = "test_user"
    
    user = MockUser()
    
    # Test case that should have good matches
    test_input = "I did 3 sets of 10 reps bench press and 5 sets of 5 squats"
    
    print(f"Testing with: '{test_input}'")
    
    # Parse the input
    parse_result = nlp.process_workout_input(test_input, user)
    
    if parse_result['success']:
        print(f"✅ Parsing successful")
        
        # Test creating missing exercises
        if any(not ex.get('db_match') for ex in parse_result['exercises']):
            print("Creating missing exercises...")
            create_result = nlp.create_missing_exercises(parse_result, user)
            print(f"Created {create_result['count']} exercises")
            
            # Re-parse to get updated matches
            parse_result = nlp.process_workout_input(test_input, user)
        
        # Test workout creation
        print("Creating workout...")
        workout_result = nlp.create_workout_from_nlp(parse_result, user)
        
        if workout_result['success']:
            print(f"✅ Workout created: {workout_result['message']}")
            workout = workout_result['workout']
            print(f"Workout ID: {workout.id}")
            print(f"Workout Name: {workout.name}")
            print(f"Exercise Count: {workout.items.count()}")
        else:
            print(f"❌ Workout creation failed: {workout_result['message']}")
    else:
        print(f"❌ Parsing failed: {parse_result['message']}")

def test_exercise_matching():
    """Test exercise matching logic"""
    print("\n🔍 Testing Exercise Matching...")
    print("=" * 50)
    
    nlp = NLPEngine()
    
    class MockUser:
        id = 1
    
    user = MockUser()
    
    # Test various exercise name variations
    test_exercises = [
        'bench press',
        'bp',
        'bench',
        'squat',
        'deadlift',
        'dl',
        'pullup',
        'pull up',
        'push up',
        'pushup',
        'bicep curl',
        'curl',
        'overhead press',
        'ohp',
        'unknown exercise'
    ]
    
    print("Testing exercise name matching:")
    
    for exercise_name in test_exercises:
        normalized = nlp._normalize_exercise_name(exercise_name)
        suggestions = nlp._get_exercise_suggestions(exercise_name)
        
        print(f"'{exercise_name}' -> '{normalized}'")
        if suggestions:
            print(f"  Suggestions: {[ex.name for ex in suggestions]}")
        else:
            print(f"  No suggestions found")

def test_confidence_calculation():
    """Test confidence calculation"""
    print("\n📊 Testing Confidence Calculation...")
    print("=" * 50)
    
    nlp = NLPEngine()
    
    # Test cases with different confidence levels
    test_cases = [
        {
            'parsed': [{'name': 'bench press'}],
            'matched': [{'name': 'bench press', 'db_match': True}],
            'expected': 'high'
        },
        {
            'parsed': [{'name': 'unknown exercise'}],
            'matched': [{'name': 'unknown exercise', 'db_match': None}],
            'expected': 'low'
        },
        {
            'parsed': [
                {'name': 'bench press'}, 
                {'name': 'squat'}, 
                {'name': 'deadlift'}
            ],
            'matched': [
                {'name': 'bench press', 'db_match': True},
                {'name': 'squat', 'db_match': True},
                {'name': 'deadlift', 'db_match': True}
            ],
            'expected': 'very high'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        confidence = nlp._calculate_confidence(
            test_case['parsed'], 
            test_case['matched']
        )
        
        print(f"Test {i}: {confidence:.1%} confidence ({test_case['expected']})")
        print(f"  Exercises: {len(test_case['parsed'])}")
        print(f"  Matches: {sum(1 for ex in test_case['matched'] if ex.get('db_match'))}")

def main():
    """Run all tests"""
    print("🚀 Starting NLP Engine Tests")
    print("=" * 60)
    
    try:
        # Setup test data
        setup_test_data()
        
        # Run tests
        test_nlp_parsing()
        test_exercise_matching()
        test_confidence_calculation()
        test_workout_creation()
        
        print("\n🎉 All tests completed!")
        print("\nNext steps:")
        print("1. Start your Django server: python manage.py runserver")
        print("2. Navigate to the home page")
        print("3. Click on '💬 Conversational Input (NEW!)'")
        print("4. Try entering natural language workout descriptions")
        print("5. Test the workflow: Input -> Confirm -> Save -> View in Calendar")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()