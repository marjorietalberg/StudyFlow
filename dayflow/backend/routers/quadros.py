from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas

router = APIRouter(prefix="/quadros", tags=["Quadros"])


@router.get("", response_model=List[schemas.QuadroSummaryResponse], summary="Listar todos os quadros")
def listar_quadros(db: Session = Depends(get_db)):
    """Retorna todos os quadros com contadores resumidos de atividades e listas."""
    quadros = db.query(models.Quadro).order_by(models.Quadro.id.desc()).all()
    resultado = []
    for q in quadros:
        total_listas = len(q.listas)
        total_atividades = sum(len(l.atividades) for l in q.listas)
        total_concluidas = sum(
            len([a for a in l.atividades if a.status == "Concluído"]) for l in q.listas
        )
        pct = round((total_concluidas / total_atividades * 100), 1) if total_atividades > 0 else 0.0

        resultado.append(
            schemas.QuadroSummaryResponse(
                id=q.id,
                nome=q.nome,
                descricao=q.descricao,
                cor=q.cor,
                data_criacao=q.data_criacao,
                total_listas=total_listas,
                total_atividades=total_atividades,
                total_concluidas=total_concluidas,
                percentual_conclusao=pct
            )
        )
    return resultado


@router.get("/{id}", response_model=schemas.QuadroDetailResponse, summary="Obter detalhes de um quadro")
def obter_quadro(id: int, db: Session = Depends(get_db)):
    """Retorna os dados completos do quadro, com todas as suas listas e cartões ordenados."""
    quadro = db.query(models.Quadro).filter(models.Quadro.id == id).first()
    if not quadro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quadro não encontrado.")

    # Formatar resposta enriquecida
    listas_resp = []
    for l in quadro.listas:
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
                    quadro_id=quadro.id,
                    quadro_nome=quadro.nome,
                    lista_nome=l.nome
                )
            )
        listas_resp.append(
            schemas.ListaResponse(
                id=l.id,
                nome=l.nome,
                posicao=l.posicao,
                quadro_id=l.quadro_id,
                atividades=atvs_resp
            )
        )

    return schemas.QuadroDetailResponse(
        id=quadro.id,
        nome=quadro.nome,
        descricao=quadro.descricao,
        cor=quadro.cor,
        data_criacao=quadro.data_criacao,
        listas=listas_resp
    )


@router.post("", response_model=schemas.QuadroDetailResponse, status_code=status.HTTP_201_CREATED, summary="Criar novo quadro")
def criar_quadro(quadro_in: schemas.QuadroCreate, db: Session = Depends(get_db)):
    """Cria um novo quadro e inicializa automaticamente as 4 listas Kanban padrão: A fazer, Em andamento, Em revisão e Concluído."""
    novo_quadro = models.Quadro(
        nome=quadro_in.nome.strip(),
        descricao=quadro_in.descricao.strip() if quadro_in.descricao else None,
        cor=quadro_in.cor or "#7C3AED"
    )
    db.add(novo_quadro)
    db.commit()
    db.refresh(novo_quadro)

    # Criação das 4 colunas padrão do Kanban
    colunas_padrao = [
        ("A fazer", 0),
        ("Em andamento", 1),
        ("Em revisão", 2),
        ("Concluído", 3)
    ]
    for nome_coluna, pos in colunas_padrao:
        lista = models.Lista(nome=nome_coluna, quadro_id=novo_quadro.id, posicao=pos)
        db.add(lista)
    db.commit()
    db.refresh(novo_quadro)

    return obter_quadro(novo_quadro.id, db)


@router.put("/{id}", response_model=schemas.QuadroDetailResponse, summary="Atualizar quadro")
def atualizar_quadro(id: int, quadro_in: schemas.QuadroUpdate, db: Session = Depends(get_db)):
    """Atualiza o nome, descrição ou cor do quadro."""
    quadro = db.query(models.Quadro).filter(models.Quadro.id == id).first()
    if not quadro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quadro não encontrado.")

    if quadro_in.nome is not None:
        quadro.nome = quadro_in.nome.strip()
    if quadro_in.descricao is not None:
        quadro.descricao = quadro_in.descricao.strip() if quadro_in.descricao else None
    if quadro_in.cor is not None:
        quadro.cor = quadro_in.cor

    db.commit()
    db.refresh(quadro)
    return obter_quadro(quadro.id, db)


@router.delete("/{id}", summary="Excluir quadro")
def excluir_quadro(id: int, db: Session = Depends(get_db)):
    """Exclui o quadro especificado e todas as suas listas e cartões relacionados."""
    quadro = db.query(models.Quadro).filter(models.Quadro.id == id).first()
    if not quadro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quadro não encontrado.")

    db.delete(quadro)
    db.commit()
    return {"message": f"Quadro '{quadro.nome}' e suas atividades foram excluídos com sucesso."}
