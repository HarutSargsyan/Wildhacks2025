# How to launch the app with docker

# Setup environement

Run this command to create a virtual environment and install the dependencies:

```bash
# Create a virtual environment
# This will create a new directory called .venv in the current directory
# and install the dependencies in that directory
python3 -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

### Build docker image and run the container
# 1. Build the docker image
docker build -t my-fastapi-app .

# 2. Run the docker container
docker run -d  -p 8000:80 --name fastapi-dev my-fastapi-app

