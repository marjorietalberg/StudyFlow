from datetime import datetime, date, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas

router = APIRouter(prefix="/atividades", tags=["Atividades"])


def formatar_atividade_response(a: models.Atividade) -> schemas.AtividadeResponse:
    quadro_id = a.lista.quadro_id if a.lista else None
    quadro_nome = a.lista.quadro.nome if a.lista and a.lista.quadro else None
    lista_nome = a.lista.nome if a.lista else None

    return schemas.AtividadeResponse(
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
        quadro_id=quadro_id,
        quadro_nome=quadro_nome,
        lista_nome=lista_nome
    )


@router.get("", response_model=List[schemas.AtividadeResponse], summary="Listar atividades com filtros")
def listar_atividades(
    q: Optional[str] = Query(None, description="Busca textual por título ou descrição"),
    status_filtro: Optional[str] = Query(None, alias="status", description="Filtrar por status"),
    prioridade: Optional[str] = Query(None, description="Filtrar por prioridade"),
    categoria_id: Optional[int] = Query(None, description="Filtrar por categoria"),
    quadro_id: Optional[int] = Query(None, description="Filtrar por quadro"),
    lista_id: Optional[int] = Query(None, description="Filtrar por lista específica"),
    prazo: Optional[str] = Query(None, description="Filtrar por prazo: 'atrasadas', 'hoje', 'semana', 'futuras'"),
    ordenar_por: Optional[str] = Query("vencimento", description="Critério de ordenação: 'vencimento', 'prioridade', 'criacao', 'titulo'"),
    db: Session = Depends(get_db)
):
    """Lista atividades cadastradas com suporte a busca global, múltiplos filtros e ordenação flexível."""
    query = db.query(models.Atividade).join(models.Lista, models.Atividade.lista_id == models.Lista.id)

    if quadro_id is not None:
        query = query.filter(models.Lista.quadro_id == quadro_id)

    if lista_id is not None:
        query = query.filter(models.Atividade.lista_id == lista_id)

    if q:
        termo = f"%{q.strip().lower()}%"
        query = query.filter(
            (models.Atividade.titulo.ilike(termo)) | (models.Atividade.descricao.ilike(termo))
        )

    if status_filtro and status_filtro != "Todos":
        query = query.filter(models.Atividade.status == status_filtro)

    if prioridade and prioridade != "Todas":
        query = query.filter(models.Atividade.prioridade == prioridade)

    if categoria_id is not None:
        query = query.filter(models.Atividade.categoria_id == categoria_id)

    hoje_str = date.today().strftime("%Y-%m-%d")
    if prazo == "atrasadas":
        query = query.filter(
            models.Atividade.status != "Concluído",
            models.Atividade.data_vencimento != None,
            models.Atividade.data_vencimento < hoje_str
        )
    elif prazo == "hoje":
        query = query.filter(models.Atividade.data_vencimento == hoje_str)
    elif prazo == "semana":
        data_limite = (date.today() + timedelta(days=7)).strftime("%Y-%m-%d")
        query = query.filter(
            models.Atividade.data_vencimento >= hoje_str,
            models.Atividade.data_vencimento <= data_limite
        )

    # Ordenação
    if ordenar_por == "vencimento":
        query = query.order_by(
            models.Atividade.data_vencimento.is_(None),
            models.Atividade.data_vencimento.asc(),
            models.Atividade.id.desc()
        )
    elif ordenar_por == "prioridade":
        # Ordem de prioridade: Urgente > Alta > Média > Baixa
        query = query.order_by(models.Atividade.id.desc())
    elif ordenar_por == "titulo":
        query = query.order_by(models.Atividade.titulo.asc())
    else:
        query = query.order_by(models.Atividade.id.desc())

    atividades = query.all()
    return [formatar_atividade_response(a) for a in atividades]


@router.get("/{id}", response_model=schemas.AtividadeResponse, summary="Obter detalhes de uma atividade")
def obter_atividade(id: int, db: Session = Depends(get_db)):
    """Retorna os dados completos da atividade, incluindo etiquetas, checklist e informações de quadro/lista."""
    atividade = db.query(models.Atividade).filter(models.Atividade.id == id).first()
    if not atividade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Atividade não encontrada.")
    return formatar_atividade_response(atividade)


