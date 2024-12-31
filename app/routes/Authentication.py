from fastapi import HTTPException, status, APIRouter
from starlette.responses import JSONResponse

from app.entity.PydanticModel import UserLogin, UserCreate
from app.operation.CRUD import authenticate_user, get_user_details, create_user
from app.operation.JwtTokenCreation import create_access_token

router = APIRouter(tags=["Original"])


@router.post("/login", status_code=status.HTTP_201_CREATED)
def login_for_access_token(form_data: UserLogin):
    try:
        user = authenticate_user(form_data.email, form_data.password)
        if not user:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "cIntResponseStatus": status.HTTP_401_UNAUTHORIZED,
                }
            )
        access_token = create_access_token(data={"sub": user.email})

        if (access_token):
            access_token_token = {"access_token": access_token, "token_type": "bearer"}
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={
                    "cIntResponseStatus": status.HTTP_201_CREATED,
                    "cObjResponseData": access_token_token
                }
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "cIntResponseStatus": status.HTTP_500_INTERNAL_SERVER_ERROR,

                }
            )
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/create_user", status_code=status.HTTP_201_CREATED)
async def create_user_data(create_user_request: UserCreate):
    try:
        existing_user = get_user_details(create_user_request.email, create_user_request.username)

        if existing_user:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "cIntResponseStatus": status.HTTP_400_BAD_REQUEST,
                    "message": 'User already exists'
                }
            )

        created_user = create_user(user=create_user_request)
        if (created_user):
            created_user_response = {"message": "User created successfully", "user": created_user}
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={
                    "cIntResponseStatus": status.HTTP_201_CREATED,
                    "cObjResponseData": created_user_response
                }
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "cIntResponseStatus": status.HTTP_500_INTERNAL_SERVER_ERROR,

                }
            )

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
