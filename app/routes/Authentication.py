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

# @router.post("/request_password_reset", status_code=status.HTTP_200_OK)
# async def request_password_reset(email: str):
#     try:
#         # Find the user by email
#         user = get_user_details(user_email=email)
#
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")
#
#         # Generate a password reset token (JWT)
#         reset_token = create_access_token(data={"sub": user.email})
#
#         # TODO: Implement email sending logic here to send the reset_token
#         # For now, we'll just return the token (in a real app, you'd email it)
#         return {"message": "Password reset link sent to your email", "reset_token": reset_token}
#     except HTTPException as http_ex:
#         raise http_ex
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         raise HTTPException(status_code=500, detail="Internal server error")

# @router.post("/reset_password", status_code=status.HTTP_200_OK)
# async def reset_password(reset_token: str, new_password: str):
#     try:
#         # Retrieve the user by reset token
#         user = get_user_details(user_email=email)
#
#         db = next(get_db())
#         user = db.query(Users).filter(Users.reset_token == reset_token).first()
#
#         if not user or user.reset_token_expiration < datetime.utcnow():
#             raise HTTPException(status_code=400, detail="Invalid or expired token")
#
#         # Hash the new password
#         hashed_password = get_password_hash(new_password)
#         user.hashed_password = hashed_password
#         user.reset_token = None  # Invalidate the reset token
#         user.reset_token_expiration = None
#         db.commit()
#
#         return {"message": "Password reset successfully"}
#     except HTTPException as http_ex:
#         raise http_ex
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         raise HTTPException(status_code=500, detail="Internal server error")

# @router.post("/request_reset", status_code=status.HTTP_200_OK)
# async def request_reset(email: str):
#     try:
#         user = get_user_details(user_email=email)
#
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")
#
#         # Generate and send reset token
#         token = create_reset_token(user.id)
#
#         # In a real application, you would send an email with the reset link
#         print(f"Reset token for {email}: {token}")
#
#         return {"message": "Reset instructions sent"}
#     except HTTPException as http_ex:
#         raise http_ex
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         raise HTTPException(status_code=500, detail="Internal server error")
