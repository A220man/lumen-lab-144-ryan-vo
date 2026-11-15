from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

from app.api.v1.auth_routes import router as auth_router  # noqa: E402
from app.api.v1.chart import router as chart_router  # noqa: E402

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(chart_router, prefix="/api/v1", tags=["chart"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "lumen-lab-ziwei"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
