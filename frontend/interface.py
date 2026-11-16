import sys
import os

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import requests
import gradio as gr
from datetime import date, timedelta, datetime
import calendar
import pandas as pd
from frontend.icons import icon

API_BASE_URL = os.environ.get("API_URL", "http://127.0.0.1:5000/api")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FAVICON_PATH = os.path.join(BASE_DIR, "favicon.svg")
if not os.path.exists(FAVICON_PATH):
    FAVICON_PATH = os.path.join(BASE_DIR, "favicon.ico")

# ==============================================================================
# Funções de Comunicação com a API (Requests)
# ==============================================================================

def api_get(endpoint, params=None):
    try:
        resp = requests.get(f"{API_BASE_URL}/{endpoint}", params=params, timeout=5)
        if resp.status_code == 200:
            return resp.json(), None
        return None, f"Erro {resp.status_code}: {resp.text}"
    except requests.exceptions.ConnectionError:
        return None, "Servidor Flask desconectado (http://127.0.0.1:5000)."
    except Exception as e:
        return None, str(e)


def api_post(endpoint, data):
    try:
        resp = requests.post(f"{API_BASE_URL}/{endpoint}", json=data, timeout=5)
        if resp.status_code in [200, 201]:
            return resp.json(), None
        dados = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
        return None, dados.get('error', resp.text)
    except requests.exceptions.ConnectionError:
        return None, "Servidor Flask desconectado."
    except Exception as e:
        return None, str(e)


def api_patch(endpoint, data=None):
    try:
        resp = requests.patch(f"{API_BASE_URL}/{endpoint}", json=data or {}, timeout=5)
        if resp.status_code == 200:
            return resp.json(), None
        dados = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
        return None, dados.get('error', resp.text)
    except requests.exceptions.ConnectionError:
        return None, "Servidor Flask desconectado."
    except Exception as e:
        return None, str(e)


def api_delete(endpoint):
    try:
        resp = requests.delete(f"{API_BASE_URL}/{endpoint}", timeout=5)
        if resp.status_code == 200:
            return resp.json(), None
        dados = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
        return None, dados.get('error', resp.text)
    except requests.exceptions.ConnectionError:
        return None, "Servidor Flask desconectado."
    except Exception as e:
        return None, str(e)


# ==============================================================================
# Handlers de Autenticação
# ==============================================================================

def login_handler(email, senha):
    email_limpo = str(email or "").strip().lower()
    senha_limpa = str(senha or "").strip()

    if not email_limpo or not senha_limpa:
        return (
            "⚠️ **Atenção:** Digite seu e-mail acadêmico cadastrado e senha para entrar.",
            None,
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(visible=False),
            ""
        )
    
    resp, erro = api_post("auth/login", {"email": email_limpo, "senha": senha_limpa})
    if erro or not resp or "usuario" not in resp:
        msg_erro = erro or "Credenciais inválidas. Verifique seu e-mail e senha."
        return (
            f"❌ **Acesso negado:** {msg_erro}",
            None,
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(visible=False),
            ""
        )
    
    user = resp["usuario"]
    user_header = (
        f'<div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 14px; width: 100%;">'
        f'  <div style="display: flex; align-items: center; gap: 14px;">'
        f'    <div style="width: 44px; height: 44px; border-radius: 12px; background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%); color: white; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 16px; box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3);">'
        f'      {user.get("nome", "A")[0].upper()}'
        f'    </div>'
        f'    <div>'
        f'      <div style="font-size: 17px; font-weight: 800; color: #09090b; letter-spacing: -0.3px;">Olá, {user.get("nome")}!</div>'
        f'      <div style="font-size: 13px; color: #64748b; font-weight: 500;">{user.get("curso")} · <span style="color: #7c3aed; font-weight: 600;">{user.get("email")}</span></div>'
        f'    </div>'
        f'  </div>'
        f'  <div style="display: flex; align-items: center; gap: 8px; background: #f5f3ff; border: 1px solid #ddd6fe; padding: 6px 14px; border-radius: 9999px; color: #6d28d9; font-size: 12px; font-weight: 700;">'
        f'    {icon("flame", 16, "#7c3aed")} 14 dias de foco consecutivo'
        f'  </div>'
        f'</div>'
    )
    return "", user, gr.update(visible=False), gr.update(visible=False), gr.update(visible=True), user_header


def cadastro_handler(nome, email, curso, senha):
    nome_limpo = str(nome or "").strip()
    email_limpo = str(email or "").strip().lower()
    curso_limpo = str(curso or "Engenharia de Software").strip()
    senha_limpa = str(senha or "").strip()

    if not nome_limpo or not email_limpo or not senha_limpa:
        return (
            "⚠️ **Atenção:** Preencha todos os campos obrigatórios (*) para criar sua conta.",
            None,
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(visible=False),
            ""
        )
    
    payload = {
        "nome": nome_limpo,
        "email": email_limpo,
        "curso": curso_limpo,
        "senha": senha_limpa
    }
    resp, erro = api_post("auth/cadastro", payload)
    if erro or not resp or "usuario" not in resp:
        msg_erro = erro or "Não foi possível cadastrar."
        return (
            f"❌ **Erro no cadastro:** {msg_erro}",
            None,
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(visible=False),
            ""
        )
    
    user = resp["usuario"]
    user_header = (
        f'<div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 14px; width: 100%;">'
        f'  <div style="display: flex; align-items: center; gap: 14px;">'
        f'    <div style="width: 44px; height: 44px; border-radius: 12px; background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%); color: white; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 16px; box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3);">'
        f'      {user.get("nome", "A")[0].upper()}'
        f'    </div>'
        f'    <div>'
        f'      <div style="font-size: 17px; font-weight: 800; color: #09090b; letter-spacing: -0.3px;">Olá, {user.get("nome")}!</div>'
        f'      <div style="font-size: 13px; color: #64748b; font-weight: 500;">{user.get("curso")} · <span style="color: #7c3aed; font-weight: 600;">{user.get("email")}</span></div>'
        f'    </div>'
        f'  </div>'
        f'  <div style="display: flex; align-items: center; gap: 8px; background: #f5f3ff; border: 1px solid #ddd6fe; padding: 6px 14px; border-radius: 9999px; color: #6d28d9; font-size: 12px; font-weight: 700;">'
        f'    {icon("flame", 16, "#7c3aed")} 14 dias de foco consecutivo'
        f'  </div>'
        f'</div>'
    )
    return "", user, gr.update(visible=False), gr.update(visible=False), gr.update(visible=True), user_header


def logout_handler():
    return None, gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), ""


# ==============================================================================
# CSS Global SaaS Premium (Fontes, Microinterações, Cores e Profundidade)
# ==============================================================================

HEAD_HTML = """
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64' width='64' height='64'%3E%3Cdefs%3E%3ClinearGradient id='bgGrad' x1='0%25' y1='0%25' x2='100%25' y2='100%25'%3E%3Cstop offset='0%25' stop-color='%237c3aed' /%3E%3Cstop offset='100%25' stop-color='%234f46e5' /%3E%3C/linearGradient%3E%3ClinearGradient id='capGrad' x1='0%25' y1='0%25' x2='100%25' y2='100%25'%3E%3Cstop offset='0%25' stop-color='%23ffffff' /%3E%3Cstop offset='100%25' stop-color='%23f5f3ff' /%3E%3C/linearGradient%3E%3C/defs%3E%3Crect width='64' height='64' rx='16' fill='url(%23bgGrad)' /%3E%3Cpolygon points='32,14 54,25 32,36 10,25' fill='url(%23capGrad)' /%3E%3Cpath d='M18,29.5 L18,39 C18,44 46,44 46,39 L46,29.5' fill='none' stroke='%23ffffff' stroke-width='3' stroke-linecap='round' /%3E%3Cpath d='M47,26.5 L53,35 L53,41' fill='none' stroke='%23c4b5fd' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round' /%3E%3Ccircle cx='53' cy='41' r='2' fill='%23c4b5fd' /%3E%3Cpath d='M22,48 C28,45 36,52 42,48' fill='none' stroke='%23c4b5fd' stroke-width='2.5' stroke-linecap='round' /%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<title>StudyFlow — Sistema Inteligente de Estudos & Gestão Acadêmica</title>
<script>
(function() {
    function enforceLight() {
        try {
            document.documentElement.classList.remove('dark');
            if (document.body) {
                document.body.classList.remove('dark');
            }
            document.documentElement.style.colorScheme = 'light';
            if (document.body) {
                document.body.style.colorScheme = 'light';
            }
        } catch(e) {}
    }
    function hideWorkspaceTabs() {
        try {
            var tabs = document.querySelectorAll('.growsync-tabs > div:first-child, .growsync-tabs [role="tablist"], .app-workspace-container [role="tablist"], .growsync-tabs > .tab-nav');
            tabs.forEach(function(el) {
                el.style.setProperty('display', 'none', 'important');
                el.style.setProperty('visibility', 'hidden', 'important');
                el.style.setProperty('height', '0px', 'important');
                el.style.setProperty('overflow', 'hidden', 'important');
            });
            var footers = document.querySelectorAll('footer:not(.landing-footer)');
            footers.forEach(function(el) {
                el.style.setProperty('display', 'none', 'important');
                el.style.setProperty('visibility', 'hidden', 'important');
                el.style.setProperty('height', '0px', 'important');
                el.style.setProperty('overflow', 'hidden', 'important');
            });
        } catch(e) {}
    }
    window.toggleMobileSidebar = function(open) {
        try {
            var sidebar = document.querySelector('.growsync-sidebar');
            var backdrop = document.getElementById('sf-mobile-backdrop');
            if (!sidebar) return;
            if (open === undefined) {
                open = !sidebar.classList.contains('mobile-drawer-open');
            }
            if (open) {
                sidebar.classList.add('mobile-drawer-open');
                if (backdrop) backdrop.classList.add('active');
                document.body.style.overflow = 'hidden';
            } else {
                sidebar.classList.remove('mobile-drawer-open');
                if (backdrop) backdrop.classList.remove('active');
                document.body.style.overflow = '';
            }
        } catch(e) {}
    };

    document.addEventListener('click', function(e) {
        if (e.target.closest('.sidebar-btn') || e.target.closest('.btn-view-pill') || e.target.closest('.sidebar-btn-logout')) {
            if (window.innerWidth <= 1024) {
                window.toggleMobileSidebar(false);
            }
        }
    });

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            window.toggleMobileSidebar(false);
        }
    });

    enforceLight();
    hideWorkspaceTabs();
    window.addEventListener('DOMContentLoaded', function() { enforceLight(); hideWorkspaceTabs(); });
    window.addEventListener('load', function() { enforceLight(); hideWorkspaceTabs(); });
    setInterval(hideWorkspaceTabs, 300);
    try {
        new MutationObserver(function() {
            if (document.documentElement.classList.contains('dark') || (document.body && document.body.classList.contains('dark'))) {
                enforceLight();
            }
            hideWorkspaceTabs();
        }).observe(document.documentElement, { attributes: true, childList: true, subtree: true });
    } catch(e) {}
})();
</script>
<style>
:root, html, body, .gradio-container, .dark, html.dark, body.dark {
    color-scheme: light !important;
    --background-fill-primary: #ffffff !important;
    --background-fill-secondary: #f8fafc !important;
    --block-background-fill: #ffffff !important;
    --body-background-fill: #ffffff !important;
    --input-background-fill: #ffffff !important;
    --border-color-primary: #e4e4e7 !important;
    --border-color-accent: #7c3aed !important;
    --block-border-color: #e4e4e7 !important;
    --body-text-color: #09090b !important;
    --block-label-text-color: #09090b !important;
    --block-title-text-color: #09090b !important;
    --input-text-color: #09090b !important;
    --primary-500: #7c3aed !important;
    --primary-600: #6d28d9 !important;
    --primary-700: #5b21b6 !important;
}

/* Ocultar Rodapé padrão do Gradio */
footer.svelte-1ed2p3z,
footer[class*="svelte"],
.gradio-container > footer:not(.landing-footer) {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    overflow: hidden !important;
}

.landing-footer {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    background: #ffffff !important;
}

.sf-footer-shortcut {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    padding: 7px 16px !important;
    border-radius: 9999px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    color: #475569 !important;
    text-decoration: none !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 7px !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    cursor: pointer !important;
}

.sf-footer-shortcut svg {
    color: #64748b !important;
    stroke: #64748b !important;
    transition: all 0.2s ease !important;
    flex-shrink: 0 !important;
}

.sf-footer-shortcut:hover {
    background: #fbfbfe !important;
    border-color: #7c3aed !important;
    color: #7c3aed !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 16px rgba(124, 58, 237, 0.14) !important;
}

.sf-footer-shortcut:hover svg {
    color: #7c3aed !important;
    stroke: #7c3aed !important;
}
</style>
"""

