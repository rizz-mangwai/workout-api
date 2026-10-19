#!/usr/bin/env python3
from .app import app
from .models import Exercise, Workout, WorkoutExercise, db


with app.app_context():
    db.drop_all()
    db.create_all()

    strength = Workout(date="2025-01-15", duration_minutes=50, notes="Upper body")
    cardio = Workout(date="2025-01-17", duration_minutes=30, notes="Cardio day")

    push_up = Exercise(
        name="Push-up", category="Strength", equipment_needed=False
    )
    squat = Exercise(name="Squat", category="Strength", equipment_needed=False)
    cycling = Exercise(name="Cycling", category="Cardio", equipment_needed=True)

    db.session.add_all([strength, cardio, push_up, squat, cycling])
    db.session.flush()
    db.session.add_all(
        [
            WorkoutExercise(
                workout=strength, exercise=push_up, reps=12, sets=3
            ),
            WorkoutExercise(
                workout=strength, exercise=squat, reps=10, sets=4
            ),
            WorkoutExercise(
                workout=cardio, exercise=cycling, duration_seconds=1800
            ),
        ]
    )
    db.session.commit()
    print("Seeded 2 workouts, 3 exercises, and 3 workout-exercise records.")
