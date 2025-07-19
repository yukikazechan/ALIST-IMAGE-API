# Alist Image API

This project is an image management service with a frontend and a backend.

## Features

- User authentication
- Image upload and management
- Tagging and searching images
- API key management for accessing images

## Prerequisites

- Python 3
- Node.js and npm

## Installation and Startup

Run the installation script. This will install all dependencies and start the application automatically.
-   For Windows, run `install.bat`.
-   For Linux and macOS, run `chmod +x install.sh` and then `./install.sh`.

The application will be available at `http://localhost:5235` (by default). Please open this address in your browser to use the application.

## Configuration

You can configure the application by creating a `.env` file in the root directory of the package. You can copy the `.env.example` file to create it.

-   `BACKEND_PORT`: Sets the port for the backend server.

**Note:** If you change the backend port, you will also need to manually update the `baseURL` in `frontend/src/services/api.js` to match the new address.

## Default Admin Credentials

-   **Username:** admin
-   **Password:** admin