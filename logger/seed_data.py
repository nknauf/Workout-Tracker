from logger.models import MuscleGroup, Equipment, Exercise, MovementType, BaseExercise
from django.db import transaction

@transaction.atomic
def run():
    # Major muscle groups and children
    structure = {
        "Biceps": [],
        "Triceps": [],
        "Chest": ["Upper Chest", "Middle Chest", "Lower Chest"],
        "Back": ["Upper Back", "Lats", "Lower Back"],
        "Shoulders": ["Front Delt", "Side Delt", "Rear Delt"],
        "Legs": ["Quads", "Hamstrings", "Glutes", "Adductors", "Calves"],
        "Core": [],
        "Forearms": []
    }

    muscle_group_objs = {}
    for parent_name, children in structure.items():
        parent = MuscleGroup.objects.create(name=parent_name)
        muscle_group_objs[parent_name] = parent
        for child in children:
            subgroup = MuscleGroup.objects.create(name=child, parent=parent)
            muscle_group_objs[child] = subgroup

    
    equipment_list = ["Barbell", "Smith", "Machine", "Cable", "Dumbbell", "Bodyweight", "Bench", "EZ Bar"]
    equipment_objs = {name: Equipment.objects.create(name=name) for name in equipment_list}


    movement_types_list = ["push", "pull", "compound", "isolation"]
    movement_type_objs = {name: MovementType.objects.create(name=name) for name in movement_types_list}



    # Single arm low to high cable fly
    # Incline push ups 

    # Define exercises (add movement_type)
    exercises = [
        # Chest
        # Incline Barbell Bench Press
        {"base": "Incline Barbell Bench Press" ,"name": "Incline Barbell Bench Press", "description": "Incline Barbell Bench Press", "muscle": ["Chest", "Upper Chest"], "equipment": ["Barbell", "Bench"], "movement_type" : ["compound", "push"]},
        {"base": "Incline Barbell Bench Press" ,"name": "Wide Grip Incline Barbell Bench Press", "description": "Wide Grip Incline Barbell Bench Press", "muscle": ["Chest", "Upper Chest"], "equipment": ["Barbell", "Bench"], "movement_type" : ["compound", "push"], "grip_type": "wide grip", "form_note": "Focuses more outside chest muscles"},
        {"base": "Incline Barbell Bench Press" ,"name": "Close Grip Incline Barbell Bench Press", "description": "Close Grip Incline Barbell Bench Press", "muscle": ["Chest", "Upper Chest", "Triceps"], "equipment": ["Barbell", "Bench"], "movement_type": ["compound", "push"], "grip_type": "close grip", "form_note": "Implements triceps among the upper chest"},
        # Incline Smith Bench Press
        {"base": "Incline Smith Bench Press" ,"name": "Incline Smith Bench Press", "description": "Incline Smith Bench Press", "muscle": ["Chest", "Upper Chest"], "equipment": ["Smith", "Bench"], "movement_type": ["isolation", "push"]},
        {"base": "Incline Smith Bench Press" ,"name": "Wide Grip Incline Smith Bench Press", "description": " Wide Grip Incline Smith Bench Press", "muscle": ["Chest", "Upper Chest"], "equipment": ["Smith", "Bench"], "movement_type": ["isolation", "push"], "grip_type": "wide grip", "form_note": "Focuses mroe outside chest muscles"},
        {"base": "Incline Smith Bench Press" ,"name": "Close Grip Incline Smith Bench Press", "description": "Close Grip Incline Smith Bench Press", "muscle": ["Chest", "Upper Chest", "Triceps"], "equipment": ["Smith", "Bench"], "movement_type": ["isolation", "push"], "grip_type": "close grip", "form_note": "Implements triceps among the upper chest"},
        # Incline Dumbbell Bench Press
        {"base": "Incline Dumbbell Bench Press" ,"name": "Incline Dumbbell Bench Press", "description": "Incline Dumbbell Bench Press", "muscle": ["Chest", "Upper Chest"], "equipment": ["Dumbbell", "Bench"], "movement_type": ["compound", "push"]},
        # Incline plate-loaded press
        {"base": "Incline Plate Loaded Bench Press" ,"name": "Incline Plate Loaded Bench Press", "description": "Incline Plate Loaded Bench Press", "muscle": ["Chest", "Upper Chest"], "equipment": ["Machine"], "movement_type": ["isolation", "push"]},
        # Low to High Cable Flys
        {"base": "Low to High Cable Flys" ,"name": "Low to High Cable Flys", "description": "Low to High Cable Flys", "muscle": ["Chest", "Upper Chest"], "equipment": ["Cable"], "movement_type": ["compound", "push"]},
        {"base": "Low to High Cable Flys" ,"name": "Single Arm Low to High Cable Flys", "description": "Single Arm Low to High Cable Flys", "muscle": ["Chest", "Upper Chest"], "equipment": ["Cable"], "movement_type": ["compound", "push"], "is_single_arm": True},
        # low to high incline cable chest press
        {"base": "Low to High Cable Chest Press", "name": "Low to High Cable Chest Press", "description": "Low to High Cable Chest Press", "muscle": ["Chest", "Upper Chest"], "equipment": ["Bench", "Cable"], "movement_type": ["isolation", "push"]},
        {"base": "Low to High Cable Chest Press", "name": "Single Arm Low to High Cable Chest Press", "description": "Low to High Cable Chest Press", "muscle": ["Chest", "Upper Chest"], "equipment": ["Bench", "Cable"], "is_single_arm": True},
        # regular push ups and decline push ups
        {"base": "Pushup", "name":"Pushup","description": "Pushup", "muscle": ["Chest"], "equipment": ["Bodyweight"]},
        {"base": "Pushup", "name":"Decline Pushup","description": "Decline Pushup", "muscle": ["Chest", "Upper Chest"], "equipment": ["Bodyweight"], "form_note": "Elevated feet gets more weight and upper chest involved"},
        # barbell bench press
        {"base": "Barbell Bench Press", "name": "Barbell Bench Press", "description":"Barbell Bench Press", "muscle": ["Chest", "Middle Chest"], "equipment": ["Bench", "Barbell"], "movement_type": ["compound", "push"]},
        {"base": "Barbell Bench Press", "name": "Wide Grip Barbell Bench Press", "description":"Wide Grip Barbell Bench Press", "muscle": ["Chest", "Middle Chest"], "equipment": ["Bench", "Barbell"], "movement_type": ["compound", "push"], "grip_type": "wide grip", "form_note": "Wide grip targets outer chest muscles"},
        # smith bench press
        {"base": "Smith Bench Press", "name": "Smith Bench Press", "description": "Smith Bench Press", "muscle": ["Chest", "Middle Chest"], "equipment": ["Bench", "Smith"], "movement_type": ["isolation", "push"]},
        {"base": "Smith Bench Press", "name": "Wide Grip Smith Bench Press", "description":"Wide Grip Smith Bench Press", "muscle": ["Chest", "Middle Chest"], "equipment": ["Bench", "Smith"], "movement_type": ["isolation", "push"], "grip_type": "wide grip", "form_note": "Wide grip targets outer chest muscles"},
        # machine chest press
        {"base": "Machine Chest Press", "name": "Machine Chest Press", "description": "Machine Chest Press", "muscle":["Chest", "Middle Chest"], "equipment": ["Machine"], "movement_type": ["isolation", "push"]},
        # flat machine plate loaded chest press
        {"base": "Machine Chest Press", "name": "Flat Bench Plate Loaded Chest Press", "description": "Flat Bench Plate Loaded Chest Press", "muscle": ["Chest", "Middle Chest"], "equipment": ["Machine"], "movement_type": ["isolation", "push"]},
        # incline plate loaded chest press
        {"base": "Machine Chest Press", "name": "Incline Plate Loaded Chest Press", "description": "Incline Plate Loaded Chest Press", "description": "Incline Plate Loaded Chest Press", "muscle": ["Chest", "Upper Chest"], "equipment": ["Machine"], "movement_type": ["isolation", "push"]},
        # pec dec
        {"base": "Pec Dec Fly", "name": "Pec Dec Fly", "description": "Pec Dec Fly", "muscle": ["Chest", "Middle Chest"], "equipment": ["Machine"], "movement_type": ["isolation", "push"]},
        # decline barbell bench press
        {"base": "Decline Barbell Bench Press", "name": "Decline Barbell Bench Press", "description": "Decline Barbell Bench Press", "muscle": ["Chest", "Lower Chest"], "equipment": ["Barbell", "Bench"], "movement_type": ["compound", "push"]},
        {"base": "Decline Barbell Bench Press", "name": "Wide Grip Decline Barbell Bench Press", "description": "Wide Grip Decline Barbell Bench Press", "muscle": ["Chest", "Lower Chest"], "equipment": ["Barbell", "Bench"], "movement_type": ["compound", "push"], "grip_type": "wide grip", "form_note": "Wide grip targets outer chest muscles"},
        # decline smith bench press
        {"base": "Decline Smith Bench Press", "name": "Decline Smith Bench Press", "description": "Decline Smith Bench Press", "muscle": ["Chest", "Lower Chest"], "equipment": ["Smith", "Bench"], "movement_type": ["isolation", "push"]},
        {"base": "Decline Smith Bench Press", "name": "Wide Grip Decline Smith Bench Press", "description": "Wide Grip Decline Smith Bench Press", "muscle": ["Chest", "Lower Chest"], "equipment": ["Smith", "Bench"], "movement_type": ["isolation", "push"], "grip_type": "wide grip", "form_note": "Wide grip targets outer chest muscles"},
        # decline machine chest press
        {"base": "Decline Machine Chest Press", "name": "Decline Machine Chest Press", "description": "Decline Machine Chest Press", "muscle": ["Chest", "Lower Chest"], "equipment": ["Machine"], "movement_type": ["isolation", "push"]},

        # Back
        # lat pulldowns and variations
        {"base": "Lat Pulldown", "name": "Lat Pulldown", "description": "Lat Pulldown", "muscle": ["Back", "Lats"], "equipment": ["Cable"], "movement_type": ["isolation", "pull"]},
        {"base": "Lat Pulldown", "name": "Wide Grip Lat Pulldown", "description": "Wide Grip Lat Pulldown", "muscle": ["Back", "Lats"], "equipment": ["Cable"], "movement_type": ["isolation", "pull"], "grip_type": "wide grip", "form_note": "Wide grip targets outer back muscles"},
        {"base": "Lat Pulldown", "name": "Neutral Grip Lat Pulldown", "description": "Neutral Grip Lat Pulldown", "muscle": ["Back", "Lats"], "equipment": ["Cable"], "movement_type": ["isolation", "pull"], "grip_type": "neutral grip", "form_note": "Neutral grip targets inner back muscles"},
        {"base": "Lat Pulldown", "name": "Single Arm Lat Pulldown", "description": "Single Arm Lat Pulldown", "muscle": ["Back", "Lats"], "equipment": ["Cable"], "movement_type": ["isolation", "pull"], "is_single_arm": True},
        # lat pullovers and single arm
        {"base": "Lat Pullover", "name": "Lat Pullover", "description": "Lat Pullover", "muscle": ["Back", "Lats"], "equipment": ["Cable"], "movement_type": ["isolation", "pull"]},
        {"base": "Lat Pullover", "name": "Single Arm Cable Lat Pullover", "description": "Single Arm Cable Lat Pullover", "muscle": ["Back", "Lats"], "equipment": ["Cable"], "movement_type": ["isolation", "pull"], "is_single_arm": True},
        {"base": "Lat Pullover", "name": "Machine Lat Pullover", "description": "Machine Lat Pullover", "muscle": ["Back", "Lats"], "equipment": ["Machine"], "movement_type": ["isolation", "pull"]},
        {"base": "Lat Pullover", "name": "Single Arm Machine Lat Pullover", "description": "Single Arm Machine Lat Pullover", "muscle": ["Back", "Lats"], "equipment": ["Machine"], "movement_type": ["isolation", "pull"], "is_single_arm": True},
        # pull ups and variations
        {"base": "Pullup", "name": "Pullup", "description": "Pullup", "muscle": ["Back", "Lats", "Upper Back", "Biceps"], "equipment": ["Bodyweight"], "movement_type": ["compound", "pull"]},
        {"base": "Pullup", "name": "Wide Grip Pullup", "description": "Wide Grip Pullup", "muscle": ["Back", "Lats", "Upper Back", "Biceps"], "equipment": ["Bodyweight"], "movement_type": ["compound", "pull"], "grip_type": "wide grip", "form_note": "Wide grip targets outer back muscles"},
        {"base": "Pullup", "name": "Chinup", "description": "Chinup", "muscle": ["Back", "Lats", "Upper Back", "Biceps"], "equipment": ["Bodyweight"], "movement_type": ["compound", "pull"], "grip_type": "underhand grip", "form_note": "Underhand grip targets inner back muscles"},
        {"base": "Pullup", "name": "Neutral Grip Pullup", "description": "Neutral Grip Pullup", "muscle": ["Back", "Lats", "Upper Back", "Biceps"], "equipment": ["Bodyweight"], "movement_type": ["compound", "pull"], "grip_type": "neutral grip", "form_note": "Neutral grip targets inner back muscles"},
        # barbell bent over rows
        {"base": "Barbell Bent Over Row", "name": "Barbell Bent Over Row", "description": "Barbell Bent Over Row", "muscle": ["Back", "Upper Back", "Lats", "Lower Back"], "equipment": ["Barbell"], "movement_type": ["compound", "pull"]},
        {"base": "Barbell Bent Over Row", "name": "Wide Grip Barbell Bent Over Row", "description": "Wide Grip Barbell Bent Over Row", "muscle": ["Back", "Upper Back", "Lats", "Lower Back"], "equipment": ["Barbell"], "movement_type": ["compound", "pull"], "grip_type": "wide grip", "form_note": "Wide grip targets outer back muscles"},
        # smith bent over rows
        {"base": "Smith Bent Over Row", "name": "Smith Bent Over Row", "description": "Smith Bent Over Row", "muscle": ["Back", "Lats", "Upper Back", "Lower Back"], "equipment": ["Smith"], "movement_type": ["isolation", "pull"]},
        {"base": "Smith Bent Over Row", "name": "Wide Grip Smith Bent Over Row", "description": "Wide Grip Smith Bent Over Row", "muscle": ["Back", "Lats", "Upper Back", "Lower Back"], "equipment": ["Smith"], "movement_type": ["isolation", "pull"], "grip_type": "wide grip", "form_note": "Wide grip targets outer back muscles"},
        # t bar rows
        {"base": "T Bar Row", "name": "T Bar Row", "description": "T Bar Row", "muscle": ["Back", "Lats", "Upper Back"], "equipment": ["Barbell", "Machine"], "movement_type": ["isolation", "pull"]},
        # machine rows
        {"base": "Machine Row", "name": "Machine Row", "description": "Machine Row", "muscle": ["Back", "Upper Back", "Lats"], "equipment": ["Machine"], "movement_type": ["isolation", "pull"]},
        {"base": "Machine Row", "name": "Single Arm Machine Row", "description": "Single Arm Machine Row", "muscle": ["Back", "Lats"], "equipment": ["Machine"], "movement_type": ["isolation", "pull"], "is_single_arm": True},
        # cable rows
        {"base": "Cable Row", "name": "Cable Row", "description": "Cable Row", "muscle": ["Back", "Lats", "Upper Back", "Lower Back"], "equipment": ["Cable"], "movement_type": ["isolation", "pull"]},
        {"base": "Cable Row", "name": "Single Arm Cable Row", "description": "Single Arm Cable Row", "muscle": ["Back", "Lats", "Upper Back", "Lower Back"], "equipment": ["Cable"], "movement_type": ["isolation", "pull"], "is_single_arm": True},
        {"base": "Cable Row", "name": "Flat Bar Cable Row", "description": "Flat Bar Cable Row", "muscle": ["Back", "Upper Back", "Lats"], "equipment": ["Cable"], "movement_type": ["isolation", "pull"]},
        {"base": "Close Grip Cable Row", "name": "Close Grip Cable Row", "description": "Close Grip Cable Row", "muscle": ["Back", "Lower Back", "Lats"], "equipment": ["Cable"], "movement_type": ["isolation", "pull"], "grip_type": "close grip", "form_note": "Close grip targets inner and lower back muscles"},
        # chest supported dumbbell rows
        {"base": "Chest Supported Dumbbell Row", "name": "Chest Supported Dumbbell Row", "description": "Chest Supported Dumbbell Row", "muscle": ["Back", "Lats", "Upper Back"], "equipment": ["Dumbbell", "Bench"], "movement_type": ["isolation", "pull"]},
        # single arm dumbbell row
        {"base": "Single Arm Dumbbell Row", "name": "Single Arm Dumbbell Row", "description": "Single Arm Dumbbell Row", "muscle": ["Back", "Lats", "Upper Back", "Lower Back"], "equipment": ["Dumbbell", "Bench"], "movement_type": ["isolation", "pull"], "is_single_arm": True},
        

        # Shoulders
        # Dumbbell Shoulder Press
        {"base": "Dumbbell Shoulder Press", "name": "Dumbbell Shoulder Press", "description": "Dumbbell Shoulder Press", "muscle": ["Shoulders", "Front Delt", "Side Delt"], "equipment": ["Dumbbell", "Bench"], "movement_type": ["isolation", "push"]},
        # Machine Shoulder Press
        {"base": "Machine Shoulder Press", "name": "Machine Shoulder Press", "description": "Machine Shoulder Press", "muscle": ["Shoulders", "Front Delt", "Side Delt"], "equipment": ["Machine"], "movement_type": ["isolation", "push"]},
        # Smith Shoulder Press
        {"base": "Smith Shoulder Press", "name": "Smith Shoulder Press", "description": "Smith Shoulder Press", "muscle": ["Shoulders", "Front Delt", "Side Delt"], "equipment": ["Smith"], "movement_type": ["isolation", "push"]},
        # Barbell Shoulder Press
        {"base": "Barbell Shoulder Press", "name": "Barbell Shoulder Press", "description": "Barbell Shoulder Press", "muscle": ["Shoulders", "Front Delt", "Side Delt"], "equipment": ["Barbell"], "movement_type": ["isolation", "push"]},
        # Front Delt Dumbbell Raise
        {"base": "Front Delt Dumbbell Raise", "name": "Front Delt Dumbbell Raise", "description": "Front Delt Dumbbell Raise", "muscle": ["Shoulders", "Front Delt"], "equipment": ["Dumbbell"], "movement_type": ["isolation", "push"]},
        # Front Delt Cable Raise
        {"base": "Front Delt Cable Raise", "name": "Front Delt Cable Raise", "description": "Front Delt Cable Raise", "muscle": ["Shoulders", "Front Delt"], "equipment": ["Cable"], "movement_type": ["isolation", "push"]},
        # Dumbbell Lateral Raise
        {"base": "Dumbbell Lateral Raise", "name": "Dumbbell Lateral Raise", "description": "Dumbbell Lateral Raise", "muscle": ["Shoulders", "Front Delt", "Side Delt"], "equipment": ["Dumbbell"], "movement_type": ["isolation", "push"]},
        # Cable Lateral Raise
        {"base": "Cable Lateral Raise", "name": "Cable Lateral Raise", "description": "Cable Lateral Raise", "muscle": ["Shoulders", "Front Delt", "Side Delt"], "equipment": ["Cable"], "movement_type": ["isolation", "push"]},
        # Machine Lateral Raise
        {"base": "Machine Lateral Raise", "name": "Machine Lateral Raise", "description": "Machine Lateral Raise", "muscle": ["Shoulders", "Front Delt", "Side Delt"], "equipment": ["Machine"], "movement_type": ["isolation", "push"]},
        # Single Arm Cable Lateral Raise
        {"base": "Single Arm Cable Lateral Raise", "name": "Single Arm Cable Lateral Raise", "description": "Single Arm Cable Lateral Raise", "muscle": ["Shoulders", "Front Delt", "Side Delt"], "equipment": ["Cable"], "movement_type": ["isolation", "push"], "is_single_arm": True},
        # Rear Delt Dumbbell Fly
        {"base": "Rear Delt Dumbbell Fly", "name": "Rear Delt Dumbbell Fly", "description": "Rear Delt Dumbbell Fly", "muscle": ["Shoulders", "Rear Delt"], "equipment": ["Dumbbell"], "movement_type": ["isolation", "push"]},
        # Rear Delt Cable Fly
        {"base": "Rear Delt Cable Fly", "name": "Rear Delt Cable Fly", "description": "Rear Delt Cable Fly", "muscle": ["Shoulders", "Rear Delt"], "equipment": ["Cable"], "movement_type": ["isolation", "push"]},
        # Single Arm Rear Delt Cable Fly
        {"base": "Single Arm Rear Delt Cable Fly", "name": "Single Arm Rear Delt Cable Fly", "description": "Single Arm Rear Delt Cable Fly", "muscle": ["Shoulders", "Rear Delt"], "equipment": ["Cable"], "movement_type": ["isolation", "push"], "is_single_arm": True},
        # Machine Rear Delt Fly
        {"base": "Machine Rear Delt Fly", "name": "Machine Rear Delt Fly", "description": "Machine Rear Delt Fly", "muscle": ["Shoulders", "Rear Delt"], "equipment": ["Machine"], "movement_type": ["isolation", "push"]},
        # Cable Face Pulls
        {"base": "Cable Face Pull", "name": "Cable Face Pull", "description": "Cable Face Pull", "muscle": ["Shoulders", "Rear Delt"], "equipment": ["Cable"], "movement_type": ["isolation", "push"]},
        # Dumbbell Shrugs
        {"base": "Dumbbell Shrug", "name": "Dumbbell Shrug", "description": "Dumbbell Shrug", "muscle": ["Shoulders", "Upper Back"], "equipment": ["Dumbbell"], "movement_type": ["isolation", "push"]},
        # EZ Bar Rear Delt Raises
        {"base": "EZ Bar Rear Delt Raise", "name": "EZ Bar Rear Delt Raise", "description": "EZ Bar Rear Delt Raise", "muscle": ["Shoulders", "Rear Delt"], "equipment": ["EZ Bar"], "movement_type": ["isolation", "push"]},

        # Triceps
        # Dips
        {"base": "Dip", "name": "Dip", "description": "Dip", "muscle": ["Triceps"], "equipment": ["Bodyweight"], "movement_type": ["compound", "push"]},
        {"base": "Dip", "name": "Weighted Dip", "description": "Weighted Dip", "muscle": ["Triceps"], "equipment": ["Bodyweight"], "movement_type": ["compound", "push"], "form_note": "Weighted dip with a belt"},
        {"base": "Dip", "name": "Machine Dip", "description": "Machine Dip", "muscle": ["Triceps"], "equipment": ["Machine"], "movement_type": ["isolation", "push"]},
        # Skull Crushers
        {"base": "Skull Crusher", "name": "Skull Crusher", "description": "Skull Crusher", "muscle": ["Triceps"], "equipment": ["EZ Bar"], "movement_type": ["isolation", "push"]},
        # Cable Tricep Extensions
        {"base": "Cable Tricep Extension", "name": "Cable Tricep Extension", "description": "Cable Tricep Extension", "muscle": ["Triceps"], "equipment": ["Cable"], "movement_type": ["isolation", "push"]},
        {"base": "Cable Tricep Extension", "name": "Single Arm Cable Tricep Extension", "description": "Single Arm Cable Tricep Extension", "muscle": ["Triceps"], "equipment": ["Cable"], "movement_type": ["isolation", "push"], "is_single_arm": True},
        # Cable Tricep Pushdowns
        {"base": "Cable Tricep Pushdown", "name": "Cable Tricep Pushdown", "description": "Tricep Pushdown", "muscle": ["Triceps"], "equipment": ["Cable"], "movement_type": ["isolation", "push"]},
        {"base": "Cable Tricep Pushdown", "name": "Single Arm Cable Tricep Pushdown", "description": "Single Arm Tricep Pushdown", "muscle": ["Triceps"], "equipment": ["Cable"], "movement_type": ["isolation", "push"], "is_single_arm": True},
        # Cable Tricep Kickbacks
        {"base": "Cable Tricep Kickback", "name": "Cable Tricep Kickback", "description": "Tricep Kickback", "muscle": ["Triceps"], "equipment": ["Cable"], "movement_type": ["isolation", "push"]},
        {"base": " Cable Tricep Kickback", "name": "Single Arm Cable Tricep Kickback", "description": "Single Arm Tricep Kickback", "muscle": ["Triceps"], "equipment": ["Cable"], "movement_type": ["isolation", "push"], "is_single_arm": True},
        # Dumbbell Tricep Kickbacks
        {"base": "Dumbbell Tricep Kickback", "name": "Dumbbell Tricep Kickback", "description": "Tricep Kickback", "muscle": ["Triceps"], "equipment": ["Dumbbell"], "movement_type": ["isolation", "push"]},
        {"base": "Dumbbell Tricep Kickback", "name": "Single Arm Dumbbell Tricep Kickback", "description": "Single Arm Tricep Kickback", "muscle": ["Triceps"], "equipment": ["Dumbbell"], "movement_type": ["isolation", "push"], "is_single_arm": True},
        # Cable Overhead Tricep Extensions
        {"base": "Cable Overhead Tricep Extension", "name": "Cable Overhead Tricep Extension", "description": "Cable Overhead Tricep Extension", "muscle": ["Triceps"], "equipment": ["Cable"], "movement_type": ["isolation", "push"]},
        {"base": "Cable Overhead Tricep Extension", "name": "Single Arm Cable Overhead Tricep Extension", "description": "Single Arm Cable Overhead Tricep Extension", "muscle": ["Triceps"], "equipment": ["Cable"], "movement_type": ["isolation", "push"], "is_single_arm": True},
        # Single Arm Dumbbell Overhead Tricep Extensions
        {"base": "Single Arm Dumbbell Overhead Tricep Extension", "name": "Single Arm Dumbbell Overhead Tricep Extension", "description": "Single Arm Dumbbell Overhead Tricep Extension", "muscle": ["Triceps"], "equipment": ["Dumbbell"], "movement_type": ["isolation", "push"], "is_single_arm": True},

        # Biceps
        # Dumbbell Bicep Curl and Incline Bicep Curl
        {"base": "Dumbbell Bicep Curl", "name": "Dumbbell Bicep Curl", "description": "Dumbbell Bicep Curl", "muscle": ["Biceps"], "equipment": ["Dumbbell"], "movement_type": ["isolation", "pull"]},
        {"base": "Dumbbell Bicep Curl", "name": "Incline Dumbbell Bicep Curl", "description": "Incline Dumbbell Bicep Curl", "muscle": ["Biceps"], "equipment": ["Dumbbell", "Bench"], "movement_type": ["isolation", "pull"]},
        # Cable Bicep Curl
        {"base": "Cable Bicep Curl", "name": "Cable Bicep Curl", "description": "Cable Bicep Curl", "muscle": ["Biceps"], "equipment": ["Cable"], "movement_type": ["isolation", "pull"]},
        {"base": "Cable Bicep Curl", "name": "Single Arm Cable Bicep Curl", "description": "Single Arm Cable Bicep Curl", "muscle": ["Biceps"], "equipment": ["Cable"], "movement_type": ["isolation", "pull"], "is_single_arm": True},
        # Machine Bicep Curl and Preacher Curl
        {"base": "Machine Bicep Curl", "name": "Machine Bicep Curl", "description": "Machine Bicep Curl", "muscle": ["Biceps"], "equipment": ["Machine"], "movement_type": ["isolation", "pull"]},
        {"base": "Machine Bicep Curl", "name": "Machine Preacher Curl", "description": "Machine Preacher Curl", "muscle": ["Biceps"], "equipment": ["Machine"], "movement_type": ["isolation", "pull"]},
        # EZ Bar Bicep Curl and EZ Bar Preacher Curl
        {"base": "EZ Bar Bicep Curl", "name": "EZ Bar Bicep Curl", "description": "EZ Bar Bicep Curl", "muscle": ["Biceps"], "equipment": ["EZ Bar"], "movement_type": ["isolation", "pull"]},
        {"base": "EZ Bar Bicep Curl", "name": "EZ Bar Preacher Curl", "description": "EZ Bar Preacher Curl", "muscle": ["Biceps"], "equipment": ["EZ Bar", "Bench"], "movement_type": ["isolation", "pull"]},
        # Hammer Curls
        {"base": "Hammer Curl", "name": "Hammer Curl", "description": "Hammer Curl", "muscle": ["Biceps"], "equipment": ["Dumbbell"], "movement_type": ["isolation", "pull"]},
        {"base": "Hammer Curl", "name": "Incline Hammer Curl", "description": "Incline Hammer Curl", "muscle": ["Biceps"], "equipment": ["Dumbbell", "Bench"], "movement_type": ["isolation", "pull"]},
        # Concentration Curls
        {"base": "Concentration Curl", "name": "Concentration Curl", "description": "Concentration Curl", "muscle": ["Biceps"], "equipment": ["Dumbbell", "Bench"], "movement_type": ["isolation", "pull"]},
        {"base": "Concentration Curl", "name": "Single Arm Concentration Curl", "description": "Single Arm Concentration Curl", "muscle": ["Biceps"], "equipment": ["Dumbbell", "Bench"], "movement_type": ["isolation", "pull"], "is_single_arm": True},
        
        # Legs
        # Barbell Squats
        {"base": "Barbell Squat", "name": "Barbell Squat", "description": "Barbell Squat", "muscle": ["Legs", "Quads", "Glutes", "Hamstrings"], "equipment": ["Barbell"], "movement_type": ["compound", "push"]},
        # Smith Squats
        {"base": "Smith Squat", "name": "Smith Squat", "description": "Smith Squat", "muscle": ["Legs", "Quads", "Glutes", "Hamstrings"], "equipment": ["Smith"], "movement_type": ["isolation", "push"]},
        # Hack Squats
        {"base": "Hack Squat", "name": "Hack Squat", "description": "Hack Squat", "muscle": ["Legs", "Quads", "Glutes", "Hamstrings"], "equipment": ["Machine"], "movement_type": ["isolation", "push"]},
        # Pendulum Squats
        {"base": "Pendulum Squat", "name": "Pendulum Squat", "description": "Pendulum Squat", "muscle": ["Legs", "Quads", "Glutes", "Hamstrings"], "equipment": ["Machine"], "movement_type": ["isolation", "push"]},
        # Leg Press
        {"base": "Leg Press", "name": "Leg Press", "description": "Leg Press", "muscle": ["Legs", "Quads", "Glutes", "Hamstrings"], "equipment": ["Machine"], "movement_type": ["isolation", "push"]},
        {"base": "Leg Press", "name": "Single Leg Press", "description": "Single Leg Press", "muscle": ["Legs", "Quads", "Glutes", "Hamstrings"], "equipment": ["Machine"], "movement_type": ["isolation", "push"], "is_single_arm": True},
        # Barbell RDLs
        {"base": "Barbell RDL", "name": "Barbell RDL", "description": "Barbell RDL", "muscle": ["Legs", "Glutes", "Hamstrings"], "equipment": ["Barbell"], "movement_type": ["compound", "pull"]},
        # Smith RDLs
        {"base": "Smith RDL", "name": "Smith RDL", "description": "Smith RDL", "muscle": ["Legs", "Glutes", "Hamstrings"], "equipment": ["Smith"], "movement_type": ["isolation", "pull"]},
        # Dumbbell RDLs
        {"base": "Dumbbell RDL", "name": "Dumbbell RDL", "description": "Dumbbell RDL", "muscle": ["Legs", "Glutes", "Hamstrings"], "equipment": ["Dumbbell"], "movement_type": ["isolation", "pull"]},
        # Machine RDLs
        {"base": "Machine RDL", "name": "Machine RDL", "description": "Machine RDL", "muscle": ["Legs", "Glutes", "Hamstrings"], "equipment": ["Machine"], "movement_type": ["isolation", "pull"]},
        # Leg Curls
        {"base": "Leg Curl", "name": "Leg Curl", "description": "Leg Curl", "muscle": ["Legs", "Hamstrings"], "equipment": ["Machine"], "movement_type": ["isolation", "pull"]},
        {"base": "Leg Curl", "name": "Single Leg Curl", "description": "Single Leg Curl", "muscle": ["Legs", "Hamstrings"], "equipment": ["Machine"], "movement_type": ["isolation", "pull"], "is_single_arm": True},
        # Leg Extensions
        {"base": "Leg Extension", "name": "Leg Extension", "description": "Leg Extension", "muscle": ["Legs", "Quads"], "equipment": ["Machine"], "movement_type": ["isolation", "push"]},
        {"base": "Leg Extension", "name": "Single Leg Extension", "description": "Single Leg Extension", "muscle": ["Legs", "Quads"], "equipment": ["Machine"], "movement_type": ["isolation", "push"], "is_single_arm": True},
        # Calf Raises
        {"base": "Calf Raise", "name": "Calf Raise", "description": "Calf Raise", "muscle": ["Legs", "Calves"], "equipment": ["Machine"], "movement_type": ["isolation", "push"]},
        # Bulgarian Split Squats
        {"base": "Bulgarian Split Squat", "name": "Bulgarian Split Squat", "description": "Single Leg Bulgarian Split Squat", "muscle": ["Legs", "Quads", "Glutes"], "equipment": ["Dumbbell", "Bench"], "movement_type": ["isolation", "push"], "is_single_arm": True},
        # Sissy Squats and Hack Squat Sissy Squats
        {"base": "Sissy Squat", "name": "Sissy Squat", "description": "Sissy Squat", "muscle": ["Legs", "Quads"], "equipment": ["Bodyweight"], "movement_type": ["isolation", "push"]},
        {"base": "Sissy Squat", "name": "Hack Squat Sissy Squat", "description": "Hack Squat Sissy Squat", "muscle": ["Legs", "Quads"], "equipment": ["Machine"], "movement_type": ["isolation", "push"]},
        # Leg Abductions
        {"base": "Leg Abduction", "name": "Leg Abduction", "description": "Leg Abduction", "muscle": ["Legs", "Glutes"], "equipment": ["Machine"], "movement_type": ["isolation", "push"]},
        # Leg Adductions
        {"base": "Leg Adduction", "name": "Leg Adduction", "description": "Leg Adduction", "muscle": ["Legs", "Adductors"], "equipment": ["Machine"], "movement_type": ["isolation", "push"]},
    ]   

    base_exercise_objs = {}

    for ex in exercises:
        base_name = ex["base"]
        if base_name not in base_exercise_objs:
            base_exercise_objs[base_name] = BaseExercise.objects.create(name=base_name)

        equipment_names = ex["equipment"]
        if isinstance(equipment_names, str):
            equipment_names = [equipment_names]

        movement_type_names = ex.get("movement_type", [])
        if isinstance(movement_type_names, str):
            movement_type_names = [movement_type_names]

        muscle_group_names = ex["muscle"]
        if isinstance(muscle_group_names, str):
            muscle_group_names = [muscle_group_names]
            
        exercise = Exercise.objects.create(
            base = base_exercise_objs[base_name],
            name= ex["name"],
            description = ex["description"],
            is_single_arm = ex.get("is_single_arm", False),
            grip_type = ex.get("grip_type"),
            form_note = ex.get("form_note"),
        )
        exercise.equipment.set([equipment_objs[e] for e in equipment_names])
        exercise.muscle_group.set([muscle_group_objs[m] for m in muscle_group_names])
        exercise.movement_type.set([movement_type_objs[mt] for mt in movement_type_names])

    print("Seed data successfully inserted.")


@transaction.atomic
def clear_data():
    from .models import MuscleGroup, Equipment, Exercise, CalorieEntry, DailyLog, Workout, MovementType

    MuscleGroup.objects.all().delete()
    Equipment.objects.all().delete()
    Exercise.objects.all().delete()
    CalorieEntry.objects.all().delete()
    DailyLog.objects.all().delete()
    Workout.objects.all().delete()
    MovementType.objects.all().delete()

    print("All data deleted")
