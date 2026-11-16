from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, Table, Boolean
)
from sqlalchemy.orm import relationship
from database import Base

# Tabela associativa Muitos-para-Muitos: Atividade <-> Etiqueta
atividade_etiquetas = Table(
    "atividade_etiquetas",
    Base.metadata,
    Column("atividade_id", Integer, ForeignKey("atividades.id", ondelete="CASCADE"), primary_key=True),
    Column("etiqueta_id", Integer, ForeignKey("etiquetas.id", ondelete="CASCADE"), primary_key=True)
)


class Quadro(Base):
    __tablename__ = "quadros"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=True)
    cor = Column(String(30), default="#7C3AED")
    data_criacao = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    listas = relationship("Lista", back_populates="quadro", cascade="all, delete-orphan", order_by="Lista.posicao")


class Lista(Base):
    __tablename__ = "listas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    quadro_id = Column(Integer, ForeignKey("quadros.id", ondelete="CASCADE"), nullable=False)
    posicao = Column(Integer, default=0)

    # Relacionamentos
    quadro = relationship("Quadro", back_populates="listas")
    atividades = relationship("Atividade", back_populates="lista", cascade="all, delete-orphan", order_by="Atividade.id")


class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(80), nullable=False, unique=True)
    cor = Column(String(30), default="#8B5CF6")

    # Relacionamentos
    atividades = relationship("Atividade", back_populates="categoria")


class Etiqueta(Base):
    __tablename__ = "etiquetas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), nullable=False, unique=True)
    cor = Column(String(30), default="#6366F1")

    # Relacionamentos
    atividades = relationship("Atividade", secondary=atividade_etiquetas, back_populates="etiquetas")


class Atividade(Base):
    __tablename__ = "atividades"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(150), nullable=False)
    descricao = Column(Text, nullable=True)
    status = Column(String(50), default="A fazer")  # "A fazer", "Em andamento", "Em revisão", "Concluído"
    prioridade = Column(String(30), default="Média")  # "Baixa", "Média", "Alta", "Urgente"
    data_criacao = Column(DateTime, default=datetime.utcnow)
    data_vencimento = Column(String(30), nullable=True)  # Formato YYYY-MM-DD ou ISO
    data_conclusao = Column(DateTime, nullable=True)
    observacoes = Column(Text, nullable=True)

    lista_id = Column(Integer, ForeignKey("listas.id", ondelete="CASCADE"), nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias.id", ondelete="SET NULL"), nullable=True)

    # Relacionamentos
    lista = relationship("Lista", back_populates="atividades")
    categoria = relationship("Categoria", back_populates="atividades")
    etiquetas = relationship("Etiqueta", secondary=atividade_etiquetas, back_populates="atividades")
    checklists = relationship("Checklist", back_populates="atividade", cascade="all, delete-orphan")


class Checklist(Base):
    __tablename__ = "checklists"

    id = Column(Integer, primary_key=True, index=True)
    atividade_id = Column(Integer, ForeignKey("atividades.id", ondelete="CASCADE"), nullable=False)
    descricao = Column(String(200), nullable=False)
    concluido = Column(Boolean, default=False)

    # Relacionamento
    atividade = relationship("Atividade", back_populates="checklists")
