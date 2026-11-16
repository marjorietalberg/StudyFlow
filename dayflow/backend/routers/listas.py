from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas

router = APIRouter(prefix="/listas", tags=["Listas"])


@router.get("", response_model=List[schemas.ListaResponse], summary="Listar listas")
def listar_listas(quadro_id: Optional[int] = Query(None, description="Filtrar pelo ID do quadro"), db: Session = Depends(get_db)):
    """Retorna as listas cadastradas, opcionalmente filtradas por quadro."""
    query = db.query(models.Lista)
    if quadro_id is not None:
        query = query.filter(models.Lista.quadro_id == quadro_id)
    listas = query.order_by(models.Lista.posicao.asc(), models.Lista.id.asc()).all()

    resultado = []
    for l in listas:
        quadro_nome = l.quadro.nome if l.quadro else None
        atvs_resp = []
        for a in l.atividades:
            atvs_resp.append(
                schemas.AtividadeResponse(
                    id=a.id,
                    titulo=a.titulo,
                    descricao=a.descricao,
                    status=a.status,
                    prioridade=a.prioridade,
                    data_criacao=a.data_criacao,
                    data_vencimento=a.data_vencimento,
                    data_conclusao=a.data_conclusao,
                    observacoes=a.observacoes,
                    lista_id=a.lista_id,
                    categoria_id=a.categoria_id,
                    categoria=a.categoria,
                    etiquetas=a.etiquetas,
                    checklists=a.checklists,
                    quadro_id=l.quadro_id,
                    quadro_nome=quadro_nome,
                    lista_nome=l.nome
                )
            )
        resultado.append(
            schemas.ListaResponse(
                id=l.id,
                nome=l.nome,
                posicao=l.posicao,
                quadro_id=l.quadro_id,
                atividades=atvs_resp
            )
        )
    return resultado


@router.post("", response_model=schemas.ListaResponse, status_code=status.HTTP_201_CREATED, summary="Criar nova lista")
def criar_lista(lista_in: schemas.ListaCreate, db: Session = Depends(get_db)):
    """Cria uma nova lista/coluna para um quadro existente."""
    quadro = db.query(models.Quadro).filter(models.Quadro.id == lista_in.quadro_id).first()
    if not quadro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quadro especificado não existe.")

    # Definir posição como última se não especificada
    pos = lista_in.posicao
    if pos == 0 and len(quadro.listas) > 0:
        pos = max(l.posicao for l in quadro.listas) + 1

    nova_lista = models.Lista(
        nome=lista_in.nome.strip(),
        quadro_id=lista_in.quadro_id,
        posicao=pos
    )
    db.add(nova_lista)
    db.commit()
    db.refresh(nova_lista)

    return schemas.ListaResponse(
        id=nova_lista.id,
        nome=nova_lista.nome,
        posicao=nova_lista.posicao,
        quadro_id=nova_lista.quadro_id,
        atividades=[]
    )


@router.put("/{id}", response_model=schemas.ListaResponse, summary="Atualizar lista")
def atualizar_lista(id: int, lista_in: schemas.ListaUpdate, db: Session = Depends(get_db)):
    """Atualiza o nome ou a posição de uma lista."""
    lista = db.query(models.Lista).filter(models.Lista.id == id).first()
    if not lista:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lista não encontrada.")

    if lista_in.nome is not None:
        lista.nome = lista_in.nome.strip()
    if lista_in.posicao is not None:
        lista.posicao = lista_in.posicao

    db.commit()
    db.refresh(lista)

    quadro_nome = lista.quadro.nome if lista.quadro else None
    atvs_resp = [
        schemas.AtividadeResponse(
            id=a.id,
            titulo=a.titulo,
            descricao=a.descricao,
            status=a.status,
            prioridade=a.prioridade,
            data_criacao=a.data_criacao,
            data_vencimento=a.data_vencimento,
            data_conclusao=a.data_conclusao,
            observacoes=a.observacoes,
            lista_id=a.lista_id,
            categoria_id=a.categoria_id,
            categoria=a.categoria,
            etiquetas=a.etiquetas,
            checklists=a.checklists,
            quadro_id=lista.quadro_id,
            quadro_nome=quadro_nome,
            lista_nome=lista.nome
        )
        for a in lista.atividades
    ]

    return schemas.ListaResponse(
        id=lista.id,
        nome=lista.nome,
        posicao=lista.posicao,
        quadro_id=lista.quadro_id,
        atividades=atvs_resp
    )


@router.delete("/{id}", summary="Excluir lista")
def excluir_lista(id: int, db: Session = Depends(get_db)):
    """Exclui a lista e todas as atividades contidas nela."""
    lista = db.query(models.Lista).filter(models.Lista.id == id).first()
    if not lista:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lista não encontrada.")

    db.delete(lista)
    db.commit()
    return {"message": f"Lista '{lista.nome}' e suas atividades foram excluídas com sucesso."}
