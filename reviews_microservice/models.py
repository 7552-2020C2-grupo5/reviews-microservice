"""SQLAlchemy models."""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy.orm import validates


db = SQLAlchemy()


class UserReview(db.Model):  # type: ignore
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    reviewer_id = db.Column(db.Integer, nullable=False)
    reviewee_id = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=func.now())

    @validates("score")
    def validate_score(self, _key, score):
        if not 1 <= score <= 4:
            raise ValueError("Score must be between 1 and 4")
        return score
