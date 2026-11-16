from datetime import date, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
from routers.atividades import formatar_atividade_response

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=schemas.DashboardStats, summary="Estatísticas globais do Dashboard")
def obter_metricas_dashboard(db: Session = Depends(get_db)):
    """Calcula indicadores de produtividade, progresso, prazos de vencimento e distribuições do sistema."""
    todas = db.query(models.Atividade).all()
    total = len(todas)

    pendentes = sum(1 for a in todas if a.status == "A fazer")
    em_andamento = sum(1 for a in todas if a.status == "Em andamento")
    em_revisao = sum(1 for a in todas if a.status == "Em revisão")
    concluidas = sum(1 for a in todas if a.status == "Concluído")

    hoje_str = date.today().strftime("%Y-%m-%d")

    atrasadas = sum(
        1 for a in todas
        if a.status != "Concluído" and a.data_vencimento and a.data_vencimento < hoje_str
    )

    vencem_hoje = sum(
        1 for a in todas
        if a.data_vencimento == hoje_str
    )

    taxa = round((concluidas / total * 100), 1) if total > 0 else 0.0

    # Atividades recentes (últimas 6 criadas)
    recentes_db = (
        db.query(models.Atividade)
        .order_by(models.Atividade.id.desc())
        .limit(6)
        .all()
    )
    atividades_recentes = [formatar_atividade_response(a) for a in recentes_db]

    # Próximas entregas (não concluídas, com prazo a partir de hoje)
    proximas_db = (
        db.query(models.Atividade)
        .filter(
            models.Atividade.status != "Concluído",
            models.Atividade.data_vencimento != None
        )
        .order_by(models.Atividade.data_vencimento.asc())
        .limit(6)
        .all()
    )
    proximas_entregas = [formatar_atividade_response(a) for a in proximas_db]

    # Distribuição por prioridade
    dist_prio = {"Baixa": 0, "Média": 0, "Alta": 0, "Urgente": 0}
    for a in todas:
        p = a.prioridade or "Média"
        if p in dist_prio:
            dist_prio[p] += 1
        else:
            dist_prio[p] = 1

    # Distribuição por categoria
    dist_cat = {}
    for a in todas:
        cat_nome = a.categoria.nome if a.categoria else "Sem Categoria"
        dist_cat[cat_nome] = dist_cat.get(cat_nome, 0) + 1

    return schemas.DashboardStats(
        total_atividades=total,
        atividades_pendentes=pendentes,
        atividades_em_andamento=em_andamento,
        atividades_em_revisao=em_revisao,
        atividades_concluidas=concluidas,
        atividades_atrasadas=atrasadas,
        atividades_hoje=vencem_hoje,
        taxa_conclusao_percentual=taxa,
        atividades_recentes=atividades_recentes,
        proximas_entregas=proximas_entregas,
        distribuicao_por_prioridade=dist_prio,
        distribuicao_por_categoria=dist_cat
    )
