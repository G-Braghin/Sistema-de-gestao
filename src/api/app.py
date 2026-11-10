from fastapi import FastAPI

from src.api.routers import autenticacao, usuarios

app = FastAPI(title='Sistema de Gestao')

app.include_router(autenticacao.router)
app.include_router(usuarios.router)
