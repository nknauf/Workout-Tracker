# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Django Development
```bash
# Run development server
python manage.py runserver

# Database migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser

# Run tests
python manage.py test

# Seed database with initial data
python manage.py shell -c "from logger.seed_data import seed_exercises; seed_exercises()"
```

### Virtual Environment
```bash
# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies (when requirements.txt is added)
pip install -r requirements.txt
```

## Architecture Overview

This is a Django-based workout and nutrition tracking application with the following key components:

### Core Application Structure
- **config/**: Django project configuration
  - `settings.py`: Main settings, uses SQLite database
  - `urls.py`: Root URL configuration with authentication views
- **logger/**: Main application for workout and meal logging
- **templates/**: HTML templates for the web interface
- **db.sqlite3**: SQLite database file

### Key Models (logger/models.py - deleted but inferred from views)
- **Exercise**: User-created exercises with muscle groups and equipment
- **BaseExercise**: Template exercises that users can base their exercises on
- **Workout**: Collections of exercises for a specific session
- **WorkoutTemplate**: Reusable workout templates
- **MealEntry**: Food logging with macronutrient tracking
- **DailyLog**: Daily container for workouts and meals
- **Equipment, Muscle**: Categorization for exercises

### Session-Based Workout Creation
The application uses Django sessions to manage workout creation flow:
- Selected exercises are stored in `request.session['workout_exercises']`
- Workout names are stored in `request.session['workout_name']`
- Sessions are cleared after saving or canceling workouts

### NLP Engine (Experimental)
- **logger/nlp_engine/**: Contains intent classification system
  - `intents.json`: Training data for various workout/meal intents
  - `intent_classification.py`: NLP processing logic
- **logger/simple_multi_turn_nlp.py**: Multi-turn dialogue processor (appears corrupted)

### Authentication System
- Uses Django's built-in authentication
- Login required for all main functionality
- Login/logout views configured at root level

### Data Management
- **logger/seed_data.py**: Contains functions to populate initial exercise data
- **logger/management/commands/import_wger.py**: Command for importing exercise data from wger API

## Development Notes

### Database
- Uses SQLite for development
- All user data is tied to Django's User model through foreign keys
- Recent changes removed user field from Exercise model (based on git status)

### Templates and UI
- Templates located in `logger/templates/logger/`
- Uses Django's template system with forms
- Key views: home, create_workout, calendar, exercise management

### Current State
Based on git status, the project is in transition:
- Multiple NLP-related files have been deleted
- New `logger/nlp_engine/` directory has been added
- Database and cache files show recent modifications
- Project appears to be moving away from complex NLP toward simpler intent classification

### Key Views and URLs
- Home dashboard with daily calorie/macro tracking
- Workout creation with template support and exercise filtering
- Calendar view for historical workout/meal data
- Exercise management (CRUD operations)
- Meal logging with macro tracking

### Forms and User Input
- Session-based workout builder with real-time updates
- Template loading and saving functionality
- Conversational input forms (though NLP backend appears to be in flux)