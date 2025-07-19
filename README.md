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

The application will be available at `http://localhost:5235` (by default).

## API Usage

You can get a random image by using the following API endpoint format. The API will act as a proxy and directly return the image.

**API Endpoint:**
`http://localhost:5235/api/v1/random/YOUR_API_KEY`

Replace `YOUR_API_KEY` with a key you generated in the "API Key Management" tab.

## Configuration

You can configure the application by creating a `.env` file in the root directory. You can copy `.env.example` to create it.

-   `BACKEND_PORT`: Sets the port for the server. If you change this, remember to update the API endpoint address.

**Note:** If you change the backend port, you will also need to manually update the `baseURL` in `frontend/src/services/api.js` to match the new address for the web interface to work.

## Default Admin Credentials

-   **Username:** admin
-   **Password:** admin