"""SQLAlchemy models."""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy.sql import func

db = SQLAlchemy()


class UserReview(db.Model):  # type: ignore
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    reviewer_id = db.Column(db.Integer, nullable=False)
    reviewee_id = db.Column(db.Integer, nullable=False)
    booking_id = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=func.now())

    __table_args__ = (
        db.UniqueConstraint('booking_id', name='unique_review_for_booking'),
    )

    @validates("score")
    def validate_score(self, _key, score):
        if not 1 <= score <= 4:
            raise ValueError("Score must be between 1 and 4")
        return score


class PublicationReview(db.Model):  # type: ignore
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    reviewer_id = db.Column(db.Integer, nullable=False)
    publication_id = db.Column(db.Integer, nullable=False)
    booking_id = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=func.now())

    __table_args__ = (
        db.UniqueConstraint('booking_id', name='unique_review_for_booking'),
    )

    @validates("score")
    def validate_score(self, _key, score):
        if not 1 <= score <= 4:
            raise ValueError("Score must be between 1 and 4")
        return score