custom_theme_css = """
:root {
    --sf-primary: #7c3aed;
    --sf-primary-hover: #6d28d9;
    --sf-primary-light: #ede9fe;
    --sf-accent: #8b5cf6;
    --sf-dark: #09090b;
    --sf-dark-surface: #18181b;
    --sf-border: #e4e4e7;
    --sf-bg-subtle: #f8fafc;
    --sf-text-main: #09090b;
    --sf-text-muted: #64748b;
    color-scheme: light !important;
}

/* Box-sizing Universal & Prevenção de Overflow Horizontal */
*, *::before, *::after {
    box-sizing: border-box !important;
}

html, body {
    overflow-x: hidden !important;
    width: 100% !important;
    max-width: 100vw !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Neutralização Total do Modo Escuro em Todo o Gradio */
html, body, .gradio-container, .main, .contain, .wrap,
.dark, html.dark, body.dark, .dark .gradio-container, .dark .main,
.dark .wrap, .dark .contain {
    max-width: 100% !important;
    width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    background-color: #ffffff !important;
    background: #ffffff !important;
    color: #09090b !important;
    font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    -webkit-font-smoothing: antialiased;
    color-scheme: light !important;
}

/* Ocultar Rodapé padrão do Gradio */
footer.svelte-1ed2p3z,
footer[class*="svelte"],
.gradio-container > footer:not(.landing-footer) {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    overflow: hidden !important;
}

.landing-footer {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    background: #ffffff !important;
}

.sf-footer-shortcut {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    padding: 7px 16px !important;
    border-radius: 9999px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    color: #475569 !important;
    text-decoration: none !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 7px !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    cursor: pointer !important;
}

.sf-footer-shortcut svg {
    color: #64748b !important;
    stroke: #64748b !important;
    transition: all 0.2s ease !important;
    flex-shrink: 0 !important;
}

.sf-footer-shortcut:hover {
    background: #fbfbfe !important;
    border-color: #7c3aed !important;
    color: #7c3aed !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 16px rgba(124, 58, 237, 0.14) !important;
}

.sf-footer-shortcut:hover svg {
    color: #7c3aed !important;
    stroke: #7c3aed !important;
}

.gradio-container,
div[class*="gradio-container"],
.main, .contain, .wrap {
    overflow-x: hidden !important;
    max-width: 100% !important;
    width: 100% !important;
    padding: 0 !important;
}

/* Remove todos os fundos escuros do Gradio */
.dark div,
.dark fieldset,
.dark form,
.dark section,
.dark .block,
.dark .group,
.dark .panel,
.dark .tabitem,
.dark .tabs,
.dark .form {
    background-color: #ffffff !important;
    background: #ffffff !important;
    color: #09090b !important;
    border-color: #e4e4e7 !important;
}

/* Navbar Fixa / Topo */
.navbar-black,
.dark .navbar-black,
div.navbar-black {
    background-color: #09090b !important;
    background: #09090b !important;
    border-bottom: 1px solid #27272a !important;
    padding: 12px 35px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    width: 100% !important;
    box-sizing: border-box !important;
}

/* Neutralizar QUALQUER fundo herdado pelo Gradio dentro da Navbar */
.navbar-black,
.navbar-black > div,
.navbar-black div,
.navbar-black .block,
.navbar-black .column,
.navbar-black .row,
.navbar-black .form,
.navbar-black .gap,
.navbar-black fieldset,
.navbar-black .wrap,
.navbar-black div[class*="block"],
.dark .navbar-black,
.dark .navbar-black > div,
.dark .navbar-black div,
.dark .navbar-black .block,
.dark .navbar-black .column,
.dark .navbar-black .row,
.dark .navbar-black .form,
.dark .navbar-black .gap,
.dark .navbar-black fieldset,
.dark .navbar-black .wrap,
.dark .navbar-black div[class*="block"],
.nav-col-logo,
.nav-col-actions,
.nav-col-logo div,
.nav-col-actions div,
.nav-col-logo .block,
.nav-col-actions .block,
.dark .nav-col-logo,
.dark .nav-col-actions,
.dark .nav-col-logo *,
.dark .nav-col-actions * {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin: 0 !important;
}

.navbar-black,
.dark .navbar-black {
    background: #09090b !important;
    background-color: #09090b !important;
}

/* Links da Navbar */
.nav-link {
    color: #a1a1aa;
    font-size: 14px;
    font-weight: 600;
    text-decoration: none;
    transition: color 0.2s ease;
    padding: 6px 12px;
    border-radius: 8px;
}
.nav-link:hover {
    color: #ffffff;
    background-color: rgba(255, 255, 255, 0.06);
}

/* Layout da Coluna e Row de Ações da Navbar (Desktop & Global) */
.nav-col-actions,
div.nav-col-actions,
.navbar-black .nav-col-actions,
.dark .navbar-black .nav-col-actions {
    display: flex !important;
    align-items: center !important;
    justify-content: flex-end !important;
    flex: 0 0 auto !important;
    width: auto !important;
    min-width: 0 !important;
    max-width: none !important;
    flex-grow: 0 !important;
    margin-left: auto !important;
}

.nav-actions-row,
div.nav-actions-row,
.navbar-black .nav-actions-row,
.dark .navbar-black .nav-actions-row {
    display: inline-flex !important;
    flex-direction: row !important;
    align-items: center !important;
    justify-content: flex-end !important;
    flex-wrap: nowrap !important;
    gap: 10px !important;
    width: auto !important;
    min-width: 0 !important;
    flex: 0 0 auto !important;
}

.nav-actions-row > div,
.navbar-black .nav-actions-row > div,
.dark .navbar-black .nav-actions-row > div,
.navbar-black div.btn-nav-login,
.navbar-black div.btn-nav-cadastrar {
    width: auto !important;
    min-width: 0 !important;
    flex: 0 0 auto !important;
    flex-grow: 0 !important;
    flex-shrink: 0 !important;
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin: 0 !important;
    display: inline-flex !important;
    align-items: center !important;
}

/* Botões da Navbar (Formato Redondo Pill, sem ícones - Largura Compacta) */
.btn-nav-login,
button.btn-nav-login,
.navbar-black .btn-nav-login,
.dark .navbar-black .btn-nav-login,
.navbar-black button.btn-nav-login {
    background: #18181b !important;
    background-color: #18181b !important;
    color: #ffffff !important;
    border: 1.5px solid #3f3f46 !important;
    border-radius: 9999px !important;
    font-weight: 700 !important;
    font-size: 13.5px !important;
    padding: 7px 18px !important;
    width: auto !important;
    min-width: 0 !important;
    max-width: fit-content !important;
    flex: 0 0 auto !important;
    flex-grow: 0 !important;
    flex-shrink: 0 !important;
    cursor: pointer !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
    white-space: nowrap !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-sizing: border-box !important;
}

.btn-nav-login:hover,
button.btn-nav-login:hover,
.navbar-black .btn-nav-login:hover,
.dark .navbar-black .btn-nav-login:hover {
    background: #27272a !important;
    background-color: #27272a !important;
    border-color: #a1a1aa !important;
    color: #ffffff !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 18px rgba(255, 255, 255, 0.14) !important;
}

.btn-nav-cadastrar,
button.btn-nav-cadastrar,
.navbar-black .btn-nav-cadastrar,
.dark .navbar-black .btn-nav-cadastrar,
.navbar-black button.btn-nav-cadastrar {
    background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%) !important;
    background-color: #7c3aed !important;
    color: #ffffff !important;
    border: 1.5px solid #8b5cf6 !important;
    border-radius: 9999px !important;
    font-weight: 700 !important;
    font-size: 13.5px !important;
    padding: 7px 20px !important;
    width: auto !important;
    min-width: 0 !important;
    max-width: fit-content !important;
    flex: 0 0 auto !important;
    flex-grow: 0 !important;
    flex-shrink: 0 !important;
    box-shadow: 0 4px 16px rgba(124, 58, 237, 0.45) !important;
    cursor: pointer !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    white-space: nowrap !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-sizing: border-box !important;
}

.btn-nav-cadastrar:hover,
button.btn-nav-cadastrar:hover,
.navbar-black .btn-nav-cadastrar:hover,
.dark .navbar-black .btn-nav-cadastrar:hover {
    background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%) !important;
    border-color: #a78bfa !important;
    color: #ffffff !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(124, 58, 237, 0.65) !important;
}

/* Estilização Geral de Todos os Botões (Formato Pill + Transição) */
button {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    border-radius: 9999px !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

button[variant="stop"] {
    background: #fff1f2 !important;
    background-color: #fff1f2 !important;
    color: #e11d48 !important;
    border: 1.5px solid #fecdd3 !important;
    border-radius: 9999px !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    padding: 8px 20px !important;
    cursor: pointer !important;
}

button[variant="stop"]:hover {
    background: #ffe4e6 !important;
    background-color: #ffe4e6 !important;
    border-color: #f87171 !important;
    color: #be123c !important;
    box-shadow: 0 4px 12px rgba(225, 29, 72, 0.15) !important;
}

/* ====================================================================== */
/* TELA DE AUTENTICAÇÃO SAAS (LOGIN & CADASTRO) - CLEAN & MODERNO */
/* ====================================================================== */
.auth-page-container,
div.auth-page-container,
fieldset.auth-page-container {
    background: #f8fafc !important;
    background-color: #f8fafc !important;
    padding: 30px 20px 60px 20px !important;
    width: 100% !important;
    min-height: 85vh !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    align-items: center !important;
    box-sizing: border-box !important;
    border: none !important;
    box-shadow: none !important;
}

/* Container Split Screen SaaS */
.auth-split-wrapper,
div.auth-split-wrapper {
    display: flex !important;
    flex-direction: row !important;
    align-items: stretch !important;
    max-width: 1100px !important;
    width: 100% !important;
    margin: 0 auto !important;
    background: #ffffff !important;
    background-color: #ffffff !important;
    border-radius: 28px !important;
    border: 1.5px solid #e2e8f0 !important;
    box-shadow: 0 25px 60px -15px rgba(124, 58, 237, 0.22), 0 4px 16px rgba(0, 0, 0, 0.04) !important;
    overflow: hidden !important;
    box-sizing: border-box !important;
}

/* Painel Esquerdo Roxo (Visual Showcase) */
.auth-left-banner,
div.auth-left-banner {
    background: linear-gradient(145deg, #1e1b4b 0%, #3b0764 45%, #7c3aed 100%) !important;
    background-color: #1e1b4b !important;
    padding: 44px 38px !important;
    color: #ffffff !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: space-between !important;
    position: relative !important;
    overflow: hidden !important;
    border: none !important;
    box-sizing: border-box !important;
}

.auth-left-banner::before {
    content: "" !important;
    position: absolute !important;
    top: -80px !important;
    right: -80px !important;
    width: 280px !important;
    height: 280px !important;
    background: radial-gradient(circle, rgba(168, 85, 247, 0.38) 0%, transparent 70%) !important;
    pointer-events: none !important;
}

/* Painel Direito (Formulário) */
.auth-right-form,
div.auth-right-form {
    background: #ffffff !important;
    background-color: #ffffff !important;
    padding: 38px 44px !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    border: none !important;
    box-sizing: border-box !important;
}

/* Neutralizar fundos escuros do Gradio dentro do formulário */
.auth-right-form,
.auth-right-form > div,
.auth-right-form .form,
.auth-right-form .block,
.auth-right-form fieldset,
.auth-right-form div[class*="block"] {
    background-color: transparent !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

.auth-right-form label,
.auth-right-form span {
    font-size: 13px !important;
    font-weight: 700 !important;
    color: #09090b !important;
    display: block !important;
}

.auth-right-form input {
    background-color: #ffffff !important;
    background: #ffffff !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 12px !important;
    color: #09090b !important;
    padding: 12px 16px !important;
    font-size: 14px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
    box-sizing: border-box !important;
}

.auth-right-form input:focus {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 4px rgba(124, 58, 237, 0.15) !important;
    outline: none !important;
}

/* Botão Voltar ao Início com ícone Arrow-Left */
.btn-voltar-inicio,
button.btn-voltar-inicio {
    background: #f1f5f9 !important;
    background-color: #f1f5f9 !important;
    color: #475569 !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 9999px !important;
    font-size: 12.5px !important;
    font-weight: 700 !important;
    padding: 7px 18px !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 8px !important;
    width: auto !important;
    margin-bottom: 8px !important;
}

button.btn-voltar-inicio::before {
    content: "" !important;
    display: inline-block !important;
    width: 15px !important;
    height: 15px !important;
    margin-right: 6px !important;
    vertical-align: middle !important;
    background-size: contain !important;
    background-repeat: no-repeat !important;
    background-position: center !important;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%2364748b' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cline x1='19' y1='12' x2='5' y2='12'/%3E%3Cpolyline points='12 19 5 12 12 5'/%3E%3C/svg%3E") !important;
}

button.btn-voltar-inicio:hover {
    background: #ede9fe !important;
    background-color: #ede9fe !important;
    color: #7c3aed !important;
    border-color: #c4b5fd !important;
    transform: translateX(-3px) !important;
}

button.btn-voltar-inicio:hover::before {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%237c3aed' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cline x1='19' y1='12' x2='5' y2='12'/%3E%3Cpolyline points='12 19 5 12 12 5'/%3E%3C/svg%3E") !important;
}

/* Botão Primário de Login com ícone Log-In */
.btn-auth-primary,
button.btn-auth-primary {
    background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%) !important;
    background-color: #7c3aed !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 800 !important;
    font-size: 14.5px !important;
    padding: 13px 26px !important;
    cursor: pointer !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 8px 24px -4px rgba(124, 58, 237, 0.45) !important;
    width: 100% !important;
    margin-top: 14px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 8px !important;
}

button.btn-auth-primary::before {
    content: "" !important;
    display: inline-block !important;
    width: 17px !important;
    height: 17px !important;
    margin-right: 8px !important;
    vertical-align: middle !important;
    background-size: contain !important;
    background-repeat: no-repeat !important;
    background-position: center !important;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%23ffffff' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4'/%3E%3Cpolyline points='10 17 15 12 10 7'/%3E%3Cline x1='15' y1='12' x2='3' y2='12'/%3E%3C/svg%3E") !important;
}

.btn-auth-primary:hover,
button.btn-auth-primary:hover {
    background: linear-gradient(135deg, #6d28d9 0%, #5b21b6 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 28px -4px rgba(124, 58, 237, 0.6) !important;
}

/* Botão de Cadastro com ícone User-Plus */
.btn-auth-cadastro,
button.btn-auth-cadastro {
    background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%) !important;
    background-color: #7c3aed !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 800 !important;
    font-size: 14.5px !important;
    padding: 13px 26px !important;
    cursor: pointer !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 8px 24px -4px rgba(124, 58, 237, 0.45) !important;
    width: 100% !important;
    margin-top: 14px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 8px !important;
}

button.btn-auth-cadastro::before {
    content: "" !important;
    display: inline-block !important;
    width: 17px !important;
    height: 17px !important;
    margin-right: 8px !important;
    vertical-align: middle !important;
    background-size: contain !important;
    background-repeat: no-repeat !important;
    background-position: center !important;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%23ffffff' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2'/%3E%3Ccircle cx='8.5' cy='7' r='4'/%3E%3Cline x1='20' y1='8' x2='20' y2='14'/%3E%3Cline x1='23' y1='11' x2='17' y2='11'/%3E%3C/svg%3E") !important;
}

.btn-auth-cadastro:hover,
button.btn-auth-cadastro:hover {
    background: linear-gradient(135deg, #6d28d9 0%, #4338ca 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 28px -4px rgba(124, 58, 237, 0.6) !important;
}

/* Responsividade Mobile da Tela de Autenticação */
@media (max-width: 900px) {
    .auth-split-wrapper,
    div.auth-split-wrapper {
        flex-direction: column !important;
        max-width: 480px !important;
        border-radius: 20px !important;
    }
    .auth-left-banner,
    div.auth-left-banner {
        display: none !important;
    }
    .auth-right-form,
    div.auth-right-form {
        padding: 30px 22px !important;
    }
}

/* Abas de Autenticação */
.auth-tabs .tab-nav {
    border-bottom: 2px solid #f1f5f9 !important;
    margin-bottom: 22px !important;
    display: flex !important;
    justify-content: center !important;
    gap: 8px !important;
    background: transparent !important;
    border-top: none !important;
    border-left: none !important;
    border-right: none !important;
}

.auth-tabs .tab-nav button {
    border-radius: 9999px !important;
    padding: 8px 22px !important;
    font-size: 14px !important;
    font-weight: 700 !important;
    color: #64748b !important;
    background: transparent !important;
    border: 1.5px solid transparent !important;
    transition: all 0.2s ease !important;
}

.auth-tabs .tab-nav button.selected {
    background: #f5f3ff !important;
    background-color: #f5f3ff !important;
    color: #7c3aed !important;
    border-color: #ddd6fe !important;
    box-shadow: 0 2px 8px rgba(124, 58, 237, 0.12) !important;
}

/* Feedback de Autenticação (Alertas de Erro e Sucesso) */
.auth-msg-box,
div.auth-msg-box {
    margin-top: 14px !important;
    font-size: 13.5px !important;
    font-weight: 600 !important;
    line-height: 1.5 !important;
    text-align: center !important;
}

.auth-msg-box p {
    margin: 0 !important;
    padding: 10px 14px !important;
    border-radius: 10px !important;
    display: inline-block !important;
    width: 100% !important;
    box-sizing: border-box !important;
}

/* ====================================================================== */
/* AMBIENTE DO ESTUDANTE (LAYOUT GROWSYNC: SIDEBAR + DASHBOARD) */
/* ====================================================================== */
.app-workspace-container {
    background: #f8fafc !important;
    background-color: #f8fafc !important;
    padding: 10px 14px 40px 14px !important;
    width: 100% !important;
    max-width: 100% !important;
    margin: 0 !important;
    box-sizing: border-box !important;
}

.growsync-workspace-layout {
    display: flex !important;
    flex-direction: row !important;
    gap: 14px !important;
    width: 100% !important;
    max-width: 100% !important;
    margin: 0 !important;
    box-sizing: border-box !important;
    align-items: flex-start !important;
}

.growsync-sidebar {
    background: #ffffff !important;
    background-color: #ffffff !important;
    border: 1.5px solid #e4e4e7 !important;
    border-radius: 18px !important;
    padding: 12px 8px !important;
    box-shadow: 0 4px 18px rgba(0, 0, 0, 0.03) !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 3px !important;
    box-sizing: border-box !important;
    width: 205px !important;
    min-width: 205px !important;
    max-width: 205px !important;
    flex-shrink: 0 !important;
    align-self: flex-start !important;
}

.sidebar-section-title {
    font-size: 10px !important;
    font-weight: 800 !important;
    letter-spacing: 1px !important;
    color: #a1a1aa !important;
    padding: 8px 10px 3px 10px !important;
    text-transform: uppercase !important;
}

.sidebar-btn,
button.sidebar-btn {
    background: transparent !important;
    background-color: transparent !important;
    color: #475569 !important;
    border: 1px solid transparent !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    padding: 8px 10px !important;
    text-align: left !important;
    justify-content: flex-start !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    display: flex !important;
    align-items: center !important;
    gap: 9px !important;
}

.sidebar-btn:hover,
button.sidebar-btn:hover {
    background: #f5f3ff !important;
    background-color: #f5f3ff !important;
    color: #7c3aed !important;
    border-color: #ddd6fe !important;
    transform: translateX(3px) !important;
    box-shadow: 0 2px 8px rgba(124, 58, 237, 0.08) !important;
}

.sidebar-btn.active,
button.sidebar-btn.active {
    background: #f5f3ff !important;
    background-color: #f5f3ff !important;
    color: #7c3aed !important;
    border-color: #ddd6fe !important;
    box-shadow: 0 2px 8px rgba(124, 58, 237, 0.12) !important;
    font-weight: 800 !important;
}

/* Ícones Lucide Vetoriais SVG nos Botões da Sidebar */
.btn-side-dash::before {
    content: '' !important;
    display: inline-block !important;
    width: 16px !important;
    height: 16px !important;
    flex-shrink: 0 !important;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%237c3aed' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect width='7' height='9' x='3' y='3' rx='1'/%3E%3Crect width='7' height='5' x='14' y='3' rx='1'/%3E%3Crect width='7' height='9' x='14' y='12' rx='1'/%3E%3Crect width='7' height='5' x='3' y='16' rx='1'/%3E%3C/svg%3E") !important;
    background-repeat: no-repeat !important;
    background-position: center !important;
}

.btn-side-agenda::before {
    content: '' !important;
    display: inline-block !important;
    width: 16px !important;
    height: 16px !important;
    flex-shrink: 0 !important;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%237c3aed' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect width='18' height='18' x='3' y='4' rx='2'/%3E%3Cpath d='M16 2v4M8 2v4M3 10h18'/%3E%3C/svg%3E") !important;
    background-repeat: no-repeat !important;
    background-position: center !important;
}

.btn-side-tarefas::before {
    content: '' !important;
    display: inline-block !important;
    width: 16px !important;
    height: 16px !important;
    flex-shrink: 0 !important;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%237c3aed' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='9 11 12 14 22 4'/%3E%3Cpath d='M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11'/%3E%3C/svg%3E") !important;
    background-repeat: no-repeat !important;
    background-position: center !important;
}

.btn-side-disc::before {
    content: '' !important;
    display: inline-block !important;
    width: 16px !important;
    height: 16px !important;
    flex-shrink: 0 !important;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%237c3aed' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z'/%3E%3Cpath d='M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z'/%3E%3C/svg%3E") !important;
    background-repeat: no-repeat !important;
    background-position: center !important;
}

.btn-side-pomodoro::before {
    content: '' !important;
    display: inline-block !important;
    width: 16px !important;
    height: 16px !important;
    flex-shrink: 0 !important;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%237c3aed' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cline x1='10' x2='14' y1='2' y2='2'/%3E%3Cline x1='12' x2='15' y1='14' y2='11'/%3E%3Ccircle cx='12' cy='14' r='8'/%3E%3C/svg%3E") !important;
    background-repeat: no-repeat !important;
    background-position: center !important;
}

.btn-side-swagger::before {
    content: '' !important;
    display: inline-block !important;
    width: 16px !important;
    height: 16px !important;
    flex-shrink: 0 !important;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%237c3aed' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolygon points='13 2 3 14 12 14 11 22 21 10 12 10 13 2'/%3E%3C/svg%3E") !important;
    background-repeat: no-repeat !important;
    background-position: center !important;
}

.sidebar-btn-logout,
button.sidebar-btn-logout {
    background: #fff1f2 !important;
    background-color: #fff1f2 !important;
    color: #e11d48 !important;
    border: 1px solid #fecdd3 !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 12.5px !important;
    padding: 8px 10px !important;
    width: 100% !important;
    margin-top: 8px !important;
    text-align: left !important;
    cursor: pointer !important;
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    transition: all 0.2s ease !important;
}

.sidebar-btn-logout:hover,
button.sidebar-btn-logout:hover {
    background: #ffe4e6 !important;
    color: #be123c !important;
    border-color: #fda4af !important;
    transform: translateX(2px) !important;
}

.btn-side-logout::before {
    content: '' !important;
    display: inline-block !important;
    width: 16px !important;
    height: 16px !important;
    flex-shrink: 0 !important;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23e11d48' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4'/%3E%3Cpolyline points='16 17 21 12 16 7'/%3E%3Cline x1='21' x2='9' y1='12' y2='12'/%3E%3C/svg%3E") !important;
    background-repeat: no-repeat !important;
    background-position: center !important;
}

.growsync-main {
    flex: 1 !important;
    width: calc(100% - 219px) !important;
    min-width: 0 !important;
    box-sizing: border-box !important;
}

/* Ocultar barra duplicada de abas do Gradio */
.growsync-tabs > div:first-child,
.growsync-tabs > div[role="tablist"],
.growsync-tabs .tab-nav,
.growsync-tabs div[role="tablist"],
.app-workspace-container div[role="tablist"],
.app-workspace-container .tab-nav,
div.tabs.growsync-tabs > div.tab-nav,
div.tabs.growsync-tabs > div:first-child {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
    border: none !important;
}

/* Toolbar Superior da Agenda & Calendário */
.cal-toolbar {
    background: #ffffff !important;
    border: 1.5px solid #e4e4e7 !important;
    border-radius: 18px !important;
    padding: 12px 18px !important;
    margin-bottom: 18px !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    flex-wrap: wrap !important;
    gap: 12px !important;
}

.cal-toolbar button {
    width: auto !important;
    margin: 0 !important;
}

.btn-cal-add,
button.btn-cal-add {
    background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%) !important;
    background-color: #7c3aed !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 9999px !important;
    font-weight: 800 !important;
    font-size: 13.5px !important;
    padding: 10px 24px !important;
    cursor: pointer !important;
    box-shadow: 0 4px 14px rgba(124, 58, 237, 0.35) !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    width: auto !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 8px !important;
}

.btn-cal-add:hover,
button.btn-cal-add:hover {
    background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(124, 58, 237, 0.5) !important;
}

.btn-cal-refresh,
button.btn-cal-refresh {
    background: #f8fafc !important;
    background-color: #f8fafc !important;
    color: #475569 !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 9999px !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    padding: 9px 20px !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    width: auto !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
}

.btn-cal-refresh:hover,
button.btn-cal-refresh:hover {
    background: #f1f5f9 !important;
    color: #09090b !important;
    border-color: #cbd5e1 !important;
    transform: translateY(-1px) !important;
}

/* ====================================================================== */
/* ESTILOS DA GRADE MENSAL DE CALENDÁRIO VIBRANTE & INOVADORA */
/* ====================================================================== */
.calendar-grid-card {
    background: #ffffff !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 24px !important;
    padding: 24px 28px !important;
    margin-bottom: 28px !important;
    box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.04), 0 0 0 1px rgba(124, 58, 237, 0.04) !important;
    position: relative !important;
    overflow: hidden !important;
}

.cal-month-header {
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    margin-bottom: 20px !important;
    flex-wrap: wrap !important;
    gap: 16px !important;
    padding-bottom: 16px !important;
    border-bottom: 1.5px solid #f1f5f9 !important;
}

.cal-weekday-grid {
    display: grid !important;
    grid-template-columns: repeat(7, 1fr) !important;
    gap: 10px !important;
    text-align: center !important;
    margin-bottom: 10px !important;
}

.cal-weekday-col {
    font-size: 11.5px !important;
    font-weight: 800 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
    color: #475569 !important;
    padding: 9px 0 !important;
    background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%) !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02) !important;
}

.cal-weekday-col.is-weekend {
    background: linear-gradient(180deg, #faf5ff 0%, #f3e8ff 100%) !important;
    border-color: #e9d5ff !important;
    color: #7c3aed !important;
}

.cal-days-grid {
    display: grid !important;
    grid-template-columns: repeat(7, 1fr) !important;
    gap: 10px !important;
}

.cal-day-cell {
    min-height: 108px !important;
    background: #ffffff !important;
    border: 1.5px solid #edf2f7 !important;
    border-radius: 16px !important;
    padding: 10px !important;
    display: flex !important;
    flex-direction: column !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-sizing: border-box !important;
    position: relative !important;
    overflow: hidden !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02) !important;
}

.cal-day-cell:hover {
    background: #ffffff !important;
    border-color: #a78bfa !important;
    transform: translateY(-3px) scale(1.012) !important;
    box-shadow: 0 12px 28px -6px rgba(124, 58, 237, 0.14) !important;
    z-index: 5 !important;
}

.cal-day-cell.is-today {
    background: linear-gradient(180deg, #fbf7ff 0%, #ffffff 100%) !important;
    border: 2px solid #a855f7 !important;
    box-shadow: 0 0 0 3px rgba(168, 85, 247, 0.18), 0 8px 24px rgba(124, 58, 237, 0.15) !important;
}

.cal-day-cell.is-empty {
    background: #f8fafc !important;
    opacity: 0.35 !important;
    border: 1px dashed #cbd5e1 !important;
    cursor: default !important;
}

.cal-day-num {
    font-size: 13.5px !important;
    font-weight: 800 !important;
    color: #334155 !important;
}

.cal-day-cell.is-today .cal-day-num {
    color: #ffffff !important;
}

.cal-heat-bar {
    position: absolute !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    height: 3.5px !important;
    border-top-left-radius: 14px !important;
    border-top-right-radius: 14px !important;
}

.cal-event-badge {
    font-size: 10px !important;
    font-weight: 700 !important;
    padding: 3.5px 7px !important;
    border-radius: 8px !important;
    margin-top: 3px !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    line-height: 1.3 !important;
    display: flex !important;
    align-items: center !important;
    gap: 4px !important;
    transition: transform 0.15s ease !important;
    cursor: pointer !important;
}

.cal-event-badge:hover {
    transform: scale(1.03) !important;
}

/* Card de formulário da agenda */
.add-agenda-card {
    background: #ffffff !important;
    background-color: #ffffff !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 24px !important;
    padding: 24px 28px !important;
    margin-top: 20px !important;
    margin-bottom: 24px !important;
    box-shadow: 0 10px 30px -5px rgba(124, 58, 237, 0.06), 0 0 0 1px rgba(124, 58, 237, 0.04) !important;
}

.add-agenda-card .form,
.add-agenda-card fieldset,
.add-agenda-card .block,
.add-agenda-card div[class*="block"],
.add-agenda-card .wrap,
.add-agenda-card .wrap-inner,
.add-agenda-card .gr-panel,
.add-agenda-card .gr-box {
    background: #ffffff !important;
    background-color: #ffffff !important;
    border-color: #e2e8f0 !important;
}

.add-agenda-card label {
    font-size: 13px !important;
    font-weight: 800 !important;
    color: #0f172a !important;
    margin-bottom: 6px !important;
    display: block !important;
}

.add-agenda-card input[type="text"],
.add-agenda-card input[type="password"],
.add-agenda-card input[type="email"],
.add-agenda-card input[type="date"],
.add-agenda-card select,
.add-agenda-card textarea {
    background: #ffffff !important;
    background-color: #ffffff !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 12px !important;
    padding: 10px 14px !important;
    color: #0f172a !important;
    font-size: 13.5px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}

.add-agenda-card input[type="text"]:focus,
.add-agenda-card input[type="password"]:focus,
.add-agenda-card input[type="email"]:focus,
.add-agenda-card input[type="date"]:focus,
.add-agenda-card select:focus,
.add-agenda-card textarea:focus {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.18) !important;
    outline: none !important;
}

.student-header-bar {
    background: #ffffff !important;
    background-color: #ffffff !important;
    border: 1.5px solid #e4e4e7 !important;
    border-radius: 18px !important;
    padding: 16px 24px !important;
    margin-bottom: 24px !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
}

/* Barra Superior de Visualizações estilo ClickUp / Trello */
.board-header-bar {
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    flex-wrap: wrap !important;
    gap: 12px !important;
    padding: 12px 20px !important;
    background: #ffffff !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 18px !important;
    margin-bottom: 16px !important;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02) !important;
}

.board-title-wrapper {
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
}

.board-title-text {
    font-size: 17px !important;
    font-weight: 900 !important;
    color: #09090b !important;
    letter-spacing: -0.4px !important;
}

.board-view-buttons {
    display: flex !important;
    align-items: center !important;
    gap: 6px !important;
    flex-wrap: wrap !important;
}

.btn-view-pill,
button.btn-view-pill {
    background: #f8fafc !important;
    color: #475569 !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 9999px !important;
    padding: 6px 16px !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    box-shadow: none !important;
}

.btn-view-pill:hover,
button.btn-view-pill:hover {
    background: #f5f3ff !important;
    color: #7c3aed !important;
    border-color: #ddd6fe !important;
    transform: translateY(-1px) !important;
}

/* Kanban Board Layout (5 Colunas Horizontais) */
.kanban-board-wrapper {
    width: 100% !important;
    overflow-x: auto !important;
    padding-bottom: 16px !important;
    margin-top: 10px !important;
}

.kanban-grid-row {
    display: flex !important;
    flex-direction: row !important;
    gap: 14px !important;
    min-width: 1150px !important;
    align-items: stretch !important;
}

.kanban-column-box {
    flex: 1 1 220px !important;
    min-width: 215px !important;
    background: #f8fafc !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 16px !important;
    display: flex !important;
    flex-direction: column !important;
    box-sizing: border-box !important;
    overflow: hidden !important;
}

.kanban-column-header {
    padding: 12px 16px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    border-bottom: 1.5px solid #e2e8f0 !important;
    background: #ffffff !important;
}

.kanban-column-header-title {
    font-size: 13.5px !important;
    font-weight: 800 !important;
    color: #0f172a !important;
    display: flex !important;
    align-items: center !important;
    gap: 6px !important;
}

.kanban-badge-count {
    font-size: 11px !important;
    font-weight: 800 !important;
    padding: 2px 7px !important;
    border-radius: 9999px !important;
    background: #f1f5f9 !important;
    color: #475569 !important;
}

.kanban-column-cards {
    padding: 12px 10px !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 10px !important;
    min-height: 280px !important;
    max-height: 65vh !important;
    overflow-y: auto !important;
}

.kanban-task-card {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    padding: 12px 14px !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03) !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-sizing: border-box !important;
    text-align: left !important;
}

.kanban-task-card:hover {
    border-color: #a78bfa !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 18px rgba(124, 58, 237, 0.1) !important;
}

.kanban-empty-placeholder {
    padding: 32px 12px !important;
    text-align: center !important;
    color: #94a3b8 !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    border: 1.5px dashed #cbd5e1 !important;
    border-radius: 10px !important;
    margin: 8px 0 !important;
    background: rgba(248, 250, 252, 0.5) !important;
}

/* Grid de Cards de Categorias */
.categories-grid {
    display: grid !important;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)) !important;
    gap: 14px !important;
    margin-top: 14px !important;
}

.category-card {
    background: #ffffff !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 16px !important;
    padding: 18px 20px !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: space-between !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02) !important;
    transition: all 0.2s ease !important;
}

.category-card:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06) !important;
    border-color: #cbd5e1 !important;
}

.app-workspace-container .tabs {
    background: transparent !important;
    border: none !important;
}

.app-workspace-container .tab-nav,
.growsync-tabs > .tab-nav {
    display: none !important;
}

.app-workspace-container .tabitem {
    background: #ffffff !important;
    background-color: #ffffff !important;
    border: 1.5px solid #e4e4e7 !important;
    border-radius: 20px !important;
    padding: 28px !important;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02) !important;
}

/* FAQ Accordion Styling com Alto Contraste */
details.faq-item {
    background: #ffffff !important;
    border: 1.5px solid #e4e4e7 !important;
    border-radius: 16px !important;
    padding: 22px 26px !important;
    margin-bottom: 14px !important;
    cursor: pointer !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02) !important;
}

details.faq-item:hover {
    border-color: #c4b5fd !important;
    box-shadow: 0 8px 20px rgba(124, 58, 237, 0.08) !important;
    transform: translateY(-2px) !important;
}

details.faq-item[open] {
    border-color: #7c3aed !important;
    box-shadow: 0 10px 25px rgba(124, 58, 237, 0.12) !important;
    background: #ffffff !important;
}

summary.faq-question {
    list-style: none !important;
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    font-weight: 800 !important;
    font-size: 17px !important;
    color: #09090b !important;
    user-select: none !important;
    outline: none !important;
}

summary.faq-question::-webkit-details-marker {
    display: none !important;
}

summary.faq-question span {
    color: #09090b !important;
    font-weight: 800 !important;
    font-size: 17px !important;
    letter-spacing: -0.3px !important;
}

details.faq-item[open] summary.faq-question span {
    color: #7c3aed !important;
}

.faq-answer {
    color: #475569 !important;
    font-size: 14.5px !important;
    line-height: 1.7 !important;
    margin: 16px 0 0 0 !important;
    padding-top: 16px !important;
    border-top: 1px solid #f1f5f9 !important;
}

.gr-input, input, select, textarea {
    background-color: #ffffff !important;
    border: 1.5px solid #e4e4e7 !important;
    border-radius: 10px !important;
    color: #09090b !important;
    font-size: 14px !important;
}

.gr-input:focus, input:focus, select:focus, textarea:focus {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.15) !important;
}

/* Gradio Tabs e Panels */
.tabs {
    border: none !important;
    margin-top: 10px !important;
}

.tab-nav {
    border-bottom: 2px solid #f1f5f9 !important;
    gap: 8px !important;
}

.tab-nav button {
    font-weight: 700 !important;
    font-size: 14px !important;
    padding: 12px 20px !important;
    border-radius: 8px 8px 0 0 !important;
    color: #64748b !important;
    transition: all 0.2s ease !important;
}

.tab-nav button.selected {
    color: #7c3aed !important;
    border-bottom: 2px solid #7c3aed !important;
    background-color: #f5f3ff !important;
}

/* Dataframe Styling */
table {
    border-collapse: separate !important;
    border-spacing: 0 !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1.5px solid #e4e4e7 !important;
}

th {
    background-color: #f8fafc !important;
    color: #09090b !important;
    font-weight: 800 !important;
    font-size: 13px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    border-bottom: 1.5px solid #e4e4e7 !important;
    padding: 12px 16px !important;
}

td {
    padding: 12px 16px !important;
    font-size: 13px !important;
    color: #334155 !important;
    border-bottom: 1px solid #f1f5f9 !important;
}

tr:hover td {
    background-color: #faf5ff !important;
}

/* ====================================================================== */
/* RESPONSIVIDADE COMPLETA & DESIGN ADAPTATIVO (MOBILE, TABLET & DESKTOP) */
/* ====================================================================== */

/* Default Mobile Top Bar & Drawer Controls (Hidden on Desktop) */
.sf-mobile-top-bar {
    display: none !important;
}

.sf-hamburger-btn {
    background: linear-gradient(135deg, #7c3aed 0%, #6366f1 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 8px 16px !important;
    font-size: 13.5px !important;
    font-weight: 700 !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 8px !important;
    cursor: pointer !important;
    box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3) !important;
    min-height: 42px !important;
}

.sf-hamburger-icon {
    font-size: 16px !important;
    line-height: 1 !important;
}

.sf-sidebar-close-btn {
    display: none !important;
    background: #f1f5f9 !important;
    border: 1px solid #e2e8f0 !important;
    color: #64748b !important;
    width: 36px !important;
    height: 36px !important;
    border-radius: 10px !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 16px !important;
    font-weight: 800 !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
}

.sf-sidebar-close-btn:hover {
    background: #fee2e2 !important;
    color: #ef4444 !important;
    border-color: #fca5a5 !important;
}

#sf-mobile-backdrop {
    display: none;
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    background: rgba(15, 23, 42, 0.65) !important;
    backdrop-filter: blur(4px) !important;
    -webkit-backdrop-filter: blur(4px) !important;
    z-index: 99998 !important;
    opacity: 0 !important;
    pointer-events: none !important;
    transition: opacity 0.25s ease !important;
}

#sf-mobile-backdrop.active {
    display: block !important;
    opacity: 1 !important;
    pointer-events: auto !important;
}

/* ====================================================================== */
/* RESPONSIVIDADE COMPLETA & DESIGN ADAPTATIVO (MOBILE, TABLET & DESKTOP) */
/* ====================================================================== */

/* Telas Médias, Tablets e Celulares (<= 1024px): Modo Off-Canvas Drawer */
@media screen and (max-width: 1024px) {
    .sf-mobile-top-bar {
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 16px !important;
        padding: 10px 14px !important;
        margin-bottom: 14px !important;
        box-shadow: 0 4px 14px -2px rgba(0, 0, 0, 0.05) !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }

    .sf-sidebar-close-btn {
        display: flex !important;
    }

    #sf-mobile-backdrop {
        display: block !important;
    }

    .app-workspace-container {
        padding: 6px 10px 30px 10px !important;
    }

    .growsync-workspace-layout,
    div.growsync-workspace-layout {
        display: block !important;
        width: 100% !important;
    }

    /* Sidebar se transforma em gaveta off-canvas deslizante */
    .growsync-sidebar,
    div.growsync-sidebar {
        position: fixed !important;
        top: 0 !important;
        left: -340px !important;
        width: min(310px, 86vw) !important;
        height: 100vh !important;
        max-height: 100vh !important;
        z-index: 99999 !important;
        background: #ffffff !important;
        box-shadow: 12px 0 40px rgba(15, 23, 42, 0.28) !important;
        overflow-y: auto !important;
        -webkit-overflow-scrolling: touch !important;
        visibility: hidden !important;
        transition: left 0.3s cubic-bezier(0.4, 0, 0.2, 1), visibility 0.3s !important;
        display: flex !important;
        flex-direction: column !important;
        padding: 20px 16px !important;
        border-radius: 0 20px 20px 0 !important;
        border-right: 1px solid #e2e8f0 !important;
        gap: 6px !important;
    }

    .growsync-sidebar.mobile-drawer-open,
    div.growsync-sidebar.mobile-drawer-open {
        left: 0 !important;
        visibility: visible !important;
    }

    .sidebar-brand-wrapper {
        width: 100% !important;
        padding-bottom: 12px !important;
        margin-bottom: 8px !important;
        border-bottom: 1px solid #f1f5f9 !important;
    }

    .sidebar-section-title {
        display: block !important;
        font-size: 10.5px !important;
        margin-top: 10px !important;
        margin-bottom: 4px !important;
    }

    .sidebar-promo-card {
        margin-top: 16px !important;
        display: block !important;
    }

    .sidebar-btn,
    button.sidebar-btn {
        width: 100% !important;
        flex: none !important;
        justify-content: flex-start !important;
        text-align: left !important;
        font-size: 13.5px !important;
        padding: 11px 14px !important;
        min-height: 44px !important;
        border-radius: 12px !important;
    }

    .growsync-main,
    div.growsync-main {
        width: 100% !important;
        min-width: 0 !important;
        max-width: 100% !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    /* Landing Page Showcase Mockup Responsivo */
    .mockup-inner-grid {
        flex-direction: column !important;
    }

    .mockup-mini-sidebar {
        display: none !important;
    }

    .mockup-main-showcase {
        width: 100% !important;
    }

    .mockup-split-row {
        grid-template-columns: 1fr !important;
    }

    /* Dashboard Split Row */
    .dashboard-split-row {
        grid-template-columns: 1fr !important;
        gap: 16px !important;
    }

    .dashboard-user-bar {
        flex-direction: column !important;
        align-items: stretch !important;
        gap: 12px !important;
    }

    .dashboard-kpi-grid {
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)) !important;
    }

    .board-header-bar {
        flex-direction: column !important;
        align-items: stretch !important;
        gap: 10px !important;
        padding: 12px 14px !important;
    }

    .board-view-buttons {
        width: 100% !important;
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch !important;
        flex-wrap: nowrap !important;
        padding-bottom: 4px !important;
    }

    .btn-view-pill,
    button.btn-view-pill {
        flex-shrink: 0 !important;
        white-space: nowrap !important;
        font-size: 12.5px !important;
        padding: 8px 16px !important;
        min-height: 42px !important;
    }

    /* Layouts de 2 colunas que devem empilhar em <= 1024px */
    .tasks-layout-row,
    div.tasks-layout-row,
    .pomodoro-layout-row,
    div.pomodoro-layout-row,
    .categories-layout-row,
    div.categories-layout-row {
        flex-direction: column !important;
        align-items: stretch !important;
        gap: 16px !important;
        width: 100% !important;
    }

    .tasks-form-card,
    .tasks-list-card,
    .pomodoro-main-col,
    .pomodoro-side-col,
    .categories-form-col,
    .categories-list-col {
        width: 100% !important;
        max-width: 100% !important;
        min-width: 0 !important;
    }
}

/* Kanban & Formulários Responsivos para Tablets e Celulares (<= 768px) */
@media screen and (max-width: 768px) {
    .kanban-board-wrapper {
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch !important;
        scroll-snap-type: x mandatory !important;
        padding-bottom: 20px !important;
    }
    .kanban-grid-row {
        min-width: unset !important;
        width: max-content !important;
        display: flex !important;
        flex-direction: row !important;
        gap: 12px !important;
    }
    .kanban-column-box {
        width: 82vw !important;
        min-width: 250px !important;
        max-width: 320px !important;
        flex: 0 0 82vw !important;
        scroll-snap-align: center !important;
    }

    /* Formulários em 1 coluna completa em telas móveis */
    .add-agenda-card .row,
    .add-agenda-card div[class*="row"],
    .tasks-form-card .row,
    .tasks-form-card div[class*="row"],
    .tasks-list-card .row,
    .tasks-list-card div[class*="row"] {
        flex-direction: column !important;
        align-items: stretch !important;
        gap: 10px !important;
        width: 100% !important;
    }

    .add-agenda-card .column,
    .add-agenda-card div[class*="column"],
    .add-agenda-card .form,
    .add-agenda-card div[class*="form"],
    .tasks-form-card div[class*="column"],
    .tasks-list-card div[class*="column"] {
        width: 100% !important;
        max-width: 100% !important;
        min-width: 0 !important;
        flex: 1 1 100% !important;
    }

    /* Toolbars e Botões de Ação do Kanban e Calendário */
    .cal-toolbar,
    div.cal-toolbar {
        flex-direction: column !important;
        align-items: stretch !important;
        gap: 10px !important;
    }

    .cal-toolbar > div {
        width: 100% !important;
        max-width: 100% !important;
    }

    .cal-toolbar .row,
    .cal-toolbar div[class*="row"] {
        flex-wrap: wrap !important;
        gap: 8px !important;
    }

    .kanban-quick-actions-row,
    div.kanban-quick-actions-row {
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 8px !important;
    }

    .kanban-quick-actions-row button {
        flex: 1 1 calc(50% - 6px) !important;
        min-width: 120px !important;
    }

    .tasks-actions-bar {
        flex-direction: column !important;
        align-items: stretch !important;
        gap: 8px !important;
    }

    .tasks-actions-bar > * {
        width: 100% !important;
        flex: 1 1 100% !important;
    }
}

/* Celulares e Telas Pequenas (<= 640px) */
@media screen and (max-width: 640px) {
    .app-workspace-container {
        padding: 4px 6px 20px 6px !important;
    }
    
    /* Navbar Mobile em Linha Única com Botões Reduzidos Somente no Celular */
    .navbar-black,
    div.navbar-black,
    .dark .navbar-black,
    .dark div.navbar-black {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: space-between !important;
        flex-wrap: nowrap !important;
        padding: 6px 10px !important;
        gap: 6px !important;
        min-height: 44px !important;
        width: 100% !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
        overflow: hidden !important;
    }
    .nav-col-logo,
    div.nav-col-logo,
    .navbar-black .nav-col-logo,
    .dark .navbar-black .nav-col-logo {
        display: flex !important;
        align-items: center !important;
        flex: 0 0 auto !important;
        width: auto !important;
        min-width: 0 !important;
        max-width: none !important;
        flex-grow: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    .sf-navbar-logo-wrap {
        display: flex !important;
        align-items: center !important;
        gap: 6px !important;
        padding: 0 !important;
        margin: 0 !important;
        flex-shrink: 0 !important;
    }
    .sf-navbar-logo-icon {
        width: 26px !important;
        height: 26px !important;
        min-width: 26px !important;
        border-radius: 7px !important;
        flex-shrink: 0 !important;
    }
    .sf-navbar-logo-icon svg {
        width: 15px !important;
        height: 15px !important;
    }
    .sf-navbar-logo-text {
        font-size: 14.5px !important;
        font-weight: 800 !important;
        letter-spacing: -0.3px !important;
        color: #ffffff !important;
        white-space: nowrap !important;
    }
    .sf-navbar-logo-dot {
        font-size: 15px !important;
        color: #a855f7 !important;
    }
    .nav-col-actions,
    div.nav-col-actions,
    .navbar-black .nav-col-actions,
    .dark .navbar-black .nav-col-actions {
        display: flex !important;
        align-items: center !important;
        justify-content: flex-end !important;
        flex: 0 0 auto !important;
        width: auto !important;
        min-width: 0 !important;
        max-width: none !important;
        flex-grow: 0 !important;
        margin-left: auto !important;
        padding: 0 !important;
    }
    .nav-actions-row,
    div.nav-actions-row,
    .navbar-black .nav-actions-row,
    .dark .navbar-black .nav-actions-row {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: flex-end !important;
        flex-wrap: nowrap !important;
        gap: 6px !important;
        width: auto !important;
        min-width: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    .navbar-black .nav-actions-row > div,
    .dark .navbar-black .nav-actions-row > div,
    .navbar-black div.btn-nav-login,
    .dark .navbar-black div.btn-nav-login,
    .navbar-black div.btn-nav-cadastrar,
    .dark .navbar-black div.btn-nav-cadastrar {
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
        width: auto !important;
        min-width: 0 !important;
        height: auto !important;
        min-height: 0 !important;
        display: inline-flex !important;
        align-items: center !important;
        flex: 0 0 auto !important;
    }
    .navbar-black button.btn-nav-login,
    .navbar-black .btn-nav-login button,
    .dark .navbar-black button.btn-nav-login,
    .dark .navbar-black .btn-nav-login button,
    .navbar-black .btn-nav-login,
    .dark .navbar-black .btn-nav-login,
    button.btn-nav-login,
    .btn-nav-login {
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: auto !important;
        min-width: 0 !important;
        max-width: fit-content !important;
        flex: 0 0 auto !important;
        flex-grow: 0 !important;
        flex-shrink: 0 !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        padding: 4px 10px !important;
        min-height: 28px !important;
        height: 28px !important;
        max-height: 28px !important;
        line-height: 1 !important;
        border-radius: 9999px !important;
        background: #18181b !important;
        background-color: #18181b !important;
        border: 1px solid #3f3f46 !important;
        color: #ffffff !important;
        box-shadow: none !important;
        white-space: nowrap !important;
        box-sizing: border-box !important;
        margin: 0 !important;
    }
    .navbar-black button.btn-nav-cadastrar,
    .navbar-black .btn-nav-cadastrar button,
    .dark .navbar-black button.btn-nav-cadastrar,
    .dark .navbar-black .btn-nav-cadastrar button,
    .navbar-black .btn-nav-cadastrar,
    .dark .navbar-black .btn-nav-cadastrar,
    button.btn-nav-cadastrar,
    .btn-nav-cadastrar {
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: auto !important;
        min-width: 0 !important;
        max-width: fit-content !important;
        flex: 0 0 auto !important;
        flex-grow: 0 !important;
        flex-shrink: 0 !important;
        font-size: 12px !important;
        font-weight: 800 !important;
        padding: 4px 12px !important;
        min-height: 28px !important;
        height: 28px !important;
        max-height: 28px !important;
        line-height: 1 !important;
        border-radius: 9999px !important;
        background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%) !important;
        background-color: #7c3aed !important;
        border: 1px solid #8b5cf6 !important;
        color: #ffffff !important;
        box-shadow: 0 2px 8px rgba(124, 58, 237, 0.45) !important;
        white-space: nowrap !important;
        box-sizing: border-box !important;
        margin: 0 !important;
    }

    /* Textos no Canto (Alinhamento à Esquerda) no Celular */
    .landing-hero-section {
        text-align: left !important;
        padding: clamp(24px, 5vw, 40px) 16px 20px 16px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: flex-start !important;
    }

    .hero-saas-badge {
        margin: 0 0 16px 0 !important;
        align-self: flex-start !important;
        text-align: left !important;
        max-width: 100% !important;
        padding: 6px 12px !important;
    }

    .hero-saas-badge span {
        font-size: 10.5px !important;
        text-align: left !important;
    }

    .hero-main-title {
        text-align: left !important;
        margin: 0 0 16px 0 !important;
        font-size: clamp(26px, 7.5vw, 40px) !important;
        letter-spacing: -1px !important;
        line-height: 1.18 !important;
    }

    .hero-subtitle {
        text-align: left !important;
        margin: 0 0 22px 0 !important;
        font-size: 14.5px !important;
        line-height: 1.55 !important;
    }

    .hero-feature-pills {
        justify-content: flex-start !important;
        align-items: flex-start !important;
        margin: 0 0 28px 0 !important;
        width: 100% !important;
        gap: 8px !important;
    }

    .hero-feature-pills > div {
        font-size: 11.5px !important;
        padding: 6px 12px !important;
    }

    .section-header-features,
    .section-header-methodology,
    .section-header-testimonials,
    .section-header-faq {
        text-align: left !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: flex-start !important;
    }

    .section-header-features h2,
    .section-header-methodology h2,
    .section-header-testimonials h2,
    .section-header-faq h2 {
        text-align: left !important;
        margin: 10px 0 8px 0 !important;
    }

    .section-header-features p,
    .section-header-methodology p,
    .section-header-testimonials p,
    .section-header-faq p {
        text-align: left !important;
        margin: 0 !important;
    }

    .section-header-features span,
    .section-header-methodology span,
    .section-header-testimonials span,
    .section-header-faq span {
        align-self: flex-start !important;
    }

    .sidebar-btn,
    button.sidebar-btn {
        width: 100% !important;
        flex: none !important;
        font-size: 13px !important;
        padding: 10px 12px !important;
        min-height: 44px !important;
        text-align: left !important;
        justify-content: flex-start !important;
    }
    .btn-side-dash::before,
    .btn-side-agenda::before,
    .btn-side-tarefas::before,
    .btn-side-disc::before,
    .btn-side-pomodoro::before,
    .btn-side-kanban::before,
    .btn-side-swagger::before,
    .btn-side-logout::before {
        width: 16px !important;
        height: 16px !important;
    }
    .calendar-grid-card {
        padding: 14px 10px !important;
        border-radius: 16px !important;
    }
    .cal-month-header {
        flex-direction: column !important;
        align-items: flex-start !important;
        gap: 10px !important;
    }
    .cal-weekday-grid {
        gap: 2px !important;
    }
    .cal-weekday-col {
        font-size: 9px !important;
        padding: 4px 1px !important;
        letter-spacing: 0 !important;
        text-transform: capitalize !important;
        border-radius: 6px !important;
    }
    .cal-days-grid {
        gap: 3px !important;
    }
    .cal-day-cell {
        min-height: 58px !important;
        padding: 4px 2px !important;
        border-radius: 8px !important;
    }
    .cal-day-num {
        font-size: 10.5px !important;
    }
    .cal-event-badge {
        font-size: 7.5px !important;
        padding: 1px 3px !important;
        border-radius: 4px !important;
        gap: 2px !important;
    }
    .btn-cal-add,
    .btn-cal-refresh {
        width: 100% !important;
        justify-content: center !important;
        font-size: 12px !important;
        padding: 8px 14px !important;
    }
    .add-agenda-card {
        padding: 16px 12px !important;
        border-radius: 16px !important;
    }
    #sf-timer-time {
        font-size: clamp(34px, 14vw, 54px) !important;
    }
    .pomodoro-system-container,
    .study-companion-container {
        padding: 16px 12px !important;
        border-radius: 16px !important;
    }
    .student-header-bar {
        padding: 12px 14px !important;
        flex-direction: column !important;
        align-items: flex-start !important;
        gap: 8px !important;
    }
}

/* Smartphones Compactos (320px a 430px) */
@media screen and (max-width: 430px) {
    .app-workspace-container {
        padding: 2px 4px 16px 4px !important;
    }
    .board-header-bar {
        padding: 10px 10px !important;
    }
    .board-title-text {
        font-size: 14.5px !important;
    }
    .btn-view-pill,
    button.btn-view-pill {
        font-size: 11.5px !important;
        padding: 6px 12px !important;
    }
    .navbar-black {
        padding: 8px 10px !important;
    }
    .tasks-form-card,
    .tasks-list-card,
    .add-agenda-card,
    .calendar-grid-card {
        padding: 12px 10px !important;
        border-radius: 14px !important;
    }
    .kanban-quick-actions-row button {
        flex: 1 1 100% !important;
        width: 100% !important;
    }
    .cal-weekday-col {
        font-size: 8px !important;
    }
    .cal-day-cell {
        min-height: 52px !important;
        padding: 2px 1px !important;
    }
    .cal-day-num {
        font-size: 9.5px !important;
    }
    .cal-event-badge {
        font-size: 6.8px !important;
        padding: 1px 2px !important;
    }
    #sf-timer-time {
        font-size: clamp(30px, 13vw, 44px) !important;
    }
}

/* Responsividade de Tabelas e Containers em Geral */
.gradio-dataframe,
table,
.table-wrap,
div[class*="dataframe"] {
    width: 100% !important;
    max-width: 100% !important;
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch !important;
    display: block !important;
}

img, svg {
    max-width: 100% !important;
    height: auto;
}

.gr-row,
div[class*="row"] {
    flex-wrap: wrap !important;
}

/* Layout & Design Moderno para Minhas Tarefas */
.tasks-layout-row {
    display: flex !important;
    gap: 20px !important;
    width: 100% !important;
    align-items: stretch !important;
}

.tasks-form-card {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 20px !important;
    padding: 22px 20px !important;
    box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.04) !important;
    box-sizing: border-box !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 8px !important;
}

.tasks-list-card {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 20px !important;
    padding: 22px 20px !important;
    box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.04) !important;
    box-sizing: border-box !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 12px !important;
}

.tasks-card-header {
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    padding-bottom: 12px !important;
    margin-bottom: 8px !important;
    border-bottom: 1px solid #f1f5f9 !important;
}

.tasks-card-header h4 {
    margin: 0 !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    color: #1e1b4b !important;
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
}

#tabela_atividades_grid {
    border-radius: 14px !important;
    border: 1px solid #e2e8f0 !important;
    overflow: hidden !important;
    background: #ffffff !important;
}

#tabela_atividades_grid table {
    width: 100% !important;
    border-collapse: separate !important;
    border-spacing: 0 !important;
}

#tabela_atividades_grid tbody tr {
    transition: background-color 0.15s ease, transform 0.15s ease !important;
    cursor: pointer !important;
}

#tabela_atividades_grid tbody tr:hover {
    background-color: rgba(124, 58, 237, 0.06) !important;
}

.btn-salvar-atv-custom {
    background: linear-gradient(135deg, #7c3aed 0%, #6366f1 100%) !important;
    color: #ffffff !important;
    border: none !important;
    font-weight: 700 !important;
    padding: 12px 18px !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 14px rgba(124, 58, 237, 0.25) !important;
    transition: all 0.2s ease !important;
}

.btn-salvar-atv-custom:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 18px rgba(124, 58, 237, 0.35) !important;
}

.tasks-actions-bar {
    background: #f8fafc !important;
    padding: 12px 14px !important;
    border-radius: 14px !important;
    border: 1px solid #e2e8f0 !important;
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    flex-wrap: wrap !important;
}

@media (max-width: 1024px) {
    .tasks-layout-row {
        flex-direction: column !important;
    }
    .tasks-form-card,
    .tasks-list-card {
        width: 100% !important;
        max-width: 100% !important;
        min-width: 0 !important;
    }
}

@media (max-width: 640px) {
    .tasks-page-header {
        padding: 14px 14px !important;
    }
    .tasks-actions-bar {
        flex-direction: column !important;
        align-items: stretch !important;
    }
    .tasks-actions-bar > * {
        width: 100% !important;
    }
}
"""

