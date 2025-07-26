from .models import User, Workout, WorkoutTemplate, DailyLog, MealEntry
from datetime import date
import logging

logger = logging.getLogger(__name__)

def create_workout_template(user, workout):
    """
    Create a workout template from an existing workout
    
    Args:
        user: User instance who owns the template
        workout: Workout instance to create template from
        
    Returns:
        WorkoutTemplate instance or None if creation fails
        
    Raises:
        ValueError: If invalid parameters are provided
        Exception: For any other errors during creation
    """
    
    # Input validation
    if not user:
        raise ValueError("User cannot be None")
    
    if not workout:
        raise ValueError("Workout cannot be None")
    
    if not hasattr(workout, 'name') or not workout.name:
        raise ValueError("Workout must have a valid name")
    
    try:
        logger.info(f"Creating workout template for user {user.id}, workout '{workout.name}'")
        
        # Create the template with error handling for duplicate names
        template_name = workout.name
        template_counter = 1
        
        # Create the template
        template = WorkoutTemplate.objects.create(
            user=user,
            name=template_name,
            created_at=workout.created_at if hasattr(workout, 'created_at') and workout.created_at else date.today(),
        )
        
        logger.info(f"Created template with ID {template.id} and name '{template.name}'")
        
        # Copy exercises from the workout to the template
        try:
            exercises = workout.get_exercises()
            
            if exercises:
                exercise_count = 0
                failed_exercises = []
                
                for exercise in exercises:
                    try:
                        if exercise:  # Make sure exercise is not None
                            template.add_exercise(exercise)
                            exercise_count += 1
                            logger.debug(f"Added exercise '{exercise.name}' to template")
                        else:
                            logger.warning("Skipping None exercise")
                            
                    except Exception as e:
                        error_msg = f"Failed to add exercise {getattr(exercise, 'name', 'Unknown')} to template: {str(e)}"
                        logger.error(error_msg)
                        failed_exercises.append(getattr(exercise, 'name', 'Unknown'))
                        continue
                
                logger.info(f"Successfully added {exercise_count} exercises to template")
                
                if failed_exercises:
                    logger.warning(f"Failed to add {len(failed_exercises)} exercises: {', '.join(failed_exercises)}")
                    
            else:
                logger.warning("No exercises found in workout to copy to template")
                
        except AttributeError as e:
            logger.error(f"Workout object doesn't have get_exercises method: {str(e)}")
            # Try alternative method if get_exercises doesn't exist
            try:
                if hasattr(workout, 'exercises'):
                    exercises = workout.exercises.all()
                    for exercise in exercises:
                        if exercise:
                            template.add_exercise(exercise)
                    logger.info(f"Used alternative method to copy {len(exercises)} exercises")
                else:
                    logger.error("No way to access exercises from workout object")
                    
            except Exception as alt_e:
                logger.error(f"Alternative exercise copying method also failed: {str(alt_e)}")
                
        except Exception as e:
            logger.error(f"Error copying exercises to template: {str(e)}")
            # Template was created but exercises failed - you might want to decide whether to delete it
            # For now, we'll keep the template even if exercises failed
        
        logger.info(f"Successfully created workout template '{template.name}' with ID {template.id}")
        return template
        
    except Exception as e:
        logger.error(f"Failed to create workout template: {str(e)}")
        
        # Clean up if template was partially created
        try:
            if 'template' in locals() and template:
                logger.info(f"Cleaning up partially created template {template.id}")
                template.delete()
        except Exception as cleanup_e:
            logger.error(f"Failed to clean up partially created template: {str(cleanup_e)}")
        
        # Re-raise the exception so calling code can handle it
        raise Exception(f"Failed to create workout template: {str(e)}")