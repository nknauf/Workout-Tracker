#!/usr/bin/env python3
"""
Test script for NLP functionality
Run this script to test the natural language processing capabilities
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from logger.nlp_processor import NLPProcessor

def test_workout_parsing():
    """Test workout text parsing"""
    print("🧪 Testing Workout Parsing...")
    print("=" * 50)
    
    nlp = NLPProcessor()
    
    test_cases = [
        "I did 3 sets of 10 reps bench press and 5 sets of 5 deadlifts at 225 lbs",
        "30 minutes of running followed by 20 pushups and 15 pullups",
        "Upper body workout: 4x12 bicep curls, 3x10 shoulder press, 2x8 pullups",
        "Cardio session: 45 minutes cycling, 20 minutes walking",
        "Strength training: 3x8 squats at 185 lbs, 4x10 lunges, 2x15 calf raises"
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Input: {text}")
        
        result = nlp.parse_workout_text(text)
        
        print(f"Workout Name: {result['workout_name']}")
        print(f"Confidence: {result['confidence']:.1%}")
        print("Exercises:")
        
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
        
        print("-" * 30)

def test_meal_parsing():
    """Test meal text parsing"""
    print("\n🍽️ Testing Meal Parsing...")
    print("=" * 50)
    
    nlp = NLPProcessor()
    
    test_cases = [
        "I ate chicken breast with 250 calories and 35g protein, plus a protein shake",
        "Breakfast: oatmeal with 150 calories, banana with 100 calories, 2g protein",
        "Lunch: salad with 300 calories and 15g protein, apple with 80 calories",
        "Dinner: salmon 400 calories 45g protein, rice 200 calories, vegetables 50 calories",
        "Snack: protein bar 200 calories 20g protein, nuts 150 calories 5g protein"
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Input: {text}")
        
        result = nlp.parse_meal_text(text)
        
        print(f"Meal Type: {result['meal_name']}")
        print(f"Confidence: {result['confidence']:.1%}")
        print(f"Total Calories: {result['total_calories']}")
        print(f"Total Protein: {result['total_protein']}g")
        print("Foods:")
        
        for j, food in enumerate(result['foods'], 1):
            print(f"  {j}. {food['name']}")
            details = []
            if food.get('calories'):
                details.append(f"{food['calories']} calories")
            if food.get('protein'):
                details.append(f"{food['protein']}g protein")
            
            if details:
                print(f"     Details: {', '.join(details)}")
        
        print("-" * 30)

def test_validation():
    """Test data validation"""
    print("\n✅ Testing Data Validation...")
    print("=" * 50)
    
    nlp = NLPProcessor()
    
    # Test workout validation
    workout_data = {
        'exercises': [
            {'name': 'Test Exercise', 'sets': 999, 'reps': 9999, 'weight': 99999, 'duration': 999}
        ]
    }
    
    validated = nlp.validate_parsed_data(workout_data, 'workout')
    print("Workout validation:")
    print(f"Before: {workout_data['exercises'][0]}")
    print(f"After: {validated['exercises'][0]}")
    
    # Test meal validation
    meal_data = {
        'foods': [
            {'name': 'Test Food', 'calories': 99999, 'protein': 9999}
        ]
    }
    
    validated = nlp.validate_parsed_data(meal_data, 'meal')
    print("\nMeal validation:")
    print(f"Before: {meal_data['foods'][0]}")
    print(f"After: {validated['foods'][0]}")

def test_workout_naming():
    """Test workout name suggestions"""
    print("\n🏷️ Testing Workout Name Suggestions...")
    print("=" * 50)
    
    nlp = NLPProcessor()
    
    test_exercises = [
        [{'name': 'bench press'}, {'name': 'deadlift'}, {'name': 'squat'}],
        [{'name': 'running'}, {'name': 'cycling'}, {'name': 'swimming'}],
        [{'name': 'pushups'}, {'name': 'pullups'}, {'name': 'plank'}],
        [{'name': 'mixed exercise'}, {'name': 'random movement'}]
    ]
    
    for i, exercises in enumerate(test_exercises, 1):
        suggested_name = nlp.suggest_workout_name(exercises)
        print(f"Test {i}: {suggested_name}")
        print(f"  Exercises: {[ex['name'] for ex in exercises]}")

if __name__ == "__main__":
    print("🚀 Starting NLP Test Suite")
    print("=" * 60)
    
    try:
        test_workout_parsing()
        test_meal_parsing()
        test_validation()
        test_workout_naming()
        
        print("\n🎉 All tests completed successfully!")
        print("\nTo use the conversational input feature:")
        print("1. Start your Django server: python manage.py runserver")
        print("2. Navigate to the home page")
        print("3. Click on '💬 Conversational Input'")
        print("4. Try entering natural language descriptions of workouts or meals")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc() 