def gerar_navbar_logo_html():
    """Logo vetorial exclusivo StudyFlow com símbolo geométrico moderno."""
    return f"""
    <div class="sf-navbar-logo-wrap" style="display: flex; align-items: center; gap: 12px; font-family: 'Plus Jakarta Sans', sans-serif; background: transparent !important; padding: 2px 0;">
        <div class="sf-navbar-logo-icon" style="background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%); color: white; width: 42px; height: 42px; border-radius: 12px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 16px rgba(124, 58, 237, 0.45); border: 1px solid rgba(255, 255, 255, 0.2); flex-shrink: 0;">
            {icon("logo_cap", 24, "#ffffff", 2.2)}
        </div>
        <div style="display: flex; align-items: baseline;">
            <span class="sf-navbar-logo-text" style="font-size: 24px; font-weight: 900; letter-spacing: -0.8px; color: #ffffff !important;">StudyFlow</span>
            <span class="sf-navbar-logo-dot" style="color: #a855f7 !important; font-size: 26px; font-weight: 900; line-height: 0; margin-left: 2px;">.</span>
        </div>
    </div>
    """


def gerar_auth_left_banner_html():
    return f"""
    <div style="height: 100%; display: flex; flex-direction: column; justify-content: space-between; font-family: 'Plus Jakarta Sans', sans-serif;">
        <!-- Top Branding -->
        <div>
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 28px;">
                <div style="background: rgba(255, 255, 255, 0.15); backdrop-filter: blur(8px); border: 1px solid rgba(255, 255, 255, 0.25); width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);">
                    {icon("logo_cap", 24, "#ffffff")}
                </div>
                <div>
                    <div style="color: #ffffff; font-size: 22px; font-weight: 900; letter-spacing: -0.6px; line-height: 1.1;">StudyFlow<span style="color: #c4b5fd;">.</span></div>
                    <div style="color: #c4b5fd; font-size: 10px; font-weight: 800; letter-spacing: 0.8px; text-transform: uppercase;">Workspace PRO</div>
                </div>
            </div>

            <!-- Headline -->
            <div style="background: rgba(255, 255, 255, 0.12); border: 1px solid rgba(255, 255, 255, 0.25); padding: 5px 14px; border-radius: 9999px; display: inline-flex; align-items: center; gap: 8px; color: #f5f3ff; font-size: 11.5px; font-weight: 700; margin-bottom: 16px;">
                {icon("sparkles", 14, "#c4b5fd")} Gestão Acadêmica Inteligente
            </div>
            
            <h1 style="color: #ffffff; font-size: 26px; font-weight: 900; line-height: 1.25; margin: 0 0 12px 0; letter-spacing: -0.8px;">
                Sua rotina universitária em <span style="background: linear-gradient(135deg, #f5f3ff 0%, #c4b5fd 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">ordem absoluta</span>.
            </h1>
            
            <p style="color: #e9d5ff; font-size: 13.5px; line-height: 1.6; margin: 0 0 28px 0; font-weight: 500;">
                Planeje matérias, acompanhe prazos com algoritmo inteligente de prioridades e alcance alta performance.
            </p>

            <!-- Mockup do Dashboard Flutuante -->
            <div style="background: rgba(255, 255, 255, 0.08); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 18px; padding: 18px; box-shadow: 0 16px 40px rgba(0, 0, 0, 0.25);">
                <div style="display: flex; align-items: center; justify-content: space-between; padding-bottom: 12px; border-bottom: 1px solid rgba(255, 255, 255, 0.12); margin-bottom: 12px;">
                    <div style="display: flex; gap: 6px;">
                        <span style="width: 10px; height: 10px; border-radius: 5px; background: #ef4444; display: inline-block;"></span>
                        <span style="width: 10px; height: 10px; border-radius: 5px; background: #f59e0b; display: inline-block;"></span>
                        <span style="width: 10px; height: 10px; border-radius: 5px; background: #10b981; display: inline-block;"></span>
                    </div>
                    <span style="color: #ffffff; font-size: 11px; font-weight: 700; letter-spacing: 0.3px;">PAINEL AO VIVO</span>
                    <span style="background: rgba(16, 185, 129, 0.2); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.4); font-size: 10px; font-weight: 800; padding: 2px 8px; border-radius: 9999px;">Sincronizado</span>
                </div>

                <!-- Tarefa 1 -->
                <div style="background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 12px; padding: 10px 12px; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <div style="background: #10b981; width: 22px; height: 22px; border-radius: 6px; display: flex; align-items: center; justify-content: center;">
                            {icon("check", 13, "#ffffff")}
                        </div>
                        <div>
                            <div style="color: #ffffff; font-size: 12px; font-weight: 700;">Artigo de Redes & IA</div>
                            <div style="color: #ddd6fe; font-size: 10px;">Engenharia de Software · Prof. Carlos</div>
                        </div>
                    </div>
                    <span style="background: rgba(239, 68, 68, 0.25); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.4); font-size: 9.5px; font-weight: 800; padding: 3px 8px; border-radius: 6px;">Alta · Score 92</span>
                </div>

                <!-- Tarefa 2 -->
                <div style="background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 12px; padding: 10px 12px; display: flex; align-items: center; justify-content: space-between;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <div style="background: rgba(255, 255, 255, 0.2); width: 22px; height: 22px; border-radius: 6px; display: flex; align-items: center; justify-content: center;">
                            {icon("clock", 13, "#ffffff")}
                        </div>
                        <div>
                            <div style="color: #ffffff; font-size: 12px; font-weight: 700;">Seminário de Banco de Dados</div>
                            <div style="color: #ddd6fe; font-size: 10px;">Modelagem Relacional · Prova N4</div>
                        </div>
                    </div>
                    <span style="background: rgba(245, 158, 11, 0.25); color: #fde68a; border: 1px solid rgba(245, 158, 11, 0.4); font-size: 9.5px; font-weight: 800; padding: 3px 8px; border-radius: 6px;">Vence Hoje</span>
                </div>

                <!-- Métricas mini -->
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-top: 14px; padding-top: 12px; border-top: 1px solid rgba(255, 255, 255, 0.12);">
                    <div style="text-align: center;">
                        <div style="color: #ffffff; font-size: 15px; font-weight: 900;">94.8%</div>
                        <div style="color: #c4b5fd; font-size: 9.5px; font-weight: 700;">Aproveitamento</div>
                    </div>
                    <div style="text-align: center; border-left: 1px solid rgba(255, 255, 255, 0.12); border-right: 1px solid rgba(255, 255, 255, 0.12);">
                        <div style="color: #ffffff; font-size: 15px; font-weight: 900;">14 Dias</div>
                        <div style="color: #c4b5fd; font-size: 9.5px; font-weight: 700;">Foco Diário</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="color: #ffffff; font-size: 15px; font-weight: 900;">0</div>
                        <div style="color: #c4b5fd; font-size: 9.5px; font-weight: 700;">Atrasadas</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Bottom Testimonial / Security Badge -->
        <div style="display: flex; align-items: center; gap: 10px; margin-top: 24px; padding-top: 16px; border-top: 1px solid rgba(255, 255, 255, 0.15); color: #e9d5ff; font-size: 11.5px; font-weight: 600;">
            <div style="background: rgba(255, 255, 255, 0.15); width: 28px; height: 28px; border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                {icon("shield_check", 16, "#c4b5fd")}
            </div>
            <span>Seus dados acadêmicos salvos e sincronizados com foco e privacidade.</span>
        </div>
    </div>
    """


def gerar_auth_card_header_html():
    return f"""
    <div style="margin: 4px 0 20px 0; font-family: 'Plus Jakarta Sans', sans-serif;">
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%); width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; box-shadow: 0 6px 18px rgba(124, 58, 237, 0.35); flex-shrink: 0;">
                {icon("logo_cap", 24, "#ffffff")}
            </div>
            <div>
                <h2 style="font-size: 22px; font-weight: 900; color: #09090b; margin: 0; letter-spacing: -0.5px;">Acesse o StudyFlow</h2>
                <p style="color: #64748b; font-size: 12.5px; margin: 2px 0 0 0; font-weight: 500;">Entre com seu e-mail acadêmico ou crie sua conta gratuitamente</p>
            </div>
        </div>
    </div>
    """


def gerar_hero_e_recursos_html():
    """Página Inicial completa estilo SaaS Premium com Mockup interativo, 6 Funcionalidades, Roadmap e Depoimentos."""
    return f"""
    <div class="landing-page-root" style="font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, sans-serif; background: #ffffff; color: #09090b; width: 100%; box-sizing: border-box; overflow-x: hidden;">
        
        <!-- HERO SECTION -->
        <section class="landing-hero-section" style="position: relative; text-align: center; padding: clamp(35px, 6vw, 70px) clamp(16px, 4vw, 24px) clamp(30px, 5vw, 50px) clamp(16px, 4vw, 24px); background: radial-gradient(circle at 50% -10%, rgba(124, 58, 237, 0.12) 0%, rgba(255, 255, 255, 0) 70%); box-sizing: border-box;">
            
            <!-- SaaS Badge Alto Contraste -->
            <div class="hero-saas-badge" style="display: inline-flex; align-items: center; gap: 8px; background: #f5f3ff; border: 1.5px solid #c4b5fd; padding: 8px clamp(14px, 3vw, 24px); border-radius: 9999px; margin-bottom: 24px; box-shadow: 0 4px 14px rgba(124, 58, 237, 0.12); max-width: 90%;">
                {icon("sparkles", 16, "#7c3aed")}
                <span style="color: #5b21b6 !important; font-weight: 900 !important; font-size: clamp(10.5px, 2.5vw, 13px) !important; letter-spacing: 0.5px !important;">PLATAFORMA SAAS DE GESTÃO ACADÊMICA & ALTO RENDIMENTO</span>
            </div>

            <!-- Main Heading -->
            <h1 class="hero-main-title" style="font-size: clamp(28px, 6.5vw, 56px); font-weight: 900; letter-spacing: -1.5px; color: #09090b; margin: 0 auto 20px auto; line-height: 1.15; max-width: 980px;">
                Organize sua rotina acadêmica <br />
                com <span style="background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">método, foco e inteligência.</span>
            </h1>

            <!-- Subtitle -->
            <p class="hero-subtitle" style="font-size: clamp(14.5px, 3vw, 19px); color: #64748b; max-width: 820px; margin: 0 auto 32px auto; line-height: 1.6; font-weight: 500;">
                O ecossistema definitivo para universitários: centralize disciplinas, antecipe entregas com nosso 
                <strong style="color: #7c3aed;">algoritmo preditivo de prioridade</strong>, acompanhe métricas reais de produtividade e alcance o estado de fluxo com o 
                <strong style="color: #09090b;">Pomodoro Focus Hub</strong>.
            </p>

            <!-- Feature Pills -->
            <div class="hero-feature-pills" style="display: flex; justify-content: center; flex-wrap: wrap; gap: 10px; margin-bottom: clamp(30px, 5vw, 50px);">
                <div style="display: inline-flex; align-items: center; gap: 6px; background: #f8fafc; border: 1px solid #e2e8f0; padding: 6px 14px; border-radius: 9999px; font-size: 12.5px; font-weight: 600; color: #475569;">
                    {icon("zap", 14, "#7c3aed")} Prioridade Dinâmica
                </div>
                <div style="display: inline-flex; align-items: center; gap: 6px; background: #f8fafc; border: 1px solid #e2e8f0; padding: 6px 14px; border-radius: 9999px; font-size: 12.5px; font-weight: 600; color: #475569;">
                    {icon("timer", 14, "#7c3aed")} Focus Pomodoro 25m
                </div>
                <div style="display: inline-flex; align-items: center; gap: 6px; background: #f8fafc; border: 1px solid #e2e8f0; padding: 6px 14px; border-radius: 9999px; font-size: 12.5px; font-weight: 600; color: #475569;">
                    {icon("shield_check", 14, "#7c3aed")} API REST Swagger 100%
                </div>
                <div style="display: inline-flex; align-items: center; gap: 6px; background: #f8fafc; border: 1px solid #e2e8f0; padding: 6px 14px; border-radius: 9999px; font-size: 12.5px; font-weight: 600; color: #475569;">
                    {icon("check_circle", 14, "#10b981")} 100% Gratuito
                </div>
            </div>

            <!-- COMPOSIÇÃO VISUAL / MOCKUP DO DASHBOARD SAAS -->
            <div class="mockup-frame-box" style="max-width: 1100px; margin: 0 auto; background: #ffffff; border-radius: 20px; border: 1.5px solid #e4e4e7; box-shadow: 0 20px 50px -15px rgba(124, 58, 237, 0.2); overflow: hidden; text-align: left;">
                
                <!-- Window Header Frame -->
                <div style="background: #09090b; padding: 12px 18px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #27272a; flex-wrap: wrap; gap: 8px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <div style="width: 10px; height: 10px; border-radius: 50%; background: #ef4444;"></div>
                        <div style="width: 10px; height: 10px; border-radius: 50%; background: #f59e0b;"></div>
                        <div style="width: 10px; height: 10px; border-radius: 50%; background: #10b981;"></div>
                        <span style="margin-left: 10px; font-size: 11px; color: #71717a; font-weight: 600;">studyflow.edu/workspace/student-dashboard</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="width: 7px; height: 7px; border-radius: 50%; background: #10b981; display: inline-block;"></span>
                        <span style="font-size: 10.5px; color: #a1a1aa; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">API REST Operacional</span>
                    </div>
                </div>

                <!-- Inner Dashboard Preview -->
                <div class="mockup-inner-grid" style="background: #f8fafc; padding: clamp(14px, 3vw, 28px); display: flex; flex-direction: row; gap: 20px;">
                    
                    <!-- Mini Sidebar (Desktop only) -->
                    <div class="mockup-mini-sidebar" style="background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 18px; padding: 18px; display: flex; flex-direction: column; justify-content: space-between; width: 210px; flex-shrink: 0; box-sizing: border-box;">
                        <div>
                            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
                                <div style="background: #7c3aed; color: white; width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center;">
                                    {icon("logo_cap", 18, "#ffffff")}
                                </div>
                                <span style="font-weight: 800; font-size: 15px; color: #09090b;">STDNT.</span>
                            </div>

                            <div style="display: flex; flex-direction: column; gap: 6px;">
                                <div style="display: flex; align-items: center; gap: 10px; background: #f5f3ff; color: #7c3aed; padding: 8px 12px; border-radius: 10px; font-weight: 700; font-size: 12.5px;">
                                    {icon("layers", 15, "#7c3aed")} Dashboard
                                </div>
                                <div style="display: flex; align-items: center; gap: 10px; color: #64748b; padding: 8px 12px; border-radius: 10px; font-weight: 600; font-size: 12.5px;">
                                    {icon("calendar", 15, "#64748b")} Cronograma
                                </div>
                                <div style="display: flex; align-items: center; gap: 10px; color: #64748b; padding: 8px 12px; border-radius: 10px; font-weight: 600; font-size: 12.5px;">
                                    {icon("check_circle", 15, "#64748b")} Minhas Tarefas
                                </div>
                                <div style="display: flex; align-items: center; gap: 10px; color: #64748b; padding: 8px 12px; border-radius: 10px; font-weight: 600; font-size: 12.5px;">
                                    {icon("book_open", 15, "#64748b")} Disciplinas
                                </div>
                            </div>
                        </div>

                        <div style="border-top: 1px solid #f1f5f9; padding-top: 14px; display: flex; align-items: center; gap: 10px;">
                            <div style="width: 32px; height: 32px; border-radius: 50%; background: #09090b; color: white; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 12px;">
                                MT
                            </div>
                            <div>
                                <div style="font-weight: 800; font-size: 12px; color: #09090b;">Aluno Demo</div>
                                <div style="font-size: 10.5px; color: #94a3b8;">Ciência da Computação</div>
                            </div>
                        </div>
                    </div>

                    <!-- Main Showcase Content -->
                    <div class="mockup-main-showcase" style="display: flex; flex-direction: column; gap: 16px; flex: 1 1 0; min-width: 0;">
                        
                        <!-- Top KPI Row -->
                        <div class="mockup-kpi-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(min(130px, 100%), 1fr)); gap: 12px;">
                            <div style="background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 14px; padding: 14px;">
                                <div style="font-size: 11.5px; color: #64748b; font-weight: 600;">Rendimento Geral</div>
                                <div style="font-size: 22px; font-weight: 900; color: #09090b; margin-top: 2px;">4.85</div>
                                <div style="font-size: 10.5px; color: #10b981; font-weight: 700; margin-top: 2px;">↑ Top 5% da turma</div>
                            </div>
                            <div style="background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 14px; padding: 14px;">
                                <div style="font-size: 11.5px; color: #64748b; font-weight: 600;">Streak de Estudo</div>
                                <div style="font-size: 22px; font-weight: 900; color: #09090b; margin-top: 2px;">14 dias</div>
                                <div style="font-size: 10.5px; color: #f59e0b; font-weight: 700; margin-top: 2px;">★ Consistência</div>
                            </div>
                            <div style="background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 14px; padding: 14px;">
                                <div style="font-size: 11.5px; color: #64748b; font-weight: 600;">Entregas Restantes</div>
                                <div style="font-size: 22px; font-weight: 900; color: #7c3aed; margin-top: 2px;">12</div>
                                <div style="font-size: 10.5px; color: #ef4444; font-weight: 700; margin-top: 2px;">3 esta semana</div>
                            </div>
                            <div style="background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 14px; padding: 14px;">
                                <div style="font-size: 11.5px; color: #64748b; font-weight: 600;">Taxa de Conclusão</div>
                                <div style="font-size: 22px; font-weight: 900; color: #09090b; margin-top: 2px;">86%</div>
                                <div style="font-size: 10.5px; color: #64748b; font-weight: 600; margin-top: 2px;">Meta em dia</div>
                            </div>
                        </div>

                        <!-- Split Cards: Tarefas Prioritárias + Pomodoro Timer -->
                        <div class="mockup-split-row" style="display: grid; grid-template-columns: 1.4fr 1fr; gap: 16px;">
                            
                            <!-- Tarefas Prioritárias -->
                            <div style="background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 16px; padding: 18px;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                                    <span style="font-weight: 800; font-size: 14px; color: #09090b;">Entregas Prioritárias</span>
                                    <span style="font-size: 11.5px; font-weight: 700; color: #7c3aed;">Algorítmica</span>
                                </div>
                                <div style="display: flex; flex-direction: column; gap: 8px;">
                                    <div style="border: 1px solid #fee2e2; background: #fff5f5; border-left: 4px solid #ef4444; border-radius: 10px; padding: 10px 12px; display: flex; justify-content: space-between; align-items: center;">
                                        <div>
                                            <div style="font-weight: 800; font-size: 12.5px; color: #09090b;">Cálculo III: Lista 4</div>
                                            <div style="font-size: 11px; color: #64748b; margin-top: 1px;">Matemática Superior</div>
                                        </div>
                                        <span style="background: #ef4444; color: white; padding: 3px 8px; border-radius: 20px; font-size: 10px; font-weight: 800;">Hoje</span>
                                    </div>

                                    <div style="border: 1px solid #fef3c7; background: #fffbeb; border-left: 4px solid #f59e0b; border-radius: 10px; padding: 10px 12px; display: flex; justify-content: space-between; align-items: center;">
                                        <div>
                                            <div style="font-weight: 800; font-size: 12.5px; color: #09090b;">Machine Learning: TCC</div>
                                            <div style="font-size: 11px; color: #64748b; margin-top: 1px;">Inteligência Artificial</div>
                                        </div>
                                        <span style="background: #f59e0b; color: white; padding: 3px 8px; border-radius: 20px; font-size: 10px; font-weight: 800;">Em 2d</span>
                                    </div>
                                </div>
                            </div>

                            <!-- Floating Pomodoro Box -->
                            <div style="background: #09090b; border: 1.5px solid #27272a; border-radius: 16px; padding: 18px; color: white; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 10px 25px rgba(0,0,0,0.25);">
                                <div>
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <span style="font-size: 10px; text-transform: uppercase; letter-spacing: 1.2px; color: #a855f7; font-weight: 800;">Focus Session</span>
                                        <span style="background: rgba(124, 58, 237, 0.25); color: #c4b5fd; padding: 2px 7px; border-radius: 6px; font-size: 10px; font-weight: 700;">Pomodoro</span>
                                    </div>
                                    <div style="text-align: center; margin: 12px 0;">
                                        <div style="font-size: 38px; font-weight: 900; font-family: monospace; letter-spacing: 2px; color: #ffffff;">25:00</div>
                                        <div style="font-size: 11px; color: #a1a1aa; margin-top: 2px;">Imersão total</div>
                                    </div>
                                </div>
                                <div style="display: flex; gap: 6px;">
                                    <div style="flex: 1; background: #7c3aed; color: white; text-align: center; padding: 8px; border-radius: 8px; font-weight: 800; font-size: 11.5px;">Iniciar Foco</div>
                                    <div style="flex: 1; background: #18181b; color: #e4e4e7; text-align: center; padding: 8px; border-radius: 8px; font-weight: 800; font-size: 11.5px; border: 1px solid #3f3f46;">Pausa 5m</div>
                                </div>
                            </div>

                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- SEÇÃO DE FUNCIONALIDADES (6 CARDS SAAS ELABORADOS) -->
        <section id="features" class="landing-section" style="padding: clamp(35px, 6vw, 70px) clamp(16px, 4vw, 40px); max-width: 1200px; margin: 0 auto; box-sizing: border-box;">
            
            <div class="section-header-features" style="text-align: center; margin-bottom: clamp(30px, 5vw, 50px);">
                <span style="background: #f5f3ff; color: #7c3aed; font-size: 11.5px; font-weight: 800; padding: 6px 16px; border-radius: 20px; text-transform: uppercase; letter-spacing: 1px; border: 1px solid #ddd6fe;">
                    FUNCIONALIDADES PREMIUM
                </span>
                <h2 style="font-size: clamp(24px, 5vw, 38px); font-weight: 900; color: #09090b; margin: 14px 0 10px 0; letter-spacing: -0.8px;">
                    Projetado para impulsionar suas notas e rendimento
                </h2>
                <p style="color: #64748b; font-size: clamp(14px, 2.5vw, 17px); margin: 0 auto; max-width: 700px; line-height: 1.6;">
                    Ferramentas avançadas que transformam o caos do semestre em clareza, rotina produtiva e resultados concretos.
                </p>
            </div>

            <!-- Grid de 6 Funcionalidades -->
            <div class="features-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(min(270px, 100%), 1fr)); gap: 20px;">
                
                <!-- Card 1: Planner de Disciplinas -->
                <div style="background: #ffffff; border: 1.5px solid #e4e4e7; border-radius: 18px; padding: clamp(20px, 4vw, 28px); box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03); transition: all 0.3s ease; border-top: 4px solid #7c3aed;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                        <div style="background: #f5f3ff; color: #7c3aed; width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center;">
                            {icon("book_open", 22, "#7c3aed")}
                        </div>
                        <span style="background: #f1f5f9; color: #475569; font-size: 10.5px; font-weight: 800; padding: 3px 8px; border-radius: 6px; letter-spacing: 0.5px;">CURRÍCULO</span>
                    </div>
                    <h3 style="font-size: 18px; font-weight: 800; margin: 0 0 8px 0; color: #09090b;">Planner de Disciplinas</h3>
                    <p style="font-size: 13.5px; color: #64748b; line-height: 1.6; margin-bottom: 16px;">
                        Cadastre todas as matérias do semestre, organize ementas, vincule professores responsáveis e mantenha seu currículo 100% centralizado.
                    </p>
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 8px 12px; font-size: 12px; font-weight: 600; color: #334155; display: flex; align-items: center; gap: 8px;">
                        {icon("check", 14, "#10b981")} Vínculo automático de tarefas por disciplina
                    </div>
                </div>

                <!-- Card 2: Acompanhamento de Tarefas -->
                <div style="background: #ffffff; border: 1.5px solid #e4e4e7; border-radius: 18px; padding: clamp(20px, 4vw, 28px); box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03); transition: all 0.3s ease; border-top: 4px solid #09090b;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                        <div style="background: #f4f4f5; color: #09090b; width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center;">
                            {icon("check_circle", 22, "#09090b")}
                        </div>
                        <span style="background: #f1f5f9; color: #475569; font-size: 10.5px; font-weight: 800; padding: 3px 8px; border-radius: 6px; letter-spacing: 0.5px;">WORKFLOW</span>
                    </div>
                    <h3 style="font-size: 18px; font-weight: 800; margin: 0 0 8px 0; color: #09090b;">Acompanhamento de Tarefas</h3>
                    <p style="font-size: 13.5px; color: #64748b; line-height: 1.6; margin-bottom: 16px;">
                        CRUD completo de trabalhos, relatórios e projetos. Alterne o status de conclusão em 1 clique e filtre por prioridade ou entrega.
                    </p>
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 8px 12px; font-size: 12px; font-weight: 600; color: #334155; display: flex; align-items: center; gap: 8px;">
                        {icon("check", 14, "#10b981")} Alternância rápida pendente ↔ concluída
                    </div>
                </div>

                <!-- Card 3: Prioridade Inteligente -->
                <div style="background: #ffffff; border: 1.5px solid #e4e4e7; border-radius: 18px; padding: clamp(20px, 4vw, 28px); box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03); transition: all 0.3s ease; border-top: 4px solid #7c3aed;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                        <div style="background: #f5f3ff; color: #7c3aed; width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center;">
                            {icon("zap", 22, "#7c3aed")}
                        </div>
                        <span style="background: #f1f5f9; color: #475569; font-size: 10.5px; font-weight: 800; padding: 3px 8px; border-radius: 6px; letter-spacing: 0.5px;">ALGORITMO</span>
                    </div>
                    <h3 style="font-size: 18px; font-weight: 800; margin: 0 0 8px 0; color: #09090b;">Prioridade Inteligente</h3>
                    <p style="font-size: 13.5px; color: #64748b; line-height: 1.6; margin-bottom: 16px;">
                        Algoritmo dinâmico que pondera dias restantes até a entrega com a criticidade da tarefa, colocando no topo o que você realmente precisa fazer hoje.
                    </p>
                    <div style="background: #f5f3ff; border: 1px solid #ddd6fe; border-radius: 10px; padding: 8px 12px; font-size: 12px; font-weight: 700; color: #6d28d9; display: flex; align-items: center; gap: 8px;">
                        {icon("clock", 14, "#7c3aed")} Alerta dinâmico: atrasadas e próximas no topo
                    </div>
                </div>

                <!-- Card 4: Métricas & Produtividade -->
                <div style="background: #ffffff; border: 1.5px solid #e4e4e7; border-radius: 18px; padding: clamp(20px, 4vw, 28px); box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03); transition: all 0.3s ease; border-top: 4px solid #09090b;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                        <div style="background: #f4f4f5; color: #09090b; width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center;">
                            {icon("trending_up", 22, "#09090b")}
                        </div>
                        <span style="background: #f1f5f9; color: #475569; font-size: 10.5px; font-weight: 800; padding: 3px 8px; border-radius: 6px; letter-spacing: 0.5px;">ANALYTICS</span>
                    </div>
                    <h3 style="font-size: 18px; font-weight: 800; margin: 0 0 8px 0; color: #09090b;">Métricas & Produtividade</h3>
                    <p style="font-size: 13.5px; color: #64748b; line-height: 1.6; margin-bottom: 16px;">
                        Acompanhe a taxa de conclusão percentual das tarefas, a distribuição de esforço por disciplina e o ritmo semanal de entregas.
                    </p>
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 8px 12px; font-size: 12px; font-weight: 600; color: #334155; display: flex; align-items: center; gap: 8px;">
                        {icon("check", 14, "#10b981")} Taxa de conclusão calculada via API Flask
                    </div>
                </div>

                <!-- Card 5: Pomodoro Focus Hub -->
                <div style="background: #ffffff; border: 1.5px solid #e4e4e7; border-radius: 18px; padding: clamp(20px, 4vw, 28px); box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03); transition: all 0.3s ease; border-top: 4px solid #7c3aed;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                        <div style="background: #f5f3ff; color: #7c3aed; width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center;">
                            {icon("timer", 22, "#7c3aed")}
                        </div>
                        <span style="background: #f1f5f9; color: #475569; font-size: 10.5px; font-weight: 800; padding: 3px 8px; border-radius: 6px; letter-spacing: 0.5px;">DEEP WORK</span>
                    </div>
                    <h3 style="font-size: 18px; font-weight: 800; margin: 0 0 8px 0; color: #09090b;">Pomodoro Focus Timer</h3>
                    <p style="font-size: 13.5px; color: #64748b; line-height: 1.6; margin-bottom: 16px;">
                        Sessões calibradas de foco profundo de 25 minutos com intervalos programados (pausa curta de 5m ou longa de 15m) para retenção máxima de estudo.
                    </p>
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 8px 12px; font-size: 12px; font-weight: 600; color: #334155; display: flex; align-items: center; gap: 8px;">
                        {icon("check", 14, "#10b981")} Modos de foco e pausas com 1 clique
                    </div>
                </div>

                <!-- Card 6: Planejamento Acadêmico -->
                <div style="background: #ffffff; border: 1.5px solid #e4e4e7; border-radius: 18px; padding: clamp(20px, 4vw, 28px); box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03); transition: all 0.3s ease; border-top: 4px solid #09090b;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                        <div style="background: #f4f4f5; color: #09090b; width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center;">
                            {icon("calendar", 22, "#09090b")}
                        </div>
                        <span style="background: #f1f5f9; color: #475569; font-size: 10.5px; font-weight: 800; padding: 3px 8px; border-radius: 6px; letter-spacing: 0.5px;">CRONOGRAMA</span>
                    </div>
                    <h3 style="font-size: 18px; font-weight: 800; margin: 0 0 8px 0; color: #09090b;">Planejamento Acadêmico</h3>
                    <p style="font-size: 13.5px; color: #64748b; line-height: 1.6; margin-bottom: 16px;">
                        Cronograma temporal que organiza seus trabalhos entre atrasados, entregas de hoje, próximos 7 dias e compromissos futuros.
                    </p>
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 8px 12px; font-size: 12px; font-weight: 600; color: #334155; display: flex; align-items: center; gap: 8px;">
                        {icon("check", 14, "#10b981")} Visualização em seções cronológicas
                    </div>
                </div>

            </div>
        </section>

        <!-- SEÇÃO PLANEJAMENTO ACADÊMICO EM 4 ETAPAS (ROADMAP CONECTADO) -->
        <section id="methodology" class="landing-section" style="margin: 0 clamp(12px, 3vw, 40px) clamp(35px, 6vw, 70px) clamp(12px, 3vw, 40px); background: #fafafa; border: 1.5px solid #e4e4e7; border-radius: 24px; padding: clamp(28px, 5vw, 60px) clamp(16px, 4vw, 40px); box-sizing: border-box;">
            <div class="section-header-methodology" style="text-align: center; margin-bottom: clamp(30px, 5vw, 50px);">
                <span style="background: #f5f3ff; color: #7c3aed; font-size: 11.5px; font-weight: 800; padding: 6px 16px; border-radius: 20px; text-transform: uppercase; letter-spacing: 1px; border: 1px solid #ddd6fe;">
                    METODOLOGIA COMPROVADA
                </span>
                <h2 style="font-size: clamp(22px, 4.5vw, 36px); font-weight: 900; color: #09090b; margin: 14px 0 10px 0; letter-spacing: -0.8px;">
                    Plano de estudo perfeito em 4 etapas
                </h2>
                <p style="color: #64748b; font-size: clamp(13.5px, 2.5vw, 16px); margin: 0; line-height: 1.6;">
                    Um fluxo simples e direto para assumir o controle total da sua vida universitária.
                </p>
            </div>

            <!-- Steps Grid com Conexão Visual -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(min(220px, 100%), 1fr)); gap: 16px; position: relative;">
                
                <div style="background: #ffffff; border: 1.5px solid #e4e4e7; border-radius: 16px; padding: 22px 18px; position: relative;">
                    <div style="background: #09090b; color: #ffffff; width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 15px; margin-bottom: 14px;">
                        01
                    </div>
                    <h4 style="font-size: 16px; font-weight: 800; margin: 0 0 6px 0; color: #09090b;">Cadastre as Matérias</h4>
                    <p style="font-size: 12.5px; color: #64748b; line-height: 1.55; margin: 0;">
                        Estruture o semestre cadastrando suas disciplinas, corpo docente e objetivos de estudo.
                    </p>
                </div>

                <div style="background: #ffffff; border: 1.5px solid #e4e4e7; border-radius: 16px; padding: 22px 18px; position: relative;">
                    <div style="background: #7c3aed; color: #ffffff; width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 15px; margin-bottom: 14px;">
                        02
                    </div>
                    <h4 style="font-size: 16px; font-weight: 800; margin: 0 0 6px 0; color: #09090b;">Mapeie Prazos e Provas</h4>
                    <p style="font-size: 12.5px; color: #64748b; line-height: 1.55; margin: 0;">
                        Adicione trabalhos, relatórios e datas de provas definindo os níveis de prioridade.
                    </p>
                </div>

                <div style="background: #ffffff; border: 1.5px solid #e4e4e7; border-radius: 16px; padding: 22px 18px; position: relative;">
                    <div style="background: #09090b; color: #ffffff; width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 15px; margin-bottom: 14px;">
                        03
                    </div>
                    <h4 style="font-size: 16px; font-weight: 800; margin: 0 0 6px 0; color: #09090b;">Ative a Prioridade</h4>
                    <p style="font-size: 12.5px; color: #64748b; line-height: 1.55; margin: 0;">
                        O algoritmo calcula os dias restantes e coloca automaticamente no topo o que é urgente.
                    </p>
                </div>

                <div style="background: #ffffff; border: 1.5px solid #e4e4e7; border-radius: 16px; padding: 22px 18px; position: relative;">
                    <div style="background: #7c3aed; color: #ffffff; width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 15px; margin-bottom: 14px;">
                        04
                    </div>
                    <h4 style="font-size: 16px; font-weight: 800; margin: 0 0 6px 0; color: #09090b;">Foque e Acompanhe</h4>
                    <p style="font-size: 12.5px; color: #64748b; line-height: 1.55; margin: 0;">
                        Execute com o Pomodoro Timer de 25 minutos e meça o crescimento no Dashboard analítico.
                    </p>
                </div>

            </div>
        </section>

        <!-- SEÇÃO DEPOIMENTOS DE ESTUDANTES -->
        <section id="testimonials" class="landing-section" style="padding: 0 clamp(16px, 4vw, 40px) clamp(35px, 6vw, 70px) clamp(16px, 4vw, 40px); max-width: 1200px; margin: 0 auto; box-sizing: border-box;">
            
            <div class="section-header-testimonials" style="text-align: center; margin-bottom: clamp(30px, 4vw, 45px);">
                <span style="background: #f5f3ff; color: #7c3aed; font-size: 11.5px; font-weight: 800; padding: 6px 16px; border-radius: 20px; text-transform: uppercase; letter-spacing: 1px; border: 1px solid #ddd6fe;">
                    FEEDBACK REAL
                </span>
                <h2 style="font-size: clamp(22px, 4.5vw, 34px); font-weight: 900; color: #09090b; margin: 14px 0 8px 0;">
                    Estudantes que transformaram seus semestres
                </h2>
                <p style="color: #64748b; font-size: clamp(13.5px, 2.5vw, 16px); margin: 0;">Avaliado com 4.9 estrelas por alunos das melhores universidades</p>
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(min(270px, 100%), 1fr)); gap: 20px;">
                
                <div style="background: #ffffff; border: 1.5px solid #e4e4e7; border-radius: 18px; padding: clamp(18px, 3.5vw, 24px); box-shadow: 0 2px 10px rgba(0,0,0,0.02);">
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                        <div style="background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%); color: white; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 14px;">
                            LG
                        </div>
                        <div>
                            <div style="font-weight: 800; font-size: 15px; color: #09090b;">Lara Gama</div>
                            <div style="font-size: 11.5px; color: #64748b;">Engenharia de Software · UFRJ</div>
                        </div>
                    </div>
                    <div style="display: flex; gap: 3px; margin-bottom: 10px;">
                        {icon("star", 15)} {icon("star", 15)} {icon("star", 15)} {icon("star", 15)} {icon("star", 15)}
                    </div>
                    <p style="font-size: 13.5px; color: #475569; line-height: 1.6; margin: 0;">
                        "O algoritmo de prioridade inteligente salvou o meu semestre de TCC. Não precisei mais ficar adivinhando o que entregar primeiro: abro o StudyFlow e o que vence hoje já está destacado no topo."
                    </p>
                </div>

                <div style="background: #ffffff; border: 1.5px solid #e4e4e7; border-radius: 18px; padding: clamp(18px, 3.5vw, 24px); box-shadow: 0 2px 10px rgba(0,0,0,0.02);">
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                        <div style="background: #09090b; color: white; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 14px;">
                            LA
                        </div>
                        <div>
                            <div style="font-weight: 800; font-size: 15px; color: #09090b;">Letícia Araújo</div>
                            <div style="font-size: 11.5px; color: #64748b;">Medicina · USP</div>
                        </div>
                    </div>
                    <div style="display: flex; gap: 3px; margin-bottom: 10px;">
                        {icon("star", 15)} {icon("star", 15)} {icon("star", 15)} {icon("star", 15)} {icon("star", 15)}
                    </div>
                    <p style="font-size: 13.5px; color: #475569; line-height: 1.6; margin: 0;">
                        "A integração entre o Pomodoro e as matérias é incrível. A interface limpa em branco e roxo dá vontade de estudar. É o melhor aplicativo acadêmico que já utilizei."
                    </p>
                </div>

                <div style="background: #ffffff; border: 1.5px solid #e4e4e7; border-radius: 18px; padding: clamp(18px, 3.5vw, 24px); box-shadow: 0 2px 10px rgba(0,0,0,0.02);">
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                        <div style="background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); color: white; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 14px;">
                            TM
                        </div>
                        <div>
                            <div style="font-weight: 800; font-size: 15px; color: #09090b;">Tarley MB</div>
                            <div style="font-size: 11.5px; color: #64748b;">Ciência da Computação · Unicamp</div>
                        </div>
                    </div>
                    <div style="display: flex; gap: 3px; margin-bottom: 10px;">
                        {icon("star", 15)} {icon("star", 15)} {icon("star", 15)} {icon("star", 15)} {icon("star", 15)}
                    </div>
                    <p style="font-size: 13.5px; color: #475569; line-height: 1.6; margin: 0;">
                        "Como estudante de computação, fiquei impressionado com a robustez da API REST em Flask e a documentação interativa Swagger. Funciona rápido, sem engasgos e com código limpo."
                    </p>
                </div>

            </div>
        </section>

        <!-- SEÇÃO PERGUNTAS FREQUENTES (FAQ ACCORDION MODERNO) -->
        <section id="faq" class="landing-section" style="margin: 0 clamp(12px, 3vw, 40px) clamp(35px, 6vw, 80px) clamp(12px, 3vw, 40px); background: #ffffff; border: 1.5px solid #e4e4e7; border-radius: 24px; padding: clamp(28px, 5vw, 60px) clamp(16px, 4vw, 45px); box-shadow: 0 4px 20px rgba(0,0,0,0.02); box-sizing: border-box;">
            <div class="section-header-faq" style="text-align: center; margin-bottom: clamp(30px, 4vw, 45px);">
                <span style="background: #f5f3ff; color: #7c3aed; font-size: 11.5px; font-weight: 800; padding: 6px 18px; border-radius: 20px; text-transform: uppercase; letter-spacing: 1px; border: 1px solid #ddd6fe;">
                    TIRE SUAS DÚVIDAS
                </span>
                <h2 style="font-size: clamp(22px, 4.5vw, 36px); font-weight: 900; color: #09090b; margin: 14px 0 8px 0; letter-spacing: -0.8px;">
                    Perguntas Frequentes
                </h2>
                <p style="color: #64748b; font-size: clamp(13.5px, 2.5vw, 16px); margin: 0;">Tudo o que você precisa saber sobre a arquitetura e funcionamento do StudyFlow</p>
            </div>

            <div style="display: flex; flex-direction: column; gap: 14px; max-width: 900px; margin: 0 auto;">
                
                <details class="faq-item">
                    <summary class="faq-question">
                        <span>O StudyFlow é gratuito para estudantes universitários?</span>
                        <div style="background: #f5f3ff; color: #7c3aed; width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-left: 10px;">
                            {icon("chevron_down", 16, "#7c3aed")}
                        </div>
                    </summary>
                    <div class="faq-answer">
                        <strong style="color: #7c3aed;">Sim, 100% gratuito.</strong> O StudyFlow é uma plataforma acadêmica de código aberto projetada para apoiar alunos universitários na organização de rotina, entregas e foco. O sistema é totalmente funcional, sem assinaturas ocultas e com banco de dados SQLite persistente.
                    </div>
                </details>

                <details class="faq-item">
                    <summary class="faq-question">
                        <span>Como funciona o algoritmo de Prioridade Inteligente?</span>
                        <div style="background: #f5f3ff; color: #7c3aed; width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-left: 10px;">
                            {icon("chevron_down", 16, "#7c3aed")}
                        </div>
                    </summary>
                    <div class="faq-answer">
                        O algoritmo calcula em tempo real o <strong style="color: #09090b;">score de urgência</strong> com base na distância entre a data atual e a data de entrega combinada ao peso da prioridade (Alta: 3x, Média: 2x, Baixa: 1x). Entregas que vencem hoje recebem pontuação máxima e tarefas atrasadas são marcadas automaticamente com badge crítico no topo da lista.
                    </div>
                </details>

                <details class="faq-item">
                    <summary class="faq-question">
                        <span>Onde posso acessar e testar a Documentação Swagger da API?</span>
                        <div style="background: #f5f3ff; color: #7c3aed; width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-left: 10px;">
                            {icon("chevron_down", 16, "#7c3aed")}
                        </div>
                    </summary>
                    <div class="faq-answer">
                        A API conta com documentação interativa Swagger (OpenAPI 2.0) disponível na rota <code style="background: #f1f5f9; padding: 2px 6px; border-radius: 6px; color: #7c3aed; font-weight: 700;">/apidocs/</code> no endereço <b>http://127.0.0.1:5000/apidocs/</b>. Nela você pode inspecionar esquemas, parâmetros e disparar requisições de teste diretamente pelo navegador.
                    </div>
                </details>

                <details class="faq-item">
                    <summary class="faq-question">
                        <span>Os dados de cadastro e tarefas ficam salvos entre as sessões?</span>
                        <div style="background: #f5f3ff; color: #7c3aed; width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-left: 10px;">
                            {icon("chevron_down", 16, "#7c3aed")}
                        </div>
                    </summary>
                    <div class="faq-answer">
                        <strong style="color: #09090b;">Sim.</strong> Todas as informações de estudantes (com senhas criptografadas via hash seguro Werkzeug), disciplinas cadastradas e atividades acadêmicas são gravadas com persistência no banco de dados SQLite (<code style="background: #f1f5f9; padding: 2px 6px; border-radius: 6px; color: #09090b;">database/studyflow.db</code>) via SQLAlchemy ORM.
                    </div>
                </details>

            </div>
        </section>

        <!-- RODAPÉ BRANCO, MODERNO E PROFISSIONAL COM LOGO REAL E ATALHOS VETORIAIS -->
        <div class="landing-footer" style="position: relative; overflow: hidden; background: #ffffff !important; border-top: 1px solid #e2e8f0; padding: 48px 24px 34px 24px; text-align: center; color: #64748b; font-family: 'Plus Jakarta Sans', sans-serif; width: 100%; box-sizing: border-box; box-shadow: 0 -8px 30px rgba(0, 0, 0, 0.03); display: block !important;">
            
            <!-- Círculos Luminosos Sutis em Tons Pastel (Aura Moderna no Branco) -->
            <div style="position: absolute; top: -60px; left: 10%; width: 280px; height: 280px; border-radius: 50%; background: radial-gradient(circle, rgba(124, 58, 237, 0.06) 0%, rgba(124, 58, 237, 0) 70%); filter: blur(50px); pointer-events: none; z-index: 0;"></div>
            <div style="position: absolute; bottom: -50px; right: 12%; width: 260px; height: 260px; border-radius: 50%; background: radial-gradient(circle, rgba(59, 130, 246, 0.05) 0%, rgba(59, 130, 246, 0) 70%); filter: blur(55px); pointer-events: none; z-index: 0;"></div>

            <!-- Conteúdo Centralizado do Rodapé -->
            <div style="position: relative; z-index: 1; max-width: 960px; margin: 0 auto; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 20px;">
                
                <!-- Identidade Visual Real e Oficial StudyFlow -->
                <div style="display: flex; flex-direction: column; align-items: center; gap: 8px;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <div style="background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%); color: white; width: 38px; height: 38px; border-radius: 11px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 14px rgba(124, 58, 237, 0.35); flex-shrink: 0;">
                            {icon("logo_cap", 20, "#ffffff", 2.2)}
                        </div>
                        <div style="display: flex; align-items: baseline;">
                            <span style="font-size: 22px; font-weight: 900; letter-spacing: -0.7px; color: #09090b;">StudyFlow</span>
                            <span style="color: #7c3aed; font-size: 24px; font-weight: 900; line-height: 0; margin-left: 2px;">.</span>
                        </div>
                    </div>
                    <div style="font-size: 13.5px; color: #64748b; font-weight: 500;">Plataforma Inteligente de Gestão Acadêmica & Alta Performance</div>
                </div>

                <!-- Seção de Atalhos Rápidos com Ícones Vetoriais SVG (Sem Emojis) -->
                <div>
                    <div style="font-size: 11px; font-weight: 800; color: #94a3b8; text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 12px;">Atalhos Rápidos</div>
                    <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 10px;">
                        <a href="#top" class="sf-footer-shortcut" onclick="window.scrollTo({{top: 0, behavior: 'smooth'}})">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="19" x2="12" y2="5"></line><polyline points="5 12 12 5 19 12"></polyline></svg>
                            Início
                        </a>
                        <a href="#features" class="sf-footer-shortcut">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                            Foco Pomodoro
                        </a>
                        <a href="#features" class="sf-footer-shortcut">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
                            Agenda Acadêmica
                        </a>
                        <a href="#methodology" class="sf-footer-shortcut">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
                            Prioridade Algorítmica
                        </a>
                        <a href="#faq" class="sf-footer-shortcut">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
                            Dúvidas Frequentes
                        </a>
                        <a href="http://127.0.0.1:5000/apidocs/" target="_blank" class="sf-footer-shortcut">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                            Swagger API Docs
                        </a>
                    </div>
                </div>

                <!-- Linha Divisória Sutil -->
                <div style="width: 100%; max-width: 560px; height: 1px; background: #e2e8f0; margin-top: 6px;"></div>

                <!-- Faixa Inferior com Copyright e Badge de Status -->
                <div style="display: flex; flex-wrap: wrap; align-items: center; justify-content: center; gap: 16px; font-size: 12.5px; color: #94a3b8;">
                    <span>© 2026 StudyFlow. Todos os direitos reservados.</span>
                    <span style="display: inline-flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 600; color: #059669; background: #ecfdf5; border: 1px solid #a7f3d0; padding: 3px 12px; border-radius: 9999px;">
                        <span style="width: 6px; height: 6px; border-radius: 50%; background: #10b981; box-shadow: 0 0 6px #10b981;"></span> Plataforma Ativa
                    </span>
                </div>

            </div>
        </div>

    </div>
    """


