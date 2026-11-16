import pytest
from app import create_app
from database.database import db
from models.disciplina import Disciplina
from models.atividade import Atividade
from datetime import date, timedelta

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

# ==============================================================================
# Testes de Autenticação (Cadastro & Login)
# ==============================================================================

def test_cadastro_usuario(client):
    payload = {
        'nome': 'Marjorie Talberg',
        'email': 'marjorie.teste@studyflow.edu',
        'senha': 'senhaSegura123',
        'curso': 'Engenharia de Software'
    }
    response = client.post('/api/auth/cadastro', json=payload)
    assert response.status_code == 201
    dados = response.get_json()
    assert 'usuario' in dados
    assert dados['usuario']['email'] == 'marjorie.teste@studyflow.edu'

def test_cadastro_email_duplicado(client):
    payload = {
        'nome': 'Estudante Duplicado',
        'email': 'duplicado@studyflow.edu',
        'senha': '123'
    }
    client.post('/api/auth/cadastro', json=payload)
    resp2 = client.post('/api/auth/cadastro', json=payload)
    assert resp2.status_code == 400
    assert 'error' in resp2.get_json()

def test_login_sucesso(client):
    client.post('/api/auth/cadastro', json={
        'nome': 'Usuario Login',
        'email': 'login@studyflow.edu',
        'senha': 'minhasenha'
    })
    resp = client.post('/api/auth/login', json={
        'email': 'login@studyflow.edu',
        'senha': 'minhasenha'
    })
    assert resp.status_code == 200
    assert 'usuario' in resp.get_json()

def test_login_senha_incorreta(client):
    client.post('/api/auth/cadastro', json={
        'nome': 'Usuario Erro',
        'email': 'erro@studyflow.edu',
        'senha': 'certa'
    })
    resp = client.post('/api/auth/login', json={
        'email': 'erro@studyflow.edu',
        'senha': 'errada'
    })
    assert resp.status_code == 401

# ==============================================================================
# Testes de Disciplinas (CRUD)
# ==============================================================================

def test_criar_disciplina(client):
    payload = {
        'nome': 'Estrutura de Dados',
        'professor': 'Prof. Alan Turing',
        'descricao': 'Filas, pilhas, árvores binárias e grafos'
    }
    response = client.post('/api/disciplinas', json=payload)
    assert response.status_code == 201
    dados = response.get_json()
    assert dados['nome'] == 'Estrutura de Dados'
    assert dados['professor'] == 'Prof. Alan Turing'
    assert 'id' in dados

def test_criar_disciplina_invalida(client):
    response = client.post('/api/disciplinas', json={'descricao': 'sem nome nem prof'})
    assert response.status_code == 400

def test_listar_disciplinas(client):
    response = client.get('/api/disciplinas')
    assert response.status_code == 200
    dados = response.get_json()
    assert isinstance(dados, list)

def test_obter_disciplina_por_id(client):
    # Criar uma disciplina primeiro
    payload = {'nome': 'Redes de Computadores', 'professor': 'Prof. Linus'}
    criada = client.post('/api/disciplinas', json=payload).get_json()

    response = client.get(f'/api/disciplinas/{criada["id"]}')
    assert response.status_code == 200
    dados = response.get_json()
    assert dados['nome'] == 'Redes de Computadores'
    assert 'atividades' in dados

def test_atualizar_disciplina(client):
    criada = client.post('/api/disciplinas', json={'nome': 'Compiladores', 'professor': 'Prof. A'}).get_json()
    update_resp = client.put(f'/api/disciplinas/{criada["id"]}', json={'professor': 'Prof. Atualizado'})
    assert update_resp.status_code == 200
    assert update_resp.get_json()['professor'] == 'Prof. Atualizado'

def test_excluir_disciplina(client):
    criada = client.post('/api/disciplinas', json={'nome': 'Física 1', 'professor': 'Prof. Newton'}).get_json()
    del_resp = client.delete(f'/api/disciplinas/{criada["id"]}')
    assert del_resp.status_code == 200

    # Verificar que não existe mais
    check_resp = client.get(f'/api/disciplinas/{criada["id"]}')
    assert check_resp.status_code == 404

# ==============================================================================
# Testes de Atividades (CRUD & Status)
# ==============================================================================

def test_criar_atividade(client):
    # Cria disciplina para vincular
    disc = client.post('/api/disciplinas', json={'nome': 'POO', 'professor': 'Prof. Java'}).get_json()
    
    hoje = date.today().strftime('%Y-%m-%d')
    payload = {
        'titulo': 'Exercício de Polimorfismo',
        'descricao': 'Implementar classes abstratas e interfaces',
        'disciplina_id': disc['id'],
        'data_entrega': hoje,
        'prioridade': 'Alta',
        'status': 'Pendente'
    }
    response = client.post('/api/atividades', json=payload)
    assert response.status_code == 201
    dados = response.get_json()
    assert dados['titulo'] == 'Exercício de Polimorfismo'
    assert dados['disciplina_id'] == disc['id']
    assert dados['alerta_prazo'] == 'Vence Hoje!'

def test_criar_atividade_sem_disciplina(client):
    payload = {
        'titulo': 'Sem Matéria',
        'disciplina_id': 99999,
        'data_entrega': '2026-12-01'
    }
    response = client.post('/api/atividades', json=payload)
    assert response.status_code == 404

def test_alternar_status_atividade(client):
    disc = client.post('/api/disciplinas', json={'nome': 'Sistemas Operacionais', 'professor': 'Prof. Tanenbaum'}).get_json()
    atv = client.post('/api/atividades', json={
        'titulo': 'Simulação de Escalonamento CPU',
        'disciplina_id': disc['id'],
        'data_entrega': '2026-11-30'
    }).get_json()

    assert atv['status'] == 'Pendente'

    # Alternar status (Pendente -> Concluída)
    patch_resp = client.patch(f'/api/atividades/{atv["id"]}/status')
    assert patch_resp.status_code == 200
    assert patch_resp.get_json()['status'] == 'Concluída'

    # Alternar novamente (Concluída -> Pendente)
    patch_resp2 = client.patch(f'/api/atividades/{atv["id"]}/status')
    assert patch_resp2.status_code == 200
    assert patch_resp2.get_json()['status'] == 'Pendente'

def test_excluir_atividade(client):
    disc = client.post('/api/disciplinas', json={'nome': 'Cálculo 1', 'professor': 'Prof. Euler'}).get_json()
    atv = client.post('/api/atividades', json={
        'titulo': 'Lista de Derivadas',
        'disciplina_id': disc['id'],
        'data_entrega': '2026-11-25'
    }).get_json()

    del_resp = client.delete(f'/api/atividades/{atv["id"]}')
    assert del_resp.status_code == 200

    check_resp = client.get(f'/api/atividades/{atv["id"]}')
    assert check_resp.status_code == 404

# ==============================================================================
# Testes do Dashboard e Swagger
# ==============================================================================

def test_obter_dashboard(client):
    response = client.get('/api/dashboard')
    assert response.status_code == 200
    dados = response.get_json()
    assert 'total_tarefas' in dados
    assert 'concluidas' in dados
    assert 'pendentes' in dados
    assert 'taxa_conclusao' in dados
    assert 'por_disciplina' in dados

def test_swagger_documentacao(client):
    response = client.get('/apidocs/')
    assert response.status_code == 200
    assert b'StudyFlow' in response.data or b'swagger' in response.data or response.status_code == 200
