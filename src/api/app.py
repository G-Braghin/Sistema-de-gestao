from fastapi import FastAPI

from src.api.routers import autenticacao, cliente, gerenciamento_usuarios, usuarios

app = FastAPI(title='Sistema de Gestao')

app.include_router(autenticacao.router)
app.include_router(usuarios.router)
app.include_router(gerenciamento_usuarios.router)
app.include_router(cliente.router)
