#!/usr/bin/env python3
"""
Comprehensive test script for the Multi-Turn NLP Engine
Run this script to thoroughly test your NLP engine and identify issues
Updated to test the exercise parsing fixes for variations in exercise names
"""

import os
import sys
import django
import re
from typing import Dict, List, Optional

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Import your NLP engine (adjust import path as needed)
try:
    from logger.improved_nlp_engine import MultiTurnNLPEngine
except ImportError:
    try:
        from logger.improved_nlp_engine import MultiTurnNLPEngine
    except ImportError:
        print("❌ Could not import MultiTurnNLPEngine. Make sure the file exists at:")
        print("   - logger/multi_turn_nlp.py OR")
        print("   - logger/improved_nlp_engine.py")
        sys.exit(1)

class NLPTester:
    def __init__(self):
        self.nlp = MultiTurnNLPEngine()
        self.passed_tests = 0
        self.failed_tests = 0
        self.errors = []
        
        # Mock user for testing
        class MockUser:
            id = 1
            username = "test_user"
        
        self.mock_user = MockUser()

    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting Comprehensive NLP Engine Tests")
        print("=" * 80)
        
        # Test individual components
        self.test_workout_type_extraction()
        self.test_exercise_parsing()
        self.test_exercise_variation_detection()  # NEW TEST
        self.test_regex_patterns()
        self.test_workout_name_formatting()
        self.test_exercise_name_normalization()
        self.test_priority_matching()
        
        # Test conversation flow
        self.test_conversation_states()
        self.test_session_data_integrity()
        self.test_full_conversation_flows()
        
        # Test edge cases and error handling
        self.test_edge_cases()
        self.test_error_handling()
        
        # Print summary
        self.print_summary()

    def test_workout_type_extraction(self):
        """Test workout type extraction logic"""
        print("\n🏷️ Testing Workout Type Extraction")
        print("-" * 50)
        
        test_cases = [
            # Compound workouts (should match first)
            ("I did a back and biceps workout", "back and biceps"),
            ("Create a chest and triceps session", "chest and triceps"),
            ("Chest tri day today", "chest and triceps"),
            ("Back bi workout", "back and biceps"),
            ("Shoulder and arms training", "shoulders and arms"),
            
            # Movement patterns
            ("I had a push day", "push"),
            ("Pull workout today", "pull"),
            ("Upper body session", "upper"),
            ("Lower body training", "lower"),
            ("Full body workout", "full"),
            
            # Individual muscles
            ("Chest workout", "chest"),
            ("Back training", "back"),
            ("Leg day", "legs"),
            ("Shoulder session", "shoulders"),
            
            # Edge cases
            ("I worked out", None),  # Should return None
            ("Had a training session", None),  # Should return None
            ("", None),  # Empty string
        ]
        
        for input_text, expected in test_cases:
            try:
                result = self.nlp._extract_workout_type(input_text)
                if result == expected:
                    print(f"✅ '{input_text}' → '{result}'")
                    self.passed_tests += 1
                else:
                    print(f"❌ '{input_text}' → '{result}' (expected '{expected}')")
                    self.failed_tests += 1
                    self.errors.append(f"Workout type: {input_text} -> {result} != {expected}")
            except Exception as e:
                print(f"💥 '{input_text}' → ERROR: {e}")
                self.failed_tests += 1
                self.errors.append(f"Workout type error: {input_text} -> {e}")

    def test_exercise_parsing(self):
        """Test exercise parsing with your specific format"""
        print("\n💪 Testing Exercise Parsing")
        print("-" * 50)
        
        test_cases = [
            {
                'input': "T Bar row: 2 working sets, 3 plates max",
                'expected': {
                    'name': 'T-Bar Row',
                    'working_sets': 2,
                    'max_weight': 135,  # 3 plates * 45
                    'weight_type': 'plates',
                    'plates': 3
                }
            },
            {
                'input': "Plate loaded lat pulldown: single arm, 3 working sets, 5 plates max",
                'expected': {
                    'name': 'Plate Loaded Lat Pulldown',
                    'working_sets': 3,
                    'max_weight': 225,  # 5 plates * 45
                    'weight_type': 'plates',
                    'variations': ['Single Arm', 'Plate Loaded']
                }
            },
            {
                'input': "Cable row: seated; flat bar, 3 workings sets,",
                'expected': {
                    'name': 'Cable Row',
                    'working_sets': 3,
                    'variations': ['Seated', 'Flat Bar', 'Cable']
                }
            },
            {
                'input': "Dumbbell curls: alternating, seated, 3 workings sets, 45 lb max",
                'expected': {
                    'name': 'Dumbbell Curls',
                    'working_sets': 3,
                    'max_weight': 45,
                    'weight_type': 'lbs',
                    'variations': ['Alternating', 'Seated', 'Dumbbell']
                }
            },
            {
                'input': "Reverse pec deck: 3 working sets, 95 lb max",
                'expected': {
                    'name': 'Reverse Pec Deck',
                    'working_sets': 3,
                    'max_weight': 95,
                    'weight_type': 'lbs'
                }
            },
            {
                'input': "Machine lat pullover: 2 working sets, 260 max",
                'expected': {
                    'name': 'Machine Lat Pullover',
                    'working_sets': 2,
                    'max_weight': 260,
                    'weight_type': 'lbs',
                    'variations': ['Machine']
                }
            },
            {
                'input': "Machine preacher curl: single arm, 75 max",
                'expected': {
                    'name': 'Machine Preacher Curl',
                    'max_weight': 75,
                    'weight_type': 'lbs',
                    'variations': ['Single Arm', 'Machine']
                }
            }
        ]
        
        for test_case in test_cases:
            try:
                result = self.nlp._parse_single_exercise(test_case['input'])
                
                if result:
                    success = True
                    expected = test_case['expected']
                    
                    # Check each expected field
                    for field, expected_value in expected.items():
                        if field == 'variations':
                            # Check if all expected variations are present
                            result_variations = result.get('variations', [])
                            missing_variations = []
                            for variation in expected_value:
                                if variation not in result_variations:
                                    missing_variations.append(variation)
                                    success = False
                            
                            if missing_variations:
                                print(f"❌ Missing variations: {missing_variations}")
                                print(f"   Expected: {expected_value}")
                                print(f"   Found: {result_variations}")
                        else:
                            if result.get(field) != expected_value:
                                print(f"❌ Field '{field}': got {result.get(field)}, expected {expected_value}")
                                success = False
                    
                    if success:
                        print(f"✅ '{test_case['input'][:50]}...'")
                        self.passed_tests += 1
                    else:
                        print(f"❌ '{test_case['input'][:50]}...'")
                        print(f"   Full Result: {result}")
                        self.failed_tests += 1
                        self.errors.append(f"Exercise parsing: {test_case['input']}")
                else:
                    print(f"❌ Failed to parse: '{test_case['input']}'")
                    self.failed_tests += 1
                    self.errors.append(f"Exercise parsing failed: {test_case['input']}")
                    
            except Exception as e:
                print(f"💥 Error parsing '{test_case['input'][:30]}...': {e}")
                self.failed_tests += 1
                self.errors.append(f"Exercise parsing error: {e}")

    def test_exercise_variation_detection(self):
        """Test that variations are detected in both exercise names and details"""
        print("\n🔧 Testing Exercise Variation Detection")
        print("-" * 50)
        
        variation_tests = [
            # Equipment in exercise name
            ("Machine press: 3 sets", ["Machine"]),
            ("Cable row: seated", ["Cable", "Seated"]),
            ("Dumbbell fly: incline", ["Dumbbell", "Incline"]),
            ("Barbell curl: standing", ["Barbell", "Standing"]),
            
            # Position/grip in details
            ("Bench press: single arm, seated", ["Single Arm", "Seated"]),
            ("Pull down: wide grip, standing", ["Wide Grip", "Standing"]),
            ("Press: neutral grip, decline", ["Neutral Grip", "Decline"]),
            
            # Combined (equipment in name, position in details)
            ("Machine press: single arm", ["Machine", "Single Arm"]),
            ("Cable row: flat bar, seated", ["Cable", "Flat Bar", "Seated"]),
            ("Dumbbell curl: alternating, standing", ["Dumbbell", "Alternating", "Standing"]),
        ]
        
        for input_text, expected_variations in variation_tests:
            try:
                result = self.nlp._parse_single_exercise(input_text)
                
                if result:
                    found_variations = result.get('variations', [])
                    missing = [v for v in expected_variations if v not in found_variations]
                    
                    if not missing:
                        print(f"✅ '{input_text}' → found all: {found_variations}")
                        self.passed_tests += 1
                    else:
                        print(f"❌ '{input_text}' → missing: {missing}")
                        print(f"   Expected: {expected_variations}")
                        print(f"   Found: {found_variations}")
                        self.failed_tests += 1
                        self.errors.append(f"Variation detection: {input_text} missing {missing}")
                else:
                    print(f"❌ Failed to parse: '{input_text}'")
                    self.failed_tests += 1
                    self.errors.append(f"Variation detection failed: {input_text}")
                    
            except Exception as e:
                print(f"💥 Error testing variations for '{input_text}': {e}")
                self.failed_tests += 1
                self.errors.append(f"Variation detection error: {input_text} -> {e}")

    def test_conversation_states(self):
        """Test conversation state transitions"""
        print("\n🔄 Testing Conversation State Transitions")
        print("-" * 50)
        
        try:
            # Test 1: Initial input with workout type
            response = self.nlp.start_conversation("Create a back and biceps workout", self.mock_user)
            
            if response['state'] == 'collecting_exercises':
                print("✅ Initial input with workout type → collecting_exercises")
                self.passed_tests += 1
            else:
                print(f"❌ Expected 'collecting_exercises', got '{response['state']}'")
                self.failed_tests += 1
                self.errors.append(f"State transition: initial -> {response['state']}")
            
            # Test 2: Exercise input
            session_data = response['session_data']
            response = self.nlp.continue_conversation("T Bar row: 2 working sets, 3 plates max", session_data)
            
            if response['state'] == 'collecting_exercises' and len(session_data['exercises']) > 0:
                print("✅ Exercise input → still collecting_exercises with exercise added")
                self.passed_tests += 1
            else:
                print(f"❌ Exercise input failed. State: {response['state']}, Exercises: {len(session_data.get('exercises', []))}")
                self.failed_tests += 1
                self.errors.append("Exercise input state transition failed")
            
            # Test 3: Done signal
            session_data = response['session_data']
            response = self.nlp.continue_conversation("done", session_data)
            
            if response['state'] == 'confirm_workout':
                print("✅ 'done' signal → confirm_workout")
                self.passed_tests += 1
            else:
                print(f"❌ Expected 'confirm_workout', got '{response['state']}'")
                self.failed_tests += 1
                self.errors.append(f"Done signal: -> {response['state']}")
            
            # Test 4: Confirmation
            session_data = response['session_data']
            response = self.nlp.continue_conversation("yes", session_data)
            
            if response['state'] == 'completed':
                print("✅ 'yes' confirmation → completed")
                self.passed_tests += 1
            else:
                print(f"❌ Expected 'completed', got '{response['state']}'")
                self.failed_tests += 1
                self.errors.append(f"Confirmation: -> {response['state']}")
                
        except Exception as e:
            print(f"💥 State transition test error: {e}")
            self.failed_tests += 1
            self.errors.append(f"State transition error: {e}")

    def test_full_conversation_flows(self):
        """Test complete conversation flows"""
        print("\n🗣️ Testing Full Conversation Flows")
        print("-" * 50)
        
        conversation_tests = [
            {
                'name': 'Back and Biceps Workout',
                'steps': [
                    "Create a back and biceps workout",
                    "T Bar row: 2 working sets, 3 plates max",
                    "Plate loaded lat pulldown: single arm, 3 working sets, 5 plates max",
                    "done",
                    "yes"
                ]
            },
            {
                'name': 'Push Day Workout',
                'steps': [
                    "I did a push day",
                    "Bench press: 4 working sets, 225 max",
                    "Overhead press: 3 working sets, 135 max",
                    "done",
                    "yes"
                ]
            },
            {
                'name': 'Machine Workout with Variations',
                'steps': [
                    "Create a machine workout",
                    "Machine lat pullover: 2 working sets, 260 max",
                    "Cable row: seated, flat bar, 3 working sets",
                    "Machine preacher curl: single arm, 75 max",
                    "done",
                    "yes"
                ]
            }
        ]
        
        for test in conversation_tests:
            try:
                print(f"\n🧪 Testing: {test['name']}")
                
                session_data = None
                success = True
                
                for i, step in enumerate(test['steps']):
                    if session_data is None:
                        response = self.nlp.start_conversation(step, self.mock_user)
                    else:
                        response = self.nlp.continue_conversation(step, session_data)
                    
                    session_data = response['session_data']
                    
                    print(f"  Step {i+1}: '{step}' → {response['state']}")
                    
                    if response.get('error'):
                        print(f"    ❌ Error: {response['message']}")
                        success = False
                        break
                
                if success and response.get('completed'):
                    print(f"✅ {test['name']} completed successfully")
                    self.passed_tests += 1
                else:
                    print(f"❌ {test['name']} failed")
                    self.failed_tests += 1
                    self.errors.append(f"Full conversation: {test['name']}")
                    
            except Exception as e:
                print(f"💥 Conversation test '{test['name']}' error: {e}")
                self.failed_tests += 1
                self.errors.append(f"Conversation error: {test['name']} -> {e}")

    def test_edge_cases(self):
        """Test edge cases and error conditions"""
        print("\n🔍 Testing Edge Cases")
        print("-" * 50)
        
        edge_cases = [
            # Empty inputs
            ("", "Should handle empty input"),
            ("   ", "Should handle whitespace-only input"),
            
            # Malformed exercise inputs
            ("random text without colon", "Should handle text without colon"),
            ("exercise: no numbers", "Should handle exercise without numbers"),
            (":", "Should handle colon only"),
            
            # Typos and variations
            ("T bar row: 2 workings sets, 3 plate max", "Should handle typos"),
            ("bench press: three sets, two hundred pounds", "Should handle word numbers"),
            
            # Multiple exercises in one line
            ("bench press and squat: 3 sets each", "Should handle multiple exercises"),
            
            # Equipment/variation edge cases
            ("machine: 3 sets", "Should handle equipment only as exercise name"),
            ("seated: 2 sets", "Should handle position only as exercise name"),
        ]
        
        for input_text, description in edge_cases:
            try:
                if input_text.strip():
                    result = self.nlp._parse_single_exercise(input_text)
                    print(f"✅ {description}: handled gracefully")
                    self.passed_tests += 1
                else:
                    # Test empty input handling
                    result = self.nlp._parse_single_exercise(input_text)
                    if result is None:
                        print(f"✅ {description}: returned None as expected")
                        self.passed_tests += 1
                    else:
                        print(f"❌ {description}: should return None")
                        self.failed_tests += 1
                        
            except Exception as e:
                print(f"❌ {description}: threw exception {e}")
                self.failed_tests += 1
                self.errors.append(f"Edge case: {description} -> {e}")

    def test_error_handling(self):
        """Test error handling and recovery"""
        print("\n🛡️ Testing Error Handling")
        print("-" * 50)
        
        try:
            # Test with invalid session data
            invalid_session = {'state': 'invalid_state'}
            response = self.nlp.process_input("test", invalid_session)
            
            if 'error' in response['message'] or 'start over' in response['message']:
                print("✅ Invalid state handled gracefully")
                self.passed_tests += 1
            else:
                print("❌ Invalid state not handled properly")
                self.failed_tests += 1
                
        except Exception as e:
            print(f"❌ Error handling test failed: {e}")
            self.failed_tests += 1
            self.errors.append(f"Error handling: {e}")

    def test_regex_patterns(self):
        """Test individual regex patterns"""
        print("\n🔧 Testing Regex Patterns")
        print("-" * 50)
        
        pattern_tests = [
            ('working_sets', '3 working sets', ['3']),
            ('working_sets', '2 workings sets', ['2']),  # Test typo tolerance
            ('working_sets', '4 sets', ['4']),
            ('max_weight_plates', '3 plates max', ['3']),
            ('max_weight_plates', '5 plate', ['5']),
            ('max_weight_lbs', '225 lb max', ['225']),
            ('max_weight_lbs', '95 lbs', ['95']),
            ('max_weight_simple', '260 max', ['260']),
            ('max_reps', '4 reps max', ['4']),
            ('max_reps', '6 max reps', ['6']),
            ('single_arm', 'single arm exercise', True),
            ('seated', 'seated position', True),
            ('plate_loaded', 'plate loaded machine', True),
            ('machine', 'machine exercise', True),
            ('cable', 'cable row', True),
            ('dumbbell', 'dumbbell press', True),
        ]
        
        for pattern_name, test_text, expected in pattern_tests:
            try:
                pattern = self.nlp.exercise_patterns[pattern_name]
                match = re.search(pattern, test_text, re.IGNORECASE)
                
                if isinstance(expected, list):
                    # Test for captured groups
                    if match and match.group(1) == expected[0]:
                        print(f"✅ {pattern_name}: '{test_text}' → captured '{match.group(1)}'")
                        self.passed_tests += 1
                    else:
                        captured = match.group(1) if match else None
                        print(f"❌ {pattern_name}: '{test_text}' → expected '{expected[0]}', got '{captured}'")
                        self.failed_tests += 1
                        self.errors.append(f"Pattern {pattern_name}: {test_text} -> {captured} != {expected[0]}")
                else:
                    # Test for boolean match
                    if bool(match) == expected:
                        print(f"✅ {pattern_name}: '{test_text}' → {'matched' if match else 'no match'}")
                        self.passed_tests += 1
                    else:
                        print(f"❌ {pattern_name}: '{test_text}' → expected {expected}, got {bool(match)}")
                        self.failed_tests += 1
                        self.errors.append(f"Pattern {pattern_name}: {test_text} -> {bool(match)} != {expected}")
                        
            except Exception as e:
                print(f"💥 Pattern test '{pattern_name}' error: {e}")
                self.failed_tests += 1
                self.errors.append(f"Pattern test error: {pattern_name} -> {e}")

    def test_workout_name_formatting(self):
        """Test workout name formatting"""
        print("\n🏷️ Testing Workout Name Formatting")
        print("-" * 50)
        
        try:
            format_tests = [
                ('chest_triceps', 'chest and triceps'),
                ('back_biceps', 'back and biceps'),
                ('push', 'push'),
                ('upper', 'upper'),
                ('legs', 'legs'),
            ]
            
            for input_type, expected in format_tests:
                if hasattr(self.nlp, '_format_workout_name'):
                    result = self.nlp._format_workout_name(input_type)
                    if result == expected:
                        print(f"✅ '{input_type}' → '{result}'")
                        self.passed_tests += 1
                    else:
                        print(f"❌ '{input_type}' → '{result}' (expected '{expected}')")
                        self.failed_tests += 1
                        self.errors.append(f"Workout name formatting: {input_type} -> {result} != {expected}")
                else:
                    print("⚠️ _format_workout_name method not found - using fallback")
                    # Test with simple replacement
                    result = input_type.replace('_', ' ')
                    print(f"ℹ️ '{input_type}' → '{result}' (fallback)")
                    
        except Exception as e:
            print(f"💥 Workout name formatting error: {e}")
            self.failed_tests += 1
            self.errors.append(f"Workout name formatting error: {e}")

    def test_exercise_name_normalization(self):
        """Test exercise name normalization"""
        print("\n📝 Testing Exercise Name Normalization")
        print("-" * 50)
        
        normalization_tests = [
            ('t bar row', 'T-Bar Row'),
            ('lat pulldown', 'Lat Pulldown'),
            ('pec deck', 'Pec Deck'),
            ('preacher curl', 'Preacher Curl'),
            ('bench press', 'Bench Press'),
            ('random exercise', 'Random Exercise'),
            ('machine lat pullover', 'Machine Lat Pullover'),
            ('cable row', 'Cable Row'),
        ]
        
        for input_name, expected in normalization_tests:
            try:
                result = self.nlp._normalize_exercise_name(input_name)
                if result == expected:
                    print(f"✅ '{input_name}' → '{result}'")
                    self.passed_tests += 1
                else:
                    print(f"❌ '{input_name}' → '{result}' (expected '{expected}')")
                    self.failed_tests += 1
                    self.errors.append(f"Exercise normalization: {input_name} -> {result} != {expected}")
                    
            except Exception as e:
                print(f"💥 Exercise normalization error for '{input_name}': {e}")
                self.failed_tests += 1
                self.errors.append(f"Exercise normalization error: {input_name} -> {e}")

    def test_priority_matching(self):
        """Test that workout type priority works correctly"""
        print("\n🥇 Testing Priority Matching")
        print("-" * 50)
        
        priority_tests = [
            # These should match compound types, not individual muscles
            ("I did back and biceps", "back and biceps", "Should match compound, not just 'back'"),
            ("chest and triceps workout", "chest and triceps", "Should match compound, not just 'chest'"),
            ("back bi day", "back and biceps", "Should match compound abbreviation"),
            ("chest tri", "chest and triceps", "Should match compound abbreviation"),
            
            # These should match individual when no compound available
            ("chest workout", "chest", "Should match individual muscle"),
            ("back training", "back", "Should match individual muscle"),
        ]
        
        for input_text, expected, description in priority_tests:
            try:
                result = self.nlp._extract_workout_type(input_text)
                if result == expected:
                    print(f"✅ {description}: '{input_text}' → '{result}'")
                    self.passed_tests += 1
                else:
                    print(f"❌ {description}: '{input_text}' → '{result}' (expected '{expected}')")
                    self.failed_tests += 1
                    self.errors.append(f"Priority matching: {input_text} -> {result} != {expected}")
                    
            except Exception as e:
                print(f"💥 Priority matching error for '{input_text}': {e}")
                self.failed_tests += 1
                self.errors.append(f"Priority matching error: {input_text} -> {e}")

    def test_session_data_integrity(self):
        """Test that session data is maintained correctly throughout conversation"""
        print("\n🔒 Testing Session Data Integrity")
        print("-" * 50)
        
        try:
            # Start conversation
            response = self.nlp.start_conversation("Create a chest workout", self.mock_user)
            session_data = response['session_data']
            
            # Verify initial session data
            required_fields = ['state', 'user_id', 'workout_type', 'exercises', 'raw_inputs']
            missing_fields = [field for field in required_fields if field not in session_data]
            
            if not missing_fields:
                print("✅ Initial session data contains all required fields")
                self.passed_tests += 1
            else:
                print(f"❌ Missing session fields: {missing_fields}")
                self.failed_tests += 1
                self.errors.append(f"Missing session fields: {missing_fields}")
            
            # Add exercise and check session persistence
            response = self.nlp.continue_conversation("Bench press: 3 sets, 225 max", session_data)
            updated_session = response['session_data']
            
            if (updated_session['user_id'] == session_data['user_id'] and 
                updated_session['workout_type'] == session_data['workout_type'] and
                len(updated_session['exercises']) > len(session_data['exercises'])):
                print("✅ Session data persisted correctly with exercise added")
                self.passed_tests += 1
            else:
                print("❌ Session data not persisted correctly")
                self.failed_tests += 1
                self.errors.append("Session data persistence failed")
                
        except Exception as e:
            print(f"💥 Session data integrity test error: {e}")
            self.failed_tests += 1
            self.errors.append(f"Session data integrity error: {e}")

    def print_summary(self):
        """Print test summary and results"""
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = self.passed_tests + self.failed_tests
        pass_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Pass Rate: {pass_rate:.1f}%")
        
        if self.failed_tests > 0:
            print(f"\n🔍 ERRORS FOUND ({len(self.errors)}):")
            print("-" * 50)
            for i, error in enumerate(self.errors, 1):
                print(f"{i}. {error}")
        
        print(f"\n🎯 RECOMMENDATIONS:")
        print("-" * 50)
        
        if pass_rate >= 90:
            print("🎉 Excellent! Your NLP engine is working very well.")
        elif pass_rate >= 75:
            print("👍 Good! Minor issues to fix, but mostly working.")
        elif pass_rate >= 50:
            print("⚠️ Moderate issues. Several areas need attention.")
        else:
            print("🚨 Major issues found. Significant fixes needed.")
        