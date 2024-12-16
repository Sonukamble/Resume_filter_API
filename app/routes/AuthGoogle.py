from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter
from starlette.config import Config

from app.Configuration import Config

config_data = {'GOOGLE_CLIENT_ID': Config.GOOGLE_CLIENT_ID, 'GOOGLE_CLIENT_SECRET': Config.GOOGLE_CLIENT_SECRET}
starlette_config = Config(environ=config_data)
oauth = OAuth(starlette_config)

google = oauth.register(
    name='google',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri='http://localhost:5020/auth/callback',
    client_kwargs={'scope': 'openid profile email'},
)

auth_router_5 = APIRouter()

# @auth_router.get("/auth/login")
# async def login_via_google(request: Request):
#     try:
#         redirect_uri = request.url_for('auth_callback')
#         return await oauth.google.authorize_redirect(request, redirect_uri)
#     except Exception as ex:
#         print(ex)
#
#
# @auth_router.post("/auth/callback")
# async def auth_callback(request: Request):
#     try:
#         # Extract the tokenId from the request body
#         body = await request.json()
#         token_id = body.get('tokenId')
#
#         if not token_id:
#             raise HTTPException(status_code=400, detail="No token provided")
#
#         # Verify the token using Google's OAuth2 API
#         try:
#             token_data = id_token.verify_oauth2_token(token_id, requests.Request(), google_client_id)
#         except ValueError:
#             raise HTTPException(status_code=400, detail="Invalid token")
#
#         if not token_data:
#             raise HTTPException(status_code=400, detail="Failed to authenticate")
#
#         # Extract user information from the token
#         user_data = {
#             "username": token_data['name'],
#             "email": token_data['email'],
#             "google_id": token_data['sub'],  # Use Google ID to uniquely identify users
#         }
#
#         # Add your logic to handle user creation or lookup
#         existing_user = get_user_details(user_data['email'])
#
#         if not existing_user:
#             created_user = create_user(UserCreate(
#                 username=user_data['username'],
#                 email=user_data['email'],
#                 password=None,  # No password needed for Google login
#                 google_id=user_data['google_id']
#             ))
#
#         # Create a session or JWT token for the user
#         access_token = create_access_token({"sub": user_data["email"]})
#         return {"access_token": access_token, "token_type": "bearer"}
#     except Exception as ex:
#         print(ex)
