"""API module."""
from flask_restx import Api, Resource, fields
from reviews_microservice import __version__
import logging
from reviews_microservice.models import db, UserReview
from sqlalchemy.exc import IntegrityError
import reqparse
from reviews_microservice.utils import FilterParam
import operator as ops


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


api = Api(prefix="/v1", version=__version__, validate=True)


@api.errorhandler
def handle_exception(error: Exception):
    """When an unhandled exception is raised"""
    message = "Error: " + getattr(error, 'message', str(error))
    return {'message': message}, getattr(error, 'code', 500)


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
        "comment": fields.Integer(required=False, description="An optional comment"),
    },
)

user_review_with_timestamp_model = api.inherit(
    "User review model",
    user_review_model,
    {"timestamp": fields.DateTime(description="The moment the review was created at")},
)


user_review_parser = reqparse.RequestParser()
user_review_model.add_argument(
    "booking_id",
    store_missing=False,
    type=FilterParam("booking_id", ops.eq),
    help="The unique identifier for the booking",
)
user_review_model.add_argument(
    "reviewer_id",
    store_missing=False,
    type=FilterParam("reviewer_id", ops.eq),
    help="The unique identifier for the reviewer",
)
user_review_model.add_argument(
    "reviewee_id",
    store_missing=False,
    type=FilterParam("reviewee_id", ops.eq),
    help="The unique identifier of the reviewee",
)


@api.route("/review/user")
class UserReviewModel(Resource):
    @api.doc("list_user_review")
    @api.marshal_list_with(user_review_with_timestamp_model)
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
    @api.expect(user_review_model)
    @api.expect(200, "Successfully created")
    @api.expect(409, "Already created")
    @api.marshal_with(user_review_with_timestamp_model)
    def post(self):
        """Create a new user review."""
        try:
            new_user_review = UserReview(**api.payload)
            db.session.add(new_user_review)
            db.session.commit()
            return new_user_review
        except IntegrityError:
            return {"message": "Review has already been created"}, 409
