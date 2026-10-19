from marshmallow import Schema, ValidationError, fields, post_load, validates_schema
from marshmallow.validate import Length, Range

from .models import Exercise, Workout, WorkoutExercise


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(required=True, strict=True, validate=Range(min=1))
    notes = fields.Str(allow_none=True)

    @post_load
    def make_workout(self, data, **_kwargs):
        return Workout(**data)


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(
        required=True,
        validate=Length(min=1, max=120, error="name must contain 1 to 120 characters"),
    )
    category = fields.Str(
        required=True,
        validate=Length(min=1, max=80, error="category must contain 1 to 80 characters"),
    )
    equipment_needed = fields.Bool(required=True)

    @validates_schema
    def validate_text(self, data, **_kwargs):
        errors = {}
        for field_name in ("name", "category"):
            value = data.get(field_name)
            if value is not None and not value.strip():
                errors[field_name] = ["Must contain non-whitespace text."]
        if errors:
            raise ValidationError(errors)

    @post_load
    def make_exercise(self, data, **_kwargs):
        return Exercise(**data)


class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)
    reps = fields.Int(allow_none=True, strict=True, validate=Range(min=0))
    sets = fields.Int(allow_none=True, strict=True, validate=Range(min=0))
    duration_seconds = fields.Int(allow_none=True, strict=True, validate=Range(min=0))

    @validates_schema
    def validate_details(self, data, **_kwargs):
        if not any(
            data.get(field_name) is not None
            for field_name in ("reps", "sets", "duration_seconds")
        ):
            raise ValidationError(
                "At least one of reps, sets, or duration_seconds is required."
            )

    @post_load
    def make_workout_exercise(self, data, **_kwargs):
        return WorkoutExercise(**data)


workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
workout_exercise_schema = WorkoutExerciseSchema()


class WorkoutExerciseDetailSchema(WorkoutExerciseSchema):
    exercise = fields.Nested(ExerciseSchema)


class WorkoutDetailSchema(WorkoutSchema):
    workout_exercises = fields.Nested(WorkoutExerciseDetailSchema, many=True)


class ExerciseDetailSchema(ExerciseSchema):
    workouts = fields.Method("serialize_workouts")

    def serialize_workouts(self, exercise):
        result = []
        for association in exercise.workout_exercises:
            workout = workout_schema.dump(association.workout)
            workout["workout_exercise"] = workout_exercise_schema.dump(association)
            result.append(workout)
        return result
