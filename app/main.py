# from fastapi import FastAPI
# from app.Configuration import Config
#
# app = FastAPI()
#
# @app.get("/")
# def read_root():
#     return {
#         "message": f"The constant is: {Config.MY_CONSTANT}",
#         "api_version": Config.API_VERSION
#     }

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from app.routes.Authentication import router
from app.routes.FileUpload import file_router
from app.routes.History import chat_history_router
from app.routes.Question import question_router
from app.routes.ResetRequest import reset_router
from app.without_auth_router.route.UploadFile import file_router_without_auth

# Create FastAPI app instance
app = FastAPI(
    title="Resume Filter API",
    version="1.0.0",
    description="API for Resume Filtering",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Page not found"
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Validation error"
        }
    }
)

# CORS Middleware configuration
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(router)
app.include_router(reset_router)
app.include_router(file_router)
app.include_router(question_router)
app.include_router(chat_history_router)
app.include_router(file_router_without_auth)

@app.get("/")
def read_root():
    return {
        "message": f"The constant is: correct"
    }