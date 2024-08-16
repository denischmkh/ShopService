from fastapi import FastAPI

routes = []

app = FastAPI(debug=True, routes=routes, title="API Service for shop")
