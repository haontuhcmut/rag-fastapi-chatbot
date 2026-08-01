from fastapi import APIRouter
from app.core.dependency import SessionDep
from app.utility.search import SearchServices
from app.config import Config

PSYCOPG_CONNECT = Config.PSYCOPG_CONNECT

search_services = SearchServices(PSYCOPG_CONNECT, "embedding")
search_router = APIRouter()

@search_router.get("/")
async def vector_search(query: str, session:SessionDep):
    response = await search_services.mmr_search(query=query, session=session)
    return response