# ==============================================================================
# Handlers do Dashboard, Atividades e Disciplinas
# ==============================================================================

def carregar_disciplinas_dropdown(user):
    user_id = user.get("id") if user else None
    params = {"usuario_id": user_id} if user_id else {}
    dados, erro = api_get("disciplinas", params=params)
    if not dados:
        return gr.Dropdown(choices=["Geral", "Estudos", "Trabalho", "Faculdade", "TCC"], value="Geral", allow_custom_value=True)
    nomes = [d['nome'] for d in dados]
    val_default = nomes[0] if nomes else "Geral"
    return gr.Dropdown(choices=nomes, value=val_default, allow_custom_value=True)


def gerar_workspace_mobile_nav_html():
    return """
    <div class="sf-mobile-top-bar">
        <button class="sf-hamburger-btn" onclick="toggleMobileSidebar(true)" aria-label="Abrir Menu">
            <span class="sf-hamburger-icon">☰</span>
            <span class="sf-hamburger-text">Menu</span>
        </button>
        <div class="sf-mobile-bar-brand">
            <span style="font-weight: 900; color: #1e1b4b; font-size: 15px;">StudyFlow<span style="color:#7c3aed;">.</span></span>
            <span style="font-size: 10px; color: #7c3aed; font-weight: 800; background: #f5f3ff; padding: 2px 8px; border-radius: 9999px; margin-left: 6px;">Workspace PRO</span>
        </div>
        <div style="font-size: 11.5px; color: #10b981; font-weight: 700; display: flex; align-items: center; gap: 5px;">
            <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #10b981;"></span> Online
        </div>
    </div>
    <div id="sf-mobile-backdrop" onclick="toggleMobileSidebar(false)"></div>
    """


def gerar_sidebar_brand_html():
    return f"""
    <div class="sidebar-brand-wrapper" style="display: flex; align-items: center; justify-content: space-between; padding: 2px 4px 12px 4px; border-bottom: 1.5px solid #f1f5f9; margin-bottom: 10px;">
        <div style="display: flex; align-items: center; gap: 9px;">
            <div style="background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%); width: 34px; height: 34px; border-radius: 10px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 14px rgba(124, 58, 237, 0.35); flex-shrink: 0;">
                {icon("logo_cap", 20, "#ffffff")}
            </div>
            <div>
                <div style="font-weight: 900; font-size: 16px; color: #09090b; letter-spacing: -0.5px; line-height: 1.2;">StudyFlow<span style="color:#7c3aed;">.</span></div>
                <div style="font-size: 9.5px; color: #94a3b8; font-weight: 800; letter-spacing: 0.6px; text-transform: uppercase;">Workspace PRO</div>
            </div>
        </div>
        <button class="sf-sidebar-close-btn" onclick="toggleMobileSidebar(false)" title="Fechar Menu">✕</button>
    </div>
    """


def gerar_sidebar_promo_html():
    return f"""
    <div style="background: linear-gradient(145deg, #1e0b36 0%, #3b0764 50%, #6b21a8 100%); border-radius: 16px; padding: 14px 12px; color: white; margin-top: auto; box-shadow: 0 8px 20px rgba(59, 7, 100, 0.3); text-align: left;">
        <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
            <span style="background: rgba(255, 255, 255, 0.2); width: 20px; height: 20px; border-radius: 5px; display: flex; align-items: center; justify-content: center;">
                {icon("sparkles", 11, "#ffffff")}
            </span>
            <span style="font-weight: 800; font-size: 12px; color: #ffffff;">StudyFlow PRO</span>
        </div>
        <p style="font-size: 10.5px; color: #d8b4fe; margin: 0 0 10px 0; line-height: 1.4;">
            IA preditiva de prioridades e gestão de prazos.
        </p>
        <a href="http://127.0.0.1:5000/apidocs/" target="_blank" style="display: block; text-align: center; background: rgba(255, 255, 255, 0.22); color: white; text-decoration: none; padding: 6px 10px; border-radius: 9999px; font-weight: 800; font-size: 11px; border: 1px solid rgba(255, 255, 255, 0.35); transition: all 0.2s ease;">
            Swagger API Docs ↗
        </a>
    </div>
    """


def gerar_dashboard_growsync_html(data, user):
    user = user or {}
    user_name = user.get("nome", "Marjorie Talberg")
    user_email = user.get("email", "aluno@studyflow.edu")
    user_initial = user_name[0].upper() if user_name else "M"

    total = data.get("total_tarefas", 0)
    concluidas = data.get("concluidas", 0)
    pendentes = data.get("pendentes", 0)
    em_andamento = data.get("em_andamento", 0)
    taxa = data.get("taxa_conclusao", 0.0)
    atrasadas = data.get("atrasadas_count", 0)
    urgentes = data.get("urgentes_count", 0)
    proximos = data.get("proximos_prazos", [])
    por_disc = data.get("por_disciplina", [])
    total_disc = data.get("total_disciplinas", len(por_disc))

    # Próxima entrega urgente
    if proximos:
        top_u = proximos[0]
        urgent_title = top_u.get("titulo", "Nenhuma pendência")
        urgent_disc = top_u.get("disciplina_nome", "Geral")
        urgent_date = top_u.get("data_entrega", "Hoje")
        urgent_badge = top_u.get("alerta_prazo", "Urgente")
        urgent_desc = top_u.get("descricao") or "Atividade com prazo prioritário registrado na agenda."
    else:
        urgent_title = "Tudo em dia!"
        urgent_disc = "Sem tarefas pendentes"
        urgent_date = date.today().strftime("%d/%m/%Y")
        urgent_badge = "100% Em Dia"
        urgent_desc = "Você não possui nenhuma atividade pendente ou atrasada no momento. Bom trabalho!"

    # Disciplinas cards
    if por_disc:
        disc_cards_html = ""
        for d in por_disc[:2]:
            nome = d.get("disciplina", "Matéria")
            tot = d.get("total", 0)
            conc = d.get("concluidas", 0)
            perc = d.get("percentual", 0.0)
            status_tag = "Concluída" if perc == 100 else ("Em Andamento" if perc > 0 else "Pendente")
            status_bg = "#ecfdf5" if perc == 100 else "#f5f3ff"
            status_color = "#10b981" if perc == 100 else "#7c3aed"
            disc_cards_html += f"""
            <div style="background: #ffffff; border: 1.5px solid #e4e4e7; border-radius: 18px; padding: 18px; box-shadow: 0 2px 8px rgba(0,0,0,0.02);">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <div style="width: 38px; height: 38px; border-radius: 10px; background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%); color: white; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 14px; box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3);">
                            {nome[:2].upper()}
                        </div>
                        <div>
                            <div style="font-weight: 800; font-size: 14px; color: #09090b;">{nome}</div>
                            <div style="font-size: 11.5px; color: #64748b;">{conc} de {tot} concluídas</div>
                        </div>
                    </div>
                    <span style="background: {status_bg}; color: {status_color}; font-size: 11px; font-weight: 800; padding: 4px 10px; border-radius: 9999px;">
                        {status_tag}
                    </span>
                </div>
                <div style="background: #f1f5f9; height: 8px; border-radius: 9999px; overflow: hidden; margin-top: 14px;">
                    <div style="background: linear-gradient(90deg, #7c3aed 0%, #a855f7 100%); width: {perc}%; height: 100%; border-radius: 9999px;"></div>
                </div>
            </div>
            """
    else:
        disc_cards_html = f"""
        <div style="background: #f8fafc; border: 1.5px dashed #cbd5e1; border-radius: 18px; padding: 24px; text-align: center; color: #64748b; font-size: 13px;">
            Nenhuma disciplina cadastrada ainda. Adicione suas matérias para acompanhar o progresso!
        </div>
        """

    return f"""
    <div style="font-family: 'Plus Jakarta Sans', 'Inter', sans-serif; background: transparent; width: 100%; box-sizing: border-box;">
        
        <!-- TOP HEADER BAR: BUSCA E PERFIL -->
        <div class="dashboard-user-bar" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; flex-wrap: wrap; gap: 14px;">
            <div style="display: flex; align-items: center; gap: 10px; background: #ffffff; border: 1.5px solid #e4e4e7; border-radius: 9999px; padding: 9px 18px; width: 100%; max-width: 340px; box-shadow: 0 2px 8px rgba(0,0,0,0.02); box-sizing: border-box;">
                {icon("search", 16, "#94a3b8")}
                <input type="text" placeholder="Buscar tarefas, matérias..." style="border: none !important; outline: none !important; background: transparent !important; font-size: 13px; color: #09090b; width: 100%; font-family: inherit;" />
                <span style="background: #f5f3ff; color: #7c3aed; font-size: 11px; font-weight: 800; padding: 3px 8px; border-radius: 6px; letter-spacing: 0.5px;">⌘ F</span>
            </div>

            <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
                <div style="width: 38px; height: 38px; border-radius: 50%; background: #ffffff; border: 1.5px solid #e4e4e7; display: flex; align-items: center; justify-content: center; color: #64748b; cursor: pointer; box-shadow: 0 2px 6px rgba(0,0,0,0.02);">
                    {icon("mail", 16, "#64748b")}
                </div>
                <div style="width: 38px; height: 38px; border-radius: 50%; background: #ffffff; border: 1.5px solid #e4e4e7; display: flex; align-items: center; justify-content: center; position: relative; color: #64748b; cursor: pointer; box-shadow: 0 2px 6px rgba(0,0,0,0.02);">
                    {icon("bell", 16, "#64748b")}
                    <span style="position: absolute; top: 8px; right: 8px; width: 8px; height: 8px; border-radius: 50%; background: #ef4444; border: 2px solid white;"></span>
                </div>
                <div style="display: flex; align-items: center; gap: 10px; background: #ffffff; border: 1.5px solid #e4e4e7; padding: 4px 14px 4px 5px; border-radius: 9999px; box-shadow: 0 2px 6px rgba(0,0,0,0.02);">
                    <div style="width: 32px; height: 32px; border-radius: 50%; background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%); color: white; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 13px; box-shadow: 0 2px 8px rgba(124, 58, 237, 0.3);">
                        {user_initial}
                    </div>
                    <div>
                        <div style="font-weight: 800; font-size: 12.5px; color: #09090b; line-height: 1.2;">{user_name}</div>
                        <div style="font-size: 10.5px; color: #94a3b8;">{user_email}</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- TÍTULO PRINCIPAL DO DASHBOARD -->
        <div style="margin-bottom: 20px;">
            <h1 style="font-size: clamp(24px, 5vw, 32px); font-weight: 900; color: #09090b; margin: 0 0 6px 0; letter-spacing: -0.8px;">Dashboard</h1>
            <p style="font-size: 13.5px; color: #64748b; margin: 0;">Planeje, priorize e conquiste suas tarefas acadêmicas com foco e inteligência.</p>
        </div>

        <!-- 4 CARDS GRADIENTES SAAS -->
        <div class="dashboard-kpi-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(min(200px, 100%), 1fr)); gap: 16px; margin-bottom: 24px;">
            
            <!-- Card 1: Total -->
            <div style="background: linear-gradient(135deg, #2e1065 0%, #4c1d95 100%); border-radius: 22px; padding: 24px; color: white; box-shadow: 0 10px 25px rgba(46, 16, 101, 0.28); position: relative; overflow: hidden;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <span style="font-size: 14px; font-weight: 700; color: #e9d5ff;">Total</span>
                    <div style="width: 32px; height: 32px; border-radius: 50%; background: rgba(255, 255, 255, 0.18); display: flex; align-items: center; justify-content: center;">
                        {icon("arrow_up_right", 16, "#ffffff")}
                    </div>
                </div>
                <div style="font-size: 46px; font-weight: 900; line-height: 1; letter-spacing: -1.5px;">{total}</div>
                <div style="font-size: 12px; color: #d8b4fe; margin-top: 6px;">Tarefas cadastradas</div>
            </div>

            <!-- Card 2: Concluídas / Ended -->
            <div style="background: linear-gradient(135deg, #7c3aed 0%, #9333ea 100%); border-radius: 22px; padding: 24px; color: white; box-shadow: 0 10px 25px rgba(124, 58, 237, 0.28); position: relative; overflow: hidden;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <span style="font-size: 14px; font-weight: 700; color: #f3e8ff;">Ended</span>
                    <div style="width: 32px; height: 32px; border-radius: 50%; background: rgba(255, 255, 255, 0.18); display: flex; align-items: center; justify-content: center;">
                        {icon("arrow_up_right", 16, "#ffffff")}
                    </div>
                </div>
                <div style="font-size: 46px; font-weight: 900; line-height: 1; letter-spacing: -1.5px;">{concluidas}</div>
                <div style="font-size: 12px; color: #f3e8ff; margin-top: 6px;">Entregas finalizadas</div>
            </div>

            <!-- Card 3: Em Andamento / Running -->
            <div style="background: linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%); border-radius: 22px; padding: 24px; color: white; box-shadow: 0 10px 25px rgba(139, 92, 246, 0.28); position: relative; overflow: hidden;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <span style="font-size: 14px; font-weight: 700; color: #fdf4ff;">Running</span>
                    <div style="width: 32px; height: 32px; border-radius: 50%; background: rgba(255, 255, 255, 0.18); display: flex; align-items: center; justify-content: center;">
                        {icon("arrow_up_right", 16, "#ffffff")}
                    </div>
                </div>
                <div style="font-size: 46px; font-weight: 900; line-height: 1; letter-spacing: -1.5px;">{em_andamento}</div>
                <div style="font-size: 12px; color: #fae8ff; margin-top: 6px;">Em produção ativa</div>
            </div>

            <!-- Card 4: Pendentes / Pending -->
            <div style="background: linear-gradient(135deg, #a855f7 0%, #c084fc 100%); border-radius: 22px; padding: 24px; color: white; box-shadow: 0 10px 25px rgba(168, 85, 247, 0.28); position: relative; overflow: hidden;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <span style="font-size: 14px; font-weight: 700; color: #ffffff;">Pending</span>
                    <div style="width: 32px; height: 32px; border-radius: 50%; background: rgba(255, 255, 255, 0.18); display: flex; align-items: center; justify-content: center;">
                        {icon("arrow_up_right", 16, "#ffffff")}
                    </div>
                </div>
                <div style="font-size: 46px; font-weight: 900; line-height: 1; letter-spacing: -1.5px;">{pendentes}</div>
                <div style="font-size: 12px; color: #ffffff; margin-top: 6px;">Atrasadas: <strong style="color: #ffe4e6;">{atrasadas}</strong></div>
            </div>

        </div>

        <!-- LINHA DO MEIO: ANALYTICS WAVE CHART (ESQUERDA) + PRÓXIMA ENTREGA (DIREITA) -->
        <div class="dashboard-split-row" style="display: grid; grid-template-columns: 1.6fr 1fr; gap: 20px; margin-bottom: 24px;">
            
            <!-- Project Analytics com Onda Suave SVG -->
            <div style="background: #ffffff; border: 1.5px solid #e4e4e7; border-radius: 24px; padding: 26px; box-shadow: 0 4px 16px rgba(0,0,0,0.02);">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 14px;">
                    <div>
                        <div style="font-size: 17px; font-weight: 900; color: #09090b;">Project Analytics</div>
                        <div style="font-size: 26px; font-weight: 900; color: #7c3aed; margin-top: 4px;">
                            {concluidas} <span style="font-size: 17px; color: #94a3b8; font-weight: 600;">/ {total} Completed</span>
                        </div>
                    </div>
                    <span style="background: #f5f3ff; color: #7c3aed; font-size: 13px; font-weight: 800; padding: 6px 14px; border-radius: 9999px; border: 1px solid #ddd6fe;">
                        {taxa}%
                    </span>
                </div>

                <!-- Gráfico em Onda SVG com Gradiente -->
                <svg viewBox="0 0 600 160" style="width: 100%; height: auto; overflow: visible;">
                    <defs>
                        <linearGradient id="waveFillGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stop-color="#8b5cf6" stop-opacity="0.32" />
                            <stop offset="100%" stop-color="#8b5cf6" stop-opacity="0.0" />
                        </linearGradient>
                    </defs>
                    <path d="M 20,125 C 100,125 120,75 180,85 C 250,98 280,32 360,50 C 440,70 480,22 580,30 L 580,145 L 20,145 Z" fill="url(#waveFillGrad)" />
                    <path d="M 20,125 C 100,125 120,75 180,85 C 250,98 280,32 360,50 C 440,70 480,22 580,30" fill="none" stroke="#7c3aed" stroke-width="3.5" stroke-linecap="round" />
                    <circle cx="360" cy="50" r="5" fill="#7c3aed" stroke="#ffffff" stroke-width="2.5" />
                    <g fill="#94a3b8" font-size="12" font-weight="700" text-anchor="middle">
                        <text x="45" y="156">S</text>
                        <text x="135" y="156">M</text>
                        <text x="225" y="156">T</text>
                        <text x="315" y="156">W</text>
                        <text x="405" y="156">T</text>
                        <text x="495" y="156">F</text>
                        <text x="565" y="156">S</text>
                    </g>
                </svg>
            </div>

            <!-- Próxima Entrega / Upcoming Deadlines -->
            <div style="background: #ffffff; border: 1.5px solid #e4e4e7; border-radius: 24px; padding: 26px; box-shadow: 0 4px 16px rgba(0,0,0,0.02); display: flex; flex-direction: column; justify-content: space-between;">
                <div>
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <div style="background: #f5f3ff; color: #7c3aed; width: 34px; height: 34px; border-radius: 10px; display: flex; align-items: center; justify-content: center;">
                                {icon("clock", 18, "#7c3aed")}
                            </div>
                            <span style="font-weight: 800; font-size: 14px; color: #09090b;">Upcoming Deadlines</span>
                        </div>
                        <span style="background: #fef2f2; color: #ef4444; font-size: 11px; font-weight: 800; padding: 4px 10px; border-radius: 9999px; border: 1px solid #fecaca;">
                            {urgent_badge}
                        </span>
                    </div>

                    <div style="font-size: 18px; font-weight: 900; color: #09090b; margin-bottom: 6px; line-height: 1.3;">
                        {urgent_title}
                    </div>
                    <div style="font-size: 13px; color: #64748b; margin-bottom: 12px;">
                        <b>Matéria:</b> {urgent_disc} · <b>Prazo:</b> {urgent_date}
                    </div>
                </div>

                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; padding: 14px; font-size: 12.5px; color: #475569; line-height: 1.5;">
                    {urgent_desc}
                </div>
            </div>

        </div>

        <!-- LINHA INFERIOR: DISCIPLINAS DO SEMESTRE (ESQUERDA) + TIME TRACKER (DIREITA) -->
        <div class="dashboard-split-row" style="display: grid; grid-template-columns: 1.6fr 1fr; gap: 20px;">
            
            <!-- Disciplinas / Team Collaboration -->
            <div style="background: #ffffff; border: 1.5px solid #e4e4e7; border-radius: 24px; padding: 26px; box-shadow: 0 4px 16px rgba(0,0,0,0.02);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px;">
                    <div>
                        <div style="font-size: 17px; font-weight: 900; color: #09090b;">Disciplinas do Semestre</div>
                        <div style="font-size: 12px; color: #64748b;">{total_disc} matérias matriculadas</div>
                    </div>
                    <span style="background: #f5f3ff; color: #7c3aed; font-size: 12px; font-weight: 800; padding: 4px 12px; border-radius: 9999px;">
                        Acadêmico
                    </span>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px;">
                    {disc_cards_html}
                </div>
            </div>

            <!-- Time Tracker Widget (Pomodoro Luxuoso) -->
            <div style="background: linear-gradient(135deg, #18092e 0%, #2e1065 50%, #4c1d95 100%); border-radius: 24px; padding: 24px; color: white; box-shadow: 0 10px 30px rgba(46, 16, 101, 0.35); text-align: center; display: flex; flex-direction: column; justify-content: space-between; position: relative; overflow: hidden; min-height: 220px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 13px; font-weight: 800; color: #e9d5ff; letter-spacing: 0.5px;">Time <span style="font-weight: 500; color: #c4b5fd;">Tracker</span></span>
                    <span style="background: rgba(255, 255, 255, 0.18); color: #ffffff; font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 9999px;">25m Foco</span>
                </div>
                <div style="font-size: 48px; font-weight: 900; font-family: monospace; letter-spacing: 2px; color: #ffffff; margin: 12px 0;">
                    00:25:00
                </div>
                <div style="font-size: 12px; color: #d8b4fe; opacity: 0.9; margin-bottom: 12px;">
                    Sessão Pomodoro: Foco pleno nos estudos
                </div>
            </div>

        </div>

    </div>
    """


