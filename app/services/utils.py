# app/services/utils.py
import logging
import ipaddress
import psutil
import subprocess
from fastapi import HTTPException
from app.schemas.routes import Route


logger = logging.getLogger(__name__)


def validate_route(route: Route) -> None:
    """
    Validates the route parameters to ensure they are safe.

    Args:
        route (Route): The route to validate.

    Raises:
        ValueError: If any parameter is invalid.
    """
    try:
        # Validate if destination is a valid IP address or subnet
        ipaddress.ip_network(route.destination, strict=False)
    except ValueError:
        raise ValueError(f"Invalid destination: {route.destination}")

    if route.gateway:
        try:
            # Validate if gateway is a valid IP address
            ipaddress.ip_address(route.gateway)
        except ValueError:
            raise ValueError(f"Invalid gateway: {route.gateway}")

    if route.interface:
        # Validate if interface exists in the system
        valid_interfaces =  psutil.net_if_addrs()
        if route.interface not in valid_interfaces:
            raise ValueError(f"Invalid network interface: {route.interface}")


def run_command(command: str) -> str:
    """
    Executes a shell command and returns its output.

    Args:
        command (str): The shell command to execute.

    Returns:
        str: The stdout of the command.

    Raises:
        HTTPException: If the command execution fails.
    """
    logger.info(f"Executing command: {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        output: str = result.stdout.decode('utf-8')
        logger.info(f"Command output: {output}")
        return output
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e.stderr.decode('utf-8')}")
        raise HTTPException(status_code=500, detail=f"Command failed: {e.stderr.decode('utf-8')}")


def route_exists(destination: str, gateway: str = None, interface: str = None) -> bool:
    """
    Checks if a specific route exists in the system.

    Args:
        destination (str): The destination network or host (e.g., "192.168.1.0/24").
        gateway (str, optional): The gateway for the route. Defaults to None.
        interface (str, optional): The interface for the route. Defaults to None.

    Returns:
        bool: True if the route exists, False otherwise.
    """
    command: str = "ip route show"
    output: str = run_command(command)

    # Build the search string
    search_str: str = destination
    if gateway:
        search_str += f" via {gateway}"
    if interface:
        search_str += f" dev {interface}"

    # Check if the route exists in the command output
    exists: bool = search_str in output
    logger.info(f"Route '{search_str}' {'DOES' if exists else 'DOES NOT'} currently exist")
    return exists
