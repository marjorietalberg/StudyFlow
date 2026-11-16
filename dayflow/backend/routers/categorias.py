from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas

router = APIRouter(prefix="/categorias", tags=["Categorias"])


@router.get("", response_model=List[schemas.CategoriaResponse], summary="Listar todas as categorias")
def listar_categorias(db: Session = Depends(get_db)):
    """Retorna todas as categorias cadastradas para classificação de atividades."""
    return db.query(models.Categoria).order_by(models.Categoria.nome.asc()).all()


@router.post("", response_model=schemas.CategoriaResponse, status_code=status.HTTP_201_CREATED, summary="Criar nova categoria")
def criar_categoria(cat_in: schemas.CategoriaCreate, db: Session = Depends(get_db)):
    """Cadastra uma nova categoria com nome e cor hexadecimal."""
    nome = cat_in.nome.strip()
    existente = db.query(models.Categoria).filter(models.Categoria.nome.ilike(nome)).first()
    if existente:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Já existe uma categoria com este nome.")

    nova_cat = models.Categoria(
        nome=nome,
        cor=cat_in.cor or "#8B5CF6"
    )
    db.add(nova_cat)
    db.commit()
    db.refresh(nova_cat)
    return nova_cat


@router.put("/{id}", response_model=schemas.CategoriaResponse, summary="Atualizar categoria")
def atualizar_categoria(id: int, cat_in: schemas.CategoriaUpdate, db: Session = Depends(get_db)):
    """Atualiza o nome ou a cor da categoria."""
    categoria = db.query(models.Categoria).filter(models.Categoria.id == id).first()
    if not categoria:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada.")

    if cat_in.nome is not None:
        nome = cat_in.nome.strip()
        outro = db.query(models.Categoria).filter(models.Categoria.nome.ilike(nome), models.Categoria.id != id).first()
        if outro:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Já existe outra categoria com este nome.")
        categoria.nome = nome

    if cat_in.cor is not None:
        categoria.cor = cat_in.cor

    db.commit()
    db.refresh(categoria)
    return categoria


@router.delete("/{id}", summary="Excluir categoria")
def excluir_categoria(id: int, db: Session = Depends(get_db)):
    """Exclui a categoria. Atividades vinculadas terão a categoria desassociada (SET NULL)."""
    categoria = db.query(models.Categoria).filter(models.Categoria.id == id).first()
    if not categoria:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada.")

    db.delete(categoria)
    db.commit()
    return {"message": f"Categoria '{categoria.nome}' excluída com sucesso."}
