from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README.md
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="soundtracker-backend",
    version="0.1.0",
    packages=find_packages(include=['backend', 'backend.*']),
    package_data={
        'backend': ['*.py', '*.json', 'templates/*', 'static/*'],
    },
    include_package_data=True,
    install_requires=[
        "fastapi>=0.68.0,<0.69.0",
        "uvicorn>=0.15.0,<0.16.0",
        "python-multipart>=0.0.5,<0.1.0",
        "python-dotenv>=0.19.0,<0.20.0",
        "sqlmodel>=0.0.8,<0.1.0",
        "sqlalchemy>=1.4.0,<2.0.0",
        "sounddevice>=0.4.4,<0.5.0",
        "numpy>=1.21.0,<2.0.0",
        "aiofiles>=23.2.1,<24.0.0",
    ],
    python_requires=">=3.8",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="",
    author_email="",
    description="Backend for SoundTracker application",
    keywords="audio monitoring sound classification",
    url="",
    project_urls={
        "Source": "",
    },
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
