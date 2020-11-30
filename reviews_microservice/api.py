"""API module."""
from flask_restx import Api
from reviews_microservice import __version__
from reviews_microservice.namespaces.users_reviews import api as users_reviews_namespace
from reviews_microservice.namespaces.publications_reviews import (
    api as publications_reviews_namespace,
)

api = Api(
    prefix="/v1",
    version=__version__,
    title="Reviews API",
    description="Reviews microservice for bookbnb",
    default="Reviews",
    default_label="Reviews operations",
    validate=True,
)

api.add_namespace(users_reviews_namespace, path='/user_reviews')
api.add_namespace(publications_reviews_namespace, path='/publication_reviews')


@api.errorhandler
def handle_exception(error: Exception):
    """When an unhandled exception is raised"""
    message = "Error: " + getattr(error, 'message', str(error))
    return {'message': message}, getattr(error, 'code', 500)
