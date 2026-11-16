import os
import sys

# Adicionar diretório atual ao sys.path para importações locais
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from database import engine, Base, SessionLocal
import models
from seed_data import popular_dados_iniciais
from routers import quadros, listas, atividades, categorias, etiquetas, checklist, dashboard

# Criação das tabelas no SQLite
Base.metadata.create_all(bind=engine)

# Inicializar seed de dados
with SessionLocal() as db:
    popular_dados_iniciais(db)

app = FastAPI(
    title="DayFlow API",
    description="API REST completa para gerenciamento inteligente de quadros, listas, atividades, categorias, etiquetas e checklists no estilo Trello.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuração de CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro dos roteadores por categorias
app.include_router(dashboard.router)
app.include_router(quadros.router)
app.include_router(listas.router)
app.include_router(atividades.router)
app.include_router(categorias.router)
app.include_router(etiquetas.router)
app.include_router(checklist.router)


@app.get("/", include_in_schema=False)
def root():
    """Redireciona a raiz para a documentação interativa Swagger."""
    return RedirectResponse(url="/docs")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
