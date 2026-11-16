import sys
import os

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from flask import Flask, jsonify, redirect
from flask_cors import CORS
from flasgger import Swagger
from config import Config
from database.database import db, init_db
from routes.disciplinas import disciplinas_bp
from routes.atividades import atividades_bp
from routes.dashboard import dashboard_bp
from routes.auth import auth_bp
from models.usuario import Usuario
from models.disciplina import Disciplina
from models.atividade import Atividade
from datetime import date, timedelta

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Habilita CORS para permitir consumo seguro
    CORS(app)

    # Inicializa banco de dados
    init_db(app)

    # Configura documentação interativa Swagger
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec_1',
                "route": '/apispec_1.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/"
    }
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "StudyFlow - Academic Management API",
            "description": "API REST completa para organização de rotina de estudos, controle de prazos e produtividade acadêmica. Desenvolvida para avaliação final N4.",
            "version": "1.0.0",
            "contact": {
                "name": "Equipe StudyFlow",
                "email": "estudante@faculdade.edu.br"
            }
        },
        "tags": [
            {"name": "Autenticação", "description": "Cadastro e login de estudantes"},
            {"name": "Dashboard", "description": "Métricas de produtividade, alertas e resumos"},
            {"name": "Disciplinas", "description": "Gestão completa de matérias e professores"},
            {"name": "Atividades", "description": "Gestão de trabalhos, prazos e prioridades inteligentes"}
        ]
    }
    Swagger(app, config=swagger_config, template=swagger_template)

    # Registro de Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(disciplinas_bp)
    app.register_blueprint(atividades_bp)
    app.register_blueprint(dashboard_bp)

    @app.route('/')
    def index():
        return jsonify({
            'sistema': 'StudyFlow API',
            'versao': '1.0.0',
            'status': 'operacional',
            'documentacao_swagger': '/apidocs/',
            'rotas_principais': {
                'dashboard': '/api/dashboard',
                'disciplinas': '/api/disciplinas',
                'atividades': '/api/atividades'
            }
        })

    # Popula dados iniciais caso o banco esteja vazio (exceto em modo de teste)
    if not app.config.get('TESTING'):
        with app.app_context():
            popular_dados_iniciais()

    return app


def popular_dados_iniciais():
    """Insere dados de exemplo para demonstração imediata do dashboard e funcionalidades."""
    usuario_demo = Usuario.query.first()
    if usuario_demo is None:
        usuario_demo = Usuario(
            nome='Estudante Demo',
            email='aluno@studyflow.edu',
            curso='Ciência da Computação'
        )
        usuario_demo.set_senha('123456')
        db.session.add(usuario_demo)
        db.session.commit()

    if Disciplina.query.first() is None:
        hoje = date.today()
        
        # Cria disciplinas de exemplo vinculadas ao usuário demo
        d1 = Disciplina(nome='Engenharia de Software', professor='Prof. Carlos Silva', descricao='Metodologias Ágeis, Arquitetura e Engenharia de Requisitos', usuario_id=usuario_demo.id)
        d2 = Disciplina(nome='Banco de Dados', professor='Profa. Helena Souza', descricao='Modelagem Relacional, SQL Avançado e ORM', usuario_id=usuario_demo.id)
        d3 = Disciplina(nome='Inteligência Artificial', professor='Prof. Ricardo Mendes', descricao='Algoritmos de Busca, Redes Neurais e Machine Learning', usuario_id=usuario_demo.id)
        d4 = Disciplina(nome='Desenvolvimento Web', professor='Profa. Mariana Costa', descricao='APIs RESTful, Flask, Gradio e Frontend Moderno', usuario_id=usuario_demo.id)

        db.session.add_all([d1, d2, d3, d4])
        db.session.commit()

        # Cria atividades com diferentes status e prazos para demonstrar os alertas
        a1 = Atividade(
            titulo='Entrega do Projeto N4 - API REST & Swagger',
            descricao='Construir API RESTful completa com SQLAlchemy, documentação Swagger e interface Gradio.',
            disciplina_id=d4.id,
            usuario_id=usuario_demo.id,
            data_entrega=(hoje + timedelta(days=2)).strftime('%Y-%m-%d'),
            prioridade='Alta',
            status='Em Andamento'
        )
        a2 = Atividade(
            titulo='Modelagem Relacional do Trabalho Final',
            descricao='Diagrama Entidade-Relacionamento e script de criação DDL.',
            disciplina_id=d2.id,
            usuario_id=usuario_demo.id,
            data_entrega=(hoje - timedelta(days=2)).strftime('%Y-%m-%d'),  # Atrasada para demonstrar alerta
            prioridade='Alta',
            status='Pendente'
        )
        a3 = Atividade(
            titulo='Seminário sobre Arquiteturas em Microsserviços',
            descricao='Apresentação em slides com estudos de caso reais.',
            disciplina_id=d1.id,
            usuario_id=usuario_demo.id,
            data_entrega=(hoje + timedelta(days=5)).strftime('%Y-%m-%d'),
            prioridade='Média',
            status='Pendente'
        )
        a4 = Atividade(
            titulo='Implementação do Classificador KNN',
            descricao='Exercício prático em Python utilizando Scikit-Learn.',
            disciplina_id=d3.id,
            usuario_id=usuario_demo.id,
            data_entrega=(hoje - timedelta(days=5)).strftime('%Y-%m-%d'),
            prioridade='Baixa',
            status='Concluída'
        )
        a5 = Atividade(
            titulo='Revisão dos Casos de Uso e User Stories',
            descricao='Documento de requisitos validado com o cliente.',
            disciplina_id=d1.id,
            usuario_id=usuario_demo.id,
            data_entrega=(hoje - timedelta(days=1)).strftime('%Y-%m-%d'),
            prioridade='Média',
            status='Concluída'
        )

        db.session.add_all([a1, a2, a3, a4, a5])
        db.session.commit()


app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Iniciando StudyFlow API em http://127.0.0.1:{port}")
    print(f"📚 Documentação Swagger disponível em: http://127.0.0.1:{port}/apidocs/")
    app.run(host='0.0.0.0', port=port, debug=True)
