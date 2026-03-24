from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.data.models.token import Token
from src.constants import DB_URL

engine = create_async_engine(DB_URL, echo=True, future=True)

async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_token(id: UUID) -> Token | None:
    async with async_session() as session, session.begin():
        result = await session.execute(select(Token).where(Token.id == id).options())
        return result.scalar()


async def insert_token(new_token: Token) -> None:
    async with async_session() as session, session.begin():
        session.add(new_token)


async def update_token(token: Token) -> None:
    async with async_session() as session, session.begin():
        result = await session.execute(select(Token).where(Token.id == token.id).options())
        token_to_update: Token = result.scalar()
        token_to_update.status = token.status
