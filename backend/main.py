from fastapi import FastAPI

app = FastAPI(
    title="My FastAPI App",
    version="0.1.0",
    description="A simple example"
)


@app.get("/")
async def root():
    return {"message": "Hello World"}

