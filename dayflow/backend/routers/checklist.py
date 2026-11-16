from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas

router = APIRouter(tags=["Checklist"])


@router.get("/atividades/{id}/checklist", response_model=List[schemas.ChecklistResponse], summary="Listar itens do checklist da atividade")
def listar_checklist_atividade(id: int, db: Session = Depends(get_db)):
    """Retorna todos os subtópicos / itens de checklist da atividade."""
    atividade = db.query(models.Atividade).filter(models.Atividade.id == id).first()
    if not atividade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Atividade não encontrada.")
    return atividade.checklists


@router.post("/atividades/{id}/checklist", response_model=schemas.ChecklistResponse, status_code=status.HTTP_201_CREATED, summary="Adicionar item ao checklist")
def adicionar_item_checklist(id: int, item_in: schemas.ChecklistCreate, db: Session = Depends(get_db)):
    """Adiciona uma nova subtarefa ao checklist da atividade."""
    atividade = db.query(models.Atividade).filter(models.Atividade.id == id).first()
    if not atividade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Atividade não encontrada.")

    novo_item = models.Checklist(
        atividade_id=id,
        descricao=item_in.descricao.strip(),
        concluido=item_in.concluido
    )
    db.add(novo_item)
    db.commit()
    db.refresh(novo_item)
    return novo_item


@router.put("/checklist/{id}", response_model=schemas.ChecklistResponse, summary="Atualizar item do checklist")
def atualizar_item_checklist(id: int, item_in: schemas.ChecklistUpdate, db: Session = Depends(get_db)):
    """Atualiza a descrição ou alterna o estado de conclusão (checked/unchecked) de um item de checklist."""
    item = db.query(models.Checklist).filter(models.Checklist.id == id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item de checklist não encontrado.")

    if item_in.descricao is not None:
        item.descricao = item_in.descricao.strip()
    if item_in.concluido is not None:
        item.concluido = item_in.concluido

    db.commit()
    db.refresh(item)
    return item


@router.delete("/checklist/{id}", summary="Excluir item do checklist")
def excluir_item_checklist(id: int, db: Session = Depends(get_db)):
    """Remove permanentemente o item do checklist."""
    item = db.query(models.Checklist).filter(models.Checklist.id == id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item de checklist não encontrado.")

    db.delete(item)
    db.commit()
    return {"message": "Item de checklist removido com sucesso."}
