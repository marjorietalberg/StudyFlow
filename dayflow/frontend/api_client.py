import os
import httpx
from typing import Any, Dict, List, Optional, Tuple

API_BASE_URL = os.environ.get("DAYFLOW_API_URL", "http://127.0.0.1:8000")


class DayFlowAPIClient:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip("/")

    def _request(self, method: str, endpoint: str, **kwargs) -> Tuple[Optional[Any], Optional[str]]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.request(method, url, **kwargs)
                if resp.status_code in [200, 201]:
                    return resp.json(), None
                elif resp.status_code == 204:
                    return True, None
                else:
                    detail = "Erro na requisição"
                    try:
                        err_json = resp.json()
                        detail = err_json.get("detail", str(err_json))
                    except Exception:
                        detail = resp.text or f"Erro {resp.status_code}"
                    return None, detail
        except httpx.ConnectError:
            return None, "Não foi possível conectar ao servidor backend (FastAPI na porta 8000). Verifique se o backend está em execução."
        except Exception as e:
            return None, f"Exceção de comunicação: {str(e)}"

    # ==========================================
    # DASHBOARD
    # ==========================================
    def get_dashboard_stats(self) -> Tuple[Optional[Dict], Optional[str]]:
        return self._request("GET", "/dashboard/stats")

    # ==========================================
    # QUADROS
    # ==========================================
    def get_quadros(self) -> Tuple[Optional[List[Dict]], Optional[str]]:
        return self._request("GET", "/quadros")

    def get_quadro(self, quadro_id: int) -> Tuple[Optional[Dict], Optional[str]]:
        return self._request("GET", f"/quadros/{quadro_id}")

    def create_quadro(self, data: Dict) -> Tuple[Optional[Dict], Optional[str]]:
        return self._request("POST", "/quadros", json=data)

    def update_quadro(self, quadro_id: int, data: Dict) -> Tuple[Optional[Dict], Optional[str]]:
        return self._request("PUT", f"/quadros/{quadro_id}", json=data)

    def delete_quadro(self, quadro_id: int) -> Tuple[Optional[Dict], Optional[str]]:
        return self._request("DELETE", f"/quadros/{quadro_id}")

    # ==========================================
    # LISTAS
    # ==========================================
    def get_listas(self, quadro_id: Optional[int] = None) -> Tuple[Optional[List[Dict]], Optional[str]]:
        params = {"quadro_id": quadro_id} if quadro_id else {}
        return self._request("GET", "/listas", params=params)

    def create_lista(self, data: Dict) -> Tuple[Optional[Dict], Optional[str]]:
        return self._request("POST", "/listas", json=data)

    def update_lista(self, lista_id: int, data: Dict) -> Tuple[Optional[Dict], Optional[str]]:
        return self._request("PUT", f"/listas/{lista_id}", json=data)

    def delete_lista(self, lista_id: int) -> Tuple[Optional[Dict], Optional[str]]:
        return self._request("DELETE", f"/listas/{lista_id}")

    # ==========================================
    # ATIVIDADES
    # ==========================================
    def get_atividades(self, params: Optional[Dict] = None) -> Tuple[Optional[List[Dict]], Optional[str]]:
        return self._request("GET", "/atividades", params=params or {})

    def get_atividade(self, atividade_id: int) -> Tuple[Optional[Dict], Optional[str]]:
        return self._request("GET", f"/atividades/{atividade_id}")

    def create_atividade(self, data: Dict) -> Tuple[Optional[Dict], Optional[str]]:
        return self._request("POST", "/atividades", json=data)

    def update_atividade(self, atividade_id: int, data: Dict) -> Tuple[Optional[Dict], Optional[str]]:
        return self._request("PUT", f"/atividades/{atividade_id}", json=data)

    def patch_atividade_status(self, atividade_id: int, data: Dict) -> Tuple[Optional[Dict], Optional[str]]:
        return self._request("PATCH", f"/atividades/{atividade_id}/status", json=data)

    def delete_atividade(self, atividade_id: int) -> Tuple[Optional[Dict], Optional[str]]:
        return self._request("DELETE", f"/atividades/{atividade_id}")

    # ==========================================
    # CATEGORIAS
    # ==========================================
    def get_categorias(self) -> Tuple[Optional[List[Dict]], Optional[str]]:
        return self._request("GET", "/categorias")

    def create_categoria(self, data: Dict) -> Tuple[Optional[Dict], Optional[str]]:
        return self._request("POST", "/categorias", json=data)

    def delete_categoria(self, categoria_id: int) -> Tuple[Optional[Dict], Optional[str]]:
        return self._request("DELETE", f"/categorias/{categoria_id}")

    # ==========================================
    # ETIQUETAS
    # ==========================================
    def get_etiquetas(self) -> Tuple[Optional[List[Dict]], Optional[str]]:
        return self._request("GET", "/etiquetas")

    def create_etiqueta(self, data: Dict) -> Tuple[Optional[Dict], Optional[str]]:
        return self._request("POST", "/etiquetas", json=data)

    def delete_etiqueta(self, etiqueta_id: int) -> Tuple[Optional[Dict], Optional[str]]:
        return self._request("DELETE", f"/etiquetas/{etiqueta_id}")

    # ==========================================
    # CHECKLIST
    # ==========================================
    def add_checklist_item(self, atividade_id: int, data: Dict) -> Tuple[Optional[Dict], Optional[str]]:
        return self._request("POST", f"/atividades/{atividade_id}/checklist", json=data)

    def update_checklist_item(self, checklist_id: int, data: Dict) -> Tuple[Optional[Dict], Optional[str]]:
        return self._request("PUT", f"/checklist/{checklist_id}", json=data)

    def delete_checklist_item(self, checklist_id: int) -> Tuple[Optional[Dict], Optional[str]]:
        return self._request("DELETE", f"/checklist/{checklist_id}")


api = DayFlowAPIClient()
