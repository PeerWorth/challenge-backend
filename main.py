from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()


@app.get("/test")
def test():
    return {"test": "ok"}


@app.get("/health")
def health():
    return {"status": "ok"}

handler = Mangum(app)