# How to launch the app with docker

# 1. Build the docker image
docker build -t my-fastapi-app .

# 2. Run the docker container
docker run -d  -p 8000:80 --name fastapi-dev my-fastapi-app

