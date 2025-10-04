from fastapi import FastAPI


app = FastAPI(title="GPS Data API")

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/gps/{user_id}")
def get_gps(user_id: int):
    return {"user_id": user_id, "gps": "Sample GPS Data"}