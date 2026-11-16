from collections import defaultdict
from flask import Blueprint, request, jsonify
from models.atividade import Atividade
from models.disciplina import Disciplina

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@dashboard_bp.route('', methods=['GET'])
def obter_dashboard():
    """
    Obter métricas consolidadas do estudante, estatísticas e alertas
    ---
    tags:
      - Dashboard
    parameters:
      - in: query
        name: usuario_id
        type: integer
        description: Filtrar métricas do usuário logado
    responses:
      200:
        description: Dados consolidados do dashboard
    """
    usuario_id = request.args.get('usuario_id')
    
    if usuario_id:
        try:
            uid = int(usuario_id)
            atividades = Atividade.query.filter_by(usuario_id=uid).all()
            disciplinas = Disciplina.query.filter_by(usuario_id=uid).all()
        except ValueError:
            atividades = Atividade.query.all()
            disciplinas = Disciplina.query.all()
    else:
        atividades = Atividade.query.all()
        disciplinas = Disciplina.query.all()

    total = len(atividades)
    concluidas = sum(1 for a in atividades if a.status == 'Concluída')
    pendentes = sum(1 for a in atividades if a.status in ['Pendente', 'Backlog', 'A Fazer'])
    em_andamento = sum(1 for a in atividades if a.status in ['Em Andamento', 'Em Validação', 'Em Revisão'])

    taxa = round((concluidas / total * 100), 1) if total > 0 else 0.0

    # Atividades não concluídas
    nao_concluidas = [a for a in atividades if a.status != 'Concluída']

    # Próximos prazos (ordenadas por data)
    proximos = sorted(nao_concluidas, key=lambda a: a.data_entrega)[:5]

    # Prioridade inteligente (ordenadas por score de urgência)
    prioritarias = sorted(nao_concluidas, key=lambda a: a.score_urgencia, reverse=True)[:6]

    # Alertas
    atrasadas = [a for a in nao_concluidas if a.is_atrasada]
    urgentes = [a for a in nao_concluidas if a.dias_restantes is not None and 0 <= a.dias_restantes <= 3]

    # Distribuição por disciplina
    disc_map = defaultdict(lambda: {'total': 0, 'concluidas': 0, 'pendentes': 0})
    for a in atividades:
        nome_disc = a.disciplina.nome if a.disciplina else 'Sem Matéria'
        disc_map[nome_disc]['total'] += 1
        if a.status == 'Concluída':
            disc_map[nome_disc]['concluidas'] += 1
        else:
            disc_map[nome_disc]['pendentes'] += 1

    por_disciplina = [
        {
            'disciplina': k,
            'total': v['total'],
            'concluidas': v['concluidas'],
            'pendentes': v['pendentes'],
            'percentual': round((v['concluidas'] / v['total'] * 100), 1) if v['total'] > 0 else 0.0
        }
        for k, v in disc_map.items()
    ]

    # Distribuição por prioridade
    por_prioridade = {
        'Alta': sum(1 for a in atividades if a.prioridade == 'Alta'),
        'Média': sum(1 for a in atividades if a.prioridade == 'Média'),
        'Baixa': sum(1 for a in atividades if a.prioridade == 'Baixa')
    }

    return jsonify({
        'total_tarefas': total,
        'concluidas': concluidas,
        'pendentes': pendentes,
        'em_andamento': em_andamento,
        'taxa_conclusao': taxa,
        'total_disciplinas': len(disciplinas),
        'atrasadas_count': len(atrasadas),
        'urgentes_count': len(urgentes),
        'proximos_prazos': [a.to_dict() for a in proximos],
        'tarefas_prioritarias': [a.to_dict() for a in prioritarias],
        'por_disciplina': por_disciplina,
        'por_prioridade': por_prioridade
    }), 200
