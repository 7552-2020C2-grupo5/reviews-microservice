"""Users reviews namespace."""
from flask_restx import Resource, fields, reqparse, Namespace
from flask import abort as flask_abort
from reviews_microservice import __version__
from reviews_microservice.models import db, UserReview
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from reviews_microservice.utils import FilterParam
import operator as ops

api = Namespace("User Reviews", description="User reviews related operations")

user_review_model = api.model(
    "User review model",
    {
        "id": fields.Integer(
            readonly=True, required=True, description="The review identifier"
        ),
        "reviewer_id": fields.Integer(
            required=True, description="The unique identifier of the reviewer"
        ),
        "reviewee_id": fields.Integer(
            required=True, description="The unique identifier of the reviewee"
        ),
        "booking_id": fields.Integer(
            requried=True,
            description="The unique identifier of the booking the review belongs to",
        ),
        "score": fields.Integer(
            required=True, description="The score between 1 (lowest) and 4 (highest)."
        ),
        "comment": fields.String(required=False, description="An optional comment"),
        "timestamp": fields.DateTime(
            description="The moment the review was created at"
        ),
    },
)

reviewee_score_model = api.model(
    "Reviewee score model",
    {
        "reviewee_id": fields.Integer(
            description="The unique identifier for the reviewee"
        ),
        "score_avg": fields.Float(description="The score average, possibly normalized"),
    },
)

user_review_create_parser = reqparse.RequestParser()
user_review_create_parser.add_argument(
    "reviewer_id", type=int, location="json", nullable=False
)
user_review_create_parser.add_argument(
    "reviewee_id", type=int, location="json", nullable=False
)
user_review_create_parser.add_argument(
    "booking_id", type=int, location="json", nullable=False
)
user_review_create_parser.add_argument(
    "score", type=int, location="json", nullable=False, choices=[1, 2, 3, 4]
)
user_review_create_parser.add_argument(
    "comment", type=str, location="json", nullable=True
)

user_review_parser = reqparse.RequestParser()
user_review_parser.add_argument(
    "booking_id",
    store_missing=False,
    type=FilterParam("booking_id", ops.eq),
    help="The unique identifier for the booking",
)
user_review_parser.add_argument(
    "reviewer_id",
    store_missing=False,
    type=FilterParam("reviewer_id", ops.eq),
    help="The unique identifier for the reviewer",
)
user_review_parser.add_argument(
    "reviewee_id",
    store_missing=False,
    type=FilterParam("reviewee_id", ops.eq),
    help="The unique identifier of the reviewee",
)


@api.route("/reviews")
class UserReviewResource(Resource):
    @api.doc("list_user_review")
    @api.marshal_list_with(user_review_model)
    @api.expect(user_review_parser)
    def get(self):
        """List all user reviews."""
        params = user_review_parser.parse_args()
        query = UserReview.query
        for _, filter_op in params.items():
            if not isinstance(filter_op, FilterParam):
                continue
            query = filter_op.apply(query, UserReview)
        return query.all()

    @api.doc("create_user_review")
    @api.expect(user_review_create_parser)
    @api.response(200, "Successfully created")
    @api.response(400, "Bad request")
    @api.response(409, "Already created")
    @api.marshal_with(user_review_model)
    def post(self):
        """Create a new user review."""
        try:
            new_user_review = UserReview(**api.payload)
            db.session.add(new_user_review)
            db.session.commit()
            return new_user_review
        except IntegrityError:
            return flask_abort(409, "Review has already been created")
        except ValueError:
            return flask_abort(400, "Score must be between 1 and 4")


@api.route("/score/user/<int:reviewee_id>")
class UserReviewRevieweeResource(Resource):
    @api.doc("get_reviewee_score")
    @api.response(204, "No data for user")
    @api.response(200, "Score successfully calculated", model=reviewee_score_model)
    def get(self, reviewee_id):
        """Get score for reviewee."""
        if (
            UserReview.query.filter(UserReview.reviewee_id == reviewee_id).first()
            is None
        ):
            return {}, 204
        score_avg = (
            UserReview.query.with_entities(
                func.avg(UserReview.score).label("score_avg")
            )
            .filter(UserReview.reviewee_id == reviewee_id)
            .scalar()
        )
        return (
            api.marshal(
                {"reviewee_id": reviewee_id, "score_avg": score_avg},
                reviewee_score_model,
            ),
            200,
        )
