import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


class CreateUserRequest(BaseModel):
    username: str = Field(..., example="Test")
    enabled: bool = Field(..., example=True)
    email: str = Field(..., example="test@anqorithm.com")
    firstName: str = Field(..., example="Test")
    lastName: str = Field(..., example="Test")
    realmRoles: Optional[List[str]] = Field(default_factory=list)


class UpdateUserRequest(BaseModel):
    enabled: bool = Field(..., example=False)


@app.post("/users/")
async def create_user(user: CreateUserRequest):
    token = await fetch_token()
    create_url = f"{KEYCLOAK_URL}/admin/realms/{REALM}/users"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    user_data = user.dict()
    user_data["disableableCredentialTypes"] = []
    user_data["requiredActions"] = []
    user_data["notBefore"] = 0
    user_data["access"] = {
        "manageGroupMembership": True,
        "view": True,
        "mapRoles": True,
        "impersonate": True,
        "manage": True,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(create_url, headers=headers, json=user_data)
        if response.status_code != 201:
            logger.error("Failed to create user: %s", response.text)
            raise HTTPException(
                status_code=response.status_code, detail="Could not create user"
            )

        logger.info("User created successfully.")
        return JSONResponse(content={"message": "User created successfully."})


@app.put("/users/{user_id}")
async def update_user(user_id: str, user: UpdateUserRequest):
    token = await fetch_token()
    update_url = f"{KEYCLOAK_URL}/admin/realms/{REALM}/users/{user_id}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Prepare the payload based on the UpdateUserRequest model
    payload = user.dict()
    async with httpx.AsyncClient() as client:
        response = await client.put(update_url, headers=headers, json=payload)
        if response.status_code != 204:
            logger.error("Failed to update user: %s", response.text)
            raise HTTPException(
                status_code=response.status_code, detail="Could not update user"
            )

        logger.info("User updated successfully.")
        return JSONResponse(content={"message": "User updated successfully."})


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
