#!/usr/bin/env python3
from datetime import date, timedelta

if __package__:
    from .app import app
    from .models import Exercise, Workout, WorkoutExercise, db
else:
    from app import app
    from models import Exercise, Workout, WorkoutExercise, db

with app.app_context():
    # Clear and recreate tables
    db.drop_all()
    db.create_all()

    # Workouts
    strength = Workout(
        date=date.today(),
        duration_minutes=50,
        notes="Upper body"
    )
    cardio = Workout(
        date=date.today() - timedelta(days=2),
        duration_minutes=30,
        notes="Cardio day"
    )

    # Exercises
    push_up = Exercise(
        name="Push-up",
        category="strength",
        equipment_needed=False
    )
    squat = Exercise(
        name="Squat",
        category="strength",
        equipment_needed=False
    )
    cycling = Exercise(
        name="Cycling",
        category="cardio",
        equipment_needed=True
    )

    db.session.add_all([strength, cardio, push_up, squat, cycling])
    db.session.flush()   # so the objects get IDs

    # WorkoutExercises
    db.session.add_all([
        WorkoutExercise(workout=strength, exercise=push_up, reps=12, sets=3),
        WorkoutExercise(workout=strength, exercise=squat, reps=10, sets=4),
        WorkoutExercise(workout=cardio, exercise=cycling, duration_seconds=1800),
    ])

    db.session.commit()
    print("Seeded 2 workouts, 3 exercises, and 3 workout-exercise records.")