def carregar_dashboard_view(user):
    user_id = user.get("id") if user else None
    params = {"usuario_id": user_id} if user_id else {}
    data, erro = api_get("dashboard", params=params)
    if erro or not data:
        html_erro = f"""
        <div style="background-color: #fee2e2; border-left: 4px solid #ef4444; padding: 15px; border-radius: 8px;">
            <p style="color: #b91c1c; font-weight: bold; margin: 0;">⚠️ Conexão com o Backend</p>
            <p style="color: #7f1d1d; margin: 5px 0 0 0;">{erro or 'Erro ao obter dados.'}</p>
        </div>
        """
        return html_erro, pd.DataFrame(), pd.DataFrame()

    cards_html = gerar_dashboard_growsync_html(data, user)

    tarefas_p = data.get("tarefas_prioritarias", [])
    if tarefas_p:
        df_p = pd.DataFrame([
            {
                "ID": t["id"],
                "Alerta": t["alerta_prazo"],
                "Título": t["titulo"],
                "Disciplina": t["disciplina_nome"],
                "Data Entrega": t["data_entrega"],
                "Prioridade": t["prioridade"],
                "Status": t["status"]
            }
            for t in tarefas_p
        ])
    else:
        df_p = pd.DataFrame(columns=["ID", "Alerta", "Título", "Disciplina", "Data Entrega", "Prioridade", "Status"])

    disc_stats = data.get("por_disciplina", [])
    if disc_stats:
        df_d = pd.DataFrame([
            {
                "Disciplina": d["disciplina"],
                "Total": d["total"],
                "Concluídas": d["concluidas"],
                "Pendentes": d["pendentes"],
                "Progresso": f"{d.get('percentual', 0)}%"
            }
            for d in disc_stats
        ])
    else:
        df_d = pd.DataFrame(columns=["Disciplina", "Total", "Concluídas", "Pendentes", "Progresso"])

    return cards_html, df_p, df_d


def resolver_ou_criar_categoria(user, val_categoria):
    user_id = user.get("id") if user else None

    if isinstance(val_categoria, int):
        return val_categoria
    if isinstance(val_categoria, str) and val_categoria.strip().isdigit():
        return int(val_categoria.strip())

    cat_str = str(val_categoria or "").strip()
    if not cat_str:
        cat_str = "Geral"

    # Remove sufixo caso venha em formato com parênteses
    if " (" in cat_str and cat_str.endswith(")"):
        nome_limpo = cat_str.split(" (")[0].strip()
    else:
        nome_limpo = cat_str

    params = {"usuario_id": user_id} if user_id else {}
    existentes, _ = api_get("disciplinas", params=params)
    existentes = existentes or []

    for d in existentes:
        if d["nome"].strip().lower() == nome_limpo.strip().lower() or d["nome"].strip().lower() == cat_str.strip().lower():
            return d["id"]

    # Cria nova categoria caso não exista
    payload_nova = {
        "nome": nome_limpo,
        "professor": "Geral",
        "descricao": f"Categoria criada pelo usuário: {nome_limpo}",
        "usuario_id": user_id
    }
    resp_nova, _ = api_post("disciplinas", payload_nova)
    if resp_nova and "id" in resp_nova:
        return resp_nova["id"]
    elif resp_nova and "disciplina" in resp_nova:
        return resp_nova["disciplina"]["id"]
    elif existentes:
        return existentes[0]["id"]
    return None


def adicionar_na_agenda_handler(user, titulo, disciplina_id, data_entrega, prioridade, descricao):
    if not titulo or not data_entrega:
        dash_html, dash_df_p, dash_df_d = carregar_dashboard_view(user)
        atv_df = listar_todas_atividades(user)
        cal_html = carregar_calendario_view(user)
        cat_dd = carregar_disciplinas_dropdown(user)
        return "❌ Erro: Título e Data de Entrega são obrigatórios!", dash_html, dash_df_p, dash_df_d, atv_df, cal_html, cat_dd, cat_dd, cat_dd

    msg, _ = cadastrar_nova_atividade(user, titulo, disciplina_id, data_entrega, prioridade, descricao)
    dash_html, dash_df_p, dash_df_d = carregar_dashboard_view(user)
    atv_df = listar_todas_atividades(user)
    cal_html = carregar_calendario_view(user)
    cat_dd = carregar_disciplinas_dropdown(user)
    return msg, dash_html, dash_df_p, dash_df_d, atv_df, cal_html, cat_dd, cat_dd, cat_dd


HINT_SELECAO_HTML = """
<div style="background: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 12px; padding: 12px 16px; color: #64748b; font-size: 0.88rem; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;">
    <div style="display: flex; align-items: center; gap: 8px;">
        <span style="font-size: 1.15rem;">💡</span>
        <span><strong>Seleção Rápida:</strong> Clique em qualquer linha da tabela para selecioná-la e realizar ações com 1 clique.</span>
    </div>
    <span style="background: #e0e7ff; color: #4338ca; font-size: 0.78rem; font-weight: 700; padding: 3px 8px; border-radius: 6px;">1-Clique Ativo</span>
</div>
"""


def on_select_tabela_atividades(evt: gr.SelectData, df):
    if df is None:
        return "", HINT_SELECAO_HTML
    try:
        row_idx = evt.index[0]
        if hasattr(df, "iloc"):
            if row_idx >= len(df):
                return "", HINT_SELECAO_HTML
            row = df.iloc[row_idx]
            atv_id = str(row.get("ID", ""))
            titulo = str(row.get("Título", ""))
            materia = str(row.get("Categoria / Matéria", ""))
            status = str(row.get("Status", ""))
            prazo = str(row.get("Data Entrega", ""))
            alerta = str(row.get("Alerta", ""))
            prio = str(row.get("Prioridade", ""))
        elif isinstance(df, dict) and "data" in df:
            data = df["data"]
            if row_idx >= len(data):
                return "", HINT_SELECAO_HTML
            r = data[row_idx]
            headers = df.get("headers", [])
            row_dict = dict(zip(headers, r)) if headers else {}
            atv_id = str(row_dict.get("ID", r[0] if len(r) > 0 else ""))
            alerta = str(row_dict.get("Alerta", r[1] if len(r) > 1 else ""))
            titulo = str(row_dict.get("Título", r[2] if len(r) > 2 else ""))
            materia = str(row_dict.get("Categoria / Matéria", r[3] if len(r) > 3 else ""))
            prazo = str(row_dict.get("Data Entrega", r[4] if len(r) > 4 else ""))
            prio = str(row_dict.get("Prioridade", r[5] if len(r) > 5 else ""))
            status = str(row_dict.get("Status", r[6] if len(r) > 6 else ""))
        else:
            return "", HINT_SELECAO_HTML

        status_color = "#10b981" if status == "Concluída" else ("#f59e0b" if status == "Em Andamento" else "#6366f1")
        prio_color = "#ef4444" if prio in ["Urgente", "Alta"] else ("#f59e0b" if prio == "Média" else "#10b981")

        info_html = f"""
        <div style="background: linear-gradient(135deg, rgba(124, 58, 237, 0.08) 0%, rgba(59, 130, 246, 0.08) 100%); border: 1px solid rgba(124, 58, 237, 0.28); border-radius: 12px; padding: 12px 16px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="background: #7c3aed; color: #fff; font-weight: 800; font-size: 0.85rem; padding: 4px 10px; border-radius: 8px;">#{atv_id}</span>
                <div>
                    <span style="font-weight: 700; color: #1e1b4b; font-size: 0.98rem;">{titulo}</span>
                    <span style="color: #64748b; font-size: 0.82rem; margin-left: 6px;">({materia})</span>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                <span style="background: #fff; color: #334155; font-weight: 600; font-size: 0.8rem; padding: 3px 8px; border-radius: 6px; border: 1px solid #e2e8f0;">📅 {prazo}</span>
                <span style="background: {prio_color}18; color: {prio_color}; font-weight: 700; font-size: 0.8rem; padding: 3px 8px; border-radius: 6px;">⚡ {prio}</span>
                <span style="background: {status_color}18; color: {status_color}; font-weight: 700; font-size: 0.8rem; padding: 3px 8px; border-radius: 6px;">● {status}</span>
                <span style="background: #fee2e2; color: #dc2626; font-weight: 700; font-size: 0.8rem; padding: 3px 8px; border-radius: 6px;">{alerta}</span>
            </div>
        </div>
        """
        return atv_id, info_html
    except Exception as e:
        return "", HINT_SELECAO_HTML


def focar_no_pomodoro_handler(user, atividade_id, df):
    if not atividade_id:
        return "⚠️ Clique em uma atividade na tabela acima para focar nela no Pomodoro.", HINT_SELECAO_HTML
    try:
        aid = int(str(atividade_id).strip())
    except ValueError:
        return "⚠️ ID inválido.", HINT_SELECAO_HTML

    tit = f"Atividade #{aid}"
    if df is not None and hasattr(df, "iloc"):
        try:
            match = df[df["ID"].astype(str) == str(aid)]
            if len(match) > 0:
                tit = f"#{aid} - {match.iloc[0]['Título']}"
        except Exception:
            pass

    msg = f"⏱️ **Foco Ativado para {tit}!** Navegue até a aba **Pomodoro Timer** no menu superior para iniciar seu ciclo de foco intenso."
    return msg, gr.update()


def listar_todas_atividades(user, status="Todos", prioridade="Todas", ordenar_inteligente=True, busca=""):
    user_id = user.get("id") if user else None
    params = {}
    if user_id:
        params["usuario_id"] = user_id
    if status and status != "Todos":
        params["status"] = status
    if prioridade and prioridade != "Todas":
        params["prioridade"] = prioridade
    params["ordenar_inteligente"] = str(ordenar_inteligente).lower()
    params["inteligente"] = str(ordenar_inteligente).lower()

    dados, erro = api_get("atividades", params=params)
    if erro or not dados:
        return pd.DataFrame(columns=["ID", "Alerta", "Título", "Categoria / Matéria", "Data Entrega", "Prioridade", "Status", "Descrição"])

    if busca and str(busca).strip():
        termo = str(busca).strip().lower()
        dados = [
            a for a in dados
            if termo in str(a.get("titulo", "")).lower()
            or termo in str(a.get("disciplina_nome", "")).lower()
            or termo in str(a.get("descricao", "")).lower()
            or termo in str(a.get("alerta_prazo", "")).lower()
            or termo in str(a.get("prioridade", "")).lower()
            or termo in str(a.get("status", "")).lower()
        ]

    return pd.DataFrame([
        {
            "ID": a["id"],
            "Alerta": a["alerta_prazo"],
            "Título": a["titulo"],
            "Categoria / Matéria": a["disciplina_nome"],
            "Data Entrega": a["data_entrega"],
            "Prioridade": a["prioridade"],
            "Status": a["status"],
            "Descrição": a.get("descricao", "")
        }
        for a in dados
    ])


def cadastrar_nova_atividade(user, titulo, disciplina_id, data_entrega, prioridade, descricao, status="Pendente"):
    if not titulo or not data_entrega:
        return "❌ Erro: Título e Data de Entrega são obrigatórios!", listar_todas_atividades(user)

    did = resolver_ou_criar_categoria(user, disciplina_id)
    if not did:
        return "❌ Erro: Não foi possível vincular ou criar a categoria informada.", listar_todas_atividades(user)

    # Normalizar prioridade com precisão
    p_raw = str(prioridade or 'Média').strip().lower()
    if p_raw in ['urgente', 'urgent']:
        p_val = 'Urgente'
    elif p_raw in ['alta', 'alto', 'high']:
        p_val = 'Alta'
    elif p_raw in ['baixa', 'baixo', 'low']:
        p_val = 'Baixa'
    else:
        p_val = 'Média'

    st_raw = str(status or 'Pendente').strip()
    status_validos = ['Backlog', 'Pendente', 'A Fazer', 'Em Andamento', 'Validação', 'Em Validação', 'Concluída']
    st_val = st_raw if st_raw in status_validos else 'Pendente'

    payload = {
        "titulo": titulo.strip(),
        "disciplina_id": did,
        "data_entrega": str(data_entrega).strip(),
        "prioridade": p_val,
        "descricao": descricao.strip() if descricao else "",
        "status": st_val,
        "usuario_id": user.get("id") if user else None
    }
    resp, erro = api_post("atividades", payload)
    if erro:
        return f"❌ {erro}", listar_todas_atividades(user)
    return f"✅ Tarefa '{titulo}' cadastrada com sucesso! [{p_val}] [{st_val}]", listar_todas_atividades(user)


def alternar_conclusao_atividade(user, atividade_id, status="Todos", prioridade="Todas", ordenar_inteligente=True, busca=""):
    if not atividade_id:
        return "⚠️ Selecione uma linha na tabela ou informe o ID da atividade.", listar_todas_atividades(user, status, prioridade, ordenar_inteligente, busca)
    try:
        aid = int(str(atividade_id).strip())
    except ValueError:
        return "❌ ID inválido.", listar_todas_atividades(user, status, prioridade, ordenar_inteligente, busca)

    resp, erro = api_patch(f"atividades/{aid}/status")
    if erro:
        return f"❌ {erro}", listar_todas_atividades(user, status, prioridade, ordenar_inteligente, busca)
    return f"🔄 Status da Tarefa #{aid} atualizado para: **{resp.get('status')}**", listar_todas_atividades(user, status, prioridade, ordenar_inteligente, busca)


def excluir_atividade_handler(user, atividade_id, status="Todos", prioridade="Todas", ordenar_inteligente=True, busca=""):
    if not atividade_id:
        return "⚠️ Selecione uma linha na tabela ou informe o ID da atividade.", listar_todas_atividades(user, status, prioridade, ordenar_inteligente, busca)
    try:
        aid = int(str(atividade_id).strip())
    except ValueError:
        return "❌ ID inválido.", listar_todas_atividades(user, status, prioridade, ordenar_inteligente, busca)

    resp, erro = api_delete(f"atividades/{aid}")
    if erro:
        return f"❌ {erro}", listar_todas_atividades(user, status, prioridade, ordenar_inteligente, busca)
    return f"🗑️ {resp.get('message', 'Atividade removida com sucesso.')}", listar_todas_atividades(user, status, prioridade, ordenar_inteligente, busca)


def listar_disciplinas_view(user):
    user_id = user.get("id") if user else None
    params = {"usuario_id": user_id} if user_id else {}
    dados, erro = api_get("disciplinas", params=params)
    if erro or not dados:
        return pd.DataFrame(columns=["ID", "Categoria / Matéria", "Cor", "Responsável", "Descrição", "Qtd Atividades"])
    return pd.DataFrame([
        {
            "ID": d["id"],
            "Categoria / Matéria": d["nome"],
            "Cor": d.get("cor", "#7c3aed"),
            "Responsável": d["professor"],
            "Descrição": d.get("descricao", ""),
            "Qtd Atividades": d.get("total_atividades", 0)
        }
        for d in dados
    ])


def cadastrar_disciplina_handler(user, nome, professor, descricao, cor="#7c3aed"):
    if not nome:
        return "❌ Erro: O Nome da categoria é obrigatório!", listar_disciplinas_view(user), carregar_disciplinas_dropdown(user)

    payload = {
        "nome": nome.strip(),
        "professor": professor.strip() if professor else "Geral",
        "descricao": descricao.strip() if descricao else "",
        "cor": cor.strip() if cor else "#7c3aed",
        "usuario_id": user.get("id") if user else None
    }
    resp, erro = api_post("disciplinas", payload)
    if erro:
        return f"❌ {erro}", listar_disciplinas_view(user), carregar_disciplinas_dropdown(user)
    return f"✅ Categoria '{nome}' cadastrada com sucesso!", listar_disciplinas_view(user), carregar_disciplinas_dropdown(user)


def excluir_disciplina_handler(user, disciplina_id):
    if not disciplina_id:
        return "Informe o ID da disciplina.", listar_disciplinas_view(user), carregar_disciplinas_dropdown(user)
    try:
        did = int(disciplina_id)
    except ValueError:
        return "ID inválido.", listar_disciplinas_view(user), carregar_disciplinas_dropdown(user)

    resp, erro = api_delete(f"disciplinas/{did}")
    if erro:
        return f"❌ {erro}", listar_disciplinas_view(user), carregar_disciplinas_dropdown(user)
    return f"🗑️ {resp.get('message', 'Disciplina removida com sucesso.')}", listar_disciplinas_view(user), carregar_disciplinas_dropdown(user)


def obter_disciplina_cor_tema(nome, cor_base=None):
    """Retorna paleta de cores e ícone contextual vibrante para cada matéria/disciplina."""
    if cor_base and cor_base.startswith("#"):
        return {
            "dot": cor_base,
            "fg": cor_base,
            "bg": "#f8fafc",
            "border": cor_base + "55",
            "icon": "📚"
        }
    nome_low = (nome or "").lower()
    if any(k in nome_low for k in ["ia", "intelig", "neural", "dados", "machine", "python", "deep"]):
        return {"dot": "#8b5cf6", "fg": "#6d28d9", "bg": "#f5f3ff", "border": "#c4b5fd", "icon": "🧠"}
    elif any(k in nome_low for k in ["rede", "infra", "segur", "cloud", "sistemas", "internet"]):
        return {"dot": "#06b6d4", "fg": "#0e7490", "bg": "#ecfeff", "border": "#a5f3fc", "icon": "🌐"}
    elif any(k in nome_low for k in ["cálculo", "calculo", "matem", "algorit", "física", "fisica", "estat", "linear"]):
        return {"dot": "#3b82f6", "fg": "#1d4ed8", "bg": "#eff6ff", "border": "#bfdbfe", "icon": "📐"}
    elif any(k in nome_low for k in ["banco", "sql", "engenh", "software", "dev", "program", "web"]):
        return {"dot": "#10b981", "fg": "#047857", "bg": "#ecfdf5", "border": "#a7f3d0", "icon": "💻"}
    elif any(k in nome_low for k in ["gest", "negoc", "adm", "projeto", "tcc", "artigo", "pesquisa"]):
        return {"dot": "#f59e0b", "fg": "#b45309", "bg": "#fffbeb", "border": "#fde68a", "icon": "⚡"}
    elif any(k in nome_low for k in ["human", "comun", "design", "ux", "ui", "metod"]):
        return {"dot": "#ec4899", "fg": "#be185d", "bg": "#fdf2f8", "border": "#fbcfe8", "icon": "🎨"}

    paletas = [
        {"dot": "#8b5cf6", "fg": "#6d28d9", "bg": "#f5f3ff", "border": "#c4b5fd", "icon": "📚"},
        {"dot": "#3b82f6", "fg": "#1d4ed8", "bg": "#eff6ff", "border": "#bfdbfe", "icon": "📘"},
        {"dot": "#10b981", "fg": "#047857", "bg": "#ecfdf5", "border": "#a7f3d0", "icon": "📗"},
        {"dot": "#f59e0b", "fg": "#b45309", "bg": "#fffbeb", "border": "#fde68a", "icon": "📙"},
        {"dot": "#ec4899", "fg": "#be185d", "bg": "#fdf2f8", "border": "#fbcfe8", "icon": "📕"},
        {"dot": "#06b6d4", "fg": "#0f766e", "bg": "#f0fdfa", "border": "#99f6e4", "icon": "🎓"},
    ]
    idx = abs(hash(nome or "Geral")) % len(paletas)
    return paletas[idx]


def gerar_grade_calendario_mensal_html(dados):
    hoje = date.today()
    ano = hoje.year
    mes = hoje.month
    nomes_meses = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    nome_mes = nomes_meses[mes - 1]

    tarefas_por_dia = {}
    total_mes = 0
    concluidas_mes = 0
    atrasadas_mes = 0
    hoje_mes = 0
    semana_mes = 0

    for a in (dados or []):
        try:
            d_obj = datetime.strptime(a["data_entrega"], "%Y-%m-%d").date()
            if d_obj.year == ano and d_obj.month == mes:
                tarefas_por_dia.setdefault(d_obj.day, []).append(a)
                total_mes += 1
                if a.get("status") == "Concluída":
                    concluidas_mes += 1
                else:
                    dias = a.get("dias_restantes")
                    if dias is not None and dias < 0:
                        atrasadas_mes += 1
                    elif dias == 0:
                        hoje_mes += 1
                    elif dias is not None and 1 <= dias <= 7:
                        semana_mes += 1
        except Exception:
            pass

    taxa_progresso = round((concluidas_mes / total_mes * 100)) if total_mes > 0 else 100
    cal = calendar.monthcalendar(ano, mes)

    html = f"""
    <div class="calendar-grid-card">
        <!-- RADAR DE PRODUTIVIDADE & METAS DO MÊS (BARRA VIBRANTE E CRIATIVA) -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; margin-bottom: 24px;">
            <!-- Card 1: Entregas do Mês -->
            <div style="background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%); border: 1.5px solid #ddd6fe; border-radius: 18px; padding: 16px 20px; box-shadow: 0 4px 14px rgba(124, 58, 237, 0.08); display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <p style="font-size: 11.5px; font-weight: 800; color: #7c3aed; text-transform: uppercase; letter-spacing: 0.6px; margin: 0;">Entregas no Mês</p>
                    <h3 style="font-size: 26px; font-weight: 900; color: #4c1d95; margin: 4px 0 0 0;">{total_mes}</h3>
                    <p style="font-size: 11.5px; color: #6d28d9; margin: 2px 0 0 0;">{nome_mes} de {ano}</p>
                </div>
                <div style="width: 46px; height: 46px; border-radius: 14px; background: linear-gradient(135deg, #7c3aed, #a855f7); color: white; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 14px rgba(124, 58, 237, 0.28);">
                    {icon("calendar", 22, "#ffffff")}
                </div>
            </div>

            <!-- Card 2: Urgências & Alertas -->
            <div style="background: linear-gradient(135deg, #fff1f2 0%, #ffe4e6 100%); border: 1.5px solid #fecdd3; border-radius: 18px; padding: 16px 20px; box-shadow: 0 4px 14px rgba(225, 29, 72, 0.08); display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <p style="font-size: 11.5px; font-weight: 800; color: #e11d48; text-transform: uppercase; letter-spacing: 0.6px; margin: 0;">Atenção Crítica</p>
                    <h3 style="font-size: 26px; font-weight: 900; color: #9f1239; margin: 4px 0 0 0;">{atrasadas_mes + hoje_mes}</h3>
                    <p style="font-size: 11.5px; color: #be123c; margin: 2px 0 0 0;">{atrasadas_mes} atrasada(s) • {hoje_mes} hoje</p>
                </div>
                <div style="width: 46px; height: 46px; border-radius: 14px; background: linear-gradient(135deg, #f43f5e, #fb7185); color: white; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 14px rgba(244, 63, 94, 0.28);">
                    {icon("zap", 22, "#ffffff")}
                </div>
            </div>

            <!-- Card 3: Radar da Semana -->
            <div style="background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%); border: 1.5px solid #fde68a; border-radius: 18px; padding: 16px 20px; box-shadow: 0 4px 14px rgba(217, 119, 6, 0.08); display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <p style="font-size: 11.5px; font-weight: 800; color: #d97706; text-transform: uppercase; letter-spacing: 0.6px; margin: 0;">Próximos 7 Dias</p>
                    <h3 style="font-size: 26px; font-weight: 900; color: #92400e; margin: 4px 0 0 0;">{semana_mes}</h3>
                    <p style="font-size: 11.5px; color: #b45309; margin: 2px 0 0 0;">Prazos aproximando</p>
                </div>
                <div style="width: 46px; height: 46px; border-radius: 14px; background: linear-gradient(135deg, #f59e0b, #fbbf24); color: white; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 14px rgba(245, 158, 11, 0.28);">
                    {icon("clock", 22, "#ffffff")}
                </div>
            </div>

            <!-- Card 4: Conclusão & Eficiência -->
            <div style="background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%); border: 1.5px solid #a7f3d0; border-radius: 18px; padding: 16px 20px; box-shadow: 0 4px 14px rgba(16, 185, 129, 0.08); display: flex; align-items: center; justify-content: space-between;">
                <div style="flex: 1; padding-right: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <p style="font-size: 11.5px; font-weight: 800; color: #059669; text-transform: uppercase; letter-spacing: 0.6px; margin: 0;">Taxa Concluída</p>
                        <span style="font-size: 15px; font-weight: 900; color: #047857;">{taxa_progresso}%</span>
                    </div>
                    <div style="height: 8px; width: 100%; background: #a7f3d0; border-radius: 999px; overflow: hidden; margin-top: 8px;">
                        <div style="width: {taxa_progresso}%; height: 100%; background: linear-gradient(90deg, #10b981, #06b6d4); border-radius: 999px; transition: width 0.5s ease;"></div>
                    </div>
                    <p style="font-size: 11px; color: #047857; margin: 4px 0 0 0;">{concluidas_mes} de {total_mes} entregas feitas</p>
                </div>
                <div style="width: 46px; height: 46px; border-radius: 14px; background: linear-gradient(135deg, #10b981, #34d399); color: white; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 14px rgba(16, 185, 129, 0.28);">
                    {icon("check_circle", 22, "#ffffff")}
                </div>
            </div>
        </div>

        <!-- Header do Mês e Legenda Estilizada -->
        <div class="cal-month-header">
            <div style="display: flex; align-items: center; gap: 14px;">
                <div style="background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%); width: 44px; height: 44px; border-radius: 14px; display: flex; align-items: center; justify-content: center; box-shadow: 0 6px 16px rgba(124, 58, 237, 0.25);">
                    {icon("calendar", 22, "#ffffff")}
                </div>
                <div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <h2 style="font-size: 24px; font-weight: 900; background: linear-gradient(135deg, #1e1b4b 0%, #4c1d95 50%, #7c3aed 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0; letter-spacing: -0.5px;">
                            {nome_mes}
                        </h2>
                        <span style="background: linear-gradient(135deg, #7c3aed, #9333ea); color: white; font-size: 12px; font-weight: 900; padding: 2px 10px; border-radius: 999px; box-shadow: 0 2px 6px rgba(124, 58, 237, 0.25);">
                            {ano}
                        </span>
                    </div>
                    <p style="font-size: 12.5px; color: #64748b; margin: 3px 0 0 0;">
                        Grade acadêmica mensal inteligente com alertas automáticos de prazos
                    </p>
                </div>
            </div>

            <!-- Legenda das Cores de Urgência (Pills Interativos) -->
            <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                <span style="display: inline-flex; align-items: center; gap: 5px; background: #fef2f2; border: 1px solid #fecaca; color: #dc2626; padding: 4px 10px; border-radius: 999px; font-size: 11px; font-weight: 800;">
                    <span style="width: 7px; height: 7px; border-radius: 50%; background: #ef4444; box-shadow: 0 0 6px #ef4444;"></span> Atrasada
                </span>
                <span style="display: inline-flex; align-items: center; gap: 5px; background: #fffbeb; border: 1px solid #fde68a; color: #b45309; padding: 4px 10px; border-radius: 999px; font-size: 11px; font-weight: 800;">
                    <span style="width: 7px; height: 7px; border-radius: 50%; background: #f59e0b; box-shadow: 0 0 6px #f59e0b;"></span> Vence Hoje
                </span>
                <span style="display: inline-flex; align-items: center; gap: 5px; background: #f5f3ff; border: 1px solid #ddd6fe; color: #6d28d9; padding: 4px 10px; border-radius: 999px; font-size: 11px; font-weight: 800;">
                    <span style="width: 7px; height: 7px; border-radius: 50%; background: #7c3aed; box-shadow: 0 0 6px #7c3aed;"></span> Próximos 7 Dias
                </span>
                <span style="display: inline-flex; align-items: center; gap: 5px; background: #f0f9ff; border: 1px solid #bae6fd; color: #0369a1; padding: 4px 10px; border-radius: 999px; font-size: 11px; font-weight: 800;">
                    <span style="width: 7px; height: 7px; border-radius: 50%; background: #0284c7;"></span> Planejada
                </span>
                <span style="display: inline-flex; align-items: center; gap: 5px; background: #ecfdf5; border: 1px solid #a7f3d0; color: #047857; padding: 4px 10px; border-radius: 999px; font-size: 11px; font-weight: 800;">
                    <span style="width: 7px; height: 7px; border-radius: 50%; background: #10b981;"></span> Concluída
                </span>
            </div>
        </div>

        <!-- Dias da Semana (SEG a DOM) com Design Inovador -->
        <div class="cal-weekday-grid">
            <div class="cal-weekday-col">Segunda</div>
            <div class="cal-weekday-col">Terça</div>
            <div class="cal-weekday-col">Quarta</div>
            <div class="cal-weekday-col">Quinta</div>
            <div class="cal-weekday-col">Sexta</div>
            <div class="cal-weekday-col is-weekend">Sábado</div>
            <div class="cal-weekday-col is-weekend">Domingo</div>
        </div>

        <!-- Grade de Dias -->
        <div class="cal-days-grid">
    """

    for semana in cal:
        for dia in semana:
            if dia == 0:
                html += '<div class="cal-day-cell is-empty"></div>'
            else:
                is_today = (dia == hoje.day)
                cell_class = "cal-day-cell is-today" if is_today else "cal-day-cell"

                dia_tarefas = tarefas_por_dia.get(dia, [])
                qtd = len(dia_tarefas)

                # Calcular linha de calor superior (Heat bar)
                heat_gradient = ""
                if any(t.get("dias_restantes") is not None and t["dias_restantes"] < 0 and t.get("status") != "Concluída" for t in dia_tarefas):
                    heat_gradient = "linear-gradient(90deg, #ef4444, #f43f5e)"
                elif any(t.get("dias_restantes") == 0 and t.get("status") != "Concluída" for t in dia_tarefas):
                    heat_gradient = "linear-gradient(90deg, #f59e0b, #fbbf24)"
                elif any(t.get("dias_restantes") is not None and 1 <= t["dias_restantes"] <= 7 and t.get("status") != "Concluída" for t in dia_tarefas):
                    heat_gradient = "linear-gradient(90deg, #7c3aed, #a855f7)"
                elif qtd > 0 and all(t.get("status") == "Concluída" for t in dia_tarefas):
                    heat_gradient = "linear-gradient(90deg, #10b981, #34d399)"
                elif qtd > 0:
                    heat_gradient = "linear-gradient(90deg, #0284c7, #38bdf8)"

                heat_bar_html = f'<div class="cal-heat-bar" style="background: {heat_gradient};"></div>' if heat_gradient else ''

                tarefas_html = ""
                for t in dia_tarefas[:3]:
                    cat_nome = t.get("disciplina_nome") or "Geral"
                    cat_tema = obter_disciplina_cor_tema(cat_nome, t.get("disciplina_cor"))

                    if t.get("status") == "Concluída":
                        bg, fg, border, icon_status = "#ecfdf5", "#059669", "#a7f3d0", "✅"
                        extra_style = "text-decoration: line-through; opacity: 0.85;"
                    elif t.get("dias_restantes") is not None and t["dias_restantes"] < 0:
                        bg, fg, border, icon_status = "#fef2f2", "#dc2626", "#fecaca", "🔥"
                        extra_style = "font-weight: 800;"
                    elif t.get("dias_restantes") == 0:
                        bg, fg, border, icon_status = "#fffbeb", "#d97706", "#fde68a", "⚡"
                        extra_style = "font-weight: 800;"
                    else:
                        bg, fg, border, icon_status = cat_tema["bg"], cat_tema["fg"], cat_tema["border"], cat_tema["icon"]
                        extra_style = ""

                    titulo_curto = t["titulo"]
                    if len(titulo_curto) > 15:
                        titulo_curto = titulo_curto[:13] + ".."

                    prio = t.get("prioridade", "Média")
                    tooltip = f"{t['titulo']} | Matéria: {cat_nome} | Prazo: {t.get('data_entrega', '')} | Prioridade: {prio} | Status: {t.get('status', 'Pendente')}"

                    tarefas_html += f"""
                    <div class="cal-event-badge" style="background: {bg}; color: {fg}; border: 1px solid {border}; {extra_style}" title="{tooltip}">
                        <span style="font-size: 11px;">{icon_status}</span>
                        <span>{titulo_curto}</span>
                    </div>
                    """

                if len(dia_tarefas) > 3:
                    mais = len(dia_tarefas) - 3
                    tarefas_html += f"""
                    <div style="font-size: 10px; color: #7c3aed; background: #f5f3ff; border: 1px solid #ddd6fe; border-radius: 6px; padding: 2px 6px; font-weight: 800; margin-top: 2px; text-align: center;">
                        +{mais} atividade(s)
                    </div>
                    """

                num_badge = (
                    f'<span style="background: linear-gradient(135deg, #7c3aed 0%, #d946ef 100%); color: #ffffff; width: 25px; height: 25px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 11.5px; font-weight: 900; box-shadow: 0 2px 8px rgba(124, 58, 237, 0.35);">{dia}</span>'
                    if is_today else
                    f'<span class="cal-day-num">{dia}</span>'
                )

                today_pill = '<span style="font-size: 9.5px; font-weight: 900; color: #ffffff; background: linear-gradient(135deg, #7c3aed, #ec4899); padding: 2px 7px; border-radius: 9999px; letter-spacing: 0.3px; box-shadow: 0 2px 6px rgba(124, 58, 237, 0.25);">✨ HOJE</span>' if is_today else ''

                html += f"""
                <div class="{cell_class}">
                    {heat_bar_html}
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        {num_badge}
                        {today_pill}
                    </div>
                    <div style="display: flex; flex-direction: column; gap: 2px;">
                        {tarefas_html}
                    </div>
                </div>
                """

    html += """
        </div>
    </div>
    """
    return html


