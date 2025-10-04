from fastapi import FastAPI


app = FastAPI(title="GPS Data API")

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/gps/{user_id}")
def get_gps(user_id: int, request: Request):
    client_ip = request.client.host
    return {"ip_location": "Estimado via IP"}