# Backend API

This is a Flask-based backend API with Google OAuth authentication and MongoDB integration.

## Setup

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
- Copy `.env.example` to `.env`
- Update the values in `.env` with your actual configuration:
  - `SECRET_KEY`: A secure random string
  - `MONGO_URL`: Your MongoDB connection string
  - `GOOGLE_CLIENT_ID`: Your Google OAuth client ID
  - `GOOGLE_CLIENT_SECRET`: Your Google OAuth client secret
  - `FRONTEND_URL`: Your frontend application URL

4. Set up Google OAuth:
- Go to the Google Cloud Console
- Create a new project or select an existing one
- Enable the Google+ API
- Create OAuth 2.0 credentials
- Add authorized redirect URIs:
  - `http://localhost:5000/auth-callback` (for development)
  - Your production callback URL

## Running the Application

1. Start MongoDB (if running locally):
```bash
mongod
```

2. Run the Flask application:
```bash
python run.py
```

The server will start at `http://localhost:5000`

## API Endpoints

### Authentication
- `GET /auth/google`: Initiate Google OAuth flow
- `GET /auth-callback`: Handle Google OAuth callback

### User
- `GET /api/user/profile`: Get user profile (requires authentication)

## Project Structure
```
backend/
├── app/
│   ├── __init__.py              # Flask app initialization
│   ├── config.py                # Configuration settings
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py              # User model
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py              # Auth routes
│   │   └── user.py              # User routes
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth.py              # Auth service logic
│   │   └── db.py                # Database service
│   └── utils/
│       ├── __init__.py
│       └── decorators.py        # Auth decorators
├── .env                         # Environment variables
├── requirements.txt             # Python dependencies
└── run.py                       # Application entry point
```

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

