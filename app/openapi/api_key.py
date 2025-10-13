from fastapi import APIRouter, Depends, HTTPException
from app.auth.dependency import get_current_user, AccessTokenBearer
from app.auth.services import APIKeyServices
from fastapi_pagination import Page
from app.auth.schema import APIKeyResponse, UserModel, APIKeyCreate, APIKeyUpdate
from app.core.dependency import SessionDep
from typing import Annotated

import logging

api_key_services = APIKeyServices()
api_key_router = APIRouter()
logger = logging.getLogger(__name__)


@api_key_router.get("/", response_model=Page[APIKeyResponse], dependencies=[Depends(AccessTokenBearer())])
async def read_api_keys(
    session: SessionDep,
    current_user: Annotated[UserModel, Depends(get_current_user)]
):
    """
    Retrieve API keys.
    """
    api_keys = await api_key_services.get_api_keys(user_id=current_user, session=session)
    return api_keys


@api_key_router.post("/", response_model=APIKeyResponse)
async def create_api_key(
    session: SessionDep,
    api_key_in: APIKeyCreate,
    current_user: Annotated[UserModel, Depends(get_current_user)]
):
    """
    Create new API key.
    """
    api_key = await api_key_services.create_api_key(user_id=current_user, name=api_key_in.name, session=session)
    logger.info(f"API key created: {api_key.key} for user {current_user.id}")
    return api_key


@api_key_router.put("/{id}", response_model=APIKeyResponse)
async def update_api_key(
    session: SessionDep,
    id: str,
    api_key_in: APIKeyUpdate,
    current_user: Annotated[UserModel, Depends(get_current_user)]
):
    """
    Update API key.
    """
    api_key = await api_key_services.update_api_key(
        session=session, update_data=api_key_in, api_key_id=id
    )
    logger.info(f"API key updated: {api_key.key} for user {current_user.id}")
    return api_key


@api_key_router.delete("/{id}", status_code=204)
async def delete_api_key(
    session: SessionDep,
    id: str,
    current_user: Annotated[UserModel, Depends(get_current_user)]
):
    """
    Delete API key.
    """
    api_key = await api_key_services.delete_api_key(session=session, api_key_id=id)
    return api_key
