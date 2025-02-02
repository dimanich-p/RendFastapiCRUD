from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi.middleware.cors import CORSMiddleware

# SQLite database URL
DATABASE_URL = "sqlite:///./clientsDB.db"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create a SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy models
Base = declarative_base()

# Define the Clients model
class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String, index=True)

# Create the database tables
Base.metadata.create_all(bind=engine)

# Pydantic model for request/response validation
class ClientCreate(BaseModel):
    name: str
    email: str
    phone: str

class ClientResponse(ClientCreate):
    id: int

    class Config:
        from_attributes = True

# FastAPI app instance
app = FastAPI()



# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://dimanich-p.github.io"],  # Allow origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Clients API"}

# Get all clients
@app.get("/clients/", response_model=list[ClientResponse])
def get_clients(db: Session = Depends(get_db)):
    clients = db.query(Client).all()
    return clients

# Get a single client by ID
@app.get("/clients/{client_id}", response_model=ClientResponse)
def get_client(client_id: int, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

# Create a new client
@app.post("/clients/", response_model=ClientResponse)
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    db_client = Client(**client.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

# Update a client by ID
@app.put("/clients/{client_id}", response_model=ClientResponse)
def update_client(client_id: int, client: ClientCreate, db: Session = Depends(get_db)):
    db_client = db.query(Client).filter(Client.id == client_id).first()
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    db_client.name = client.name
    db_client.email = client.email
    db_client.phone = client.phone
    db.commit()
    db.refresh(db_client)
    return db_client

# Delete a client by ID
@app.delete("/clients/{client_id}", response_model=ClientResponse)
def delete_client(client_id: int, db: Session = Depends(get_db)):
    db_client = db.query(Client).filter(Client.id == client_id).first()
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    db.delete(db_client)
    db.commit()
    return db_client