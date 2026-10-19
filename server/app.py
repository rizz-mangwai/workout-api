from pathlib import Path

from flask import Flask, jsonify, request
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError

from .models import Exercise, Workout, db
from .schemas import (
    ExerciseDetailSchema,
    WorkoutDetailSchema,
    exercise_schema,
    exercises_schema,
    workout_exercise_schema,
    workout_schema,
    workouts_schema,
)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{Path(__file__).resolve().parent / 'app.db'}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"connect_args": {"check_same_thread": False}}

db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    @event.listens_for(db.engine, "connect")
    def enable_sqlite_foreign_keys(connection, _record):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


@app.errorhandler(ValidationError)
def handle_validation_error(error):
    return jsonify({"errors": error.messages}), 400


def request_json():
    if not request.is_json:
        return None, (
            jsonify({"errors": {"json": ["Content-Type must be application/json."]}}),
            400,
        )
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return None, (
            jsonify({"errors": {"json": ["Request body must be a valid JSON object."]}}),
            400,
        )
    return payload, None


def commit_or_conflict():
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return (
            jsonify(
                {"errors": {"database": ["The request conflicts with existing data."]}}
            ),
            409,
        )
    return None


@app.get("/workouts")
def list_workouts():
    return jsonify(workouts_schema.dump(Workout.query.order_by(Workout.id).all()))


@app.get("/workouts/<int:workout_id>")
def get_workout(workout_id):
    workout = db.session.get(Workout, workout_id)
    if workout is None:
        return jsonify({"error": "Workout not found."}), 404
    return jsonify(WorkoutDetailSchema().dump(workout))


@app.post("/workouts")
def create_workout():
    payload, error_response = request_json()
    if error_response:
        return error_response
    workout = workout_schema.load(payload)
    db.session.add(workout)
    error_response = commit_or_conflict()
    if error_response:
        return error_response
    return jsonify(workout_schema.dump(workout)), 201


@app.delete("/workouts/<int:workout_id>")
def delete_workout(workout_id):
    workout = db.session.get(Workout, workout_id)
    if workout is None:
        return jsonify({"error": "Workout not found."}), 404
    db.session.delete(workout)
    error_response = commit_or_conflict()
    if error_response:
        return error_response
    return "", 204


@app.get("/exercises")
def list_exercises():
    return jsonify(exercises_schema.dump(Exercise.query.order_by(Exercise.id).all()))


@app.get("/exercises/<int:exercise_id>")
def get_exercise(exercise_id):
    exercise = db.session.get(Exercise, exercise_id)
    if exercise is None:
        return jsonify({"error": "Exercise not found."}), 404
    return jsonify(ExerciseDetailSchema().dump(exercise))


@app.post("/exercises")
def create_exercise():
    payload, error_response = request_json()
    if error_response:
        return error_response
    exercise = exercise_schema.load(payload)
    db.session.add(exercise)
    error_response = commit_or_conflict()
    if error_response:
        return error_response
    return jsonify(exercise_schema.dump(exercise)), 201


@app.delete("/exercises/<int:exercise_id>")
def delete_exercise(exercise_id):
    exercise = db.session.get(Exercise, exercise_id)
    if exercise is None:
        return jsonify({"error": "Exercise not found."}), 404
    db.session.delete(exercise)
    error_response = commit_or_conflict()
    if error_response:
        return error_response
    return "", 204


@app.post(
    "/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises"
)
def add_exercise_to_workout(workout_id, exercise_id):
    workout = db.session.get(Workout, workout_id)
    if workout is None:
        return jsonify({"error": "Workout not found."}), 404
    exercise = db.session.get(Exercise, exercise_id)
    if exercise is None:
        return jsonify({"error": "Exercise not found."}), 404

    payload, error_response = request_json()
    if error_response:
        return error_response
    association = workout_exercise_schema.load(payload)
    association.workout = workout
    association.exercise = exercise
    db.session.add(association)
    error_response = commit_or_conflict()
    if error_response:
        return error_response
    return jsonify(workout_exercise_schema.dump(association)), 201


if __name__ == "__main__":
    app.run(port=5555, debug=True)
