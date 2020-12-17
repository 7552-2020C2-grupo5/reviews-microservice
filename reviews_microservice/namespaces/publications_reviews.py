"""Publications reviews namespace."""
import operator as ops

from flask import abort as flask_abort
from flask_restx import Namespace, Resource, fields, reqparse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func

from reviews_microservice import __version__
from reviews_microservice.models import PublicationReview, db
from reviews_microservice.utils import FilterParam

api = Namespace(
    "Publication Reviews", description="Publication reviews related operations"
)

publication_review_model = api.model(
    "Publication review model",
    {
        "id": fields.Integer(
            readonly=True, required=True, description="The review identifier"
        ),
        "reviewer_id": fields.Integer(
            required=True, description="The unique identifier of the reviewer"
        ),
        "publication_id": fields.Integer(
            required=True,
            description="The unique identifier of the reviewed publication",
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

publication_score_model = api.model(
    "Publication score model",
    {
        "publication_id": fields.Integer(
            description="The unique identifier for the reviewed publication"
        ),
        "score_avg": fields.Float(description="The score average, possibly normalized"),
    },
)

publication_review_create_parser = reqparse.RequestParser()
publication_review_create_parser.add_argument(
    "reviewer_id", type=int, location="json", nullable=False
)
publication_review_create_parser.add_argument(
    "publication_id", type=int, location="json", nullable=False
)
publication_review_create_parser.add_argument(
    "booking_id", type=int, location="json", nullable=False
)
publication_review_create_parser.add_argument(
    "score", type=int, location="json", nullable=False, choices=[1, 2, 3, 4]
)
publication_review_create_parser.add_argument(
    "comment", type=str, location="json", nullable=True
)

publication_review_parser = reqparse.RequestParser()
publication_review_parser.add_argument(
    "booking_id",
    store_missing=False,
    type=FilterParam("booking_id", ops.eq),
    help="The unique identifier for the booking",
)
publication_review_parser.add_argument(
    "reviewer_id",
    store_missing=False,
    type=FilterParam("reviewer_id", ops.eq),
    help="The unique identifier for the reviewer",
)
publication_review_parser.add_argument(
    "publication_id",
    store_missing=False,
    type=FilterParam("publication_id", ops.eq),
    help="The unique identifier of the reviewed publication",
)


@api.route("/reviews")
class PublicationReviewResource(Resource):
    @api.doc("list_publication_review")
    @api.marshal_list_with(publication_review_model)
    @api.expect(publication_review_parser)
    def get(self):
        """List all publication reviews."""
        params = publication_review_parser.parse_args()
        query = PublicationReview.query
        for _, filter_op in params.items():
            if not isinstance(filter_op, FilterParam):
                continue
            query = filter_op.apply(query, PublicationReview)
        return query.all()

    @api.doc("create_publication_review")
    @api.expect(publication_review_create_parser)
    @api.response(200, "Successfully created")
    @api.response(400, "Bad request")
    @api.response(409, "Already created")
    @api.marshal_with(publication_review_model)
    def post(self):
        """Create a new publication review."""
        try:
            new_publication_review = PublicationReview(**api.payload)
            db.session.add(new_publication_review)
            db.session.commit()
            return new_publication_review
        except IntegrityError:
            return flask_abort(409, "Review has already been created")
        except ValueError:
            return flask_abort(400, "Score must be between 1 and 4")


@api.route("/score/publication/<int:publication_id>")
class PublicationReviewRevieweeResource(Resource):
    @api.doc("get_publication_score")
    @api.response(204, "No data for publication")
    @api.response(200, "Score successfully calculated", model=publication_score_model)
    def get(self, publication_id):
        """Get score for publication."""
        if (
            PublicationReview.query.filter(
                PublicationReview.publication_id == publication_id
            ).first()
            is None
        ):
            return {}, 204
        score_avg = (
            PublicationReview.query.with_entities(
                func.avg(PublicationReview.score).label("score_avg")
            )
            .filter(PublicationReview.publication_id == publication_id)
            .scalar()
        )
        return (
            api.marshal(
                {"publication_id": publication_id, "score_avg": score_avg},
                publication_score_model,
            ),
            200,
        )
