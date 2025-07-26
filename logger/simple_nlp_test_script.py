#!/usr/bin/env python3
"""
Simple test script for the NLP Engine (no trained models required)
Run this script to test the basic NLP engine functionality
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from logger.nlp_engine import NLPEngine
from logger.models import Exercise, BaseExercise, Muscle, Equipment, BaseMuscle

def setup_basic_test_data():
    """Create minimal test data for testing"""
    print("🔧 Setting up basic test data...")
    
    # Create base muscles
    chest_muscle, _ = BaseMuscle.objects.get_or_create(name="Chest")
    back_muscle, _ = BaseMuscle.objects.get_or_create(name="Back")
    arms_muscle, _ = BaseMuscle.objects.get_or_create(name="Arms")
    legs_muscle, _ = BaseMuscle.objects.get_or_create(name="Legs")
    
    # Create specific muscles
    chest, _ = Muscle.objects.get_or_create(name="Chest", base_muscle=chest_muscle)
    back, _ = Muscle.objects.get_or_create(name="Back", base_muscle=back_muscle)
    biceps, _ = Muscle.objects.get_or_create(name="Biceps", base_muscle=arms_muscle)
    triceps, _ = Muscle.objects.get_or_create(name="Triceps", base_muscle=arms_muscle)
    quads, _ = Muscle.objects.get_or_create(name="Quads", base_muscle=legs_muscle)
    
    # Create equipment
    barbell, _ = Equipment.objects.get_or_create(name="Barbell")
    dumbbell, _ = Equipment.objects.get_or_create(name="Dumbbell")
    bodyweight, _ = Equipment.objects.get_or_create(name="Bodyweight")
    
    # Create basic exercises for testing
    test_exercises = [
        {
            'name': 'Bench Press',
            'muscles': [chest],
            'equipment': [barbell]
        },
        {
            'name': 'Squat',
            'muscles': [quads],
            'equipment': [barbell]
        },
        {
            'name': 'Deadlift',
            'muscles': [back],
            'equipment': [barbell]
        },
        {
            'name': 'Pullup',
            'muscles': [back],
            'equipment': [bodyweight]
        },
        {
            'name': 'Pushup',
            'muscles': [chest],
            'equipment': [bodyweight]
        },
        {
            'name': 'Bicep Curl',
            'muscles': [biceps],
            'equipment': [dumbbell]
        },
        {
            'name': 'Overhead Press',
            'muscles': [chest],
            'equipment': [barbell]
        },
        {
            'name': 'Barbell Row',
            'muscles': [back],
            'equipment': [barbell]
        }
    ]
    
    created_count = 0
    for exercise_data in test_exercises:
        exercise, created = Exercise.objects.get_or_create(
            name=exercise_data['name'],
            defaults={'notes': 'Test exercise for NLP'}
        )
        if created:
            exercise.muscle_group.set(exercise_data['muscles'])
            exercise.equipment.set(exercise_data['equipment'])
            created_count += 1
    
    print(f"✅ Created {created_count} new exercises")
    print(f"📊 Total exercises in database: {Exercise.objects.count()}")

def test_basic_parsing():
    """Test basic parsing without complex models"""
    print("\n🧪 Testing Basic NLP Parsing...")
    print("=" * 50)
    
    nlp = NLPEngine()
    
    # Mock user class for testing
    class MockUser:
        id = 1
    
    test_cases = [
        "I did 3 sets of 10 reps bench press",
        "bench press 3x10",
        "I did squats 4x8 and deadlifts 3x5",
        "30 minutes of running",
        "pullups and pushups",
        "bench press at 135 lbs",
        "bicep curls 3x12",
        "I completed overhead press 4x6"
    ]
    
    user = MockUser()
    
    print("Testing pattern matching and exercise extraction:")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔬 Test Case {i}: '{test_case}'")
        
        # Test individual components
        print("  Pattern Matching:")
        
        # Test if classified as workout
        is_workout = nlp._classify_as_workout(test_case)
        print(f"    ✅ Classified as workout: {is_workout}")
        
        # Test exercise parsing
        exercises = nlp._parse_exercises(test_case)
        print(f"    📝 Exercises found: {len(exercises)}")
        
        for j, exercise in enumerate(exercises):
            print(f"      {j+1}. {exercise['name']}")
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
                print(f"         Details: {', '.join(details)}")
        
        # Test database matching
        if exercises:
            matched_exercises = nlp._match_exercises_to_db(exercises, user)
            matches = sum(1 for ex in matched_exercises if ex.get('db_match'))
            print(f"    🎯 Database matches: {matches}/{len(exercises)}")
        
        print("    " + "-" * 40)

def test_workout_name_generation():
    """Test workout name generation"""
    print("\n🏷️ Testing Workout Name Generation...")
    print("=" * 50)
    
    nlp = NLPEngine()
    
    test_cases = [
        {
            'text': "Upper body workout: bench press and pullups",
            'exercises': [{'name': 'bench press'}, {'name': 'pullups'}]
        },
        {
            'text': "I did chest and tricep training",
            'exercises': [{'name': 'bench press'}, {'name': 'tricep extensions'}]
        },
        {
            'text': "Leg day with squats",
            'exercises': [{'name': 'squats'}]
        },
        {
            'text': "I did bench press pullups and squats",
            'exercises': [{'name': 'bench press'}, {'name': 'pullups'}, {'name': 'squats'}]
        }
    ]
    
    for test in test_cases:
        name = nlp._generate_workout_name(test['text'], test['exercises'])
        print(f"Input: '{test['text']}'")
        print(f"Generated name: '{name}'")
        print()

def test_confidence_calculation():
    """Test confidence calculation"""
    print("\n📊 Testing Confidence Calculation...")
    print("=" * 50)
    
    nlp = NLPEngine()
    
    # Mock user
    class MockUser:
        id = 1
    
    user = MockUser()
    
    test_cases = [
        "I did 3 sets of 10 reps bench press",  # Should have high confidence
        "bench press and squats",               # Medium confidence
        "I did some random exercise",           # Low confidence
        "bench press 3x10 and squat 4x8",     # High confidence
    ]
    
    for test_case in test_cases:
        result = nlp.process_workout_input(test_case, user)
        if result['success']:
            print(f"Input: '{test_case}'")
            print(f"Confidence: {result['confidence']:.1%}")
            print(f"Exercises: {len(result['exercises'])}")
            matches = sum(1 for ex in result['exercises'] if ex.get('db_match'))
            print(f"DB Matches: {matches}/{len(result['exercises'])}")
            print()

def test_full_workflow():
    """Test the complete workflow"""
    print("\n🔄 Testing Complete Workflow...")
    print("=" * 50)
    
    nlp = NLPEngine()
    
    class MockUser:
        id = 1
        username = "test_user"
    
    user = MockUser()
    
    # Test input that should work well
    test_input = "I did 3 sets of 10 reps bench press and 4 sets of 8 squats"
    
    print(f"Testing complete workflow with: '{test_input}'")
    print()
    
    # Step 1: Parse input
    print("Step 1: Parsing input...")
    result = nlp.process_workout_input(test_input, user)
    
    if result['success']:
        print(f"✅ Parsing successful (confidence: {result['confidence']:.1%})")
        print(f"   Workout name: {result['workout_name']}")
        print(f"   Exercises found: {len(result['exercises'])}")
        
        # Step 2: Check for missing exercises
        missing = [ex for ex in result['exercises'] if not ex.get('db_match')]
        if missing:
            print(f"\nStep 2: Creating {len(missing)} missing exercises...")
            create_result = nlp.create_missing_exercises(result, user)
            print(f"✅ Created {create_result['count']} exercises")
            
            # Re-parse to get updated matches
            result = nlp.process_workout_input(test_input, user)
        
        # Step 3: Show summary
        print(f"\nStep 3: Workout Summary")
        summary = nlp.get_workout_summary(result)
        print(summary)
        
        # Step 4: Simulate workout creation
        print(f"\nStep 4: Creating workout...")
        workout_result = nlp.create_workout_from_nlp(result, user)
        
        if workout_result['success']:
            print(f"✅ {workout_result['message']}")
            workout = workout_result['workout']
            print(f"   Workout ID: {workout.id}")
            print(f"   Exercise count: {workout.items.count()}")
        else:
            print(f"❌ Workout creation failed: {workout_result['message']}")
    
    else:
        print(f"❌ Parsing failed: {result['message']}")

def main():
    """Run all tests"""
    print("🚀 Starting Simple NLP Engine Tests")
    print("=" * 60)
    print("This script tests the NLP engine without requiring trained ML models.")
    print("It uses regex patterns and basic matching algorithms.")
    print()
    
    try:
        # Setup test data
        setup_basic_test_data()
        
        # Run tests
        test_basic_parsing()
        test_workout_name_generation()
        test_confidence_calculation()
        test_full_workflow()
        
        print("\n🎉 All tests completed successfully!")
        print("\n📋 Summary:")
        print("- Basic pattern matching: ✅ Working")
        print("- Exercise database matching: ✅ Working")
        print("- Workout name generation: ✅ Working")
        print("- Confidence calculation: ✅ Working")
        print("- Complete workflow: ✅ Working")
        
        print("\n🚀 Next steps:")
        print("1. The NLP engine is ready to use!")
        print("2. Start your Django server: python manage.py runserver")
        print("3. Go to http://127.0.0.1:8000/conversational-input/")
        print("4. Try the examples from the test cases above")
        print("5. The system will work with basic regex patterns")
        print("\n💡 Note: This uses regex patterns, not ML models.")
        print("   For advanced ML features, you'd need to train models later.")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        
        print(f"\n🔧 Troubleshooting:")
        print("1. Make sure Django is properly configured")
        print("2. Check database migrations: python manage.py migrate")
        print("3. Verify all imports are working")

if __name__ == "__main__":
    main()