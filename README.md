# Route Manager API

A REST API developed with FastAPI for managing network routes on a Linux machine using the `ip` command. It allows you to query active routes, create new routes, and delete existing routes, with token-based authentication and persistence of scheduled routes to ensure their availability even after service restarts.

## Table of Contents

- [Features](#features)
- [Repository Layout](#repository-layout)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Create and Activate a Virtual Environment](#2-create-and-activate-a-virtual-environment)
  - [3. Install Dependencies](#3-install-dependencies)
  - [4. Configure the Database](#4-configure-the-database)
  - [5. Configure the systemd Service](#5-configure-the-systemd-service)
- [Usage](#usage)
  - [Available Endpoints](#available-endpoints)
  - [Usage Examples with `curl`](#usage-examples-with-curl)
- [API Documentation](#api-documentation)
- [Logging](#logging)
- [Security Considerations](#security-considerations)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Query Active Routes:** Retrieve all active network routes on the Linux machine.
- **Create Routes:** Add new routes with options to schedule their creation and deletion.
- **Delete Routes:** Remove existing routes and unschedule their deletion.
- **Authentication:** Protect endpoints using a Bearer token for authentication.
- **Persistence:** Store scheduled routes in a SQLite database to ensure they are reloaded after service restarts.
- **systemd Service:** Integrate with systemd to run the API as a system service.
- **Logging:** Detailed logging of operations and errors for monitoring and debugging.
- **OpenAPI Documentation:** An `openapi.yaml` file describing the API specifications.

## Repository Layout
```
route-manager-api/
├── .devcontainer/           # (Optional) Configuration for devcontainers.
├── app/                     # Contains the main application files.
│   ├── __init__.py          # Makes "app" a "Python package"
│   ├── core/                # Configurations and global logic.
│   │   ├── __init__.py
│   │   ├── config.py        # Global configuration of the application
│   │   ├── logging.py       # (Not yet implemented) Logging configuration
│   │   └── scheduler.py     # Task scheduler functions and configuration
│   ├── db/                  # Database settings
│   │   ├── __init__.py
│   │   ├── database.py      # SQLAlchemy configuration
│   │   └── models/          # Contains database model modules
│   │       ├── __init__.py
│   │       └── routes.py    # Defines database models for Routes
│   ├── routers/             # Contains router modules
│   │   ├── __init__.py
│   │   └── routes.py        # Defines endpoints related to Routes
│   ├── schemas/             # Contains Pydantic schema modules
│   │   ├── __init__.py
│   │   └── routes.py        # Defines schemas for Routes
│   ├── services/            # Checkout logic and auxiliary services
│   │   ├── __init__.py
│   │   ├── auth.py          # Functions related to user authentication and authorization
│   │   ├── routes.py        # Auxiliary functions for the API endpoints
│   │   └── utils.py         # General auxiliary functions
│   ├── tests/               # (Not yet implemented) Contains test modules
│   │   ├── __init__.py
│   │   └─── test_routes.py  # (Not yet implemented) Tests for the Routes module
│   ├── __init__.py
│   └── main.py              # Initializes the FastAPI application.
├── .env                     # (Optional) Default configuration values
├── .gitignore
├── .python-version
├── LICENSE
├── pyproject.toml
├── README.md
└── uv.lock

```

## Prerequisites

- **Operating System:** Linux
- **Python:** Version 3.7 or higher
- **Permissions:** Superuser permissions to manage network routes and configure systemd services.

## Installation

### 1. Clone the Repository

Clone this repository to your local machine:

```bash
git https://github.com/6G-SANDBOX/route-manager-api
cd route-manager-api
```

### 2. Create and Activate a Virtual Environment

It's recommended to use a virtual environment to manage the project's dependencies.

```bash
uv run -m app.main

python3 -m venv routemgr
source routemgr/bin/activate
```

### 3. Install Dependencies

Install all necessary dependencies using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

**Contents of `requirements.txt`:**

```plaintext
fastapi==0.112.2
pydantic==2.8.2
apscheduler==3.10.4
SQLAlchemy==2.0.32
```

### 4. Configure the Database

The project uses SQLite to persist scheduled routes. The database is created automatically when you start the application. No additional configuration is required.

### 5. Configure the systemd Service

To run the API as a system service, create a systemd unit file.

#### 5.1. Create the Unit File

Create a file named `route-manager.service` in `/etc/systemd/system/`:

```bash
sudo nano /etc/systemd/system/route-manager.service
```

#### 5.2. Add Content to the File

Replace `/path/to/your/app` with the directory where your `main.py` file is located:

```ini
[Unit]
Description=Route Manager Service
After=network.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/path/to/your/app
ExecStart=/usr/bin/python3 main.py
Restart=on-failure
RestartSec=10s
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

**Note:** Ensure that the user and group (`root` in this case) have the appropriate permissions for the application directory.

#### 5.3. Reload systemd and Start the Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable route-manager.service
sudo systemctl start route-manager.service
```

#### 5.4. Verify the Service Status

```bash
sudo systemctl status route-manager.service
```

You should see that the service is active and running. If there are any errors, they will appear in the output of this command.

## Usage

### Available Endpoints

The API offers the following endpoints:

- **GET /routes:** Retrieve all active routes.
- **POST /routes:** Schedule the creation of a new route.
- **DELETE /routes:** Delete an existing route and remove its schedule.

### Usage Examples with `curl`

#### Retrieve Active Routes

```bash
curl -X GET "http://localhost:8172/routes" \
-H "Authorization: Bearer this_is_something_secret" \
-H "Accept: application/json"
```

**Successful Response:**

```json
{
  "routes": [
    "default via 192.168.1.1 dev eth0",
    "192.168.1.0/24 dev eth0 proto kernel scope link src 192.168.1.100"
  ]
}
```

#### Add a Scheduled Route

```bash
curl -X POST "http://localhost:8172/routes" \
-H "Authorization: Bearer this_is_something_secret" \
-H "Content-Type: application/json" \
-d '{
  "destination": "192.168.20.0/24",
  "gateway": "192.168.2.1",
  "interface": "eth0",
  "create_at": "2024-10-10T12:00:00",
  "delete_at": "2024-10-10T18:00:00"
}'
```

**Successful Response:**

```json
{
  "message": "Route scheduled successfully"
}
```

#### Delete a Route

```bash
curl -X DELETE "http://localhost:8172/routes" \
-H "Authorization: Bearer this_is_something_secret" \
-H "Content-Type: application/json" \
-d '{
  "destination": "192.168.2.0/24",
  "gateway": "192.168.2.1",
  "interface": "eth0"
}'
```

**Successful Response:**

```json
{
  "message": "Route deleted and removed from schedule"
}
```

**Response When Route Not Found:**

```json
{
  "detail": "Route not found"
}
```

## API Documentation

FastAPI automatically generates interactive API documentation accessible at:

- **Swagger UI:** [http://localhost:8172/docs](http://localhost:8172/docs)
- **Redoc:** [http://localhost:8172/redoc](http://localhost:8172/redoc)

Additionally, an `openapi.yaml` file is provided that describes the OpenAPI specification of the API.

### **Using Swagger UI**

Open your browser and visit [http://localhost:8000/8172](http://localhost:8172/docs) to interact with the API through the Swagger UI interface.

## Logging

The application logs detailed information about its operations and errors using Python's standard `logging` module. Logs include:

- Executed commands and their outputs.
- Route existence checks.
- Route creation and deletion operations.
- Database interactions.
- Authentication events.

### **Log File Location**

By default, logs are displayed in the console where the service is running. To redirect logs to a file, modify the logging configuration in `main.py`:

```python
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
```

## Security Considerations

- **Authentication Token:** The API uses a static token for Bearer authentication. Ensure you protect this token and change it to a secure value before deploying to production.
- **Input Validation:** While `pydantic` is used for data validation, consider implementing additional security measures as needed for your environment.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

**Note:** This project is designed for Linux environments with appropriate permissions to manage network routes. Ensure you understand the commands and configurations used before deploying to a production environment.