def carregar_calendario_view(user):
    user_id = user.get("id") if user else None
    params = {"usuario_id": user_id} if user_id else {}
    dados, erro = api_get("atividades", params=params)
    dados = dados or []

    grade_calendario_html = gerar_grade_calendario_mensal_html(dados)

    atrasadas, hoje_list, semana_list, futuras, concluidas = [], [], [], [], []

    for a in sorted(dados, key=lambda x: x["data_entrega"]):
        if a["status"] == "Concluída":
            concluidas.append(a)
        else:
            dias = a.get("dias_restantes")
            if dias is not None and dias < 0:
                atrasadas.append(a)
            elif dias == 0:
                hoje_list.append(a)
            elif dias is not None and 1 <= dias <= 7:
                semana_list.append(a)
            else:
                futuras.append(a)

    def render_card_inovador(item, status_tipo="futura"):
        config = {
            "atrasada": {
                "border_color": "#ef4444",
                "badge_bg": "#fef2f2",
                "badge_fg": "#dc2626",
                "badge_border": "#fecaca",
                "icon": "🚨",
                "shadow": "rgba(239, 68, 68, 0.08)"
            },
            "hoje": {
                "border_color": "#f59e0b",
                "badge_bg": "#fffbeb",
                "badge_fg": "#b45309",
                "badge_border": "#fde68a",
                "icon": "⚡",
                "shadow": "rgba(245, 158, 11, 0.08)"
            },
            "semana": {
                "border_color": "#7c3aed",
                "badge_bg": "#f5f3ff",
                "badge_fg": "#6d28d9",
                "badge_border": "#ddd6fe",
                "icon": "🔮",
                "shadow": "rgba(124, 58, 237, 0.08)"
            },
            "futura": {
                "border_color": "#0284c7",
                "badge_bg": "#f0f9ff",
                "badge_fg": "#0369a1",
                "badge_border": "#bae6fd",
                "icon": "📅",
                "shadow": "rgba(2, 132, 199, 0.06)"
            },
            "concluida": {
                "border_color": "#10b981",
                "badge_bg": "#ecfdf5",
                "badge_fg": "#047857",
                "badge_border": "#a7f3d0",
                "icon": "✅",
                "shadow": "rgba(16, 185, 129, 0.06)"
            }
        }[status_tipo]

        cat_nome = item.get("disciplina_nome") or "Geral"
        cat_tema = obter_disciplina_cor_tema(cat_nome, item.get("disciplina_cor"))

        prio = item.get("prioridade", "Média")
        prio_badges = {
            "Urgente": '<span style="background: #fef2f2; color: #ef4444; border: 1px solid #fecaca; font-size: 11px; font-weight: 800; padding: 3px 9px; border-radius: 9999px;">🔴 Urgente</span>',
            "Alta": '<span style="background: #fff7ed; color: #ea580c; border: 1px solid #fed7aa; font-size: 11px; font-weight: 800; padding: 3px 9px; border-radius: 9999px;">🟠 Alta</span>',
            "Média": '<span style="background: #eff6ff; color: #2563eb; border: 1px solid #bfdbfe; font-size: 11px; font-weight: 800; padding: 3px 9px; border-radius: 9999px;">🟡 Média</span>',
            "Baixa": '<span style="background: #f0fdf4; color: #16a34a; border: 1px solid #bbf7d0; font-size: 11px; font-weight: 800; padding: 3px 9px; border-radius: 9999px;">🟢 Baixa</span>',
        }
        prio_html = prio_badges.get(prio, prio_badges["Média"])

        alerta_text = item.get("alerta_prazo", "")
        prazo_pill = f"""
        <span style="background: {config['badge_bg']}; color: {config['badge_fg']}; border: 1px solid {config['badge_border']}; padding: 4px 12px; border-radius: 9999px; font-size: 11.5px; font-weight: 800; display: inline-flex; align-items: center; gap: 4px; box-shadow: 0 2px 6px {config['shadow']};">
            {config['icon']} {alerta_text}
        </span>
        """

        desc_html = f"""
        <div style="margin-top: 10px; font-size: 13px; color: #475569; background: #f8fafc; border: 1px solid #f1f5f9; padding: 9px 14px; border-radius: 12px; line-height: 1.45;">
            {item['descricao']}
        </div>
        """ if item.get('descricao') else ''

        return f"""
        <div style="background: #ffffff; border: 1.5px solid #e2e8f0; border-left: 5px solid {config['border_color']}; border-radius: 16px; padding: 16px 20px; margin-bottom: 12px; box-shadow: 0 4px 16px {config['shadow']}; transition: transform 0.2s ease, box-shadow 0.2s ease;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; flex-wrap: wrap;">
                <div>
                    <h4 style="font-size: 16px; font-weight: 800; color: #0f172a; margin: 0; line-height: 1.3;">
                        {item['titulo']}
                    </h4>
                    <div style="display: flex; align-items: center; gap: 10px; margin-top: 8px; flex-wrap: wrap;">
                        <span style="background: {cat_tema['bg']}; color: {cat_tema['fg']}; border: 1px solid {cat_tema['border']}; padding: 3px 9px; border-radius: 8px; font-size: 11px; font-weight: 800; display: inline-flex; align-items: center; gap: 4px;">
                            {cat_tema['icon']} {cat_nome}
                        </span>
                        <span style="color: #64748b; font-size: 12px; font-weight: 700; display: inline-flex; align-items: center; gap: 4px; background: #f8fafc; border: 1px solid #e2e8f0; padding: 3px 9px; border-radius: 8px;">
                            📅 {item['data_entrega']}
                        </span>
                        {prio_html}
                    </div>
                </div>
                {prazo_pill}
            </div>
            {desc_html}
        </div>
        """

    html = f"""
    <div style="font-family: 'Plus Jakarta Sans', sans-serif;">
        {grade_calendario_html}
        <div style="margin-top: 32px;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 18px; flex-wrap: wrap; gap: 10px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="background: linear-gradient(135deg, #7c3aed, #a855f7); color: white; width: 34px; height: 34px; border-radius: 10px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(124, 58, 237, 0.25);">
                        {icon("clock", 18, "#ffffff")}
                    </div>
                    <div>
                        <h3 style="font-size: 20px; font-weight: 900; color: #0f172a; margin: 0; letter-spacing: -0.4px;">Cronograma Detalhado & Timeline</h3>
                        <p style="font-size: 12.5px; color: #64748b; margin: 2px 0 0 0;">Linha do tempo segmentada por urgência e proximidade de entrega</p>
                    </div>
                </div>
                <span style="background: #f5f3ff; color: #7c3aed; border: 1px solid #ddd6fe; font-size: 11.5px; font-weight: 800; padding: 4px 12px; border-radius: 9999px;">
                    {len(dados)} atividade(s) rastreada(s)
                </span>
            </div>
    """

    if not dados:
        html += """
        <div style="background: #ffffff; border: 1.5px dashed #cbd5e1; border-radius: 18px; padding: 32px; text-align: center;">
            <div style="font-size: 32px; margin-bottom: 8px;">🎉</div>
            <h4 style="font-size: 16px; font-weight: 800; color: #0f172a; margin: 0;">Nenhuma atividade pendente no cronograma!</h4>
            <p style="color: #64748b; font-size: 13px; margin: 4px 0 0 0;">Cadastre novas entregas no formulário acima para ver seu calendário em ação.</p>
        </div>
        """
    else:
        if atrasadas:
            html += f"""
            <div style="margin-top: 20px; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;">
                <span style="width: 8px; height: 8px; border-radius: 50%; background: #ef4444; box-shadow: 0 0 8px #ef4444;"></span>
                <h4 style="color: #ef4444; font-weight: 900; font-size: 16px; margin: 0;">Atenção Crítica — Atrasadas ({len(atrasadas)})</h4>
            </div>
            """
            for item in atrasadas:
                html += render_card_inovador(item, "atrasada")

        if hoje_list:
            html += f"""
            <div style="margin-top: 24px; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;">
                <span style="width: 8px; height: 8px; border-radius: 50%; background: #f59e0b; box-shadow: 0 0 8px #f59e0b;"></span>
                <h4 style="color: #d97706; font-weight: 900; font-size: 16px; margin: 0;">Prioridade de Hoje — Vencendo Hoje ({len(hoje_list)})</h4>
            </div>
            """
            for item in hoje_list:
                html += render_card_inovador(item, "hoje")

        if semana_list:
            html += f"""
            <div style="margin-top: 24px; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;">
                <span style="width: 8px; height: 8px; border-radius: 50%; background: #7c3aed; box-shadow: 0 0 8px #7c3aed;"></span>
                <h4 style="color: #7c3aed; font-weight: 900; font-size: 16px; margin: 0;">Radar da Semana — Próximos 7 Dias ({len(semana_list)})</h4>
            </div>
            """
            for item in semana_list:
                html += render_card_inovador(item, "semana")

        if futuras:
            html += f"""
            <div style="margin-top: 24px; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;">
                <span style="width: 8px; height: 8px; border-radius: 50%; background: #0284c7;"></span>
                <h4 style="color: #0369a1; font-weight: 900; font-size: 16px; margin: 0;">Planejamento Futuro — Mais Adiante ({len(futuras)})</h4>
            </div>
            """
            for item in futuras:
                html += render_card_inovador(item, "futura")

        if concluidas:
            html += f"""
            <div style="margin-top: 28px; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;">
                <span style="width: 8px; height: 8px; border-radius: 50%; background: #10b981;"></span>
                <h4 style="color: #059669; font-weight: 900; font-size: 16px; margin: 0;">Missões Concluídas com Sucesso ({len(concluidas)})</h4>
            </div>
            """
            for item in concluidas:
                html += render_card_inovador(item, "concluida")

    html += "</div></div>"
    return html


def gerar_quadro_kanban_html(dados):
    dados = dados or []

    colunas = [
        {
            "id": "backlog",
            "titulo": "Backlog",
            "icone": "⚪",
            "cor": "#64748b",
            "status_target": "Backlog",
            "itens": [a for a in dados if a.get("status") == "Backlog"]
        },
        {
            "id": "afazer",
            "titulo": "A Fazer",
            "icone": "🔵",
            "cor": "#2563eb",
            "status_target": "A Fazer",
            "itens": [a for a in dados if a.get("status") in ["Pendente", "A Fazer", "Briefing"]]
        },
        {
            "id": "andamento",
            "titulo": "Em Andamento",
            "icone": "🟡",
            "cor": "#d97706",
            "status_target": "Em Andamento",
            "itens": [a for a in dados if a.get("status") == "Em Andamento"]
        },
        {
            "id": "validacao",
            "titulo": "Validação",
            "icone": "🟣",
            "cor": "#7c3aed",
            "status_target": "Validação",
            "itens": [a for a in dados if a.get("status") in ["Validação", "Em Validação", "Revisão", "Em Revisão"]]
        },
        {
            "id": "concluido",
            "titulo": "Concluído",
            "icone": "🟢",
            "cor": "#10b981",
            "status_target": "Concluída",
            "itens": [a for a in dados if a.get("status") in ["Concluída", "Concluído", "Ajustes"]]
        }
    ]

    html = """
    <div class="kanban-board-wrapper">
        <div class="kanban-grid-row">
    """

    for col in colunas:
        qtd = len(col["itens"])
        html += f"""
        <div class="kanban-column-box">
            <div class="kanban-column-header">
                <div class="kanban-column-header-title">
                    <span>{col['icone']}</span>
                    <span>{col['titulo']}</span>
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span class="kanban-badge-count">{qtd}</span>
                    <span style="color: #94a3b8; font-size: 14px; font-weight: 800; cursor: default;">···</span>
                </div>
            </div>
            <div class="kanban-column-cards">
        """

        if not col["itens"]:
            html += """
            <div class="kanban-empty-placeholder">
                <div style="font-size: 18px; margin-bottom: 4px; opacity: 0.6;">📭</div>
                Nenhuma tarefa nesta etapa
            </div>
            """
        else:
            for item in col["itens"]:
                cat_nome = item.get("disciplina_nome") or "Geral"
                cat_cor = item.get("disciplina_cor") or "#7c3aed"
                prio = item.get("prioridade", "Média")

                if prio == "Urgente":
                    prio_badge = '<span style="background: #fef2f2; color: #ef4444; border: 1px solid #fecaca; font-size: 10px; font-weight: 800; padding: 2px 7px; border-radius: 9999px;">🔴 Urgente</span>'
                elif prio == "Alta":
                    prio_badge = '<span style="background: #fff7ed; color: #ea580c; border: 1px solid #fed7aa; font-size: 10px; font-weight: 800; padding: 2px 7px; border-radius: 9999px;">🟠 Alta</span>'
                elif prio == "Baixa":
                    prio_badge = '<span style="background: #f0fdf4; color: #16a34a; border: 1px solid #bbf7d0; font-size: 10px; font-weight: 800; padding: 2px 7px; border-radius: 9999px;">🟢 Baixa</span>'
                else:
                    prio_badge = '<span style="background: #eff6ff; color: #2563eb; border: 1px solid #bfdbfe; font-size: 10px; font-weight: 800; padding: 2px 7px; border-radius: 9999px;">🟡 Média</span>'

                alerta = item.get("alerta_prazo", "")
                if "Atrasada" in alerta:
                    prazo_badge = f'<span style="background: #fee2e2; color: #dc2626; font-size: 10px; font-weight: 800; padding: 2px 6px; border-radius: 4px;">⚠️ {alerta}</span>'
                elif "Hoje" in alerta:
                    prazo_badge = f'<span style="background: #fef3c7; color: #d97706; font-size: 10px; font-weight: 800; padding: 2px 6px; border-radius: 4px;">⚡ {alerta}</span>'
                else:
                    prazo_badge = f'<span style="color: #64748b; font-size: 11px; font-weight: 600;">📅 {item.get("data_entrega", "")}</span>'

                desc_html = f'<div style="font-size: 11.5px; color: #64748b; line-height: 1.4; margin-top: 6px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">{item["descricao"]}</div>' if item.get("descricao") else ""

                html += f"""
                <div class="kanban-task-card" style="border-left: 3.5px solid {cat_cor};">
                    <div style="display: flex; justify-content: space-between; align-items: center; gap: 6px;">
                        <span style="background: {cat_cor}18; color: {cat_cor}; border: 1px solid {cat_cor}33; font-size: 10.5px; font-weight: 800; padding: 2px 7px; border-radius: 6px;">
                            {cat_nome}
                        </span>
                        {prio_badge}
                    </div>
                    <div style="font-size: 13.5px; font-weight: 800; color: #0f172a; margin-top: 8px; line-height: 1.35;">
                        {item.get('titulo', '')}
                    </div>
                    {desc_html}
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px; padding-top: 8px; border-top: 1px solid #f1f5f9;">
                        {prazo_badge}
                        <span style="font-size: 10px; font-weight: 800; color: #7c3aed; background: #f5f3ff; border: 1px solid #ddd6fe; padding: 1.5px 6px; border-radius: 4px;">
                            #{item.get('id')}
                        </span>
                    </div>
                </div>
                """

        html += """
            </div>
        </div>
        """

    html += """
        </div>
    </div>
    """
    return html


def carregar_kanban_view(user, filtro_cat="Todas", filtro_prio="Todas", busca=""):
    user_id = user.get("id") if user else None
    params = {"usuario_id": user_id} if user_id else {}
    dados, erro = api_get("atividades", params=params)
    dados = dados or []

    if filtro_cat and filtro_cat != "Todas":
        dados = [d for d in dados if d.get("disciplina_nome") == filtro_cat]
    if filtro_prio and filtro_prio != "Todas":
        dados = [d for d in dados if d.get("prioridade") == filtro_prio]
    if busca and str(busca).strip():
        b = str(busca).strip().lower()
        dados = [d for d in dados if b in d.get("titulo", "").lower() or b in d.get("descricao", "").lower()]

    return gerar_quadro_kanban_html(dados)


def carregar_atividades_dropdown(user):
    user_id = user.get("id") if user else None
    params = {"usuario_id": user_id} if user_id else {}
    dados, _ = api_get("atividades", params=params)
    dados = dados or []
    if not dados:
        return gr.Dropdown(choices=["(Nenhuma tarefa)"], value="(Nenhuma tarefa)")
    choices = [f"#{a['id']} - {a['titulo']}" for a in dados]
    return gr.Dropdown(choices=choices, value=choices[0] if choices else None)


def mover_card_kanban_handler(user, atv_selection, target_status):
    if not atv_selection or atv_selection == "(Nenhuma tarefa)":
        return "Selecione uma tarefa para mover.", carregar_kanban_view(user), carregar_atividades_dropdown(user), listar_todas_atividades(user)

    aid = None
    try:
        if str(atv_selection).startswith("#"):
            aid = int(atv_selection.split(" - ")[0].replace("#", "").strip())
        else:
            aid = int(str(atv_selection).strip())
    except Exception:
        return "ID inválido.", carregar_kanban_view(user), carregar_atividades_dropdown(user), listar_todas_atividades(user)

    resp, erro = api_patch(f"atividades/{aid}/status", {"status": target_status})
    if erro:
        return f"❌ {erro}", carregar_kanban_view(user), carregar_atividades_dropdown(user), listar_todas_atividades(user)
    return f"🚀 Tarefa #{aid} movida para a coluna '{target_status}'!", carregar_kanban_view(user), carregar_atividades_dropdown(user), listar_todas_atividades(user)


def gerar_categorias_cards_html(user):
    user_id = user.get("id") if user else None
    params = {"usuario_id": user_id} if user_id else {}
    dados, _ = api_get("disciplinas", params=params)
    dados = dados or []

    if not dados:
        return "<p style='color: #64748b; font-size: 13.5px;'>Nenhuma categoria cadastrada ainda. Cadastre sua primeira categoria ao lado!</p>"

    html = '<div class="categories-grid">'
    for d in dados:
        cor = d.get("cor") or "#7c3aed"
        nome = d.get("nome", "Geral")
        desc = d.get("descricao") or "Sem descrição cadastrada"
        total_atv = d.get("total_atividades", 0)
        cid = d.get("id")

        html += f"""
        <div class="category-card" style="border-top: 4px solid {cor};">
            <div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="width: 12px; height: 12px; border-radius: 50%; background: {cor}; display: inline-block;"></span>
                        <span style="font-size: 16px; font-weight: 900; color: #09090b;">{nome}</span>
                    </div>
                    <span style="font-size: 10.5px; font-weight: 800; color: #64748b; background: #f1f5f9; padding: 2px 8px; border-radius: 9999px;">
                        ID #{cid}
                    </span>
                </div>
                <div style="font-size: 12.5px; color: #64748b; line-height: 1.4; margin-bottom: 12px;">
                    {desc}
                </div>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #f1f5f9; padding-top: 10px; font-size: 12px; color: #475569;">
                <span><b>{total_atv}</b> afazeres vinculados</span>
                <span style="color: {cor}; font-weight: 800;">Ativa</span>
            </div>
        </div>
        """
    html += '</div>'
    return html


# ==============================================================================
# SISTEMA DE ESTUDOS COMPLETO & POMODORO FOCUS HUB (100% INTERATIVO / REAL-TIME)
# ==============================================================================

