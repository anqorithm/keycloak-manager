import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import httpx
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

KEYCLOAK_URL = os.getenv("KEYCLOAK_URL")
CLIENT_ID = os.getenv("CLIENT_ID")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
REALM = os.getenv("REALM")


async def fetch_token() -> str:
    token_url = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token"
    data = {
        "client_id": CLIENT_ID,
        "username": USERNAME,
        "password": PASSWORD,
        "grant_type": "password",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data)
        if response.status_code != 200:
            logger.error("Failed to fetch token: %s", response.text)
            raise HTTPException(
                status_code=response.status_code, detail="Could not fetch token"
            )

        token_data = response.json()
        logger.info("Token fetched successfully.")
        return token_data["access_token"]


@app.get("/")
async def root():
    return {"message": "Welcome to the Keycloak User Management API"}


@app.get("/users/")
async def get_users():
    token = await fetch_token()
    users_url = f"{KEYCLOAK_URL}/admin/realms/{REALM}/users"
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(users_url, headers=headers)
        if response.status_code != 200:
            logger.error("Failed to fetch users: %s", response.text)
            raise HTTPException(
                status_code=response.status_code, detail="Could not fetch users"
            )

        users_data = response.json()
        logger.info("Users fetched successfully.")
        return JSONResponse(content=users_data)


class UpdateUserRequest(BaseModel):
    id: str
    enabled: bool


# Other imports and initial setup remain unchanged


@app.put("/users/{user_id}/enable")
async def enable_user(user_id: str):
    token = await fetch_token()
    enable_url = f"{KEYCLOAK_URL}/admin/realms/{REALM}/users/{user_id}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"enabled": True}

    async with httpx.AsyncClient() as client:
        response = await client.put(enable_url, headers=headers, json=payload)
        if response.status_code != 204:
            logger.error("Failed to enable user: %s", response.text)
            raise HTTPException(
                status_code=response.status_code, detail="Could not enable user"
            )

        logger.info("User enabled successfully.")
        return JSONResponse(content={"message": "User enabled successfully."})


@app.put("/users/{user_id}/disable")
async def disable_user(user_id: str):
    token = await fetch_token()
    disable_url = f"{KEYCLOAK_URL}/admin/realms/{REALM}/users/{user_id}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"enabled": False}

    async with httpx.AsyncClient() as client:
        response = await client.put(disable_url, headers=headers, json=payload)
        if response.status_code != 204:
            logger.error("Failed to disable user: %s", response.text)
            raise HTTPException(
                status_code=response.status_code, detail="Could not disable user"
            )

        logger.info("User disabled successfully.")
        return JSONResponse(content={"message": "User disabled successfully."})


@app.delete("/users/{user_id}")
async def delete_user(user_id: str):
    token = await fetch_token()
    delete_url = f"{KEYCLOAK_URL}/admin/realms/{REALM}/users/{user_id}"
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:
        response = await client.delete(delete_url, headers=headers)
        if response.status_code != 204:
            logger.error("Failed to delete user: %s", response.text)
            raise HTTPException(
                status_code=response.status_code, detail="Could not delete user"
            )

        logger.info("User deleted successfully.")
        return JSONResponse(content={"message": "User deleted successfully."})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
