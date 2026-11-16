import os
import sys
import asyncio
import httpx

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(TEST_DIR, ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from main import app


async def run_all():
    print("🚀 Iniciando testes diretos da API DayFlow...")
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Stats
        resp = await client.get("/dashboard/stats")
        assert resp.status_code == 200, f"Erro status: {resp.status_code}"
        stats = resp.json()
        print("✅ GET /dashboard/stats OK - Total:", stats["total_atividades"])

        # 2. Quadros
        resp_q = await client.get("/quadros")
        assert resp_q.status_code == 200
        print("✅ GET /quadros OK - Total:", len(resp_q.json()))

        # 3. Criar Quadro
        novo_q = {"nome": "Quadro Teste Exec", "cor": "#7C3AED"}
        resp_cq = await client.post("/quadros", json=novo_q)
        assert resp_cq.status_code == 201
        q_dados = resp_cq.json()
        qid = q_dados["id"]
        assert len(q_dados["listas"]) == 4
        print(f"✅ POST /quadros OK - ID: {qid} com 4 listas padrão")

        # 4. Atividades
        lid = q_dados["listas"][0]["id"]
        nova_atv = {
            "titulo": "Atividade de Verificação",
            "status": "A fazer",
            "prioridade": "Alta",
            "lista_id": lid
        }
        resp_atv = await client.post("/atividades", json=nova_atv)
        assert resp_atv.status_code == 201
        aid = resp_atv.json()["id"]
        print(f"✅ POST /atividades OK - ID: {aid}")

        # 5. Checklist
        resp_ck = await client.post(f"/atividades/{aid}/checklist", json={"descricao": "Subtarefa 1", "concluido": False})
        assert resp_ck.status_code == 201
        ckid = resp_ck.json()["id"]
        print(f"✅ POST /atividades/{aid}/checklist OK - ID: {ckid}")

        # 6. Patch status
        resp_patch = await client.patch(f"/atividades/{aid}/status", json={"status": "Concluído"})
        assert resp_patch.status_code == 200
        assert resp_patch.json()["status"] == "Concluído"
        print("✅ PATCH /atividades/{id}/status OK")

        # 7. Cleanup
        await client.delete(f"/atividades/{aid}")
        await client.delete(f"/quadros/{qid}")
        print("✅ Limpeza e exclusão de teste OK")

    print("\n🎉 TODOS OS TESTES DA API PASSARAM COM 100% DE SUCESSO!\n")


if __name__ == "__main__":
    asyncio.run(run_all())
