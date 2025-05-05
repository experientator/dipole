from sqlmodel import create_engine, SQLModel

engine = create_engine("postgresql://postgres:postgres@localhost:5432/dipole", echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)