@router.post("", response_model=schemas.AtividadeResponse, status_code=status.HTTP_201_CREATED, summary="Criar nova atividade")
def criar_atividade(atv_in: schemas.AtividadeCreate, db: Session = Depends(get_db)):
    """Cria uma nova atividade em uma lista, associando opcionalmente categoria e etiquetas."""
    lista = db.query(models.Lista).filter(models.Lista.id == atv_in.lista_id).first()
    if not lista:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="A lista informada não existe.")

    # Se a lista tiver nome como 'Concluído', ajustar status
    status_final = atv_in.status
    data_conclusao = None
    if lista.nome.strip().lower() in ["concluído", "concluido", "finalizado"] or status_final == "Concluído":
        status_final = "Concluído"
        data_conclusao = datetime.utcnow()

    nova_atv = models.Atividade(
        titulo=atv_in.titulo.strip(),
        descricao=atv_in.descricao.strip() if atv_in.descricao else None,
        status=status_final,
        prioridade=atv_in.prioridade or "Média",
        data_vencimento=atv_in.data_vencimento.strip() if atv_in.data_vencimento else None,
        data_conclusao=data_conclusao,
        observacoes=atv_in.observacoes.strip() if atv_in.observacoes else None,
        lista_id=atv_in.lista_id,
        categoria_id=atv_in.categoria_id
    )

    if atv_in.etiqueta_ids:
        etiquetas = db.query(models.Etiqueta).filter(models.Etiqueta.id.in_(atv_in.etiqueta_ids)).all()
        nova_atv.etiquetas = etiquetas

    db.add(nova_atv)
    db.commit()
    db.refresh(nova_atv)

    return formatar_atividade_response(nova_atv)


@router.put("/{id}", response_model=schemas.AtividadeResponse, summary="Atualizar atividade completa")
def atualizar_atividade(id: int, atv_in: schemas.AtividadeUpdate, db: Session = Depends(get_db)):
    """Atualiza qualquer campo de uma atividade existente."""
    atividade = db.query(models.Atividade).filter(models.Atividade.id == id).first()
    if not atividade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Atividade não encontrada.")

    if atv_in.titulo is not None:
        atividade.titulo = atv_in.titulo.strip()
    if atv_in.descricao is not None:
        atividade.descricao = atv_in.descricao.strip() if atv_in.descricao else None
    if atv_in.prioridade is not None:
        atividade.prioridade = atv_in.prioridade
    if atv_in.data_vencimento is not None:
        atividade.data_vencimento = atv_in.data_vencimento.strip() if atv_in.data_vencimento else None
    if atv_in.observacoes is not None:
        atividade.observacoes = atv_in.observacoes.strip() if atv_in.observacoes else None
    if atv_in.categoria_id is not None:
        atividade.categoria_id = atv_in.categoria_id if atv_in.categoria_id > 0 else None

    if atv_in.lista_id is not None:
        lista = db.query(models.Lista).filter(models.Lista.id == atv_in.lista_id).first()
        if lista:
            atividade.lista_id = lista.id
            if lista.nome.strip().lower() in ["concluído", "concluido"]:
                atividade.status = "Concluído"
                atividade.data_conclusao = datetime.utcnow()

    if atv_in.status is not None:
        atividade.status = atv_in.status
        if atv_in.status == "Concluído":
            atividade.data_conclusao = datetime.utcnow()
        else:
            atividade.data_conclusao = None

    if atv_in.etiqueta_ids is not None:
        etiquetas = db.query(models.Etiqueta).filter(models.Etiqueta.id.in_(atv_in.etiqueta_ids)).all()
        atividade.etiquetas = etiquetas

    db.commit()
    db.refresh(atividade)
    return formatar_atividade_response(atividade)


@router.patch("/{id}/status", response_model=schemas.AtividadeResponse, summary="Atualizar status ou lista da atividade")
def patch_status_atividade(id: int, patch_in: schemas.AtividadeStatusPatch, db: Session = Depends(get_db)):
    """Permite mover a atividade entre listas do Kanban ou alterar seu status diretamente com um toque."""
    atividade = db.query(models.Atividade).filter(models.Atividade.id == id).first()
    if not atividade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Atividade não encontrada.")

    if patch_in.lista_id is not None:
        lista_alvo = db.query(models.Lista).filter(models.Lista.id == patch_in.lista_id).first()
        if not lista_alvo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lista de destino não encontrada.")
        atividade.lista_id = lista_alvo.id

        # Ajustar status automaticamente pelo nome da lista caso status explícito não seja passado
        if not patch_in.status:
            nome_lista = lista_alvo.nome.strip().lower()
            if "fazer" in nome_lista:
                atividade.status = "A fazer"
                atividade.data_conclusao = None
            elif "andamento" in nome_lista:
                atividade.status = "Em andamento"
                atividade.data_conclusao = None
            elif "revis" in nome_lista:
                atividade.status = "Em revisão"
                atividade.data_conclusao = None
            elif "conclu" in nome_lista or "finaliz" in nome_lista:
                atividade.status = "Concluído"
                atividade.data_conclusao = datetime.utcnow()

    if patch_in.status is not None:
        atividade.status = patch_in.status
        if patch_in.status == "Concluído":
            atividade.data_conclusao = datetime.utcnow()
        else:
            atividade.data_conclusao = None

    db.commit()
    db.refresh(atividade)
    return formatar_atividade_response(atividade)


@router.delete("/{id}", summary="Excluir atividade")
def excluir_atividade(id: int, db: Session = Depends(get_db)):
    """Exclui a atividade especificada e seus itens de checklist associados."""
    atividade = db.query(models.Atividade).filter(models.Atividade.id == id).first()
    if not atividade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Atividade não encontrada.")

    db.delete(atividade)
    db.commit()
    return {"message": f"Atividade '{atividade.titulo}' excluída com sucesso."}
