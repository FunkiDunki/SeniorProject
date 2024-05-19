import uvicorn

if __name__ == "__main__":

    config = uvicorn.Config("src.server:app", port=11000, reload=True)

    server = uvicorn.Server(config)
    server.run()
