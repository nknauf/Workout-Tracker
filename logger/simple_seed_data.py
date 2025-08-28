# simple_seed_data.py
from django.db import transaction
from .models import MuscleGroup, Equipment, Exercise

@transaction.atomic
def run():
    """Create simple seed data for testing n8n integration"""
    
    # 1. Create MuscleGroups (simple, generic groups)
    muscle_groups_data = [
        "upper_chest", "mid_chest", "lower_chest",
        "upper_back", "lats", "lower_back", "traps",
        "front_delt", "side_delt", "rear_delt",
        "biceps", "triceps", "forearms",
        "quads", "hamstrings", "glutes", "calves", "adductors", "abductors",
        "abs", "obliques",
    ]

    all_muscle_objs = {}
    for group in muscle_groups_data:
        mg, _ = MuscleGroup.objects.get_or_create(name=group)
        all_muscle_objs[group] = mg

    print(f"Created {len(all_muscle_objs)} total muscle groups")
    
    # 2. Create Equipment (simple types)
    equipment_data = [
        'barbell',
        'dumbbell',
        'cable',
        'smith_machine',
        'machine',
        'ez_bar',
        'flat_bar',
        'bodyweight'
    ]
    
    equipment_objs = {}
    for name in equipment_data:
        eq, created = Equipment.objects.get_or_create(name=name)
        equipment_objs[name] = eq
    
    print(f"Created {len(equipment_objs)} equipment types")
    
    # 3. Create Exercises (~1 per muscle group + some extras)
    exercises_data = [
        # Chest exercises
        {
            'name': 'bench_press',
            'primary': 'mid_chest',
            'secondary': ['triceps', 'front_delt'],
            'equipment': 'barbell',
            'notes': 'Classic chest exercise'
        },
        {
            'name': 'push_ups',
            'primary': 'mid_chest',
            'secondary': ['front_delt', 'triceps'],
            'equipment': 'bodyweight',
            'notes': 'Bodyweight chest exercise'
        },
        
        # Back exercises
        {
            'name': 'pull_ups',
            'primary': 'lats',
            'secondary': ['upper_back', 'biceps'],
            'equipment': 'bodyweight',
            'notes': 'Great back builder'
        },
        {
            'name': 'bent_over_row',
            'primary': 'upper_back',
            'secondary': ['lats', 'biceps'],
            'equipment': 'barbell',
            'notes': 'Horizontal pulling movement'
        },
        
        # Shoulder exercises
        {
            'name': 'barbell_shoulder_press',
            'primary': 'front_delt',
            'secondary': ['side_delt'],
            'equipment': 'barbell',
            'notes': 'Vertical pressing movement'
        },
        {
            'name': 'dumbbell_lat_raises',
            'primary': 'side_delt',
            'secondary': ['front_delt'],
            'equipment': 'dumbbell',
            'notes': 'Isolation for side delts'
        },
        
        # Arm exercises
        {
            'name': 'dumbbell_bicep_curls',
            'primary': 'biceps',
            'secondary': ['forearms'],
            'equipment': 'dumbbell',
            'notes': 'Bicep isolation'
        },
        {
            'name': 'bodyweight_tricep_dips',
            'primary': 'triceps',
            'secondary': ['lower_chest'],
            'equipment': 'bodyweight',
            'notes': 'Tricep focused exercise'
        },
        
        # Leg exercises
        {
            'name': 'barbell_squats',
            'primary': 'glutes',
            'secondary': ['quads', 'hamstrings'],
            'equipment': 'barbell',
            'notes': 'King of leg exercises'
        },
        {
            'name': 'machine_leg_press',
            'primary': 'glutes',
            'secondary': ['quads', 'hamstrings'],
            'equipment': 'machine',
            'notes': 'Machine-based leg exercise'
        },
        
        # Core exercises
        {
            'name': 'planks',
            'primary': 'abs',
            'secondary': ['obliques'],
            'equipment': 'bodyweight',
            'notes': 'Isometric core exercise'
        },
    ]
    
    exercise_objects = {}
    for ex_data in exercises_data:
        exercise, created = Exercise.objects.get_or_create(
            name=ex_data['name'],
            defaults={
                'primary_muscle_group': all_muscle_objs[ex_data['primary']],
                'equipment': equipment_objs[ex_data['equipment']],
                'notes': ex_data['notes']
            }
        )
        
        # Add secondary muscle groups
        if ex_data['secondary']:
            secondary_groups = [all_muscle_objs[mg] for mg in ex_data['secondary']]
            exercise.secondary_muscle_groups.set(secondary_groups)
        
        exercise_objects[ex_data['name']] = exercise
    
    print(f"Created {len(exercise_objects)} exercises")
    
    # Summary
    print("\n=== SEED DATA SUMMARY ===")
    print(f"✅ Muscle Groups: {MuscleGroup.objects.count()}")
    print(f"✅ Equipment: {Equipment.objects.count()}")
    print(f"✅ Exercises: {Exercise.objects.count()}")
    print("\n🎯 Perfect for n8n API testing!")

@transaction.atomic 
def clear_data():
    """Clear all data for fresh start"""
    from .models import Exercise, Equipment, MuscleGroup
    Exercise.objects.all().delete()
    Equipment.objects.all().delete()
    MuscleGroup.objects.all().delete()
    
    print("🗑️ All data cleared")

if __name__ == "__main__":
    print("Creating seed data...")
    run()