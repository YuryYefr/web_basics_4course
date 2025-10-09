""" Варіант 16
Спроектувати базу даних про договори: назва фірми-клієнта, вид договору, термін дії."""

from fastapi import FastAPI, Depends
from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List

from models import Company, Contract, Client
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel
from sqladmin import Admin, ModelView


# always yield to allow for app startup
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Startup: Creating database and tables...")
    await create_db_and_tables()
    yield
    print("Shutdown: App is closing.")


app = FastAPI(lifespan=lifespan)

sqlite_file_name = "companies.db"
sqlite_url = f"sqlite+aiosqlite:///{sqlite_file_name}"
engine = create_async_engine(sqlite_url, echo=True)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


# adding UI
class CompanyAdmin(ModelView, model=Company):
    name = "Company"
    name_plural = "Companies"
    column_list = [Company.id, Company.name, Company.address]
    column_searchable_list = [Company.name]
    column_sortable_list = [Company.id, Company.name]


class ContractAdmin(ModelView, model=Contract):
    column_list = [Contract.id, Contract.date]
    column_searchable_list = [Contract.client_id, Contract.company_id]
    column_sortable_list = [Contract.id]


class ClientAdmin(ModelView, model=Client):
    column_list = [Client.id, Client.name, Client.address]
    column_searchable_list = [Client.name]
    column_sortable_list = [Client.id, Client.name]


admin = Admin(app, engine)
admin.add_view(CompanyAdmin)
admin.add_view(ContractAdmin)
admin.add_view(ClientAdmin)


async def get_session():
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with AsyncSessionLocal() as session:
        yield session


@app.get("/companies/", response_model=List[Company])
async def read_companies(session: AsyncSession = Depends(get_session)):
    companies = await session.execute(select(Company))
    return companies


@app.post("/companies/", response_model=Company)
async def create_company(company: Company, session: AsyncSession = Depends(get_session)):
    session.add(company)
    await session.commit()
    await session.refresh(company)
    return company


@app.get("/contracts/", response_model=List[Contract])
async def read_contracts(contract: Contract, session: AsyncSession = Depends(get_session)):
    session.add(contract)
    contracts = await session.execute(select(Contract))
    return contracts


@app.post("/contracts/", response_model=Contract)
async def create_contract(contract: Contract, session: AsyncSession = Depends(get_session)):
    session.add(contract)
    await session.commit()
    await session.refresh(contract)
    return contract
