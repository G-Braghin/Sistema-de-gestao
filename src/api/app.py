from fastapi import FastAPI

from src.api.routers import autenticacao

app = FastAPI(title='Sistema de Gestao')

app.include_router(autenticacao.router)
