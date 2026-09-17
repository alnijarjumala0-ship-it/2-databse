#!/usr/bin/env python3
"""
Startup script for FastAPI MVC Backend.
Run this script to start the application server.
"""
import subprocess
import sys
import os


def main():
    """Start the FastAPI application."""
    print("=" * 60)
    print("  FastAPI MVC Backend - Starting Server")
    print("=" * 60)
    print(f"  Host: 0.0.0.0")
    print(f"  Port: 8000")
    print(f"  Docs: http://localhost:8000/docs")
    print(f"  Admin: http://localhost:8000/admin")
    print("=" * 60)
    print()

    # Run uvicorn
    cmd = [
        sys.executable, "-m", "uvicorn",
        "main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload",
    ]

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nServer stopped.")
        sys.exit(0)


if __name__ == "__main__":
    main()