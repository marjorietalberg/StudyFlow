import os
import sys
import pytest
import httpx

# Adicionar diretório do backend ao sys.path
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(TEST_DIR, ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_dashboard_stats():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/dashboard/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_atividades" in data
        assert "taxa_conclusao_percentual" in data
        assert "atividades_recentes" in data
        assert "proximas_entregas" in data


@pytest.mark.anyio
async def test_listar_e_criar_quadro():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Listar
        resp = await client.get("/quadros")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

        # 2. Criar novo quadro
        novo = {
            "nome": "Quadro de Testes Automatizados",
            "descricao": "Quadro criado para validação de endpoints",
            "cor": "#7C3AED"
        }
        resp_create = await client.post("/quadros", json=novo)
        assert resp_create.status_code == 201
        dados = resp_create.json()
        assert dados["nome"] == novo["nome"]
        qid = dados["id"]

        # 3. Verificar se as 4 listas padrão foram criadas
        listas = dados.get("listas", [])
        nomes_listas = [l["nome"] for l in listas]
        assert "A fazer" in nomes_listas
        assert "Em andamento" in nomes_listas
        assert "Em revisão" in nomes_listas
        assert "Concluído" in nomes_listas

        # 4. Obter detalhes
        resp_get = await client.get(f"/quadros/{qid}")
        assert resp_get.status_code == 200
        assert resp_get.json()["id"] == qid

        # 5. Atualizar quadro
        resp_put = await client.put(f"/quadros/{qid}", json={"nome": "Quadro Atualizado"})
        assert resp_put.status_code == 200
        assert resp_put.json()["nome"] == "Quadro Atualizado"


@pytest.mark.anyio
async def test_ciclo_completo_atividade():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Criar Quadro e obter lista
        resp_q = await client.post("/quadros", json={"nome": "Sprint Kanban", "cor": "#4F46E5"})
        assert resp_q.status_code == 201
        quadro = resp_q.json()
        qid = quadro["id"]
        lista_fazer_id = quadro["listas"][0]["id"]
        lista_concluido_id = quadro["listas"][3]["id"]

        # 2. Criar Categoria e Etiqueta
        resp_cat = await client.post("/categorias", json={"nome": "Testes de API", "cor": "#10B981"})
        cat_id = resp_cat.json()["id"] if resp_cat.status_code == 201 else None

        resp_et = await client.post("/etiquetas", json={"nome": "Bugfix", "cor": "#EF4444"})
        et_id = resp_et.json()["id"] if resp_et.status_code == 201 else None

        # 3. Criar Atividade
        payload_atv = {
            "titulo": "Implementar Validações do Pydantic",
            "descricao": "Garantir tipos e limites de caracteres",
            "status": "A fazer",
            "prioridade": "Alta",
            "data_vencimento": "2026-11-25",
            "lista_id": lista_fazer_id,
            "categoria_id": cat_id,
            "etiqueta_ids": [et_id] if et_id else []
        }
        resp_atv = await client.post("/atividades", json=payload_atv)
        assert resp_atv.status_code == 201
        atv = resp_atv.json()
        aid = atv["id"]
        assert atv["titulo"] == payload_atv["titulo"]
        assert atv["prioridade"] == "Alta"

        # 4. Adicionar item ao checklist
        resp_ck = await client.post(f"/atividades/{aid}/checklist", json={"descricao": "Escrever teste unitário", "concluido": False})
        assert resp_ck.status_code == 201
        ck_id = resp_ck.json()["id"]

        # 5. Marcar checklist como concluído
        resp_ck_put = await client.put(f"/checklist/{ck_id}", json={"concluido": True})
        assert resp_ck_put.status_code == 200
        assert resp_ck_put.json()["concluido"] is True

        # 6. Mover atividade para lista 'Concluído'
        resp_patch = await client.patch(f"/atividades/{aid}/status", json={"lista_id": lista_concluido_id})
        assert resp_patch.status_code == 200
        assert resp_patch.json()["status"] == "Concluído"

        # 7. Listar atividades com filtro
        resp_filter = await client.get("/atividades?status=Concluído")
        assert resp_filter.status_code == 200
        ids = [a["id"] for a in resp_filter.json()]
        assert aid in ids

        # 8. Limpar registros de teste
        await client.delete(f"/atividades/{aid}")
        await client.delete(f"/quadros/{qid}")
