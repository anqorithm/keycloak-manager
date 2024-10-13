# Keycloak User Management API

This is a FastAPI application that provides endpoints to manage users in Keycloak. It includes functionalities to fetch users, update user details, and delete users.

## Table of Contents

- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Endpoints](#endpoints)
  - [Root Endpoint](#root-endpoint)
  - [Get Users](#get-users)
  - [Update User](#update-user)
  - [Delete User](#delete-user)
- [Running the Application](#running-the-application)
- [License](#license)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/keycloak-user-management-api.git
   cd keycloak-user-management-api
   ```

2. Install dependencies using Poetry:

   ```bash
   poetry install
   ```

3. Create a `.env` file in the root directory with the following variables:

   ```env
   KEYCLOAK_URL=https://sso.anqorithm.com
   CLIENT_ID=admin-cli
   USERNAME=your-username
   PASSWORD=your-password
   REALM=master
   ```

## Environment Variables

The following environment variables are required:

- `KEYCLOAK_URL`: The base URL of your Keycloak server.
- `CLIENT_ID`: The client ID used for authentication.
- `USERNAME`: Your Keycloak username.
- `PASSWORD`: Your Keycloak password.
- `REALM`: The realm to operate within.

## Endpoints

### Root Endpoint

- **GET `/`**
  
  Returns a welcome message.

  **Response:**

  ```json
  {
    "message": "Welcome to the Keycloak User Management API"
  }
  ```

### Get Users

- **GET `/users/`**
  
  Retrieves all users from the specified Keycloak realm.

  **Response:**

  Returns a list of users in JSON format.

### Update User

- **PUT `/users/{user_id}`**

  Updates the details of a user.

  **Request Body:**

  ```json
  {
    "id": "user-id",
    "enabled": false
  }
  ```

  **Response:**

  ```json
  {
    "message": "User updated successfully."
  }
  ```

### Delete User

- **DELETE `/users/{user_id}`**

  Deletes a user from Keycloak.

  **Response:**

  ```json
  {
    "message": "User deleted successfully."
  }
  ```

## Running the Application

To run the FastAPI application locally, use the following command:

```bash
python main.py
```

The application will be available at `http://127.0.0.1:8000`.

If you're using Docker, you can build and run the application with:

```bash
docker-compose up --build
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
