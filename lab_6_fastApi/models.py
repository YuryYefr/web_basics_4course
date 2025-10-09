from sqlmodel import Field, SQLModel, Relationship
import datetime as dt



class Company(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str = Field()
    address: str = Field(
        default=None
    )
    client: bool = Field(default=None)
    contractor: bool = Field(default=None)
    contracts: list["Contract"] = Relationship(back_populates="company")

    def __str__(self):
        return self.name

class Client(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    address: str = Field(
        default=None,
    )
    contracts: list["Contract"] = Relationship(back_populates="client")

    def __str__(self):
        return self.name

class Contract(SQLModel, table=True):
    id: int = Field(primary_key=True)
    company_id: int = Field(foreign_key="company.id")
    client_id: int = Field(foreign_key="client.id")
    amount: float
    date: dt.date = Field(default=None, description='Date when contract ends')
    company: Company = Relationship(back_populates="contracts")
    client: Client = Relationship(back_populates="contracts")

    def __str__(self):
        return f"{self.company.name} - {self.client.name} - {self.amount} - {self.date}"
