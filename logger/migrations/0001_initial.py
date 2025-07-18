# Generated by Django 5.2.3 on 2025-07-14 20:42

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseExercise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='BaseMuscle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='DropSetExercise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('description', models.TextField(blank=True)),
                ('instructions', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('base_exercise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='drop_sets', to='logger.baseexercise')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='baseexercise',
            name='equipment',
            field=models.ManyToManyField(to='logger.equipment'),
        ),
        migrations.CreateModel(
            name='MealEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('calories', models.PositiveIntegerField()),
                ('protein', models.PositiveIntegerField()),
                ('carbs', models.PositiveIntegerField(default=0)),
                ('fats', models.PositiveIntegerField(default=0)),
                ('is_template', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MealTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('calories', models.PositiveIntegerField()),
                ('protein', models.PositiveIntegerField()),
                ('carbs', models.PositiveIntegerField(default=0)),
                ('fats', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Muscle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('base_muscle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='muscles', to='logger.basemuscle')),
            ],
        ),
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('base_exercise', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='exercises', to='logger.baseexercise')),
                ('equipment', models.ManyToManyField(to='logger.equipment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('muscle_group', models.ManyToManyField(to='logger.muscle')),
            ],
        ),
        migrations.AddField(
            model_name='baseexercise',
            name='muscle_group',
            field=models.ManyToManyField(to='logger.muscle'),
        ),
        migrations.CreateModel(
            name='SuperSetExercise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('description', models.TextField(blank=True)),
                ('instructions', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('rest_time_between_sets', models.PositiveIntegerField(default=60, help_text='Rest time in seconds between super sets')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Workout',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DailyLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('meals', models.ManyToManyField(blank=True, related_name='daily_logs', to='logger.mealentry')),
                ('workouts', models.ManyToManyField(blank=True, related_name='daily_logs', to='logger.workout')),
            ],
        ),
        migrations.CreateModel(
            name='WorkoutTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DropSetRound',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('round_number', models.PositiveIntegerField()),
                ('weight', models.DecimalField(decimal_places=2, max_digits=6)),
                ('reps', models.PositiveIntegerField()),
                ('rest_time_seconds', models.PositiveIntegerField(default=0, help_text='Rest time before next round')),
                ('notes', models.TextField(blank=True)),
                ('drop_set', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rounds', to='logger.dropsetexercise')),
            ],
            options={
                'ordering': ['round_number'],
                'unique_together': {('drop_set', 'round_number')},
            },
        ),
        migrations.CreateModel(
            name='SuperSetExerciseItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField()),
                ('sets', models.PositiveIntegerField(default=3)),
                ('reps', models.PositiveIntegerField(default=10)),
                ('weight', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('rest_time_seconds', models.PositiveIntegerField(default=0, help_text='Rest time after this exercise')),
                ('notes', models.TextField(blank=True)),
                ('base_exercise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='logger.baseexercise')),
                ('super_set', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exercises', to='logger.supersetexercise')),
            ],
            options={
                'ordering': ['order'],
                'unique_together': {('super_set', 'order')},
            },
        ),
        migrations.CreateModel(
            name='WorkoutExerciseItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('order', models.PositiveIntegerField(default=0)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('workout', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='logger.workout')),
            ],
            options={
                'ordering': ['order'],
                'unique_together': {('workout', 'order')},
            },
        ),
    ]
