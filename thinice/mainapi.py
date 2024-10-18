from .thinice import app
import uvicorn

"""
This is the main entry point. This calls uvicorn to run the ASGI app.
"""
def main():
    uvicorn.run(app, host="127.0.0.1", port=8000)

