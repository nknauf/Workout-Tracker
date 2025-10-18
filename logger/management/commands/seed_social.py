# logger/management/commands/seed_social.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from pathlib import Path
from random import randint, choice, sample
import io, os

# ---- Adjust these imports to your actual app if needed ----
from logger.models import Post, PostLike  # your app label
try:
    from logger.models import Comment
except Exception:
    Comment = None

try:
    from logger.models import PostImage
except Exception:
    # If your image model has a different name, change here.
    from logger.models import PostPhoto as PostImage  # pragma: no cover

# BEGIN: SEED_SOCIAL
# ---- Optional: simple image generator using Pillow (pretty placeholders) ----
def generate_image_bytes(text: str, w: int = 900, h: int = 1200):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception:
        # Fallback: 1x1 transparent PNG
        return b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0bIDATx\x9cc``\x00\x00\x00\x02\x00\x01\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82"

    # Colored background with label text
    img = Image.new("RGB", (w, h), (randint(180,245), randint(180,245), randint(180,245)))
    draw = ImageDraw.Draw(img)
    msg = text[:36]
    try:
        font = ImageFont.truetype("arial.ttf", size=48)
    except Exception:
        font = ImageFont.load_default()
    tw, th = draw.textbbox((0, 0), msg, font=font)[2:]
    draw.text(((w-tw)//2, (h-th)//2), msg, fill=(20,20,20), font=font)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()

class Command(BaseCommand):
    help = "Seed ~10 mixed social posts (text + single/multi images, comments, likes)."

    def handle(self, *args, **opts):
        User = get_user_model()

        # --- Ensure media folder exists ---
        media_root = Path(settings.MEDIA_ROOT or "media").resolve()
        seed_dir = media_root / "dev_seed"
        seed_dir.mkdir(parents=True, exist_ok=True)

        # --- Users ---
        usernames = ["noah", "sam", "alex", "mike", "sara"]
        users = []
        for name in usernames:
            u, _ = User.objects.get_or_create(
                username=name,
                defaults={"email": f"{name}@example.com"}
            )
            users.append(u)
        if not users:
            self.stdout.write(self.style.ERROR("No users found/created."))
            return
        me = users[0]

        # --- Content pools ---
        workouts = [
            ("Push Day (Chest/Tris)", [("Bench Press", 225), ("Incline DB", 80), ("Cable Fly", 35)]),
            ("Pull Day (Back/Bis)", [("Deadlift", 365), ("Lat Pulldown", 150), ("Seated Row", 140)]),
            ("Leg Day", [("Squat", 315), ("Leg Press", 540), ("RDL", 225)]),
        ]
        captions = [
            "Mid-workout snapshot—focus dialed in.",
            "Post-workout mirror check-in. Pump was real.",
            "Recipe breakdown: High-protein chicken bowl.",
            "Meal prep stack for the week—macros on point.",
            "Workout summary + machine maxes below.",
            "Coach says: form > ego. Sticking to it.",
            "Sprints done. Lungs on fire, progress made.",
            "Upper body volume day—hit all targets.",
            "New movement: Cuff lateral raises—shoulders lit.",
            "Recovery meal + steps. Consistency wins.",
        ]
        meal_names = [
            "Chicken & Rice Bowl", "Beef Stir Fry", "Greek Yogurt Parfait",
            "Oats & Whey", "Salmon & Potatoes", "Turkey Pasta Marinara",
        ]
        recipe_notes = [
            "Grill chicken, season with paprika/garlic. Add jasmine rice, steamed broccoli.",
            "Cook lean beef with peppers/onions. Soy, ginger, garlic. Serve on rice.",
            "Layer Greek yogurt, honey, berries, and granola.",
            "Quick oats, whey, banana, peanut butter swirl.",
            "Pan-sear salmon, roast potatoes, asparagus.",
            "Whole-wheat pasta, lean turkey, marinara, parmesan.",
        ]

        # --- Helpers to attach images ---
        def attach_images(post, labels):
            """
            Create 1..N images for a post under MEDIA_ROOT/dev_seed/
            and add PostImage rows.
            """
            for idx, label in enumerate(labels, start=1):
                fname = f"{post.id:04d}_{idx}_{label.replace(' ','_').lower()}.jpg"
                fpath = seed_dir / fname
                if not fpath.exists():
                    fpath.write_bytes(generate_image_bytes(label))
                # Store relative path to MEDIA_ROOT so ImageField can resolve URL
                rel_path = f"{seed_dir.relative_to(media_root).as_posix()}/{fname}"
                PostImage.objects.create(post=post, image=rel_path, alt_text=label)

        # --- Build 10 mixed posts ---
        created = []
        for i in range(10):
            author = choice(users)
            base_caption = captions[i % len(captions)]
            created_at = timezone.now() - timezone.timedelta(hours=randint(1, 72))

            # alternate types: workout summary, meal, mid-workout photo, recipe, mirror selfie
            kind = i % 5

            if kind == 0:
                # Mid-workout pictures (1–3 images)
                p = Post.objects.create(author=author, content=base_caption, created_at=created_at)
                n = randint(1, 3)
                labels = [f"mid-workout {j}" for j in range(1, n+1)]
                attach_images(p, labels)

            elif kind == 1:
                # Mirror selfie post-workout (single image)
                p = Post.objects.create(author=author, content=base_caption, created_at=created_at)
                attach_images(p, ["mirror-selfie"])

            elif kind == 2:
                # Workout summary + machine maxes (text + optionally 1 image of board)
                wname, lifts = choice(workouts)
                summary_lines = [f"{wname} | Machine maxes:"]
                for name, wt in lifts:
                    summary_lines.append(f"• {name}: {wt} lbs max")
                content = base_caption + "\n\n" + "\n".join(summary_lines)
                p = Post.objects.create(author=author, content=content, created_at=created_at)
                if randint(0, 1):
                    attach_images(p, ["whiteboard-maxes"])

            elif kind == 3:
                # Meal photo(s)
                meal = choice(meal_names)
                p = Post.objects.create(author=author, content=f"{base_caption}\nMeal: {meal}", created_at=created_at)
                n = randint(1, 2)
                labels = [f"{meal} #{j}" for j in range(1, n+1)]
                attach_images(p, labels)

            else:
                # Recipe steps (images of ingredients/steps)
                recipe = choice(recipe_notes)
                title = choice(meal_names)
                content = f"{base_caption}\nRecipe: {title}\n{recipe}"
                p = Post.objects.create(author=author, content=content, created_at=created_at)
                labels = ["ingredients", "steps"]
                attach_images(p, labels)

            created.append(p)

        # --- Random likes/comments ---
        for p in created:
            for _ in range(randint(0, 4)):
                PostLike.objects.get_or_create(post=p, user=choice(users))
            if Comment:
                for _ in range(randint(0, 3)):
                    commenter = choice(users)
                    Comment.objects.create(
                        post=p,
                        user=commenter,
                        content=choice(captions),
                    )

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(created)} posts with images at {seed_dir}"))
# END: SEED_SOCIAL
