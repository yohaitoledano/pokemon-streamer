from setuptools import setup, find_packages

setup(
    name="gurdio",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn==0.24.0",
        "httpx==0.25.1",
        "protobuf==4.25.1",
        "pydantic==2.4.2",
        "pytest==7.4.3",
        "pytest-asyncio==0.21.1"
    ],
) 