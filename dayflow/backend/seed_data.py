from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
import models


def popular_dados_iniciais(db: Session):
    """Popula o banco de dados com dados de exemplo caso esteja vazio."""
    # Se já existem quadros, não fazer nada
    if db.query(models.Quadro).count() > 0:
        return

    print("🌱 Populando banco de dados com estrutura inicial do DayFlow...")

    # 1. Categorias
    cat_estudos = models.Categoria(nome="Estudos", cor="#8B5CF6")
    cat_trabalho = models.Categoria(nome="Trabalho", cor="#3B82F6")
    cat_pessoal = models.Categoria(nome="Pessoal", cor="#EC4899")
    cat_saude = models.Categoria(nome="Saúde", cor="#10B981")
    cat_projetos = models.Categoria(nome="Projetos", cor="#F59E0B")
    cat_compromissos = models.Categoria(nome="Compromissos", cor="#6366F1")

    db.add_all([cat_estudos, cat_trabalho, cat_pessoal, cat_saude, cat_projetos, cat_compromissos])
    db.commit()

    # 2. Etiquetas
    et_design = models.Etiqueta(nome="Design", cor="#8B5CF6")
    et_backend = models.Etiqueta(nome="Backend", cor="#10B981")
    et_pesquisa = models.Etiqueta(nome="Pesquisa", cor="#06B6D4")
    et_urgente = models.Etiqueta(nome="Prioritário", cor="#EF4444")
    et_revisao = models.Etiqueta(nome="Revisão", cor="#F59E0B")

    db.add_all([et_design, et_backend, et_pesquisa, et_urgente, et_revisao])
    db.commit()

    # 3. Quadros
    q_pessoal = models.Quadro(
        nome="Organização Pessoal",
        descricao="Tarefas de rotina diária, bem-estar, finanças e compromissos.",
        cor="#7C3AED"
    )
    q_estudos = models.Quadro(
        nome="Estudos & Faculdade",
        descricao="Acompanhamento de disciplinas acadêmicas, provas, seminários e TCC.",
        cor="#4F46E5"
    )
    q_projetos = models.Quadro(
        nome="Projetos Profissionais",
        descricao="Sprints de desenvolvimento, entregas de clientes e design de produtos.",
        cor="#0284C7"
    )

    db.add_all([q_pessoal, q_estudos, q_projetos])
    db.commit()

    hoje = date.today()
    ontem_str = (hoje - timedelta(days=2)).strftime("%Y-%m-%d")
    hoje_str = hoje.strftime("%Y-%m-%d")
    amanha_str = (hoje + timedelta(days=1)).strftime("%Y-%m-%d")
    semana_str = (hoje + timedelta(days=5)).strftime("%Y-%m-%d")
    futuro_str = (hoje + timedelta(days=12)).strftime("%Y-%m-%d")

    # Configuração de listas e atividades para cada quadro
    for quadro in [q_pessoal, q_estudos, q_projetos]:
        l_fazer = models.Lista(nome="A fazer", quadro_id=quadro.id, posicao=0)
        l_andamento = models.Lista(nome="Em andamento", quadro_id=quadro.id, posicao=1)
        l_revisao = models.Lista(nome="Em revisão", quadro_id=quadro.id, posicao=2)
        l_concluido = models.Lista(nome="Concluído", quadro_id=quadro.id, posicao=3)

        db.add_all([l_fazer, l_andamento, l_revisao, l_concluido])
        db.commit()

        if quadro == q_estudos:
            a1 = models.Atividade(
                titulo="Pesquisa de Referências para o Artigo Científico",
                descricao="Levantar 10 artigos no IEEE Xplore e Google Scholar sobre arquitetura de microsserviços.",
                status="A fazer",
                prioridade="Alta",
                data_vencimento=semana_str,
                lista_id=l_fazer.id,
                categoria_id=cat_estudos.id,
                observacoes="Formato ABNT"
            )
            a1.etiquetas = [et_pesquisa]
            db.add(a1)
            db.commit()

            c1_1 = models.Checklist(atividade_id=a1.id, descricao="Buscar artigos indexados", concluido=True)
            c1_2 = models.Checklist(atividade_id=a1.id, descricao="Resumir conclusões principais", concluido=False)
            c1_3 = models.Checklist(atividade_id=a1.id, descricao="Formatar referências no Zotero", concluido=False)
            db.add_all([c1_1, c1_2, c1_3])

            a2 = models.Atividade(
                titulo="Estudo para Prova de Engenharia de Software",
                descricao="Revisar padrões de projeto GoF (Factory, Singleton, Observer) e arquitetura hexagonal.",
                status="Em andamento",
                prioridade="Urgente",
                data_vencimento=hoje_str,
                lista_id=l_andamento.id,
                categoria_id=cat_estudos.id
            )
            a2.etiquetas = [et_urgente, et_revisao]
            db.add(a2)
            db.commit()

            c2_1 = models.Checklist(atividade_id=a2.id, descricao="Resolver lista de exercícios 4", concluido=True)
            c2_2 = models.Checklist(atividade_id=a2.id, descricao="Simular prova de anos anteriores", concluido=False)
            db.add_all([c2_1, c2_2])

            a3 = models.Atividade(
                titulo="Submissão do Relatório de Laboratório",
                descricao="Enviar PDF final pelo portal do aluno.",
                status="Concluído",
                prioridade="Média",
                data_vencimento=ontem_str,
                data_conclusao=datetime.utcnow() - timedelta(days=1),
                lista_id=l_concluido.id,
                categoria_id=cat_estudos.id
            )
            db.add(a3)

        elif quadro == q_projetos:
            a4 = models.Atividade(
                titulo="Implementar Endpoints REST do Módulo de Pagamento",
                descricao="Criar webhook e autenticação JWT conforme especificações OpenAPI.",
                status="Em andamento",
                prioridade="Alta",
                data_vencimento=amanha_str,
                lista_id=l_andamento.id,
                categoria_id=cat_trabalho.id
            )
            a4.etiquetas = [et_backend]
            db.add(a4)

            a5 = models.Atividade(
                titulo="Refatorar Componente de Navegação no Figma",
                descricao="Alinhar tokens de design com paleta roxa SaaS e modo responsivo.",
                status="Em revisão",
                prioridade="Média",
                data_vencimento=semana_str,
                lista_id=l_revisao.id,
                categoria_id=cat_projetos.id
            )
            a5.etiquetas = [et_design, et_revisao]
            db.add(a5)

            a6 = models.Atividade(
                titulo="Setup de Integração Contínua (CI/CD GitHub Actions)",
                descricao="Pipeline automatizada para execução de testes unitários em pytest.",
                status="Concluído",
                prioridade="Média",
                data_vencimento=ontem_str,
                data_conclusao=datetime.utcnow() - timedelta(days=2),
                lista_id=l_concluido.id,
                categoria_id=cat_trabalho.id
            )
            db.add(a6)

        elif quadro == q_pessoal:
            a7 = models.Atividade(
                titulo="Agendar Consulta Médica e Check-up Anual",
                descricao="Marcar exames de rotina no laboratório central.",
                status="A fazer",
                prioridade="Média",
                data_vencimento=futuro_str,
                lista_id=l_fazer.id,
                categoria_id=cat_saude.id
            )
            db.add(a7)

            a8 = models.Atividade(
                titulo="Planejamento Financeiro e Orçamento do Mês",
                descricao="Categorizar extratos bancários e definir metas de investimentos.",
                status="Em andamento",
                prioridade="Alta",
                data_vencimento=hoje_str,
                lista_id=l_andamento.id,
                categoria_id=cat_pessoal.id
            )
            db.add(a8)

    db.commit()
    print("✅ Dados de exemplo semeados com sucesso!")