def gerar_pomodoro_hub_html():
    return """
    <div class="pomodoro-system-container" style="background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 24px; padding: 24px 28px; box-shadow: 0 10px 30px -5px rgba(124, 58, 237, 0.06); font-family: 'Plus Jakarta Sans', sans-serif;">
        <!-- Header -->
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; border-bottom: 1px solid #f1f5f9; padding-bottom: 14px;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="background: linear-gradient(135deg, #7c3aed, #a855f7); width: 42px; height: 42px; border-radius: 12px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 14px rgba(124, 58, 237, 0.28);">
                    <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                </div>
                <div>
                    <h3 style="font-size: 20px; font-weight: 900; color: #0f172a; margin: 0; letter-spacing: -0.4px;">Pomodoro Focus Hub</h3>
                    <p style="font-size: 12.5px; color: #64748b; margin: 2px 0 0 0;">Sistema Interativo de Foco Profundo e Gestão de Estudos</p>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <span id="sf-status-badge" style="background: #f5f3ff; color: #7c3aed; border: 1px solid #ddd6fe; padding: 4px 12px; border-radius: 9999px; font-size: 11.5px; font-weight: 800;">
                    Pronto para Focar
                </span>
            </div>
        </div>

        <!-- Meta da Sessão (O que vou estudar agora?) -->
        <div style="background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 14px; padding: 12px 16px; margin-bottom: 18px;">
            <label style="font-size: 11.5px; font-weight: 800; color: #64748b; text-transform: uppercase; letter-spacing: 0.6px; display: block; margin-bottom: 5px;">
                🎯 O que você está estudando nesta sessão?
            </label>
            <input id="sf-study-goal-input" type="text" placeholder="Ex: Resolver lista de Inteligência Artificial / Ler capítulo 4" value="Estudo & Foco Profundo" style="width: 100%; box-sizing: border-box; background: #ffffff; border: 1px solid #cbd5e1; border-radius: 10px; padding: 9px 13px; font-size: 13.5px; font-weight: 600; color: #0f172a; outline: none;" oninput="if(window.sfPomodoro) window.sfPomodoro.setGoal(this.value);" />
        </div>

        <!-- Modo de Foco / Pausa Tabs -->
        <div style="display: flex; gap: 8px; margin-bottom: 18px; flex-wrap: wrap;">
            <button id="sf-btn-mode-focus" onclick="window.sfPomodoro.setMode('focus', 25)" style="flex: 1; min-width: 110px; background: linear-gradient(135deg, #7c3aed, #9333ea); color: white; border: none; padding: 10px 12px; border-radius: 12px; font-size: 12.5px; font-weight: 800; cursor: pointer; transition: all 0.2s ease; box-shadow: 0 4px 12px rgba(124, 58, 237, 0.25);">
                🎯 Foco (25m)
            </button>
            <button id="sf-btn-mode-deep" onclick="window.sfPomodoro.setMode('deep', 50)" style="flex: 1; min-width: 110px; background: #f8fafc; color: #475569; border: 1px solid #e2e8f0; padding: 10px 12px; border-radius: 12px; font-size: 12.5px; font-weight: 700; cursor: pointer; transition: all 0.2s ease;">
                ⚡ Super Foco (50m)
            </button>
            <button id="sf-btn-mode-short" onclick="window.sfPomodoro.setMode('short_break', 5)" style="flex: 1; min-width: 110px; background: #f8fafc; color: #475569; border: 1px solid #e2e8f0; padding: 10px 12px; border-radius: 12px; font-size: 12.5px; font-weight: 700; cursor: pointer; transition: all 0.2s ease;">
                ☕ Pausa Curta (5m)
            </button>
            <button id="sf-btn-mode-long" onclick="window.sfPomodoro.setMode('long_break', 15)" style="flex: 1; min-width: 110px; background: #f8fafc; color: #475569; border: 1px solid #e2e8f0; padding: 10px 12px; border-radius: 12px; font-size: 12.5px; font-weight: 700; cursor: pointer; transition: all 0.2s ease;">
                🏖️ Pausa Longa (15m)
            </button>
        </div>

        <!-- Display Central do Timer (Grande, Moderno, com Glassmorphism) -->
        <div style="background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #09090b 80%); border: 2.5px solid #7c3aed; border-radius: 24px; padding: 32px 24px; text-align: center; box-shadow: 0 12px 35px -5px rgba(124, 58, 237, 0.35); position: relative; overflow: hidden;">
            <!-- Barra de Progresso Superior Integrada -->
            <div style="position: absolute; top: 0; left: 0; right: 0; height: 5px; background: rgba(255,255,255,0.1);">
                <div id="sf-timer-bar" style="height: 100%; width: 0%; background: linear-gradient(90deg, #7c3aed, #ec4899, #3b82f6); transition: width 0.3s ease;"></div>
            </div>

            <div id="sf-mode-title" style="font-size: 13px; font-weight: 900; letter-spacing: 2px; color: #c084fc; text-transform: uppercase; margin-bottom: 6px;">
                🎯 SESSÃO DE FOCO PROFUNDO
            </div>

            <!-- Relógio Digital em Tempo Real -->
            <div id="sf-timer-time" style="font-size: 74px; font-weight: 900; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; letter-spacing: 3px; color: #ffffff; text-shadow: 0 0 30px rgba(168, 85, 247, 0.5); line-height: 1; margin: 16px 0;">
                25:00
            </div>

            <div id="sf-goal-reminder" style="font-size: 13.5px; color: #cbd5e1; font-weight: 600; margin-bottom: 22px; min-height: 20px;">
                Meta: Estudo & Foco Profundo
            </div>

            <!-- Botões de Controle do Timer -->
            <div style="display: flex; justify-content: center; align-items: center; gap: 12px; flex-wrap: wrap;">
                <button id="sf-btn-play-pause" onclick="window.sfPomodoro.toggle()" style="background: linear-gradient(135deg, #7c3aed, #9333ea); color: white; border: none; padding: 13px 36px; border-radius: 9999px; font-size: 15px; font-weight: 900; cursor: pointer; box-shadow: 0 6px 20px rgba(124, 58, 237, 0.5); transition: all 0.2s ease;">
                    ▶️ Iniciar Foco
                </button>
                <button onclick="window.sfPomodoro.reset()" style="background: rgba(255,255,255,0.1); color: #f1f5f9; border: 1px solid rgba(255,255,255,0.2); padding: 13px 22px; border-radius: 9999px; font-size: 14px; font-weight: 700; cursor: pointer; transition: all 0.2s ease;">
                    🔄 Resetar
                </button>
                <button onclick="window.sfPomodoro.skip()" style="background: rgba(255,255,255,0.1); color: #f1f5f9; border: 1px solid rgba(255,255,255,0.2); padding: 13px 18px; border-radius: 9999px; font-size: 13.5px; font-weight: 700; cursor: pointer; transition: all 0.2s ease;" title="Pular para a próxima etapa">
                    ⏭️ Pular
                </button>
                <div style="display: flex; gap: 4px; margin-left: 6px;">
                    <button onclick="window.sfPomodoro.adjustTime(60)" style="background: rgba(255,255,255,0.08); color: #c084fc; border: 1px solid rgba(192, 132, 252, 0.3); padding: 8px 12px; border-radius: 8px; font-size: 12px; font-weight: 800; cursor: pointer;" title="Adicionar 1 minuto">+1m</button>
                    <button onclick="window.sfPomodoro.adjustTime(-60)" style="background: rgba(255,255,255,0.08); color: #c084fc; border: 1px solid rgba(192, 132, 252, 0.3); padding: 8px 12px; border-radius: 8px; font-size: 12px; font-weight: 800; cursor: pointer;" title="Subtrair 1 minuto">-1m</button>
                </div>
            </div>
        </div>

        <!-- Rodapé do Pomodoro: Métricas de Ciclos & Sons Ambientes -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; margin-top: 20px;">
            <!-- Card de Ciclos Pomodoro -->
            <div style="background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 16px; padding: 14px 18px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-size: 11.5px; font-weight: 800; color: #64748b; text-transform: uppercase;">🍅 Ciclos de Hoje</span>
                    <span id="sf-total-studied" style="font-size: 12px; font-weight: 900; color: #7c3aed;">0 min foco</span>
                </div>
                <div id="sf-cycles-display" style="font-size: 18px; display: flex; align-items: center; gap: 4px;">
                    ⚪ ⚪ ⚪ ⚪ <span style="font-size: 11.5px; color: #64748b; margin-left: 4px;">(0 concluídos)</span>
                </div>
            </div>

            <!-- Som Ambiente de Foco (Web Audio) -->
            <div style="background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 16px; padding: 14px 18px;">
                <div style="font-size: 11.5px; font-weight: 800; color: #64748b; text-transform: uppercase; margin-bottom: 8px;">
                    🎧 Som Ambiente de Foco
                </div>
                <div style="display: flex; gap: 6px;">
                    <button id="sf-amb-none" onclick="window.sfPomodoro.setAmbient('none')" style="flex: 1; background: #e2e8f0; color: #0f172a; border: 1px solid #cbd5e1; padding: 6px 8px; border-radius: 8px; font-size: 11px; font-weight: 800; cursor: pointer;">
                        🔇 Silêncio
                    </button>
                    <button id="sf-amb-rain" onclick="window.sfPomodoro.setAmbient('rain')" style="flex: 1; background: #ffffff; color: #475569; border: 1px solid #e2e8f0; padding: 6px 8px; border-radius: 8px; font-size: 11px; font-weight: 700; cursor: pointer;">
                        🌧️ Chuva
                    </button>
                    <button id="sf-amb-brown" onclick="window.sfPomodoro.setAmbient('brown')" style="flex: 1; background: #ffffff; color: #475569; border: 1px solid #e2e8f0; padding: 6px 8px; border-radius: 8px; font-size: 11px; font-weight: 700; cursor: pointer;">
                        🌊 Ruído
                    </button>
                </div>
            </div>
        </div>

        <!-- Script de Inicialização e Motor do Cronômetro -->
        <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'%3E%3C/svg%3E" style="display:none;" onerror="
        if (!window.sfPomodoro) {
            window.sfPomodoro = (function() {
                var totalSeconds = 25 * 60;
                var remainingSeconds = 25 * 60;
                var timerInterval = null;
                var isRunning = false;
                var currentMode = 'focus';
                var currentGoal = 'Estudo & Foco Profundo';
                var completedCycles = parseInt(localStorage.getItem('sf_pomodoro_cycles') || '0', 10);
                var totalMinutesStudied = parseInt(localStorage.getItem('sf_pomodoro_minutes') || '0', 10);
                var audioCtx = null;
                var ambientSource = null;
                var currentAmbient = 'none';

                function getAudioContext() {
                    if (!audioCtx) {
                        var AudioCtx = window.AudioContext || window.webkitAudioContext;
                        if (AudioCtx) audioCtx = new AudioCtx();
                    }
                    if (audioCtx && audioCtx.state === 'suspended') {
                        audioCtx.resume();
                    }
                    return audioCtx;
                }

                function playChime() {
                    try {
                        var ctx = getAudioContext();
                        if (!ctx) return;
                        var now = ctx.currentTime;
                        var freqs = [523.25, 659.25, 783.99, 1046.50];
                        freqs.forEach(function(freq, i) {
                            var osc = ctx.createOscillator();
                            var gain = ctx.createGain();
                            osc.type = 'sine';
                            osc.frequency.setValueAtTime(freq, now + i * 0.14);
                            gain.gain.setValueAtTime(0.25, now + i * 0.14);
                            gain.gain.exponentialRampToValueAtTime(0.0001, now + i * 0.14 + 1.8);
                            osc.connect(gain);
                            gain.connect(ctx.destination);
                            osc.start(now + i * 0.14);
                            osc.stop(now + i * 0.14 + 1.8);
                        });
                    } catch (err) {
                        console.error('Audio chime error:', err);
                    }
                }

                function setAmbient(type) {
                    try {
                        var ctx = getAudioContext();
                        if (!ctx) return;
                        if (ambientSource) {
                            try { ambientSource.stop(); } catch(e){}
                            ambientSource = null;
                        }
                        if (type === 'none') {
                            currentAmbient = 'none';
                            updateAmbientUI();
                            return;
                        }
                        var bufferSize = ctx.sampleRate * 2;
                        var buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
                        var data = buffer.getChannelData(0);
                        var lastOut = 0.0;
                        for (var i = 0; i < bufferSize; i++) {
                            var white = Math.random() * 2 - 1;
                            lastOut = (lastOut + (0.02 * white)) / 1.02;
                            data[i] = lastOut * 3.5;
                        }
                        var noiseNode = ctx.createBufferSource();
                        noiseNode.buffer = buffer;
                        noiseNode.loop = true;

                        var filter = ctx.createBiquadFilter();
                        filter.type = type === 'rain' ? 'bandpass' : 'lowpass';
                        filter.frequency.value = type === 'rain' ? 800 : 400;

                        var gainNode = ctx.createGain();
                        gainNode.gain.value = 0.06;

                        noiseNode.connect(filter);
                        filter.connect(gainNode);
                        gainNode.connect(ctx.destination);
                        noiseNode.start();
                        ambientSource = noiseNode;
                        currentAmbient = type;
                        updateAmbientUI();
                    } catch(e) {
                        console.error(e);
                    }
                }

                function updateAmbientUI() {
                    ['none', 'rain', 'brown'].forEach(function(t) {
                        var btn = document.getElementById('sf-amb-' + t);
                        if (btn) {
                            if (t === currentAmbient) {
                                btn.style.borderColor = '#a855f7';
                                btn.style.background = '#2e1065';
                                btn.style.color = '#ffffff';
                            } else {
                                btn.style.borderColor = '#cbd5e1';
                                btn.style.background = '#ffffff';
                                btn.style.color = '#475569';
                            }
                        }
                    });
                }

                function updateUI() {
                    var min = Math.floor(remainingSeconds / 60);
                    var sec = remainingSeconds % 60;
                    var timeStr = String(min).padStart(2, '0') + ':' + String(sec).padStart(2, '0');
                    var displayEl = document.getElementById('sf-timer-time');
                    if (displayEl) displayEl.innerText = timeStr;

                    if (isRunning) {
                        document.title = '(' + timeStr + ') ' + currentGoal + ' | StudyFlow';
                    } else {
                        document.title = 'StudyFlow - Gestão Acadêmica';
                    }

                    var progress = totalSeconds > 0 ? (totalSeconds - remainingSeconds) / totalSeconds : 0;
                    var barEl = document.getElementById('sf-timer-bar');
                    if (barEl) barEl.style.width = (progress * 100) + '%';

                    var playBtn = document.getElementById('sf-btn-play-pause');
                    var badgeEl = document.getElementById('sf-status-badge');
                    if (playBtn) {
                        if (isRunning) {
                            playBtn.innerHTML = '⏸️ Pausar';
                            playBtn.style.background = 'linear-gradient(135deg, #d97706, #f59e0b)';
                            if (badgeEl) {
                                badgeEl.innerText = '🔥 Foco Ativo (' + timeStr + ')';
                                badgeEl.style.color = '#d97706';
                                badgeEl.style.borderColor = '#fde68a';
                                badgeEl.style.background = '#fffbeb';
                            }
                        } else {
                            playBtn.innerHTML = (remainingSeconds < totalSeconds) ? '▶️ Retomar' : '▶️ Iniciar Foco';
                            playBtn.style.background = 'linear-gradient(135deg, #7c3aed, #9333ea)';
                            if (badgeEl) {
                                badgeEl.innerText = (remainingSeconds < totalSeconds) ? '⏸️ Pausado' : 'Pronto para Focar';
                                badgeEl.style.color = '#7c3aed';
                                badgeEl.style.borderColor = '#ddd6fe';
                                badgeEl.style.background = '#f5f3ff';
                            }
                        }
                    }

                    var cyclesEl = document.getElementById('sf-cycles-display');
                    if (cyclesEl) {
                        var html = '';
                        var totalInSet = 4;
                        var currentInSet = completedCycles % totalInSet;
                        for (var i = 0; i < totalInSet; i++) {
                            if (i < currentInSet || (completedCycles > 0 && currentInSet === 0)) {
                                html += '🍅 ';
                            } else {
                                html += '⚪ ';
                            }
                        }
                        cyclesEl.innerHTML = html + '<span style=\'font-size: 11.5px; color: #64748b; margin-left: 6px;\'>(' + completedCycles + ' concluídos)</span>';
                    }

                    var statsEl = document.getElementById('sf-total-studied');
                    if (statsEl) {
                        statsEl.innerText = totalMinutesStudied + ' min foco';
                    }
                }

                function tick() {
                    if (remainingSeconds > 0) {
                        remainingSeconds--;
                        updateUI();
                    } else {
                        clearInterval(timerInterval);
                        timerInterval = null;
                        isRunning = false;
                        playChime();
                        if (currentMode === 'focus' || currentMode === 'deep') {
                            completedCycles++;
                            totalMinutesStudied += Math.round(totalSeconds / 60);
                            localStorage.setItem('sf_pomodoro_cycles', String(completedCycles));
                            localStorage.setItem('sf_pomodoro_minutes', String(totalMinutesStudied));
                            alert('🎉 Parabéns! Você concluiu uma sessão de foco com sucesso!\\n\\nMeta: ' + currentGoal + '\\nTempo dedicado: ' + Math.round(totalSeconds / 60) + ' minutos.\\n\\nAgora descanse na pausa recomendada!');
                            if (completedCycles % 4 === 0) {
                                setMode('long_break', 15);
                            } else {
                                setMode('short_break', 5);
                            }
                        } else {
                            alert('☕ Pausa finalizada! Seus olhos e mente estão descansados. Pronto para o próximo ciclo?');
                            setMode('focus', 25);
                        }
                        updateUI();
                    }
                }

                function toggle() {
                    getAudioContext();
                    if (isRunning) {
                        clearInterval(timerInterval);
                        timerInterval = null;
                        isRunning = false;
                    } else {
                        isRunning = true;
                        timerInterval = setInterval(tick, 1000);
                    }
                    updateUI();
                }

                function updateModeButtons(activeMode) {
                    var modes = ['focus', 'deep', 'short', 'long'];
                    modes.forEach(function(m) {
                        var btn = document.getElementById('sf-btn-mode-' + m);
                        if (btn) {
                            if (m === activeMode || (activeMode === 'short_break' && m === 'short') || (activeMode === 'long_break' && m === 'long')) {
                                btn.style.background = 'linear-gradient(135deg, #7c3aed, #9333ea)';
                                btn.style.color = 'white';
                                btn.style.border = 'none';
                                btn.style.boxShadow = '0 4px 12px rgba(124, 58, 237, 0.25)';
                            } else {
                                btn.style.background = '#f8fafc';
                                btn.style.color = '#475569';
                                btn.style.border = '1px solid #e2e8f0';
                                btn.style.boxShadow = 'none';
                            }
                        }
                    });
                }

                function setMode(mode, customMins) {
                    currentMode = mode;
                    if (isRunning) {
                        clearInterval(timerInterval);
                        timerInterval = null;
                        isRunning = false;
                    }
                    if (mode === 'focus') {
                        totalSeconds = (customMins || 25) * 60;
                        document.getElementById('sf-mode-title').innerText = '🎯 SESSÃO DE FOCO PROFUNDO';
                        document.getElementById('sf-mode-title').style.color = '#c084fc';
                        updateModeButtons('focus');
                    } else if (mode === 'deep') {
                        totalSeconds = (customMins || 50) * 60;
                        document.getElementById('sf-mode-title').innerText = '⚡ SESSÃO DE SUPER FOCO (50M)';
                        document.getElementById('sf-mode-title').style.color = '#f59e0b';
                        updateModeButtons('deep');
                    } else if (mode === 'short_break') {
                        totalSeconds = (customMins || 5) * 60;
                        document.getElementById('sf-mode-title').innerText = '☕ PAUSA CURTA DE DESCANSO';
                        document.getElementById('sf-mode-title').style.color = '#34d399';
                        updateModeButtons('short');
                    } else if (mode === 'long_break') {
                        totalSeconds = (customMins || 15) * 60;
                        document.getElementById('sf-mode-title').innerText = '🏖️ PAUSA LONGA REVIGORANTE';
                        document.getElementById('sf-mode-title').style.color = '#38bdf8';
                        updateModeButtons('long');
                    }
                    remainingSeconds = totalSeconds;
                    updateUI();
                }

                function reset() {
                    if (isRunning) {
                        clearInterval(timerInterval);
                        timerInterval = null;
                        isRunning = false;
                    }
                    remainingSeconds = totalSeconds;
                    updateUI();
                }

                function skip() {
                    if (confirm('Deseja avançar para a próxima etapa?')) {
                        if (currentMode === 'focus' || currentMode === 'deep') {
                            setMode('short_break', 5);
                        } else {
                            setMode('focus', 25);
                        }
                    }
                }

                function adjustTime(deltaSec) {
                    remainingSeconds = Math.max(60, remainingSeconds + deltaSec);
                    totalSeconds = Math.max(totalSeconds, remainingSeconds);
                    updateUI();
                }

                function setGoal(goalText) {
                    currentGoal = goalText || 'Estudo & Foco Profundo';
                    var remEl = document.getElementById('sf-goal-reminder');
                    if (remEl) remEl.innerText = 'Meta: ' + currentGoal;
                }

                setTimeout(updateUI, 100);

                return {
                    toggle: toggle,
                    reset: reset,
                    skip: skip,
                    setMode: setMode,
                    adjustTime: adjustTime,
                    setGoal: setGoal,
                    setAmbient: setAmbient
                };
            })();
        }
        " />
    </div>
    """


def gerar_painel_estudos_companion_html():
    return """
    <div class="study-companion-container" style="background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 24px; padding: 22px 24px; box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.04); font-family: 'Plus Jakarta Sans', sans-serif; margin-top: 16px;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="background: #ecfdf5; color: #10b981; width: 34px; height: 34px; border-radius: 10px; display: flex; align-items: center; justify-content: center;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
                </div>
                <div>
                    <h4 style="font-size: 15px; font-weight: 800; color: #0f172a; margin: 0;">Bloco de Notas da Sessão</h4>
                    <p style="font-size: 11.5px; color: #64748b; margin: 2px 0 0 0;">Ideias, fórmulas e dúvidas salvas automaticamente</p>
                </div>
            </div>
            <button onclick="if(confirm('Limpar anotações?')){document.getElementById('sf-scratchpad-input').value=''; localStorage.removeItem('sf_scratchpad_notes');}" style="background: none; border: none; color: #ef4444; font-size: 11.5px; font-weight: 700; cursor: pointer;">Limpar</button>
        </div>

        <!-- Bloco de notas salvo em localStorage -->
        <textarea id="sf-scratchpad-input" placeholder="Anote fórmulas, dúvidas para pesquisar na pausa, conceitos importantes..." style="width: 100%; min-height: 110px; background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 12px; padding: 10px 14px; font-size: 13px; font-family: inherit; color: #0f172a; resize: vertical; outline: none; box-sizing: border-box;" oninput="localStorage.setItem('sf_scratchpad_notes', this.value);"></textarea>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 5px; font-size: 11px; color: #94a3b8;">
            <span>💾 Salvo automaticamente no seu navegador</span>
        </div>

        <!-- Script para restaurar notas salvas -->
        <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'%3E%3C/svg%3E" style="display:none;" onerror="
        var savedNotes = localStorage.getItem('sf_scratchpad_notes');
        if (savedNotes) {
            var el = document.getElementById('sf-scratchpad-input');
            if (el) el.value = savedNotes;
        }
        " />

        <!-- Guia da Técnica Pomodoro & Foco -->
        <div style="margin-top: 16px; background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%); border: 1px solid #ddd6fe; border-radius: 14px; padding: 12px 14px;">
            <div style="font-size: 12px; font-weight: 900; color: #5b21b6; margin-bottom: 6px; display: flex; align-items: center; gap: 6px;">
                💡 Dicas para Sessão de Alto Rendimento
            </div>
            <div style="font-size: 11.5px; color: #4c1d95; line-height: 1.5;">
                • <b>25 min de imersão:</b> silencie notificações e concentre-se em 1 objetivo.<br/>
                • <b>Pausa ativa (5m):</b> beba água e alongue-se sem olhar telas.<br/>
                • <b>Ciclo 4:</b> ao fechar 4 tomates 🍅, desfrute de 15 min de descanso.
            </div>
        </div>
    </div>
    """


# ==============================================================================
# Interface Gradio Estilo SaaS Premium (100% Full-Width)
# ==============================================================================

custom_theme = gr.themes.Default(
    primary_hue="purple",
    neutral_hue="slate",
)

