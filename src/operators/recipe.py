import uuid

from src.schemas.recipe import RecipeSchema, RecipesSchema
from src.schemas.response import ResponseSchema
from src.models.recipe import Recipe
from src.models.base_model import get_session
from src.models.logger import Logger


def create_recipe(recipe: RecipeSchema) -> ResponseSchema:
    recipe_state = Recipe().fill(**recipe.dict())

    with get_session() as session:
        session.add(recipe_state)
        session.commit()

        logger_data = {
            "id": uuid.uuid4(),
            "table": "recipe",
            "action": "delete",
            "object_info": RecipeSchema.from_orm(recipe_state).dict()
        }

        logger_state = Logger().fill(**logger_data)
        session.add(logger_state)
        session.commit()

        return ResponseSchema(
            data=RecipeSchema.from_orm(recipe_state),
            message="Recipe created successfuly",
            success=True
        )


def get_recipes_by_user_id(id: str) -> ResponseSchema:
    with get_session() as session:
        recipe_state = session.query(Recipe).filter_by(user_id=id).all()

        if not recipe_state:
            return ResponseSchema(
                data=[],
                success=False,
                message="Same recipe doesn't exist"
            )

        return ResponseSchema(
            data=RecipesSchema.from_orm(recipe_state).dict(by_alias=True)["data"],
            success=True
        )

def get_recipe(id: str) -> ResponseSchema:
    with get_session() as session:
        recipe_state = session.query(Recipe).filter_by(id=id).all()

        if not recipe_state:
            return ResponseSchema(
                data=[],
                success=False,
                message="Same recipe doesn't exist"
            )

        return ResponseSchema(
            data=RecipeSchema.from_orm(recipe_state).dict(by_alias=True)["data"],
            success=True
        )