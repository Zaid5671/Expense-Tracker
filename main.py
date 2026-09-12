from fastapi import FastAPI
from database import engine
from models import base
from routers import auth, categories, expenses

# Create all database tables automatically on startup
base.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Expense Tracker API")

# Include routers
app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(expenses.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Expense Tracker API!"}
