from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# IMPORT ROUTERS CORRECTLY
from routes.user import router as user_router
from routes.admin import router as admin_router

app = FastAPI()

# CORS settings - MUST be added BEFORE routers and static files
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4300",
        "http://localhost:4200",
        "http://127.0.0.1:4300",
        "http://127.0.0.1:4200",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Static hosting for uploaded profile images
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Register routers
app.include_router(user_router)
app.include_router(admin_router)
