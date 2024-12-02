from fastapi import APIRouter, Depends, Path

from app.api.controllers.auth_controller import has_role
from app.api.controllers.category_controller import CategoryController
from models.schemas import (
    CategoryCreateSchema,
    CategoryUpdateSchema,
    ErrorResponseModel,
    ResponseSchema,
)
from models.schemas import Role as R

router = APIRouter(prefix="/categories", tags=["Category"])


@router.post(
    "",
    response_model=ResponseSchema,
    responses={
        200: {"model": ResponseSchema, "description": "Successful Response"},
        400: {"model": ErrorResponseModel, "description": "Bad Request"},
    },
)
async def create_category_route(
    category_schema: CategoryCreateSchema, user=Depends(has_role(R.USER))
) -> ResponseSchema:
    category_id = await CategoryController.create_category(category_schema, user.id)
    message = "Category created successfully"
    data = {"id": category_id}
    return ResponseSchema(data=data, message=message)


@router.get("/{category_id}", response_model=ResponseSchema)
async def read_category_route(
    category_id: str = Path(..., description="The ID of the category to retrieve"),
    user=Depends(has_role(R.USER)),
) -> ResponseSchema:
    category = await CategoryController.get_category(category_id, user.id)
    return ResponseSchema(
        data={"category": category}, message="Category retrieved successfully"
    )


@router.get("", response_model=ResponseSchema)
async def read_all_categories_route(user=Depends(has_role(R.USER))) -> ResponseSchema:
    categories = await CategoryController.get_all_categories(user.id)
    return ResponseSchema(
        data={"categories": categories},
        message="Categories retrieved successfully",
    )


@router.put("/{category_id}", response_model=ResponseSchema)
async def update_category_route(
    category_schema: CategoryUpdateSchema,
    category_id: str = Path(..., description="The ID of the category to update"),
    user=Depends(has_role(R.USER)),
) -> ResponseSchema:
    updated_category = await CategoryController.update_category(
        category_id, category_schema, user.id
    )
    return ResponseSchema(
        data={"category": updated_category},
        message="Category updated successfully",
    )


@router.delete("/{category_id}", response_model=ResponseSchema)
async def delete_category_route(
    category_id: str = Path(..., description="The ID of the category to delete"),
    user=Depends(has_role(R.USER)),
) -> ResponseSchema:
    success = await CategoryController.delete_category(category_id, user.id)
    return ResponseSchema(message="Category deleted successfully")
