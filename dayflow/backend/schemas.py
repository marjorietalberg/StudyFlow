from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# ==========================================
# CATEGORIA SCHEMAS
# ==========================================
class CategoriaBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=80, example="Estudos")
    cor: str = Field("#8B5CF6", example="#8B5CF6")


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaUpdate(BaseModel):
    nome: Optional[str] = None
    cor: Optional[str] = None


class CategoriaResponse(CategoriaBase):
    id: int

    class Config:
        from_attributes = True


# ==========================================
# ETIQUETA SCHEMAS
# ==========================================
class EtiquetaBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=50, example="Design")
    cor: str = Field("#6366F1", example="#6366F1")


class EtiquetaCreate(EtiquetaBase):
    pass


class EtiquetaUpdate(BaseModel):
    nome: Optional[str] = None
    cor: Optional[str] = None


class EtiquetaResponse(EtiquetaBase):
    id: int

    class Config:
        from_attributes = True


# ==========================================
# CHECKLIST SCHEMAS
# ==========================================
class ChecklistBase(BaseModel):
    descricao: str = Field(..., min_length=1, max_length=200, example="Revisar referências bibliográficas")
    concluido: bool = False


class ChecklistCreate(ChecklistBase):
    pass


class ChecklistUpdate(BaseModel):
    descricao: Optional[str] = None
    concluido: Optional[bool] = None


class ChecklistResponse(ChecklistBase):
    id: int
    atividade_id: int

    class Config:
        from_attributes = True


# ==========================================
# ATIVIDADE SCHEMAS
# ==========================================
class AtividadeBase(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=150, example="Elaborar wireframe do Dashboard")
    descricao: Optional[str] = Field(None, example="Desenvolver fluxo UX e protótipo de alta fidelidade")
    status: str = Field("A fazer", example="A fazer")
    prioridade: str = Field("Média", example="Alta")  # Baixa, Média, Alta, Urgente
    data_vencimento: Optional[str] = Field(None, example="2026-11-20")
    observacoes: Optional[str] = Field(None, example="Alinhado com a equipe")
    lista_id: int = Field(..., example=1)
    categoria_id: Optional[int] = Field(None, example=1)


class AtividadeCreate(AtividadeBase):
    etiqueta_ids: Optional[List[int]] = Field(default_factory=list)


class AtividadeUpdate(BaseModel):
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    status: Optional[str] = None
    prioridade: Optional[str] = None
    data_vencimento: Optional[str] = None
    observacoes: Optional[str] = None
    lista_id: Optional[int] = None
    categoria_id: Optional[int] = None
    etiqueta_ids: Optional[List[int]] = None


class AtividadeStatusPatch(BaseModel):
    status: Optional[str] = None
    lista_id: Optional[int] = None


class AtividadeResponse(BaseModel):
    id: int
    titulo: str
    descricao: Optional[str] = None
    status: str
    prioridade: str
    data_criacao: datetime
    data_vencimento: Optional[str] = None
    data_conclusao: Optional[datetime] = None
    observacoes: Optional[str] = None
    lista_id: int
    categoria_id: Optional[int] = None
    categoria: Optional[CategoriaResponse] = None
    etiquetas: List[EtiquetaResponse] = []
    checklists: List[ChecklistResponse] = []
    quadro_id: Optional[int] = None
    quadro_nome: Optional[str] = None
    lista_nome: Optional[str] = None

    class Config:
        from_attributes = True


# ==========================================
# LISTA SCHEMAS
# ==========================================
class ListaBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100, example="A fazer")
    posicao: int = Field(0, example=0)


class ListaCreate(ListaBase):
    quadro_id: int = Field(..., example=1)


class ListaUpdate(BaseModel):
    nome: Optional[str] = None
    posicao: Optional[int] = None


class ListaResponse(ListaBase):
    id: int
    quadro_id: int
    atividades: List[AtividadeResponse] = []

    class Config:
        from_attributes = True


# ==========================================
# QUADRO SCHEMAS
# ==========================================
class QuadroBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100, example="Estudos & Faculdade")
    descricao: Optional[str] = Field(None, example="Organização das disciplinas e provas")
    cor: str = Field("#7C3AED", example="#7C3AED")


class QuadroCreate(QuadroBase):
    pass


class QuadroUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    cor: Optional[str] = None


class QuadroSummaryResponse(QuadroBase):
    id: int
    data_criacao: datetime
    total_listas: int = 0
    total_atividades: int = 0
    total_concluidas: int = 0
    percentual_conclusao: float = 0.0

    class Config:
        from_attributes = True


class QuadroDetailResponse(QuadroBase):
    id: int
    data_criacao: datetime
    listas: List[ListaResponse] = []

    class Config:
        from_attributes = True


# ==========================================
# DASHBOARD STATS SCHEMA
# ==========================================
class DashboardStats(BaseModel):
    total_atividades: int
    atividades_pendentes: int
    atividades_em_andamento: int
    atividades_em_revisao: int
    atividades_concluidas: int
    atividades_atrasadas: int
    atividades_hoje: int
    taxa_conclusao_percentual: float
    atividades_recentes: List[AtividadeResponse]
    proximas_entregas: List[AtividadeResponse]
    distribuicao_por_prioridade: dict
    distribuicao_por_categoria: dict
