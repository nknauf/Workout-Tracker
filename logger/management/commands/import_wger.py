import requests
import json
from django.core.management.base import BaseCommand
from logger.models import Exercise, Equipment, Muscle, MovementType

class Command(BaseCommand):
    help = 'Import exercises and related data from wger workout manager database.'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Remove all imported wger data')

    def handle(self, *args, **options):
        def clear_wger_data():
            Exercise.objects.all().delete()
            Muscle.objects.all().delete()
            Equipment.objects.all().delete()
            MovementType.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('All imported wger data deleted.'))

        if options.get('clear'):
            clear_wger_data()
            return

        # Helper to handle paginated endpoints
        def fetch_all(url):
            results = []
            while url:
                response = requests.get(url)
                data = response.json()
                results.extend(data['results'])
                url = data.get('next')
            return results

        # Import equipment
        equipment_url = 'https://wger.de/api/v2/equipment/'
        equipment = fetch_all(equipment_url)
        for item in equipment:
            Equipment.objects.get_or_create(name=item['name'])
        self.stdout.write(self.style.SUCCESS(f"Imported {len(equipment)} equipment items."))

        # Import exercise categories as MovementType
        category_url = 'https://wger.de/api/v2/exercisecategory/'
        categories = fetch_all(category_url)
        for cat in categories:
            MovementType.objects.get_or_create(name=cat['name'])
        self.stdout.write(self.style.SUCCESS(f"Imported {len(categories)} exercise categories as MovementType."))

        # --- Import exercises ---
        exercise_url = 'https://wger.de/api/v2/exercise/?language=2'
        exercises = fetch_all(exercise_url)
        equipment_lookup = {e.name: e for e in Equipment.objects.all()}
        equipment_id_lookup = {item['id']: item['name'] for item in equipment}
        muscle_lookup = {m.name: m for m in Muscle.objects.all()}
        muscle_id_lookup = {item['id']: item['name'] for item in []}  # No direct mapping from wger
        category_lookup = {c['id']: c['name'] for c in categories}
        movement_type_lookup = {mt.name: mt for mt in MovementType.objects.all()}

        for ex in exercises:
            if not ex.get('name'):
                continue
            # Example: just create Exercise with name and movement_type for now
            movement_type = movement_type_lookup.get(category_lookup.get(ex['category']))
            exercise_obj, _ = Exercise.objects.update_or_create(
                name=ex['name'],
                defaults={
                    'movement_type': movement_type,
                }
            )
            # Link equipment (M2M)
            equipment_ids = ex.get('equipment', [])
            equipment_objs = [equipment_lookup.get(equipment_id_lookup[eid]) for eid in equipment_ids if eid in equipment_id_lookup and equipment_id_lookup[eid] in equipment_lookup]
            exercise_obj.equipment.set(equipment_objs)

        self.stdout.write(self.style.SUCCESS(f"Imported {len(exercises)} exercises.")) 