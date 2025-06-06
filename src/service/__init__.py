from fastapi.security import OAuth2PasswordBearer

# --- Security scheme ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login") # This tokenUrl must match the actual login endpoint
