# app/utils.py
import subprocess
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

def run_command(command: str) -> str:
    logger.info(f"Executing command: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        logger.info(f"Command output: {output}")
        return output
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e.stderr.decode('utf-8')}")
        raise HTTPException(status_code=500, detail=f"Command failed: {e.stderr.decode('utf-8')}")

def route_exists(destination: str, gateway: str = None, interface: str = None) -> bool:
    command = "ip route show"
    output = run_command(command)
    search_str = f"{destination}"
    if gateway:
        search_str += f" via {gateway}"
    if interface:
        search_str += f" dev {interface}"
    exists = search_str in output
    logger.info(f"Route exists check: {'Yes' if exists else 'No'} for {search_str}")
    return exists
