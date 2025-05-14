from logger.models import MuscleGroup, Equipment
from django.db import transaction

@transaction.atomic
def run():
    # Major muscle groups and children
    structure = {
        "Chest": ["Upper", "Middle", "Lower"],
        "Back": ["Lats", "UpperBack", "LowerBack", "Traps"],
        "Shoulders": ["Front", "Side", "Rear"],
        "Legs": ["Quads", "Hamstrings", "Glutes", "Calves"],
        "Biceps": [],
        "Triceps": [],
        "Forearms": [],
        "Core": [],
    }

    for parent_name, children in structure.items():
        parent = MuscleGroup.objects.create(name=parent_name)
        for child in children:
            MuscleGroup.objects.create(name=child, parent=parent)

    equipment_structure = {
        "Barbell": ["Back Row", "Bench Press", "Incline Bench Press", "Military Press", "Squats", "Cleans", "RDLs"],
        "Smith": ["Incline Press", "Bench Press", "Back Row", "Squat", "Shoulder Press", "RDLs"],
        "Machine": ["Bicep Curls", "Tricep Extensions", "Leg Curls", "Leg Extensions"],
        "Cable": [],
        "Dumbbell": [],
        "Bodyweight": [],
    }

    for parent_name, children in equipment_structure.items():
        parent = Equipment.objects.create(name=parent_name)
        for child in children:
            Equipment.objects.create(name=child, parent=parent)

    print("Seed data successfully inserted.")