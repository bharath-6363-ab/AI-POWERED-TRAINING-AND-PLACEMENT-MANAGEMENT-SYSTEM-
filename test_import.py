from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from backend.app.main import app

# Check app imported
print('FastAPI App ready, routes count:', len(app.routes))
