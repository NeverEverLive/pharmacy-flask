import logging
from flask import Response, json, Blueprint
from flask_pydantic import validate

from src.schemas.check import CheckSchema
from src.operators.check import create_check


check = Blueprint("check", __name__)


@check.post('/')
@validate()
def create(body: CheckSchema):
    response = create_check(body)
    return Response(
        json.dumps(response),
        status=201,
        content_type='application/json'
    )

# @article.get('/<string:id>')
# def get(token, id):
#     response = get_article(id)
#     return Response(
#         json.dumps(response),
#         status=200,
#         content_type='application/json'
#     )


# @article.get('/')
# def get_all(token):
#     response = get_all_article()
#     return Response(
#         json.dumps(response),
#         status=200,
#         content_type='application/json'
#     )

# @article.put('/')
# @validate()
# def update(token, body: ArticleSchema):
#     response = update_article(body)
#     return Response(
#         json.dumps(response),
#         status=201,
#         content_type='application/json'
#     )


# @article.delete('/')
# @validate()
# def delete(token, query: GetArticleSchema):
#     response = delete_article(query)
#     return Response(
#         json.dumps(response),
#         status=202,
#         content_type='application/json'
#     )
