from fastapi import HTTPException, status, APIRouter

from app.operation.CRUD import get_user_details, update_created_user
from app.operation.JwtTokenCreation import create_access_token
from app.operation.ResetOperation import send_email

reset_router = APIRouter(tags=["reset"])


@reset_router.post("/request_password_reset", status_code=status.HTTP_200_OK)
async def request_password_reset(email: str):
    try:
        # Find the user by email
        user = get_user_details(user_email=email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Generate a password reset token (JWT)
        reset_token = create_access_token(data={"sub": user['username']})

        # Store the reset token and expiration in the user record
        updated_response = update_created_user(user_email=user["email"], reset_token=reset_token)
        if updated_response:
            send_email(user["email"], reset_token)

        return {"message": "Password reset link sent to your email"}
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
