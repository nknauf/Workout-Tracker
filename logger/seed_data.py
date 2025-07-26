from django.db import transaction
from .models import BaseMuscle, Muscle, Equipment, BaseExercise, Exercise

@transaction.atomic
def run():
    # 1. Create BaseMuscle & Muscles
    base_muscles_data = [
        {"name": "Chest", "muscles": ["UpperChest", "MidChest", "LowerChest"]},
        {"name": "Back", "muscles": ["UpperBack", "MidBack", "LowerBack", "Lats", "Traps"]},
        {"name": "Shoulders", "muscles": ["FrontDelt", "SideDelt", "RearDelt"]},
        {"name": "Arms", "muscles": ["Biceps", "Triceps", "Forearms"]},
        {"name": "Legs", "muscles": ["Quads", "Hamstrings", "Glutes", "Calves", "Adductors", "Abductors"]},
        {"name": "Core", "muscles": ["Abs", "Obliques", "LowerBack"]},
    ]

    muscle_objs = {}
    
    for base_muscle_data in base_muscles_data:
        base_muscle = BaseMuscle.objects.create(name=base_muscle_data["name"])
        for muscle_name in base_muscle_data["muscles"]:
            muscle = Muscle.objects.create(name=muscle_name, base_muscle=base_muscle)
            muscle_objs[muscle_name] = muscle
    
    print("Created base muscles and muscles successfully!")

    # 2. Create Equipment
    equipment_data = [
        "Barbell", "Dumbbell", "Cable", "Machine", "Smith", "EZBar", "Bench", "Bodyweight"
    ]
    
    equipment_objs = {}
    for equipment_name in equipment_data:
        equipment = Equipment.objects.create(name=equipment_name)
        equipment_objs[equipment_name] = equipment
    
    print("Created equipment successfully!")

    # 3. Create BaseExercise objects (templates for users to create their own exercises)
    exercises = [
        # Chest
        {"base_name": "Bench Press", "name": "Barbell Bench Press", "muscles": ["MidChest"], "equipment": ["Barbell", "Bench"], "notes": ""},
        {"base_name": "Bench Press", "name": "Dumbbell Bench Press", "muscles": ["MidChest"], "equipment": ["Dumbbell", "Bench"], "notes": ""},
        {"base_name": "Bench Press", "name": "Smith Machine Bench Press", "muscles": ["MidChest"], "equipment": ["Smith", "Bench"], "notes": ""},
        {"base_name": "Bench Press", "name": "PlateLoaded Bench Press", "muscles": ["MidChest"], "equipment": ["Machine"], "notes": ""},
        {"base_name": "Bench Press", "name": "PinLoaded Bench Press", "muscles": ["MidChest"], "equipment": ["Machine"], "notes": ""},

        {"base_name": "Incline Press", "name": "Barbell Incline Press", "muscles": ["UpperChest"], "equipment": ["Barbell", "Bench"], "notes": ""},
        {"base_name": "Incline Press", "name": "Dumbbell Incline Press", "muscles": ["UpperChest"], "equipment": ["Dumbbell", "Bench"], "notes": ""},
        {"base_name": "Incline Press", "name": "Smith Machine Incline Press", "muscles": ["UpperChest"], "equipment": ["Smith", "Bench"], "notes": ""},
        {"base_name": "Incline Press", "name": "PlateLoaded Incline Press", "muscles": ["UpperChest"], "equipment": ["Machine"], "notes": ""},
        {"base_name": "Incline Press", "name": "PinLoaded Incline Press", "muscles": ["UpperChest"], "equipment": ["Machine"], "notes": ""},

        {"base_name": "Decline Press", "name": "Barbell Decline Press", "muscles": ["LowerChest"], "equipment": ["Barbell", "Bench"], "notes": ""},
        {"base_name": "Decline Press", "name": "Dumbbell Decline Press", "muscles": ["LowerChest"], "equipment": ["Dumbbell", "Bench"], "notes": ""},
        {"base_name": "Decline Press", "name": "Smith Machine Decline Press", "muscles": ["LowerChest"], "equipment": ["Smith", "Bench"], "notes": ""},
        {"base_name": "Decline Press", "name": "PlateLoaded Decline Press", "muscles": ["LowerChest"], "equipment": ["Machine"], "notes": ""},
        {"base_name": "Decline Press", "name": "PinLoaded Decline Press", "muscles": ["LowerChest"], "equipment": ["Machine"], "notes": ""},

        {"base_name": "Fly", "name": "Dumbbell Fly", "muscles": ["MidChest"], "equipment": ["Dumbbell", "Bench"], "notes": ""},
        {"base_name": "Fly", "name": "Cable Fly", "muscles": ["MidChest"], "equipment": ["Cable"], "notes": ""},
        {"base_name": "Fly", "name": "PlateLoaded Fly", "muscles": ["MidChest"], "equipment": ["Machine"], "notes": ""},
        {"base_name": "Fly", "name": "PinLoaded Fly", "muscles": ["MidChest"], "equipment": ["Machine"], "notes": ""},

        {"base_name": "Incline Fly", "name": "Dumbbell Incline Fly", "muscles": ["UpperChest"], "equipment": ["Dumbbell", "Bench"], "notes": ""},
        {"base_name": "Incline Fly", "name": "Cable Incline Fly", "muscles": ["UpperChest"], "equipment": ["Cable"], "notes": ""},
        {"base_name": "Incline Fly", "name": "PlateLoaded Incline Fly", "muscles": ["UpperChest"], "equipment": ["Machine"], "notes": ""},
        {"base_name": "Incline Fly", "name": "PinLoaded Incline Fly", "muscles": ["UpperChest"], "equipment": ["Machine"], "notes": ""},

        {"base_name": "Decline Fly", "name": "Dumbbell Decline Fly", "muscles": ["LowerChest"], "equipment": ["Dumbbell", "Bench"], "notes": ""},
        {"base_name": "Decline Fly", "name": "Cable Decline Fly", "muscles": ["LowerChest"], "equipment": ["Cable"], "notes": ""},
        {"base_name": "Decline Fly", "name": "PlateLoaded Decline Fly", "muscles": ["LowerChest"], "equipment": ["Machine"], "notes": ""},
        {"base_name": "Decline Fly", "name": "PinLoaded Decline Fly", "muscles": ["LowerChest"], "equipment": ["Machine"], "notes": ""},

        {"base_name": "Push Up", "name": "Bodyweight Push Up", "muscles": ["MidChest"], "equipment": ["Bodyweight"], "notes": ""},
        {"base_name": "Push Up", "name": "Dumbbell Push Up", "muscles": ["MidChest"], "equipment": ["Dumbbell"], "notes": ""},
        {"base_name": "Push Up", "name": "Incline Push Up", "muscles": ["MidChest"], "equipment": ["Bodyweight", "Bench"], "notes": ""},
        {"base_name": "Push Up", "name": "Decline Push Up", "muscles": ["MidChest"], "equipment": ["Bodyweight", "Bench"], "notes": ""},

        {"base_name": "Dips", "name": "Bodyweight Dips", "muscles": ["MidChest"], "equipment": ["Bodyweight"], "notes": ""},
        {"base_name": "Dips", "name": "Weighted Dips", "muscles": ["MidChest"], "equipment": ["Bodyweight"], "notes": ""},
        {"base_name": "Dips", "name": "Machine Dips", "muscles": ["MidChest"], "equipment": ["Machine"], "notes": ""},

        # Back
        {"base_name": "Pull Up", "name": "Bodyweight Pull Up", "muscles": ["Lats"], "equipment": ["Bodyweight"], "notes": ""},
        {"base_name": "Pull Up", "name": "Weighted Pull Up", "muscles": ["Lats"], "equipment": ["Bodyweight"], "notes": ""},
        {"base_name": "Pull Up", "name": "Assisted Pull Up", "muscles": ["Lats"], "equipment": ["Machine"], "notes": ""},

        {"base_name": "Lat Pulldown", "name": "Cable Lat Pulldown", "muscles": ["Lats"], "equipment": ["Cable"], "notes": ""},
        {"base_name": "Lat Pulldown", "name": "PlateLoaded Lat Pulldown", "muscles": ["Lats"], "equipment": ["Machine"], "notes": ""},
        {"base_name": "Lat Pulldown", "name": "PinLoaded Lat Pulldown", "muscles": ["Lats"], "equipment": ["Machine"], "notes": ""},

        {"base_name": "Row", "name": "Barbell Row", "muscles": ["MidBack"], "equipment": ["Barbell"], "notes": ""},
        {"base_name": "Row", "name": "Dumbbell Row", "muscles": ["MidBack"], "equipment": ["Dumbbell"], "notes": ""},
        {"base_name": "Row", "name": "Cable Row", "muscles": ["MidBack"], "equipment": ["Cable"], "notes": ""},
        {"base_name": "Row", "name": "PlateLoaded Row", "muscles": ["MidBack"], "equipment": ["Machine"], "notes": ""},
        {"base_name": "Row", "name": "PinLoaded Row", "muscles": ["MidBack"], "equipment": ["Machine"], "notes": ""},
        {"base_name": "Row", "name": "Smith Machine Row", "muscles": ["MidBack"], "equipment": ["Smith"], "notes": ""},

        {"base_name": "T-Bar Row", "name": "T-Bar Row", "muscles": ["MidBack"], "equipment": ["Barbell"], "notes": ""},
        {"base_name": "T-Bar Row", "name": "PlateLoaded T-Bar Row", "muscles": ["MidBack"], "equipment": ["Machine"], "notes": ""},

        {"base_name": "Deadlift", "name": "Barbell Deadlift", "muscles": ["LowerBack", "MidBack"], "equipment": ["Barbell"], "notes": ""},
        {"base_name": "Deadlift", "name": "Dumbbell Deadlift", "muscles": ["LowerBack", "MidBack"], "equipment": ["Dumbbell"], "notes": ""},
        {"base_name": "Deadlift", "name": "Smith Machine Deadlift", "muscles": ["LowerBack", "MidBack"], "equipment": ["Smith"], "notes": ""},
        {"base_name": "Deadlift", "name": "Trap Bar Deadlift", "muscles": ["LowerBack", "MidBack"], "equipment": ["Barbell"], "notes": ""},

        {"base_name": "Shrug", "name": "Barbell Shrug", "muscles": ["Traps"], "equipment": ["Barbell"], "notes": ""},
        {"base_name": "Shrug", "name": "Dumbbell Shrug", "muscles": ["Traps"], "equipment": ["Dumbbell"], "notes": ""},
        {"base_name": "Shrug", "name": "Smith Machine Shrug", "muscles": ["Traps"], "equipment": ["Smith"], "notes": ""},
        {"base_name": "Shrug", "name": "PlateLoaded Shrug", "muscles": ["Traps"], "equipment": ["Machine"], "notes": ""},
        {"base_name": "Shrug", "name": "PinLoaded Shrug", "muscles": ["Traps"], "equipment": ["Machine"], "notes": ""},

        # Shoulders
        {"base_name": "Overhead Press", "name": "Barbell Overhead Press", "muscles": ["FrontDelt"], "equipment": ["Barbell"], "notes": ""},
        {"base_name": "Overhead Press", "name": "Dumbbell Overhead Press", "muscles": ["FrontDelt"], "equipment": ["Dumbbell"], "notes": ""},
        {"base_name": "Overhead Press", "name": "Smith Machine Overhead Press", "muscles": ["FrontDelt"], "equipment": ["Smith"], "notes": ""},
        {"base_name": "Overhead Press", "name": "PlateLoaded Overhead Press", "muscles": ["FrontDelt"], "equipment": ["Machine"], "notes": ""},
        {"base_name": "Overhead Press", "name": "PinLoaded Overhead Press", "muscles": ["FrontDelt"], "equipment": ["Machine"], "notes": ""},

        {"base_name": "Lateral Raise", "name": "Dumbbell Lateral Raise", "muscles": ["SideDelt"], "equipment": ["Dumbbell"], "notes": ""},
        {"base_name": "Lateral Raise", "name": "Cable Lateral Raise", "muscles": ["SideDelt"], "equipment": ["Cable"], "notes": ""},
        {"base_name": "Lateral Raise", "name": "PlateLoaded Lateral Raise", "muscles": ["SideDelt"], "equipment": ["Machine"], "notes": ""},
        {"base_name": "Lateral Raise", "name": "PinLoaded Lateral Raise", "muscles": ["SideDelt"], "equipment": ["Machine"], "notes": ""},

        {"base_name": "Reverse Fly", "name": "Dumbbell Reverse Fly", "muscles": ["RearDelt"], "equipment": ["Dumbbell"], "notes": ""},
        {"base_name": "Reverse Fly", "name": "Cable Reverse Fly", "muscles": ["RearDelt"], "equipment": ["Cable"], "notes": ""},
        {"base_name": "Reverse Fly", "name": "Reverse Pec Deck", "muscles": ["RearDelt"], "equipment": ["Machine"], "notes": ""},
        {"base_name": "Reverse Fly", "name": "Rear Delt PlateLoaded Machine Fly", "muscles": ["RearDelt"], "equipment": ["Machine"], "notes": ""},
        {"base_name": "Reverse Fly", "name": "Bent-over Rear Delt Raise", "muscles": ["RearDelt"], "equipment": ["Barbell"], "notes": ""},
        # Front/Side combination
        {"base_name": "Y Raise", "name": "Dumbbell Y Raise", "muscles": ["FrontDelt", "SideDelt"], "equipment": ["Dumbbell"], "notes": ""},
        {"base_name": "Y Raise", "name": "Cable Y Raise", "muscles": ["FrontDelt", "SideDelt"], "equipment": ["Cable"], "notes": ""},

        # Arms
        # Biceps – Curl
        {"base_name": "Curl", "name": "Barbell Curl", "muscles": ["Biceps"], "equipment": ["Barbell"], "notes": ""},
        {"base_name": "Curl", "name": "EZBar Curl", "muscles": ["Biceps"], "equipment": ["EZBar"], "notes": ""},
        {"base_name": "Curl", "name": "Dumbbell Curl", "muscles": ["Biceps"], "equipment": ["Dumbbell"], "notes": ""},
        {"base_name": "Curl", "name": "Cable Curl", "muscles": ["Biceps"], "equipment": ["Cable"], "notes": ""},
        {"base_name": "Curl", "name": "PlateLoaded Machine Curl", "muscles": ["Biceps"], "equipment": ["Machine"], "notes": ""},
        {"base_name": "Curl", "name": "PinLoaded Machine Curl", "muscles": ["Biceps"], "equipment": ["Machine"], "notes": ""},
        {"base_name": "Curl", "name": "PlateLoaded Preacher Curl", "muscles": ["Biceps"], "equipment": ["Machine", "Bench"], "notes": ""},
        {"base_name": "Curl", "name": "PinLoaded Preacher Curl", "muscles": ["Biceps"], "equipment": ["Machine", "Bench"], "notes": ""},
        {"base_name": "Curl", "name": "Dumbbell Preacher Curl", "muscles": ["Biceps"], "equipment": ["Dumbbell", "Bench"], "notes": ""},
        {"base_name": "Curl", "name": "Incline Dumbbell Curl", "muscles": ["Biceps"], "equipment": ["Dumbbell", "Bench"], "notes": ""},
        {"base_name": "Curl", "name": "Zottman Curl", "muscles": ["Biceps"], "equipment": ["Dumbbell"], "notes": ""},
        {"base_name": "Curl", "name": "Dumbbell Spider Curl", "muscles": ["Biceps"], "equipment": ["Dumbbell"], "notes": ""},
        {"base_name": "Curl", "name": "EZBar Spider Curl", "muscles": ["Biceps"], "equipment": ["EZBar"], "notes": ""},
        {"base_name": "Curl", "name": "Dumbbell Drag Curl", "muscles": ["Biceps"], "equipment": ["Dumbbell"], "notes": ""},
        {"base_name": "Curl", "name": "Cable Drag Curl", "muscles": ["Biceps"], "equipment": ["Cable"], "notes": ""},
        {"base_name": "Curl", "name": "Cable Bayesian Curl", "muscles": ["Biceps"], "equipment": ["Cable"], "notes": ""},

        # Chin Up
        {"base_name": "Chin Up", "name": "Bodyweight Chin Up", "muscles": ["Biceps"], "equipment": ["Bodyweight"], "notes": ""},
        {"base_name": "Chin Up", "name": "Cable Chin Up", "muscles": ["Biceps"], "equipment": ["Cable"], "notes": ""},

        # Triceps – Extension-Pushdown
        {"base_name": "Extension-Pushdown", "name": "PlateLoaded Tricep Extension", "muscles": ["Triceps"], "equipment": ["Machine"], "notes": ""},
        {"base_name": "Extension-Pushdown", "name": "PinLoaded Tricep Extension", "muscles": ["Triceps"], "equipment": ["Machine"], "notes": ""},
        {"base_name": "Extension-Pushdown", "name": "Overhead Dumbbell Tricep Extension", "muscles": ["Triceps"], "equipment": ["Dumbbell"], "notes": ""},
        {"base_name": "Extension-Pushdown", "name": "EZBar Tricep Skullcrusher", "muscles": ["Triceps"], "equipment": ["EZBar"], "notes": ""},
        {"base_name": "Extension-Pushdown", "name": "FlatBar Tricep Skullcrusher", "muscles": ["Triceps"], "equipment": ["Barbell"], "notes": ""},
        {"base_name": "Extension-Pushdown", "name": "Dumbbell Tricep Skullcrusher", "muscles": ["Triceps"], "equipment": ["Dumbbell"], "notes": ""},
        {"base_name": "Extension-Pushdown", "name": "Cable Tricep Skullcrusher", "muscles": ["Triceps"], "equipment": ["Cable"], "notes": ""},

        # Cross Cable & Kickbacks
        {"base_name": "Cross Cable Tricep Extensions", "name": "Cross Cable Tricep Extensions", "muscles": ["Triceps"], "equipment": ["Cable"], "notes": ""},
        {"base_name": "Tricep Kickback", "name": "Dumbbell Tricep Kickbacks", "muscles": ["Triceps"], "equipment": ["Dumbbell"], "notes": ""},
        {"base_name": "Tricep Kickback", "name": "Cable Tricep Kickbacks", "muscles": ["Triceps"], "equipment": ["Cable"], "notes": ""},

        # Pushdowns & JM Press
        {"base_name": "Extension-Pushdown", "name": "PinLoaded Tricep Pushdown", "muscles": ["Triceps"], "equipment": ["Machine"], "notes": ""},
        {"base_name": "Extension-Pushdown", "name": "PlateLoaded Tricep Pushdown", "muscles": ["Triceps"], "equipment": ["Machine"], "notes": ""},
        {"base_name": "JM Press", "name": "Barbell JM Press", "muscles": ["Triceps"], "equipment": ["Barbell"], "notes": ""},
        {"base_name": "JM Press", "name": "Dumbbell JM Press", "muscles": ["Triceps"], "equipment": ["Dumbbell"], "notes": ""},
        {"base_name": "JM Press", "name": "Smith Machine JM Press", "muscles": ["Triceps"], "equipment": ["Smith"], "notes": ""},

        # Forearms – Wrist Curl/Extension
        {"base_name": "Wrist Curl-Extension", "name": "Barbell Wrist Curl", "muscles": ["Forearms"], "equipment": ["Barbell"], "notes": ""},
        {"base_name": "Wrist Curl-Extension", "name": "Dumbbell Wrist Curl", "muscles": ["Forearms"], "equipment": ["Dumbbell"], "notes": ""},
        {"base_name": "Wrist Curl-Extension", "name": "Reverse EZBar Curl", "muscles": ["Forearms"], "equipment": ["EZBar"], "notes": ""},
        {"base_name": "Wrist Curl-Extension", "name": "Reverse FlatBar Curl", "muscles": ["Forearms"], "equipment": ["Barbell"], "notes": ""},
        {"base_name": "Wrist Curl-Extension", "name": "Reverse Dumbbell Curl", "muscles": ["Forearms"], "equipment": ["Dumbbell"], "notes": ""},
        {"base_name": "Wrist Curl-Extension", "name": "Behind-the-Back FlatBar Wrist Curl", "muscles": ["Forearms"], "equipment": ["Barbell"], "notes": ""},
        {"base_name": "Wrist Curl-Extension", "name": "Behind-the-Back EZBar Wrist Curl", "muscles": ["Forearms"], "equipment": ["EZBar"], "notes": ""},

        # GripRotation
        {"base_name": "GripRotation", "name": "Plate Pinches", "muscles": ["Forearms"], "equipment": ["Machine"], "notes": ""},
        {"base_name": "GripRotation", "name": "Fat Grip Dumbbell Hold", "muscles": ["Forearms"], "equipment": ["Dumbbell"], "notes": ""},
        {"base_name": "GripRotation", "name": "Barbell Hold", "muscles": ["Forearms"], "equipment": ["Barbell"], "notes": ""},
        {"base_name": "GripRotation", "name": "Wrist Roller", "muscles": ["Forearms"], "equipment": ["Machine"], "notes": ""},

        # Quads – Leg Extension
        {"base_name": "Leg Extension", "name": "PlateLoaded Leg Extensions", "muscles": ["Quads"], "equipment": ["Machine"], "notes": ""},
        {"base_name": "Leg Extension", "name": "PinLoaded Leg Extensions", "muscles": ["Quads"], "equipment": ["Machine"], "notes": ""},

        # Quads – Sissy Squat
        {"base_name": "Sissy Squat", "name": "Bodyweight Sissy Squat", "muscles": ["Quads"], "equipment": ["Bodyweight"], "notes": ""},
        {"base_name": "Sissy Squat", "name": "Weighted Sissy Squat", "muscles": ["Quads"], "equipment": ["Barbell"], "notes": ""},
        {"base_name": "Sissy Squat", "name": "Smith Machine Sissy Squat", "muscles": ["Quads"], "equipment": ["Smith"], "notes": ""},
        {"base_name": "Sissy Squat", "name": "Hacksquat Sissy Squat", "muscles": ["Quads"], "equipment": ["Machine"], "notes": ""},

        # Quads – Front Squat
        {"base_name": "Front Squat", "name": "Barbell Front Squat", "muscles": ["Quads"], "equipment": ["Barbell"], "notes": ""},
        {"base_name": "Front Squat", "name": "Dumbbell Front Squat", "muscles": ["Quads"], "equipment": ["Dumbbell"], "notes": ""},
        {"base_name": "Front Squat", "name": "Smith Machine Front Squat", "muscles": ["Quads"], "equipment": ["Smith"], "notes": ""},
        {"base_name": "Front Squat", "name": "Goblet Squat", "muscles": ["Quads"], "equipment": ["Dumbbell"], "notes": ""},

        # Hamstrings – Leg Curl
        {"base_name": "Leg Curl", "name": "Lying PlateLoaded Leg Curl", "muscles": ["Hamstrings"], "equipment": ["Machine"], "notes": ""},
        {"base_name": "Leg Curl", "name": "Lying PinLoaded Leg Curl", "muscles": ["Hamstrings"], "equipment": ["Machine"], "notes": ""},
        {"base_name": "Leg Curl", "name": "PlateLoaded Leg Curl", "muscles": ["Hamstrings"], "equipment": ["Machine"], "notes": ""},
        {"base_name": "Leg Curl", "name": "PinLoaded Leg Curl", "muscles": ["Hamstrings"], "equipment": ["Machine"], "notes": ""},
        {"base_name": "Leg Curl", "name": "Standing Leg Curl", "muscles": ["Hamstrings"], "equipment": ["Machine"], "notes": ""},
        {"base_name": "Leg Curl", "name": "Cable Leg Curl", "muscles": ["Hamstrings"], "equipment": ["Cable"], "notes": ""},

        # Hamstrings – RDL
        {"base_name": "RDL", "name": "Barbell RDL", "muscles": ["Hamstrings"], "equipment": ["Barbell"], "notes": ""},
        {"base_name": "RDL", "name": "Dumbbell RDL", "muscles": ["Hamstrings"], "equipment": ["Dumbbell"], "notes": ""},
        {"base_name": "RDL", "name": "Smith Machine RDL", "muscles": ["Hamstrings"], "equipment": ["Smith"], "notes": ""},
        {"base_name": "RDL", "name": "PlateLoaded RDL", "muscles": ["Hamstrings"], "equipment": ["Machine"], "notes": ""},
        {"base_name": "RDL", "name": "PinLoaded RDL", "muscles": ["Hamstrings"], "equipment": ["Machine"], "notes": ""},

        # Glutes – Hip Thrust
        {"base_name": "Hip Thrust", "name": "Barbell Hip Thrust", "muscles": ["Glutes"], "equipment": ["Barbell"], "notes": ""},
        {"base_name": "Hip Thrust", "name": "Dumbbell Hip Thrust", "muscles": ["Glutes"], "equipment": ["Dumbbell"], "notes": ""},
        {"base_name": "Hip Thrust", "name": "Smith Machine Hip Thrust", "muscles": ["Glutes"], "equipment": ["Smith"], "notes": ""},
        {"base_name": "Hip Thrust", "name": "PlateLoaded Hip Thrust", "muscles": ["Glutes"], "equipment": ["Machine"], "notes": ""},
        {"base_name": "Hip Thrust", "name": "PinLoaded Hip Thrust", "muscles": ["Glutes"], "equipment": ["Machine"], "notes": ""},

        # Glutes – Glute Kickback
        {"base_name": "Glute Kickback", "name": "Cable Glute Kickback", "muscles": ["Glutes"], "equipment": ["Cable"], "notes": ""},
        {"base_name": "Glute Kickback", "name": "PlateLoaded Glute Kickback", "muscles": ["Glutes"], "equipment": ["Machine"], "notes": ""},
        {"base_name": "Glute Kickback", "name": "PinLoaded Glute Kickback", "muscles": ["Glutes"], "equipment": ["Machine"], "notes": ""},

        # Glutes – Glute Bridges
        {"base_name": "Glute Bridges", "name": "Bodyweight Glute Bridge", "muscles": ["Glutes"], "equipment": ["Bodyweight"], "notes": ""},
        {"base_name": "Glute Bridges", "name": "Barbell Glute Bridge", "muscles": ["Glutes"], "equipment": ["Barbell"], "notes": ""},
        {"base_name": "Glute Bridges", "name": "Dumbbell Glute Bridge", "muscles": ["Glutes"], "equipment": ["Dumbbell"], "notes": ""},

        # Calves – Calf Raise
        {"base_name": "Calf Raise", "name": "Barbell Calf Raise", "muscles": ["Calves"], "equipment": ["Barbell"], "notes": ""},
        {"base_name": "Calf Raise", "name": "Dumbbell Calf Raise", "muscles": ["Calves"], "equipment": ["Dumbbell"], "notes": ""},
        {"base_name": "Calf Raise", "name": "PlateLoaded Calf Raise", "muscles": ["Calves"], "equipment": ["Machine"], "notes": ""},
        {"base_name": "Calf Raise", "name": "PinLoaded Calf Raise", "muscles": ["Calves"], "equipment": ["Machine"], "notes": ""},
        {"base_name": "Calf Raise", "name": "Seated PlateLoaded Calf Raise", "muscles": ["Calves"], "equipment": ["Machine"], "notes": ""},
        {"base_name": "Calf Raise", "name": "Seated PinLoaded Calf Raise", "muscles": ["Calves"], "equipment": ["Machine"], "notes": ""},
        {"base_name": "Calf Raise", "name": "Smith Machine Calf Raise", "muscles": ["Calves"], "equipment": ["Smith"], "notes": ""},

        # Adductors – Adduction Machine
        {"base_name": "Adduction Machine", "name": "PinLoaded Adduction Machine", "muscles": ["Adductors"], "equipment": ["Machine"], "notes": ""},
        {"base_name": "Adduction Machine", "name": "PlateLoaded Adduction Machine", "muscles": ["Adductors"], "equipment": ["Machine"], "notes": ""},

        # Adductors – Cable Adduction
        {"base_name": "Cable Adduction", "name": "Standing Cable Inner Thigh Adduction", "muscles": ["Adductors"], "equipment": ["Cable"], "notes": ""},
        {"base_name": "Cable Adduction", "name": "Lying Cable Adduction", "muscles": ["Adductors"], "equipment": ["Cable"], "notes": ""},

        # Abductors – Abduction Machine
        {"base_name": "Abduction Machine", "name": "PinLoaded Abduction Machine", "muscles": ["Abductors"], "equipment": ["Machine"], "notes": ""},
        {"base_name": "Abduction Machine", "name": "PlateLoaded Abduction Machine", "muscles": ["Abductors"], "equipment": ["Machine"], "notes": ""},

        # Abductors – Cable Abduction
        {"base_name": "Cable Abduction", "name": "Standing Cable Outer Thigh Abduction", "muscles": ["Abductors"], "equipment": ["Cable"], "notes": ""},
        {"base_name": "Cable Abduction", "name": "Lying Cable Outer Leg Raise", "muscles": ["Abductors"], "equipment": ["Cable"], "notes": ""},

        # Compound – Squat
        {"base_name": "Squat", "name": "Barbell Back Squat", "muscles": ["Glutes", "Hamstrings", "Quads"], "equipment": ["Barbell"], "notes": ""},
        {"base_name": "Squat", "name": "Barbell Front Squat", "muscles": ["Glutes", "Hamstrings", "Quads"], "equipment": ["Barbell"], "notes": ""},
        {"base_name": "Squat", "name": "Dumbbell Squat", "muscles": ["Glutes", "Hamstrings", "Quads"], "equipment": ["Dumbbell"], "notes": ""},
        {"base_name": "Squat", "name": "Goblet Squat", "muscles": ["Glutes", "Hamstrings", "Quads"], "equipment": ["Dumbbell"], "notes": ""},
        {"base_name": "Squat", "name": "Smith Machine Squat", "muscles": ["Glutes", "Hamstrings", "Quads"], "equipment": ["Smith"], "notes": ""},
        {"base_name": "Squat", "name": "Zercher Squat", "muscles": ["Glutes", "Hamstrings", "Quads"], "equipment": ["Barbell"], "notes": ""},
        {"base_name": "Squat", "name": "Hack Squat", "muscles": ["Glutes", "Hamstrings", "Quads"], "equipment": ["Machine"], "notes": ""},
        {"base_name": "Squat", "name": "Trap Bar Squat", "muscles": ["Glutes", "Hamstrings", "Quads"], "equipment": ["Barbell"], "notes": ""},

        # Compound – Lunge
        {"base_name": "Lunge", "name": "Bodyweight Lunge", "muscles": ["Glutes", "Hamstrings", "Quads"], "equipment": ["Bodyweight"], "notes": ""},
        {"base_name": "Lunge", "name": "Dumbbell Lunge", "muscles": ["Glutes", "Hamstrings", "Quads"], "equipment": ["Dumbbell"], "notes": ""},
        {"base_name": "Lunge", "name": "Barbell Lunge", "muscles": ["Glutes", "Hamstrings", "Quads"], "equipment": ["Barbell"], "notes": ""},
        {"base_name": "Lunge", "name": "Dumbbell Bulgarian Split Squat", "muscles": ["Glutes", "Hamstrings", "Quads"], "equipment": ["Dumbbell", "Bench"], "notes": ""},
        {"base_name": "Lunge", "name": "Barbell Bulgarian Split Squat", "muscles": ["Glutes", "Hamstrings", "Quads"], "equipment": ["Barbell", "Bench"], "notes": ""},
        {"base_name": "Lunge", "name": "Smith Machine Bulgarian Split Squat", "muscles": ["Glutes", "Hamstrings", "Quads"], "equipment": ["Smith", "Bench"], "notes": ""},
        {"base_name": "Lunge", "name": "Smith Machine Lunge", "muscles": ["Glutes", "Hamstrings", "Quads"], "equipment": ["Smith"], "notes": ""},

        # Compound – Leg Press
        {"base_name": "Leg Press", "name": "PinLoaded Leg Press", "muscles": ["Glutes", "Hamstrings", "Quads"], "equipment": ["Machine"], "notes": ""},
        {"base_name": "Leg Press", "name": "PlateLoaded Leg Press", "muscles": ["Glutes", "Hamstrings", "Quads"], "equipment": ["Machine"], "notes": ""},

    ]
    created_base_exercises = {}
    
    for exercise in exercises:
        base_name = exercise['base_name']
        muscle_names = exercise['muscles']
        
        # Create or get BaseExercise
        if base_name not in created_base_exercises:
            base_exercise, created = BaseExercise.objects.get_or_create(name=base_name)
            # Set muscle groups for the base exercise
            base_exercise.muscle_group.set([muscle_objs[m] for m in muscle_names])
            base_exercise.save()
            created_base_exercises[base_name] = base_exercise
        else:
            base_exercise = created_base_exercises[base_name]
        
        # Create Exercise object (specific implementation with equipment)
        exercise_obj, created = Exercise.objects.get_or_create(
            base_exercise=base_exercise,
            name=exercise['name'],
            defaults={
                'notes': exercise['notes']
            }
        )
        
        # Set muscle groups and equipment for the specific exercise
        exercise_obj.muscle_group.set([muscle_objs[m] for m in muscle_names])
        exercise_obj.equipment.set([equipment_objs[e] for e in exercise['equipment']])
        exercise_obj.save()
    
    print(f"Created {len(created_base_exercises)} base exercises and {len(exercises)} specific exercises successfully!")

@transaction.atomic
def clear_data():
    from .models import BaseMuscle, Muscle, Equipment, BaseExercise
    BaseMuscle.objects.all().delete()
    Muscle.objects.all().delete()
    Equipment.objects.all().delete()
    BaseExercise.objects.all().delete()
    print("All data deleted")