def criar_interface():
    with gr.Blocks(title="StudyFlow - Gestão Acadêmica & Produtividade", fill_width=True) as demo:
        user_state = gr.State(None)

        # ======================================================================
        # NAVBAR PRETA SUPERIOR COM LOGO VETORIAL E BOTÕES REDONDOS
        # ======================================================================
        with gr.Row(elem_classes=["navbar-black"]):
            with gr.Column(scale=1, min_width=0, elem_classes=["nav-col-logo"]):
                gr.HTML(value=gerar_navbar_logo_html())
            with gr.Column(scale=1, min_width=0, elem_classes=["nav-col-actions"]):
                with gr.Row(elem_classes=["nav-actions-row"]):
                    btn_nav_login = gr.Button("Entrar", variant="secondary", elem_classes=["btn-nav-login"])
                    btn_nav_cad = gr.Button("Cadastrar", variant="primary", elem_classes=["btn-nav-cadastrar"])

        # ======================================================================
        # TELA 1: LANDING PAGE SAAS (HERO + MOCKUP + 6 CARDS + ROADMAP + FAQ)
        # ======================================================================
        with gr.Group(visible=True) as landing_page_view:
            home_content_html = gr.HTML(value=gerar_hero_e_recursos_html())

        # ======================================================================
        # TELA 2: TELA DEDICADA DE LOGIN / CADASTRO (DESIGN SAAS PREMIUM SPLIT-SCREEN)
        # ======================================================================
        with gr.Column(visible=False, elem_classes=["auth-page-container"]) as auth_page_view:
            with gr.Row(elem_classes=["auth-split-wrapper"]):
                
                # PAINEL ESQUERDO: BANNER VISUAL ROXO SAAS PREMIUM
                with gr.Column(scale=5, elem_classes=["auth-left-banner"]):
                    gr.HTML(gerar_auth_left_banner_html())

                # PAINEL DIREITO: FORMULÁRIO DE LOGIN / CADASTRO
                with gr.Column(scale=5, elem_classes=["auth-right-form"]):
                    with gr.Row(elem_classes=["auth-back-row"]):
                        btn_voltar_home = gr.Button("Voltar ao Início", variant="secondary", size="sm", elem_classes=["btn-voltar-inicio"])
                    
                    gr.HTML(gerar_auth_card_header_html())
                    
                    with gr.Tabs(elem_classes=["auth-tabs"]) as auth_tabs:
                        with gr.Tab("Entrar na Conta", id="tab_login"):
                            login_email = gr.Textbox(label="E-mail Acadêmico *", value="", placeholder="seu.email@faculdade.edu.br", elem_classes=["auth-field"])
                            login_senha = gr.Textbox(label="Senha *", type="password", value="", placeholder="Digite sua senha cadastrada", elem_classes=["auth-field"])
                            with gr.Column():
                                btn_login_submit = gr.Button("Entrar no StudyFlow", variant="primary", elem_classes=["btn-auth-primary"])
                            login_msg = gr.Markdown(elem_classes=["auth-msg-box"])

                        with gr.Tab("Criar Nova Conta", id="tab_cad"):
                            cad_nome = gr.Textbox(label="Nome Completo *", placeholder="Ex: Marjorie Talberg", elem_classes=["auth-field"])
                            cad_email = gr.Textbox(label="E-mail Acadêmico *", placeholder="marjorie@faculdade.edu.br", elem_classes=["auth-field"])
                            cad_curso = gr.Textbox(label="Curso / Graduação", placeholder="Ex: Engenharia de Software", elem_classes=["auth-field"])
                            cad_senha = gr.Textbox(label="Senha de Acesso *", type="password", elem_classes=["auth-field"])
                            with gr.Column():
                                btn_cadastro_submit = gr.Button("Cadastrar e Começar", variant="primary", elem_classes=["btn-auth-cadastro"])
                            cad_msg = gr.Markdown(elem_classes=["auth-msg-box"])

        # ======================================================================
        # TELA 3: AMBIENTE DO ESTUDANTE (PAINEL SAAS COMPLETO ESTILO GROWSYNC)
        # ======================================================================
        with gr.Column(visible=False, elem_classes=["app-workspace-container"]) as app_workspace:
            # HEADER MOBILE & HAMBÚRGUER (ATIVO EM TELAS <= 1024px)
            gr.HTML(value=gerar_workspace_mobile_nav_html())
            with gr.Row(elem_classes=["growsync-workspace-layout"]):
                
                # --------------------------------------------------------------
                # SIDEBAR LATERAL ESQUERDA (SAAS COMPACTA DOCKED À ESQUERDA)
                # --------------------------------------------------------------
                with gr.Column(scale=1, min_width=0, elem_classes=["growsync-sidebar"]):
                    gr.HTML(gerar_sidebar_brand_html())
                    
                    gr.HTML('<div class="sidebar-section-title">MENU</div>')
                    btn_side_kanban = gr.Button("Quadro Kanban", elem_classes=["sidebar-btn", "btn-side-kanban", "active"])
                    btn_side_dash = gr.Button("Dashboard", elem_classes=["sidebar-btn", "btn-side-dash"])
                    btn_side_agenda = gr.Button("Agenda & Calendário", elem_classes=["sidebar-btn", "btn-side-agenda"])
                    btn_side_tarefas = gr.Button("Minhas Tarefas", elem_classes=["sidebar-btn", "btn-side-tarefas"])
                    btn_side_disc = gr.Button("Categorias & Rotina", elem_classes=["sidebar-btn", "btn-side-disc"])
                    btn_side_pomodoro = gr.Button("Pomodoro Focus", elem_classes=["sidebar-btn", "btn-side-pomodoro"])
                    
                    gr.HTML('<div class="sidebar-section-title" style="margin-top: 8px;">GERAL</div>')
                    btn_side_swagger = gr.Button("Swagger API Docs", elem_classes=["sidebar-btn", "btn-side-swagger"])
                    btn_logout = gr.Button("Sair da Conta", variant="stop", elem_classes=["sidebar-btn-logout", "btn-side-logout"])
                    
                    gr.HTML(gerar_sidebar_promo_html())

                # --------------------------------------------------------------
                # ÁREA PRINCIPAL (DASHBOARD + ABAS DE GESTÃO)
                # --------------------------------------------------------------
                with gr.Column(scale=5, min_width=0, elem_classes=["growsync-main"]):
                    user_header_text = gr.HTML(visible=False)

                    # BARRA SUPERIOR DE VISUALIZAÇÕES ESTILO CLICKUP / TRELLO
                    with gr.Row(elem_classes=["board-header-bar"]):
                        with gr.Column(scale=4, min_width=0):
                            gr.HTML(
                                """
                                <div class="board-title-wrapper">
                                    <span style="font-size: 22px;">📋</span>
                                    <div>
                                        <div class="board-title-text">Gerenciador de Atividades & Rotina</div>
                                        <div style="font-size: 11.5px; color: #10b981; font-weight: 700; margin-top: 1px;">
                                            ● Quadro Ativo · Visualização Kanban & Rotina Integrada
                                        </div>
                                    </div>
                                </div>
                                """
                            )
                        with gr.Column(scale=6, min_width=0):
                            with gr.Row(elem_classes=["board-view-buttons"]):
                                btn_view_kanban = gr.Button("📋 Kanban", elem_classes=["btn-view-pill"])
                                btn_view_tarefas = gr.Button("📑 Lista", elem_classes=["btn-view-pill"])
                                btn_view_agenda = gr.Button("📅 Calendário", elem_classes=["btn-view-pill"])
                                btn_view_dash = gr.Button("📊 Dashboard", elem_classes=["btn-view-pill"])
                                btn_view_categorias = gr.Button("🏷️ Categorias", elem_classes=["btn-view-pill"])

                    with gr.Tabs(elem_classes=["growsync-tabs"]) as workspace_tabs:
                        
                        # ------------------------------------------------------
                        # ABA 1: QUADRO KANBAN (COLUNAS VISUAIS DE AFAZERES E ROTINA)
                        # ------------------------------------------------------
                        with gr.Tab("Quadro Kanban", id="tab_kanban"):
                            kanban_add_vis = gr.State(False)
                            kanban_cat_vis = gr.State(False)

                            # BARRA DE FILTROS & AÇÕES DO KANBAN
                            with gr.Row(elem_classes=["cal-toolbar"]):
                                with gr.Column(scale=4, min_width=0):
                                    with gr.Row():
                                        kanban_filtro_cat = gr.Dropdown(choices=["Todas"], value="Todas", label="Categoria / Tipo", scale=2)
                                        kanban_filtro_prio = gr.Dropdown(choices=["Todas", "Urgente", "Alta", "Média", "Baixa"], value="Todas", label="Prioridade", scale=1)
                                        kanban_busca = gr.Textbox(placeholder="Buscar tarefa ou rotina...", label="Pesquisar", scale=2)
                                with gr.Column(scale=3, min_width=0):
                                    with gr.Row():
                                        btn_kanban_filtrar = gr.Button("Filtrar", size="sm", variant="secondary")
                                        btn_toggle_add_kanban = gr.Button("+ Novo Afazer", variant="primary", size="sm")
                                        btn_toggle_add_cat = gr.Button("+ Nova Categoria", variant="secondary", size="sm")
                                        btn_refresh_kanban = gr.Button("🔄 Atualizar", size="sm")

                            # FORMULÁRIO EXPANSÍVEL: NOVO AFAZER
                            with gr.Group(visible=False, elem_classes=["add-agenda-card"]) as kanban_add_card:
                                gr.Markdown("### 📝 Cadastrar Novo Afazer ou Tarefa de Rotina")
                                with gr.Row():
                                    kanban_input_titulo = gr.Textbox(label="Título da Tarefa / Afazer *", placeholder="Ex: Treino diário, Relatório N4, Compras...", scale=3)
                                    kanban_input_cat = gr.Dropdown(label="Categoria / Tipo (Escolha ou Digite) *", choices=[], scale=2, allow_custom_value=True)
                                    kanban_input_data = gr.Textbox(
                                        label="Data / Prazo * (AAAA-MM-DD)",
                                        value=date.today().strftime("%Y-%m-%d"),
                                        scale=2
                                    )
                                with gr.Row():
                                    kanban_input_prio = gr.Dropdown(["Alta", "Urgente", "Média", "Baixa"], label="Nível de Prioridade *", value="Alta", scale=1)
                                    kanban_input_coluna = gr.Dropdown(["A Fazer", "Backlog", "Em Andamento", "Validação", "Concluída"], label="Coluna Inicial *", value="A Fazer", scale=1)
                                    kanban_input_desc = gr.Textbox(label="Descrição / Detalhes (opcional)", placeholder="Anotações, critérios e detalhes...", scale=3)
                                with gr.Row():
                                    btn_salvar_kanban_atv = gr.Button("+ Salvar Afazer no Kanban", variant="primary")
                                kanban_add_msg = gr.Markdown()

                            # FORMULÁRIO EXPANSÍVEL: NOVA CATEGORIA COM COR
                            with gr.Group(visible=False, elem_classes=["add-agenda-card"]) as kanban_cat_card:
                                gr.Markdown("### 🏷️ Cadastrar Nova Categoria com Cor Visual")
                                with gr.Row():
                                    kanban_new_cat_nome = gr.Textbox(label="Nome da Categoria *", placeholder="Ex: Rotina Diária, Trabalho, Saúde, Estudos, Finanças...", scale=3)
                                    kanban_new_cat_cor = gr.Dropdown(
                                        label="Cor da Categoria *",
                                        choices=[
                                            "🟣 Roxo (#7c3aed)",
                                            "🔵 Azul (#2563eb)",
                                            "🟢 Verde (#10b981)",
                                            "🟠 Laranja (#f59e0b)",
                                            "🌸 Rosa (#ec4899)",
                                            "🔴 Vermelho (#ef4444)",
                                            "🔷 Ciano (#06b6d4)",
                                            "🟡 Âmbar (#d97706)",
                                            "🔘 Grafite (#475569)"
                                        ],
                                        value="🟣 Roxo (#7c3aed)",
                                        scale=2
                                    )
                                    kanban_new_cat_desc = gr.Textbox(label="Descrição (opcional)", placeholder="Ex: Hábitos e afazeres diários", scale=3)
                                with gr.Row():
                                    btn_salvar_kanban_cat = gr.Button("+ Salvar Nova Categoria", variant="primary")
                                kanban_cat_msg = gr.Markdown()

                            # O QUADRO KANBAN VISUAL (5 COLUNAS HORIZONTAIS)
                            kanban_view = gr.HTML()

                            # BARRA DE AÇÕES RÁPIDAS (MOVER COLUNAS INSTANTANEAMENTE)
                            with gr.Group(elem_classes=["add-agenda-card"]):
                                gr.Markdown("#### ⚡ Ações Rápidas no Kanban: Mover Afazer de Coluna")
                                with gr.Row():
                                    kanban_select_atv = gr.Dropdown(label="Selecione a Tarefa pelo Título ou ID", choices=[], scale=3)
                                with gr.Row(elem_classes=["kanban-quick-actions-row"]):
                                    btn_move_backlog = gr.Button("⚪ Mover p/ Backlog", size="sm")
                                    btn_move_afazer = gr.Button("🔵 Mover p/ A Fazer", size="sm")
                                    btn_move_andamento = gr.Button("🟡 Mover p/ Andamento", size="sm")
                                    btn_move_validacao = gr.Button("🟣 Mover p/ Validação", size="sm")
                                    btn_move_concluido = gr.Button("🟢 Mover p/ Concluído", size="sm")
                                    btn_delete_kanban_atv = gr.Button("🗑️ Excluir Afazer", variant="stop", size="sm")
                                kanban_action_msg = gr.Markdown()

                        # ------------------------------------------------------
                        # ABA 2: DASHBOARD GROWSYNC + ADICIONAR NA AGENDA
                        # ------------------------------------------------------
                        with gr.Tab("Dashboard", id="tab_dash"):
                            # Dashboard Rico (Cards Gradientes, Onda SVG, Próximas Entregas, Tracker)
                            dash_cards = gr.HTML()

                            # SEÇÃO INTERATIVA: ADICIONAR ATIVIDADE NA AGENDA
                            with gr.Group(elem_classes=["add-agenda-card"]):
                                gr.HTML(
                                    f"""
                                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; flex-wrap: wrap; gap: 8px;">
                                        <div style="display: flex; align-items: center; gap: 10px;">
                                            <div style="background: #f5f3ff; color: #7c3aed; width: 38px; height: 38px; border-radius: 10px; display: flex; align-items: center; justify-content: center;">
                                                {icon("calendar", 20, "#7c3aed")}
                                            </div>
                                            <div>
                                                <h3 style="font-size: 18px; font-weight: 800; color: #09090b; margin: 0;">Adicionar Atividade na Agenda</h3>
                                                <p style="font-size: 13px; color: #64748b; margin: 2px 0 0 0;">Agende entregas, trabalhos e provas com cálculo inteligente de prioridade.</p>
                                            </div>
                                        </div>
                                        <span style="background: #f5f3ff; color: #7c3aed; font-size: 12px; font-weight: 800; padding: 5px 14px; border-radius: 9999px; border: 1px solid #ddd6fe;">
                                            + Agendamento Rápido
                                        </span>
                                    </div>
                                    """
                                )
                                with gr.Row():
                                    dash_input_titulo = gr.Textbox(label="Título da Atividade / Entrega *", placeholder="Ex: Artigo de Redes Neurais", scale=3)
                                    dash_input_disciplina = gr.Dropdown(label="Categoria / Matéria (Escolha ou Digite)", choices=[], scale=2, allow_custom_value=True)
                                    dash_input_data = gr.Textbox(
                                        label="Data de Entrega * (AAAA-MM-DD)",
                                        value=(date.today() + timedelta(days=3)).strftime("%Y-%m-%d"),
                                        placeholder="2026-11-20",
                                        scale=2
                                    )
                                    dash_input_prioridade = gr.Dropdown(["Alta", "Média", "Baixa"], label="Nível de Prioridade *", value="Média", scale=2)
                                dash_input_descricao = gr.Textbox(label="Descrição / Orientações (opcional)", lines=2, placeholder="Ex: Critérios de avaliação, orientações ou links úteis...")
                                with gr.Row():
                                    btn_dash_adicionar_agenda = gr.Button("+ Salvar e Agendar na Agenda", variant="primary", elem_classes=["btn-auth-primary"])
                                dash_msg_agenda = gr.Markdown()

                        # ------------------------------------------------------
                        # ABA 2: AGENDA & CALENDÁRIO ACADÊMICO
                        # ------------------------------------------------------
                        with gr.Tab("Agenda & Calendário", id="tab_calendario"):
                            cal_form_visible = gr.State(True)

                            # BARRA SUPERIOR DE AÇÕES (TOOLBAR ELEGANTE)
                            with gr.Row(elem_classes=["cal-toolbar"]):
                                with gr.Column(scale=3, min_width=0):
                                    gr.HTML(
                                        f"""
                                        <div style="display: flex; align-items: center; gap: 12px;">
                                            <div style="background: #f5f3ff; color: #7c3aed; width: 40px; height: 40px; border-radius: 12px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(124, 58, 237, 0.18);">
                                                {icon("calendar", 20, "#7c3aed")}
                                            </div>
                                            <div>
                                                <h3 style="font-size: 17px; font-weight: 900; color: #09090b; margin: 0; letter-spacing: -0.4px;">Agenda & Calendário Mensal</h3>
                                                <p style="font-size: 12.5px; color: #64748b; margin: 2px 0 0 0;">Planejamento preditivo de entregas, provas e trabalhos acadêmicos</p>
                                            </div>
                                        </div>
                                        """
                                    )
                                with gr.Column(scale=2, min_width=0):
                                    with gr.Row():
                                        btn_toggle_cal_form = gr.Button("+ Cadastrar Atividade", variant="primary", elem_classes=["btn-cal-add"])
                                        btn_refresh_cal = gr.Button("Atualizar Cronograma", variant="secondary", elem_classes=["btn-cal-refresh"])

                            # CARD DE CADASTRO DE ATIVIDADE NO CALENDÁRIO
                            with gr.Group(visible=True, elem_classes=["add-agenda-card"]) as cal_form_card:
                                gr.HTML(
                                    f"""
                                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; flex-wrap: wrap; gap: 8px;">
                                        <div style="display: flex; align-items: center; gap: 10px;">
                                            <div style="background: #f5f3ff; color: #7c3aed; width: 34px; height: 34px; border-radius: 10px; display: flex; align-items: center; justify-content: center;">
                                                {icon("plus", 18, "#7c3aed")}
                                            </div>
                                            <div>
                                                <h4 style="font-size: 16px; font-weight: 800; color: #09090b; margin: 0;">Cadastrar Nova Atividade na Agenda</h4>
                                                <p style="font-size: 12.5px; color: #64748b; margin: 1px 0 0 0;">Insira a atividade e veja-a refletida instantaneamente na grade mensal.</p>
                                            </div>
                                        </div>
                                        <span style="background: #f5f3ff; color: #7c3aed; font-size: 11px; font-weight: 800; padding: 4px 12px; border-radius: 9999px; border: 1px solid #ddd6fe;">
                                            Cálculo Inteligente de Prioridade
                                        </span>
                                    </div>
                                    """
                                )
                                with gr.Row():
                                    cal_input_titulo = gr.Textbox(label="Título da Atividade / Prova *", placeholder="Ex: Prova 1 de Redes Neurais", scale=3)
                                    cal_input_disciplina = gr.Dropdown(label="Categoria / Matéria (Escolha ou Digite)", choices=[], scale=2, allow_custom_value=True)
                                    cal_input_data = gr.Textbox(
                                        label="Data de Entrega * (AAAA-MM-DD)",
                                        value=(date.today() + timedelta(days=3)).strftime("%Y-%m-%d"),
                                        placeholder="2026-11-20",
                                        scale=2
                                    )
                                    cal_input_prioridade = gr.Dropdown(["Alta", "Média", "Baixa"], label="Nível de Prioridade *", value="Média", scale=2)
                                cal_input_descricao = gr.Textbox(label="Descrição / Detalhes (opcional)", lines=2, placeholder="Ex: Sala de aula, conteúdo da prova, orientações...")
                                with gr.Row():
                                    btn_salvar_cal_atividade = gr.Button("+ Salvar e Inserir no Calendário", variant="primary", elem_classes=["btn-auth-primary"])
                                cal_msg_feedback = gr.Markdown()

                            # GRADE MENSAL DE DIAS E CRONOGRAMA DETALHADO
                            cal_view = gr.HTML()

                        # ------------------------------------------------------
                        # ABA 3: MINHAS TAREFAS (CRUD COMPLETO)
                        # ------------------------------------------------------
                        with gr.Tab("Minhas Tarefas", id="tab_atividades"):
                            # BANNER SUPERIOR DA CENTRAL DE TAREFAS
                            gr.HTML("""
                            <div class="tasks-page-header" style="background: linear-gradient(135deg, rgba(124, 58, 237, 0.08) 0%, rgba(99, 102, 241, 0.04) 100%); border-radius: 18px; padding: 18px 24px; border: 1px solid rgba(124, 58, 237, 0.16); margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px; box-shadow: 0 4px 16px rgba(124, 58, 237, 0.04);">
                                <div style="display: flex; align-items: center; gap: 14px;">
                                    <div style="width: 44px; height: 44px; border-radius: 12px; background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%); display: flex; align-items: center; justify-content: center; font-size: 22px; box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3); color: #fff;">
                                        📋
                                    </div>
                                    <div>
                                        <h3 style="margin: 0; font-size: 1.25rem; font-weight: 800; color: #1e1b4b; letter-spacing: -0.02em;">
                                            Central de Atividades & Entregas Acadêmicas
                                        </h3>
                                        <p style="margin: 3px 0 0 0; color: #64748b; font-size: 0.88rem; font-weight: 500;">
                                            Controle prazos, pesquise em tempo real e execute ações imediatas com 1 clique na tabela.
                                        </p>
                                    </div>
                                </div>
                                <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                                    <span style="font-size: 0.82rem; background: #ffffff; padding: 6px 14px; border-radius: 20px; border: 1px solid #e2e8f0; font-weight: 700; color: #7c3aed; box-shadow: 0 2px 6px rgba(0,0,0,0.03); display: flex; align-items: center; gap: 6px;">
                                        <span style="width: 8px; height: 8px; border-radius: 50%; background: #10b981; display: inline-block;"></span>
                                        Seleção Direta Ativa
                                    </span>
                                    <span style="font-size: 0.82rem; background: #ffffff; padding: 6px 14px; border-radius: 20px; border: 1px solid #e2e8f0; font-weight: 600; color: #475569; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
                                        ⚡ Urgência Algorítmica IA
                                    </span>
                                </div>
                            </div>
                            """)

                            with gr.Row(elem_classes=["tasks-layout-row"]):
                                # COLUNA ESQUERDA: FORMULÁRIO DE CADASTRO
                                with gr.Column(scale=2, min_width=0, elem_classes=["tasks-form-card"]):
                                    gr.HTML("""
                                    <div class="tasks-card-header">
                                        <h4><span>✨</span> Cadastrar Nova Atividade</h4>
                                        <span style="background: rgba(124, 58, 237, 0.1); color: #7c3aed; font-size: 0.75rem; font-weight: 700; padding: 3px 8px; border-radius: 6px;">Nova Entrega</span>
                                    </div>
                                    """)
                                    input_titulo = gr.Textbox(label="Título da Atividade / Prova *", placeholder="Ex: Artigo de Inteligência Artificial")
                                    input_disciplina = gr.Dropdown(label="Categoria / Matéria (Escolha ou Digite)", choices=[], allow_custom_value=True)
                                    input_data = gr.Textbox(
                                        label="Data de Entrega * (AAAA-MM-DD)",
                                        value=(date.today() + timedelta(days=3)).strftime("%Y-%m-%d"),
                                        placeholder="2026-11-20"
                                    )
                                    input_prioridade = gr.Dropdown(["Alta", "Urgente", "Média", "Baixa"], label="Nível de Prioridade *", value="Alta")
                                    input_descricao = gr.Textbox(label="Descrição / Orientações (opcional)", lines=2, placeholder="Critérios de avaliação e detalhes...")
                                    btn_cadastrar_atv = gr.Button("＋ Salvar Atividade", variant="primary", elem_classes=["btn-salvar-atv-custom"])
                                    status_cadastro_atv = gr.Markdown()

                                # COLUNA DIREITA: GESTÃO, PESQUISA E AÇÕES
                                with gr.Column(scale=4, min_width=0, elem_classes=["tasks-list-card"]):
                                    gr.HTML("""
                                    <div class="tasks-card-header">
                                        <h4><span>📋</span> Gestão de Atividades Acadêmicas</h4>
                                        <span style="background: #f1f5f9; color: #475569; font-size: 0.75rem; font-weight: 600; padding: 3px 8px; border-radius: 6px;">Pesquisa & Filtros Inteligentes</span>
                                    </div>
                                    """)

                                    # BARRA DE PESQUISA E FILTROS DINÂMICOS
                                    with gr.Row():
                                        filtro_busca = gr.Textbox(
                                            label="🔍 Pesquisar em Tempo Real",
                                            placeholder="Digite para filtrar por título, disciplina, prazo ou descrição...",
                                            scale=3
                                        )
                                        filtro_inteligente = gr.Checkbox(label="Ordenar por Urgência Algorítmica", value=True, scale=1)

                                    with gr.Row():
                                        filtro_status = gr.Dropdown(["Todos", "Backlog", "Pendente", "Em Andamento", "Validação", "Concluída"], label="Filtrar por Status", value="Todos", scale=2)
                                        filtro_prioridade = gr.Dropdown(["Todas", "Urgente", "Alta", "Média", "Baixa"], label="Filtrar por Prioridade", value="Todas", scale=2)
                                        btn_filtrar = gr.Button("🔄 Atualizar Lista", size="sm", scale=1)

                                    # TABELA COM SCROLL RESPONSIVO
                                    tabela_atividades = gr.Dataframe(
                                        headers=["ID", "Alerta", "Título", "Categoria / Matéria", "Data Entrega", "Prioridade", "Status", "Descrição"],
                                        interactive=False,
                                        elem_id="tabela_atividades_grid"
                                    )

                                    # PAINEL DE AÇÃO COM 1 CLIQUE
                                    card_selecao_html = gr.HTML(value=HINT_SELECAO_HTML)

                                    with gr.Row(elem_classes=["tasks-actions-bar"]):
                                        input_id_acao = gr.Textbox(label="ID Selecionado", placeholder="Clique na linha acima", scale=1)
                                        btn_toggle_status = gr.Button("🔄 Alternar Conclusão", variant="secondary", scale=2)
                                        btn_focar_tarefa = gr.Button("⏱️ Focar no Pomodoro", variant="secondary", scale=2)
                                        btn_excluir_atv = gr.Button("🗑️ Excluir", variant="stop", scale=1)

                                    msg_acao = gr.Markdown()

                        # ------------------------------------------------------
                        # ABA 5: CATEGORIAS & AFACERES DE ROTINA (CRUD COMPLETO)
                        # ------------------------------------------------------
                        with gr.Tab("Categorias & Rotina", id="tab_disciplinas"):
                            with gr.Row(elem_classes=["categories-layout-row"]):
                                with gr.Column(scale=2, min_width=0, elem_classes=["categories-form-col"]):
                                    gr.Markdown("#### Cadastrar Categoria / Tipo de Rotina")
                                    input_disc_nome = gr.Textbox(label="Nome da Categoria *", placeholder="Ex: Rotina Diária, Trabalho, Saúde, Estudos, Finanças...")
                                    input_disc_cor = gr.Dropdown(
                                        label="Cor de Identificação *",
                                        choices=[
                                            "🟣 Roxo (#7c3aed)",
                                            "🔵 Azul (#2563eb)",
                                            "🟢 Verde (#10b981)",
                                            "🟠 Laranja (#f59e0b)",
                                            "🌸 Rosa (#ec4899)",
                                            "🔴 Vermelho (#ef4444)",
                                            "🔷 Ciano (#06b6d4)",
                                            "🟡 Âmbar (#d97706)",
                                            "🔘 Grafite (#475569)"
                                        ],
                                        value="🟣 Roxo (#7c3aed)"
                                    )
                                    input_disc_prof = gr.Textbox(label="Responsável / Detalhes (opcional)", value="Geral", placeholder="Ex: Pessoal, Equipe...")
                                    input_disc_desc = gr.Textbox(label="Descrição / Anotações", lines=3, placeholder="Anotações e detalhes desta categoria...")
                                    btn_cadastrar_disc = gr.Button("+ Cadastrar Categoria", variant="primary")
                                    msg_cadastro_disc = gr.Markdown()

                                with gr.Column(scale=3, min_width=0, elem_classes=["categories-list-col"]):
                                    gr.Markdown("#### Minhas Categorias Cadastradas")
                                    btn_refresh_disc = gr.Button("Atualizar Categorias", size="sm")
                                    categorias_cards_view = gr.HTML()
                                    tabela_disciplinas = gr.Dataframe(
                                        headers=["ID", "Categoria / Matéria", "Cor", "Responsável", "Descrição", "Qtd Atividades"],
                                        interactive=False
                                    )
                                    with gr.Row():
                                        input_id_disc_excluir = gr.Textbox(label="ID da Categoria para Excluir", placeholder="Ex: 1", scale=3)
                                        btn_excluir_disc = gr.Button("Excluir Categoria", variant="stop", scale=2)
                                    msg_excluir_disc = gr.Markdown()

                        # ------------------------------------------------------
                        # ABA 5: POMODORO FOCUS TIMER
                        # ------------------------------------------------------
                        with gr.Tab("Pomodoro Timer", id="tab_home"):
                            with gr.Row(elem_classes=["pomodoro-layout-row"]):
                                with gr.Column(scale=4, min_width=0, elem_classes=["pomodoro-main-col"]):
                                    gr.HTML(gerar_pomodoro_hub_html())

                                with gr.Column(scale=3, min_width=0, elem_classes=["pomodoro-side-col"]):
                                    gr.Markdown("### 🎯 Entregas Imediatas & Foco Acadêmico")
                                    tabela_home_prioritarias = gr.Dataframe(
                                        headers=["ID", "Alerta", "Título", "Disciplina", "Data Entrega", "Prioridade", "Status"],
                                        interactive=False
                                    )
                                    btn_refresh_home = gr.Button("Atualizar Foco", size="sm")
                                    gr.HTML(gerar_painel_estudos_companion_html())

                        # ------------------------------------------------------
                        # ABA 6: DOCUMENTAÇÃO SWAGGER API
                        # ------------------------------------------------------
                        with gr.Tab("Documentação Swagger API", id="tab_swagger"):
                            gr.Markdown(
                                f"""
                                <div style="background: #ffffff; border: 1.5px solid #e4e4e7; border-radius: 20px; padding: 30px;">
                                    <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 20px;">
                                        <div style="background: #f5f3ff; color: #7c3aed; width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center;">
                                            {icon("shield_check", 24, "#7c3aed")}
                                        </div>
                                        <div>
                                            <h3 style="font-size: 22px; font-weight: 900; margin: 0; color: #09090b;">Documentação OpenAPI & Swagger</h3>
                                            <p style="color: #64748b; font-size: 14px; margin: 2px 0 0 0;">Interface interativa para inspeção e testes de todos os endpoints REST da plataforma.</p>
                                        </div>
                                    </div>

                                    <p style="font-size: 14px; color: #475569; line-height: 1.6;">
                                        A API REST do <b>StudyFlow</b> foi construída em <b>Flask 3.0</b> com <b>SQLAlchemy ORM</b> e <b>SQLite</b>, documentada em conformidade com a especificação OpenAPI 2.0 via <b>Flasgger</b>.
                                    </p>

                                    <div style="display: flex; gap: 14px; margin: 24px 0;">
                                        <a href="http://127.0.0.1:5000/apidocs/" target="_blank" style="display: inline-flex; align-items: center; gap: 8px; background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%); color: white; text-decoration: none; padding: 12px 24px; border-radius: 9999px; font-weight: 700; font-size: 14px; box-shadow: 0 4px 14px rgba(124, 58, 237, 0.35);">
                                            {icon("external_link", 16, "#ffffff")} Abrir Swagger UI (/apidocs/)
                                        </a>
                                        <a href="http://127.0.0.1:5000/" target="_blank" style="display: inline-flex; align-items: center; gap: 8px; background: #09090b; color: white; text-decoration: none; padding: 12px 24px; border-radius: 9999px; font-weight: 700; font-size: 14px;">
                                            {icon("layers", 16, "#ffffff")} Root da API (JSON)
                                        </a>
                                    </div>
                                </div>
                                """
                            )

                            with gr.Row(visible=False):
                                tabela_prioritarias = gr.Dataframe(visible=False)
                                tabela_disciplinas_metricas = gr.Dataframe(visible=False)
                                home_logged_banner = gr.HTML(visible=False)
                                btn_refresh_dash = gr.Button(visible=False)

        # ======================================================================
        # Conexões de Eventos e Callbacks
        # ======================================================================

        # Pomodoro Hub agora é gerenciado 100% em tempo real no cliente com Web Audio e LocalStorage

        # Eventos de Navegação da Navbar
        def abrir_tela_login():
            return gr.update(visible=False), gr.update(visible=True), gr.update(selected="tab_login"), "", ""

        def abrir_tela_cadastro():
            return gr.update(visible=False), gr.update(visible=True), gr.update(selected="tab_cad"), "", ""

        def voltar_para_landing():
            return gr.update(visible=True), gr.update(visible=False), "", ""

        btn_nav_login.click(fn=abrir_tela_login, outputs=[landing_page_view, auth_page_view, auth_tabs, login_msg, cad_msg])
        btn_nav_cad.click(fn=abrir_tela_cadastro, outputs=[landing_page_view, auth_page_view, auth_tabs, login_msg, cad_msg])
        btn_voltar_home.click(fn=voltar_para_landing, outputs=[landing_page_view, auth_page_view, login_msg, cad_msg])

        def on_login_success(user):
            if not user:
                return (
                    gr.update(), gr.update(),
                    gr.update(), gr.update(), gr.update(),
                    gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update(),
                    gr.update(), gr.update(), gr.update(), gr.update(), gr.update()
                )
            dash_html, dash_df_p, dash_df_d = carregar_dashboard_view(user)
            atv_df = listar_todas_atividades(user)
            disc_df = listar_disciplinas_view(user)
            disc_dd = carregar_disciplinas_dropdown(user)
            cal_html = carregar_calendario_view(user)
            hero_html = gerar_hero_e_recursos_html()
            kanban_html = carregar_kanban_view(user)
            cat_cards_html = gerar_categorias_cards_html(user)
            atv_dd = carregar_atividades_dropdown(user)

            opcoes_filtro = ["Todas"] + (list(disc_dd.choices) if hasattr(disc_dd, 'choices') and disc_dd.choices else ["Todas"])
            kanban_filter_dd = gr.Dropdown(choices=opcoes_filtro, value="Todas")

            return (
                hero_html, dash_df_p,
                dash_html, dash_df_p, dash_df_d,
                atv_df, disc_df, disc_dd, disc_dd, disc_dd, cal_html,
                kanban_html, cat_cards_html, atv_dd, kanban_filter_dd, disc_dd
            )

        btn_login_submit.click(
            fn=login_handler,
            inputs=[login_email, login_senha],
            outputs=[login_msg, user_state, landing_page_view, auth_page_view, app_workspace, user_header_text]
        ).then(
            fn=on_login_success,
            inputs=[user_state],
            outputs=[
                home_logged_banner, tabela_home_prioritarias,
                dash_cards, tabela_prioritarias, tabela_disciplinas_metricas,
                tabela_atividades, tabela_disciplinas, input_disciplina, dash_input_disciplina, cal_input_disciplina, cal_view,
                kanban_view, categorias_cards_view, kanban_select_atv, kanban_filtro_cat, kanban_input_cat
            ]
        )

        btn_cadastro_submit.click(
            fn=cadastro_handler,
            inputs=[cad_nome, cad_email, cad_curso, cad_senha],
            outputs=[cad_msg, user_state, landing_page_view, auth_page_view, app_workspace, user_header_text]
        ).then(
            fn=on_login_success,
            inputs=[user_state],
            outputs=[
                home_logged_banner, tabela_home_prioritarias,
                dash_cards, tabela_prioritarias, tabela_disciplinas_metricas,
                tabela_atividades, tabela_disciplinas, input_disciplina, dash_input_disciplina, cal_input_disciplina, cal_view,
                kanban_view, categorias_cards_view, kanban_select_atv, kanban_filtro_cat, kanban_input_cat
            ]
        )

        btn_logout.click(
            fn=logout_handler,
            outputs=[user_state, landing_page_view, auth_page_view, app_workspace, user_header_text]
        )

        # Navegação da Barra Superior de Visualizações (Estilo ClickUp / Trello)
        btn_view_kanban.click(fn=lambda: gr.update(selected="tab_kanban"), outputs=[workspace_tabs])
        btn_view_tarefas.click(fn=lambda: gr.update(selected="tab_atividades"), outputs=[workspace_tabs])
        btn_view_agenda.click(fn=lambda: gr.update(selected="tab_calendario"), outputs=[workspace_tabs])
        btn_view_dash.click(fn=lambda: gr.update(selected="tab_dash"), outputs=[workspace_tabs])
        btn_view_categorias.click(fn=lambda: gr.update(selected="tab_disciplinas"), outputs=[workspace_tabs])

        # Navegação da Sidebar Lateral GrowSync
        btn_side_kanban.click(fn=lambda: gr.update(selected="tab_kanban"), outputs=[workspace_tabs])
        btn_side_dash.click(fn=lambda: gr.update(selected="tab_dash"), outputs=[workspace_tabs])
        btn_side_agenda.click(fn=lambda: gr.update(selected="tab_calendario"), outputs=[workspace_tabs])
        btn_side_tarefas.click(fn=lambda: gr.update(selected="tab_atividades"), outputs=[workspace_tabs])
        btn_side_disc.click(fn=lambda: gr.update(selected="tab_disciplinas"), outputs=[workspace_tabs])
        btn_side_pomodoro.click(fn=lambda: gr.update(selected="tab_home"), outputs=[workspace_tabs])
        btn_side_swagger.click(fn=lambda: gr.update(selected="tab_swagger"), outputs=[workspace_tabs])

        # Ações e Eventos do Quadro Kanban
        btn_toggle_add_kanban.click(
            fn=lambda v: (not v, gr.update(visible=not v)),
            inputs=[kanban_add_vis],
            outputs=[kanban_add_vis, kanban_add_card]
        )
        btn_toggle_add_cat.click(
            fn=lambda v: (not v, gr.update(visible=not v)),
            inputs=[kanban_cat_vis],
            outputs=[kanban_cat_vis, kanban_cat_card]
        )

        btn_kanban_filtrar.click(
            fn=carregar_kanban_view,
            inputs=[user_state, kanban_filtro_cat, kanban_filtro_prio, kanban_busca],
            outputs=[kanban_view]
        )
        btn_refresh_kanban.click(
            fn=carregar_kanban_view,
            inputs=[user_state, kanban_filtro_cat, kanban_filtro_prio, kanban_busca],
            outputs=[kanban_view]
        )

        def sync_cadastrar_kanban_atv(u, tit, cat, data_e, prio, col, desc):
            msg, _ = cadastrar_nova_atividade(u, tit, cat, data_e, prio, desc, status=col)
            k_view = carregar_kanban_view(u)
            atv_dd = carregar_atividades_dropdown(u)
            atv_df = listar_todas_atividades(u)
            cal_h = carregar_calendario_view(u)
            dash_h, _, _ = carregar_dashboard_view(u)
            cat_dd = carregar_disciplinas_dropdown(u)
            return msg, k_view, atv_dd, atv_df, cal_h, dash_h, cat_dd, cat_dd, cat_dd, cat_dd

        btn_salvar_kanban_atv.click(
            fn=sync_cadastrar_kanban_atv,
            inputs=[user_state, kanban_input_titulo, kanban_input_cat, kanban_input_data, kanban_input_prio, kanban_input_coluna, kanban_input_desc],
            outputs=[kanban_add_msg, kanban_view, kanban_select_atv, tabela_atividades, cal_view, dash_cards, kanban_input_cat, input_disciplina, dash_input_disciplina, cal_input_disciplina]
        )

        def sync_cadastrar_cat_kanban(u, nome, cor_val, desc):
            cor_hex = "#7c3aed"
            if "(" in str(cor_val) and ")" in str(cor_val):
                cor_hex = str(cor_val).split("(")[-1].replace(")", "").strip()
            msg, disc_df, disc_dd = cadastrar_disciplina_handler(u, nome, "Geral", desc, cor=cor_hex)
            cards_h = gerar_categorias_cards_html(u)
            k_view = carregar_kanban_view(u)
            nomes_cats = ["Todas"] + (list(disc_dd.choices) if hasattr(disc_dd, 'choices') and disc_dd.choices else ["Todas"])
            filtro_dd = gr.Dropdown(choices=nomes_cats, value="Todas")
            return msg, cards_h, disc_df, filtro_dd, disc_dd, disc_dd, disc_dd, disc_dd, k_view

        btn_salvar_kanban_cat.click(
            fn=sync_cadastrar_cat_kanban,
            inputs=[user_state, kanban_new_cat_nome, kanban_new_cat_cor, kanban_new_cat_desc],
            outputs=[kanban_cat_msg, categorias_cards_view, tabela_disciplinas, kanban_filtro_cat, kanban_input_cat, input_disciplina, dash_input_disciplina, cal_input_disciplina, kanban_view]
        )

        # Mover afazeres entre colunas no Kanban
        def sync_mover_kanban(u, atv_sel, col_target):
            msg, k_view, atv_dd, atv_df = mover_card_kanban_handler(u, atv_sel, col_target)
            dash_h, _, _ = carregar_dashboard_view(u)
            cal_h = carregar_calendario_view(u)
            return msg, k_view, atv_dd, atv_df, dash_h, cal_h

        btn_move_backlog.click(
            fn=lambda u, atv: sync_mover_kanban(u, atv, "Backlog"),
            inputs=[user_state, kanban_select_atv],
            outputs=[kanban_action_msg, kanban_view, kanban_select_atv, tabela_atividades, dash_cards, cal_view]
        )
        btn_move_afazer.click(
            fn=lambda u, atv: sync_mover_kanban(u, atv, "A Fazer"),
            inputs=[user_state, kanban_select_atv],
            outputs=[kanban_action_msg, kanban_view, kanban_select_atv, tabela_atividades, dash_cards, cal_view]
        )
        btn_move_andamento.click(
            fn=lambda u, atv: sync_mover_kanban(u, atv, "Em Andamento"),
            inputs=[user_state, kanban_select_atv],
            outputs=[kanban_action_msg, kanban_view, kanban_select_atv, tabela_atividades, dash_cards, cal_view]
        )
        btn_move_validacao.click(
            fn=lambda u, atv: sync_mover_kanban(u, atv, "Validação"),
            inputs=[user_state, kanban_select_atv],
            outputs=[kanban_action_msg, kanban_view, kanban_select_atv, tabela_atividades, dash_cards, cal_view]
        )
        btn_move_concluido.click(
            fn=lambda u, atv: sync_mover_kanban(u, atv, "Concluída"),
            inputs=[user_state, kanban_select_atv],
            outputs=[kanban_action_msg, kanban_view, kanban_select_atv, tabela_atividades, dash_cards, cal_view]
        )

        def sync_delete_kanban_atv(u, atv_sel):
            if not atv_sel or atv_sel == "(Nenhuma tarefa)":
                return "Selecione uma tarefa para excluir.", carregar_kanban_view(u), carregar_atividades_dropdown(u), listar_todas_atividades(u), carregar_dashboard_view(u)[0], carregar_calendario_view(u)
            try:
                aid = int(atv_sel.split(" - ")[0].replace("#", "").strip()) if str(atv_sel).startswith("#") else int(str(atv_sel).strip())
            except Exception:
                return "ID inválido.", carregar_kanban_view(u), carregar_atividades_dropdown(u), listar_todas_atividades(u), carregar_dashboard_view(u)[0], carregar_calendario_view(u)
            msg, atv_df = excluir_atividade_handler(u, aid)
            k_view = carregar_kanban_view(u)
            atv_dd = carregar_atividades_dropdown(u)
            dash_h, _, _ = carregar_dashboard_view(u)
            cal_h = carregar_calendario_view(u)
            return msg, k_view, atv_dd, atv_df, dash_h, cal_h

        btn_delete_kanban_atv.click(
            fn=sync_delete_kanban_atv,
            inputs=[user_state, kanban_select_atv],
            outputs=[kanban_action_msg, kanban_view, kanban_select_atv, tabela_atividades, dash_cards, cal_view]
        )

        # Atualização da aba Categorias & Rotina
        def sync_cadastrar_disc_completa(u, nome, cor_val, prof, desc):
            cor_hex = "#7c3aed"
            if "(" in str(cor_val) and ")" in str(cor_val):
                cor_hex = str(cor_val).split("(")[-1].replace(")", "").strip()
            msg, df, dd = cadastrar_disciplina_handler(u, nome, prof, desc, cor=cor_hex)
            cards_h = gerar_categorias_cards_html(u)
            k_view = carregar_kanban_view(u)
            nomes_cats = ["Todas"] + (list(dd.choices) if hasattr(dd, 'choices') and dd.choices else ["Todas"])
            filtro_dd = gr.Dropdown(choices=nomes_cats, value="Todas")
            return msg, df, cards_h, dd, dd, dd, dd, filtro_dd, k_view

        btn_cadastrar_disc.click(
            fn=sync_cadastrar_disc_completa,
            inputs=[user_state, input_disc_nome, input_disc_cor, input_disc_prof, input_disc_desc],
            outputs=[msg_cadastro_disc, tabela_disciplinas, categorias_cards_view, input_disciplina, dash_input_disciplina, cal_input_disciplina, kanban_input_cat, kanban_filtro_cat, kanban_view]
        )

        btn_refresh_disc.click(
            fn=lambda u: (listar_disciplinas_view(u), gerar_categorias_cards_html(u)),
            inputs=[user_state],
            outputs=[tabela_disciplinas, categorias_cards_view]
        )

        def sync_excluir_disc_completa(u, did):
            msg, df, dd = excluir_disciplina_handler(u, did)
            cards_h = gerar_categorias_cards_html(u)
            k_view = carregar_kanban_view(u)
            nomes_cats = ["Todas"] + (list(dd.choices) if hasattr(dd, 'choices') and dd.choices else ["Todas"])
            filtro_dd = gr.Dropdown(choices=nomes_cats, value="Todas")
            return msg, df, cards_h, dd, dd, dd, dd, filtro_dd, k_view

        btn_excluir_disc.click(
            fn=sync_excluir_disc_completa,
            inputs=[user_state, input_id_disc_excluir],
            outputs=[msg_excluir_disc, tabela_disciplinas, categorias_cards_view, input_disciplina, dash_input_disciplina, cal_input_disciplina, kanban_input_cat, kanban_filtro_cat, kanban_view]
        )

        # Ação Adicionar Atividade na Agenda diretamente do Dashboard
        btn_dash_adicionar_agenda.click(
            fn=adicionar_na_agenda_handler,
            inputs=[user_state, dash_input_titulo, dash_input_disciplina, dash_input_data, dash_input_prioridade, dash_input_descricao],
            outputs=[dash_msg_agenda, dash_cards, tabela_prioritarias, tabela_disciplinas_metricas, tabela_atividades, cal_view, dash_input_disciplina, cal_input_disciplina, input_disciplina]
        )

        # Ações na Aba Agenda & Calendário
        def toggle_cal_form_handler(current_vis):
            novo_vis = not current_vis
            btn_txt = "− Ocultar Formulário" if novo_vis else "+ Cadastrar Atividade"
            return novo_vis, gr.update(visible=novo_vis), gr.update(value=btn_txt)

        btn_toggle_cal_form.click(
            fn=toggle_cal_form_handler,
            inputs=[cal_form_visible],
            outputs=[cal_form_visible, cal_form_card, btn_toggle_cal_form]
        )

        btn_salvar_cal_atividade.click(
            fn=adicionar_na_agenda_handler,
            inputs=[user_state, cal_input_titulo, cal_input_disciplina, cal_input_data, cal_input_prioridade, cal_input_descricao],
            outputs=[cal_msg_feedback, dash_cards, tabela_prioritarias, tabela_disciplinas_metricas, tabela_atividades, cal_view, dash_input_disciplina, cal_input_disciplina, input_disciplina]
        )

        # Atualizações manuais
        btn_refresh_home.click(
            fn=lambda u: (gerar_hero_e_recursos_html(), carregar_dashboard_view(u)[1]),
            inputs=[user_state],
            outputs=[home_logged_banner, tabela_home_prioritarias]
        )

        btn_refresh_dash.click(
            fn=carregar_dashboard_view,
            inputs=[user_state],
            outputs=[dash_cards, tabela_prioritarias, tabela_disciplinas_metricas]
        )

        def sync_cadastrar_atv_handler(u, tit, disc, data_e, prio, desc, st, pr, smart, busca):
            msg, _ = cadastrar_nova_atividade(u, tit, disc, data_e, prio, desc)
            df = listar_todas_atividades(u, st, pr, smart, busca)
            cat_dd = carregar_disciplinas_dropdown(u)
            return msg, df, cat_dd, cat_dd, cat_dd

        btn_cadastrar_atv.click(
            fn=sync_cadastrar_atv_handler,
            inputs=[user_state, input_titulo, input_disciplina, input_data, input_prioridade, input_descricao, filtro_status, filtro_prioridade, filtro_inteligente, filtro_busca],
            outputs=[status_cadastro_atv, tabela_atividades, input_disciplina, dash_input_disciplina, cal_input_disciplina]
        )

        # Seleção com 1-Clique na Tabela de Atividades
        tabela_atividades.select(
            fn=on_select_tabela_atividades,
            inputs=[tabela_atividades],
            outputs=[input_id_acao, card_selecao_html]
        )

        # Pesquisa e Filtros Reativos em Tempo Real
        filtro_busca.change(
            fn=listar_todas_atividades,
            inputs=[user_state, filtro_status, filtro_prioridade, filtro_inteligente, filtro_busca],
            outputs=[tabela_atividades]
        )

        filtro_status.change(
            fn=listar_todas_atividades,
            inputs=[user_state, filtro_status, filtro_prioridade, filtro_inteligente, filtro_busca],
            outputs=[tabela_atividades]
        )

        filtro_prioridade.change(
            fn=listar_todas_atividades,
            inputs=[user_state, filtro_status, filtro_prioridade, filtro_inteligente, filtro_busca],
            outputs=[tabela_atividades]
        )

        filtro_inteligente.change(
            fn=listar_todas_atividades,
            inputs=[user_state, filtro_status, filtro_prioridade, filtro_inteligente, filtro_busca],
            outputs=[tabela_atividades]
        )

        btn_filtrar.click(
            fn=listar_todas_atividades,
            inputs=[user_state, filtro_status, filtro_prioridade, filtro_inteligente, filtro_busca],
            outputs=[tabela_atividades]
        )

        # Ações Rápidas de Atividades
        btn_toggle_status.click(
            fn=alternar_conclusao_atividade,
            inputs=[user_state, input_id_acao, filtro_status, filtro_prioridade, filtro_inteligente, filtro_busca],
            outputs=[msg_acao, tabela_atividades]
        )

        btn_focar_tarefa.click(
            fn=focar_no_pomodoro_handler,
            inputs=[user_state, input_id_acao, tabela_atividades],
            outputs=[msg_acao, card_selecao_html]
        )

        btn_excluir_atv.click(
            fn=excluir_atividade_handler,
            inputs=[user_state, input_id_acao, filtro_status, filtro_prioridade, filtro_inteligente, filtro_busca],
            outputs=[msg_acao, tabela_atividades]
        )

        btn_refresh_cal.click(
            fn=carregar_calendario_view,
            inputs=[user_state],
            outputs=[cal_view]
        )

    return demo


if __name__ == "__main__":
    app_gradio = criar_interface()
    port = int(os.environ.get("GRADIO_PORT", 7860))
    print(f"🚀 Iniciando Interface Gradio em http://127.0.0.1:{port}")
    app_gradio.launch(
        server_name="127.0.0.1",
        server_port=port,
        inbrowser=False,
        css=custom_theme_css,
        favicon_path=FAVICON_PATH,
        head=HEAD_HTML
    )
