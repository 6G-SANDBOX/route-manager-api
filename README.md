# Route Manager API

A REST API developed with FastAPI for managing network routes on a Linux machine using the `ip` command. It allows you to query active routes, create new routes, and delete existing routes, with token-based authentication and persistence of scheduled routes to ensure their availability even after service restarts.

## Table of Contents

- [Features](#features)
- [Repository Layout](#repository-layout)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Install uv](#2-install-uv)
  - [3. Create a Virtual Environment](#3-create-a-virtual-environment)
  - [4. (Optional) Create a systemd service](#4-optional-create-a-systemd-service)
- [Usage](#usage)
  - [Available Endpoints](#available-endpoints)
  - [Usage Examples with `curl`](#usage-examples-with-curl)
- [API Documentation](#api-documentation)
- [Logging](#logging)
- [Future development](#future-development)
- [Security Considerations](#security-considerations)
- [License](#license)

## Features

- **Query Active Routes:** Retrieve all active network routes on the Linux machine.
- **Create Routes:** Add new routes with options to schedule their creation and deletion.
- **Delete Routes:** Remove existing routes and unschedule their deletion.
- **Authentication:** Protect endpoints using a Bearer token for authentication.
- **Persistence:** Store scheduled routes in a SQLite database to ensure they are reloaded after service restarts.
- **Service:** Integrate with systemd to run the API as a system service.
- **Logging:** Detailed logging of operations and errors for monitoring and debugging.


## Repository Layout
```
├── LICENSE                # Licensing information for the repository
├── README.md              # The documentation you are reading right now
├── .devcontainer/         # (Optional) Configuration for devcontainers.
├── .env                   # (Optional) Sample configuration values to overwrite the defaults
├── app/                   # Main directory for the application code
│   ├── __init__.py            # Makes "app" a "Python package" (ignore it)
│   ├── core/                  # Configurations and global logic.
│   │   ├── __init__.py
│   │   ├── config.py              # Global application settings
│   │   ├── logging.py             # Global logging settings
│   ├── db/                    # Database-related modules and utilities
│   │   ├── __init__.py
│   │   ├── database.py            # Handles database connection and initialization
│   │   ├── models/                # Database models
│   │   │   ├── __init__.py
│   │   │   └── routes.py              # SQLModel for stored routes
│   │   └── routes.py              # Utilities for interaction with the routes database
│   ├── routers/               # Manage application routes
│   │   ├── __init__.py
│   │   └── routes.py              # Defines API endpoints for routes
│   ├── schemas/               # Pydantic models for data validation and serialization
│   │   ├── __init__.py
│   │   └── routes.py              # Main schemas for routes
│   ├── services/              # Auxiliary utilities and services for the API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py                # Functions related to user authentication and authorization
│   │   ├── routes.py              # Service functions for routes
│   │   └── utils.py               # Miscellaneous utility functions
│   ├── tests/                 # (Not yet implemented) Contains test modules
│   │   ├── __init__.py
│   │   └─── test_routes.py        # (Not yet implemented) Tests for the Routes module
│   ├── __init__.py
│   └── main.py                # Initializes the FastAPI application.
├── app_flow.drawio        # Visual representation of the API endpoints and expected behaviour of the app
├── pyproject.toml         # Python project configuration file used by tools like Poetry or uv (uv in our case)
└── uv.lock                # Lock file where uv manages app dependencies


```

## Prerequisites

- **Operating System:** Linux-based. Tested on Ubuntu 22.04 and Debian 12.
- **Python:** Version 3.12 or higher
- **Permissions:** Superuser permissions to manage network routes (capability `NET_ADMIN`) and to configure `systemd` services

## Installation
All steps are intended to be run as `root`.
### 1. Clone the Repository

Clone this repository to your local machine:

```bash
git https://github.com/6G-SANDBOX/route-manager-api /opt/route-manager-api
cd route-manager-api
```

### 2. Install uv

The tool `uv` will take care for everything python-releated, from python versions, to virtual enviroments and dependencies.
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. Create a Virtual Environment
Download all necessary dependencies in a virtual environment as specified in the `pyproject.toml` file using `uv`

```bash
uv sync
```

### 4. (Optional) Create a systemd service
To run the API as a system service, create a systemd unit file.
Uf you want to directly try the tool, run:
```bash 
uv run fastapi run --port 8172  # Default port is 8000
```

#### 4.1. Create the Unit File

Create a file named `route-manager-api.service` in `/etc/systemd/system/`:

```bash
cat > /etc/systemd/system/route-manager-api.service << 'EOF'
[Unit]
Description=A REST API developed with FastAPI for managing network routes on a Linux machine using the ip command. It allows you to query active routes, create new routes, and delete existing routes, with token-based authentication and persistence of scheduled routes to ensure their availability even after service restarts.
After=network.target

[Service]
Type=simple
User=root
Group=root
ExecStart=/root/.local/bin/uv --directory /opt/route-manager-api/ run fastapi run --port 8172
StandardOutput=append:/var/log/route_manager.log
StandardError=append:/var/log/route_manager.log
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
```

#### 4.2. Reload systemd and start the service

```bash
systemctl daemon-reload
systemctl enable route-manager-api.service
systemctl start route-manager-api.service
```

#### 4.3. Verify the service Status

```bash
systemctl status route-manager.service
```

You should see that the service is active and running. If there are any errors, they will appear in the output of this command.

## Usage

### Available Endpoints

The API offers the following endpoints:

- **GET /routes/:** Retrieve all active routes.
- **PUT /routes/:** Schedule the creation of a new route.
- **DELETE /routes/:** Delete an existing route and remove its schedule.
> WARNING: Beware the trailing slash

### Usage Examples with `curl`

#### Retrieve Active Routes

```bash
curl -X 'GET' \
  'http://localhost:8172/routes/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer this_is_something_secret'
```

**Successful Response:**
Code: `200`
```json
{
  "database_routes": [
    {
      "via": "192.168.215.100",
      "create_at": "2025-01-27T03:03:44.501824+00:00",
      "to": "10.10.2.10/32",
      "active": true,
      "dev": null,
      "delete_at": null
    },
    {
      "via": null,
      "create_at": "2027-01-30T09:38:59.284000+00:00",
      "to": "10.20.30.0/24",
      "active": false,
      "dev": "eth0",
      "delete_at": "2027-02-4T09:38:59.284000+00:00"
    }
  ],
  "system_routes": [
    "default via 192.168.215.1 dev eth0",
    "10.10.2.10/32 via 192.168.215.100 scope link",
    "192.168.215.0/24 dev eth0 proto kernel scope link src 192.168.215.2"
  ]
}
```

#### Add a Route

```bash
curl -X 'PUT' \
  'http://localhost:8172/routes/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer this_is_something_secret' \
  -H 'Content-Type: application/json' \
  -d '{
  "to": "10.10.2.10/32",
  "via": "192.168.215.100",
  "create_at": "2025-01-27T03:03:44.501824+00:00"
}'
```

**Successful Response:**
Code: `201`
```json
{
  "message": "Route succesfully added or scheduled"
}
```

**Route already exists:**
Also succesful to achieve idempotency
Code: `200`
```json
{
  "message": "A route to 10.10.2.10/32 already exists in the system"
}
```

#### Delete a Route

```bash
curl -X 'DELETE' \
  'http://localhost:8172/routes/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer this_is_something_secret' \
  -H 'Content-Type: application/json' \
  -d '{
  "to": "10.10.2.10"
}'
```

**Successful Response:**
Code: `200`
```json
{
  "message": "Route succesfully deleted"
}
```

**Route Not Found:**
Code: `404`
```json
{
  "detail": "Route to 10.10.2.10/32 not found in the database."
}
```

## API Documentation

FastAPI automatically generates interactive API documentation accessible at:

- **Swagger UI:** [http://localhost:8172/docs](http://localhost:8172/docs)
- **Redoc:** [http://localhost:8172/redoc](http://localhost:8172/redoc)


## Logging

The application logs detailed information about its operations and errors using Python's standard `logging` module. Logs include:

- Executed commands and their outputs.
- Route existence checks.
- Route creation and deletion operations.
- Database interactions.
- Authentication events.

### **Log File Location**

By default, logs are displayed in the console where the service is running. To redirect logs to a file, modify the logging configuration in `app/core/logging.py`:

```python
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
```

## Future development
#### Validation Loop
As seen in the `app_flow.drawio`, an internal loop will manage the lifecycle of routes stored in the database.

#### Exit Function
By default, the app will remove all routes added by it when terminating the service.
This will be an optional feature, that can be disabled with an envvar.

#### nftables exceptions
When using this component inside the 6G-Sandbox bastion, added routes should also create exceptions for the
highly restrictive firewall of the bastion.

#### Future iptools2 options
Currently, the integration of the following `ip route` subcommands:
- `metric`
- `table`
- `scope`
- `proto`
- `src`
- `nexthop`
- `onlink`
is not an urgent task, but the tool may be expanded to include them

#### Improve Documentation
Help is always welcomed, but yeah, some stuff might be improcise/wrong

## Security Considerations

- **Authentication Token:** The API uses a static token for Bearer authentication. Ensure you protect this token and change it to a secure value before deploying to production.
- **Input Validation:** While `pydantic` is used for data validation, consider implementing additional security measures as needed for your environment.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

**Note:** This project is designed for Linux environments with appropriate permissions to manage network routes. Ensure you understand the commands and configurations used before deploying to a production environment.
