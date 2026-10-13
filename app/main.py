from fastapi import FastAPI

from app.routes import router

app = FastAPI(
    title="Microservicio de clustering de riesgo - UUBR",
    description="K-Means (k=3) sobre actas de inspeccion cerradas. Servicio interno, sin estado.",
    version="1.0.0",
)
app.include_router(router)
