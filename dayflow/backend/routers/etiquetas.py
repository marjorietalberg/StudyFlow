from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas

router = APIRouter(prefix="/etiquetas", tags=["Etiquetas"])


@router.get("", response_model=List[schemas.EtiquetaResponse], summary="Listar todas as etiquetas")
def listar_etiquetas(db: Session = Depends(get_db)):
    """Retorna todas as etiquetas (tags) cadastradas no sistema."""
    return db.query(models.Etiqueta).order_by(models.Etiqueta.nome.asc()).all()


@router.post("", response_model=schemas.EtiquetaResponse, status_code=status.HTTP_201_CREATED, summary="Criar nova etiqueta")
def criar_etiqueta(etiq_in: schemas.EtiquetaCreate, db: Session = Depends(get_db)):
    """Cria uma nova etiqueta para identificar cartões de atividades."""
    nome = etiq_in.nome.strip()
    existente = db.query(models.Etiqueta).filter(models.Etiqueta.nome.ilike(nome)).first()
    if existente:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Já existe uma etiqueta com este nome.")

    nova_etiq = models.Etiqueta(
        nome=nome,
        cor=etiq_in.cor or "#6366F1"
    )
    db.add(nova_etiq)
    db.commit()
    db.refresh(nova_etiq)
    return nova_etiq


@router.put("/{id}", response_model=schemas.EtiquetaResponse, summary="Atualizar etiqueta")
def atualizar_etiqueta(id: int, etiq_in: schemas.EtiquetaUpdate, db: Session = Depends(get_db)):
    """Atualiza o nome ou a cor da etiqueta."""
    etiqueta = db.query(models.Etiqueta).filter(models.Etiqueta.id == id).first()
    if not etiqueta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Etiqueta não encontrada.")

    if etiq_in.nome is not None:
        nome = etiq_in.nome.strip()
        outro = db.query(models.Etiqueta).filter(models.Etiqueta.nome.ilike(nome), models.Etiqueta.id != id).first()
        if outro:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Já existe outra etiqueta com este nome.")
        etiqueta.nome = nome

    if etiq_in.cor is not None:
        etiqueta.cor = etiq_in.cor

    db.commit()
    db.refresh(etiqueta)
    return etiqueta


@router.delete("/{id}", summary="Excluir etiqueta")
def excluir_etiqueta(id: int, db: Session = Depends(get_db)):
    """Exclui a etiqueta especificada."""
    etiqueta = db.query(models.Etiqueta).filter(models.Etiqueta.id == id).first()
    if not etiqueta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Etiqueta não encontrada.")

    db.delete(etiqueta)
    db.commit()
    return {"message": f"Etiqueta '{etiqueta.nome}' excluída com sucesso."}
