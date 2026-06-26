import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "working_test:app",  # Import string format
        host="0.0.0.0",
        port=8000,
        reload=True  # Now this works!
    )
