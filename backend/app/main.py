from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import chart as chart_router

app = FastAPI(
    title="Lumen Lab - Ziwei Doushu",
    description="Ziwei Doushu chart generation API based on 瞿海藩《天纪》系统",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chart_router.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "lumen-lab-ziwei"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)