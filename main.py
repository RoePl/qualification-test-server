from os import environ
from dotenv import load_dotenv
import uvicorn

if __name__ == "__main__":
    load_dotenv()

    uvicorn.run(
        "app.server:app",
        host=environ["SERVER_HOST"],
        port=int(environ["SERVER_PORT"]),
        reload=True
    )
