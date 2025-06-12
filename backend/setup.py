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
        "fastapi==0.68.2",
        "uvicorn[standard]==0.15.0",
        "python-multipart==0.0.20",
        "python-dotenv==1.0.0",
        "sqlmodel==0.0.11",
        "sqlalchemy==1.4.54",
        "sounddevice==0.5.2",
        "numpy==1.23.5",
        "aiofiles==0.7.0",
        "tensorflow==2.12.0",
        "tensorflow-hub==0.13.0",
        "soundfile==0.12.1",
        "librosa==0.10.1",
        "resampy==0.3.1",
        "httpx==0.19.0",
        "jinja2==3.0.3",
        "websockets==10.0",
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
