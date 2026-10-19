# Workout API

A Flask, SQLAlchemy, and Marshmallow backend for managing workouts, reusable exercises, and the details of exercises performed in each workout.

## Requirements

- Python 3.8.13 or newer
- Pipenv

## Setup

From the repository root:

```bash
pipenv install
pipenv run flask --app server.app db init
pipenv run flask --app server.app db migrate -m "Create workout and exercise tables"
pipenv run flask --app server.app db upgrade
pipenv run python -m server.seed
pipenv run python -m server.app
```

The API runs at `http://127.0.0.1:5555`. The SQLite database is stored at `server/app.db`.
For subsequent schema changes, run `flask --app server.app db migrate -m "Describe the change"` and `flask --app server.app db upgrade` through Pipenv.

## Data model

- A `Workout` has many `WorkoutExercise` records and many `Exercise` records through them.
- An `Exercise` can be reused across workouts and has many `WorkoutExercise` records.
- A `WorkoutExercise` stores the reps, sets, and/or duration for one exercise in one workout. The same exercise can only be attached to a given workout once.

Exercise names are unique. Names and categories must contain non-whitespace text, workout durations must be positive, and association counts/durations cannot be negative. These rules are enforced with schema validation, model validation, and database constraints.

## API

All request and response bodies use JSON. Validation errors return `400`, missing resources return `404`, and uniqueness conflicts return `409`.

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/workouts` | List workouts |
| `GET` | `/workouts/<id>` | Show a workout and its exercises with per-workout details |
| `POST` | `/workouts` | Create a workout |
| `DELETE` | `/workouts/<id>` | Delete a workout and its associations |
| `GET` | `/exercises` | List exercises |
| `GET` | `/exercises/<id>` | Show an exercise and its associated workouts |
| `POST` | `/exercises` | Create an exercise |
| `DELETE` | `/exercises/<id>` | Delete an exercise and its associations |
| `POST` | `/workouts/<workout_id>/exercises/<exercise_id>/workout_exercises` | Add an exercise to a workout |

Workout creation accepts `date` (`YYYY-MM-DD`), `duration_minutes`, and optional `notes`. Exercise creation accepts `name`, `category`, and `equipment_needed`. For example:

```json
{
  "date": "2025-01-15",
  "duration_minutes": 45,
  "notes": "Upper body"
}
```

Adding an exercise accepts any of `reps`, `sets`, and `duration_seconds`:

```json
{
  "reps": 10,
  "sets": 3,
  "duration_seconds": 60
}
```

An association must include at least one of those three values. There are no update or association-removal endpoints.
