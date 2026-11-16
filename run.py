"""
Script unificado para iniciar o ecossistema StudyFlow (API Flask + Frontend Gradio)
com apenas um comando: python run.py
"""

import sys
import os

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import time
import threading
import argparse
import webbrowser
import requests
from app import create_app
from frontend.interface import criar_interface, custom_theme_css, FAVICON_PATH, HEAD_HTML, custom_theme

def rodar_flask(port=5000):
    app = create_app()
    # Desativa reloader ao rodar em thread para evitar spawning duplicado
    app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)

def rodar_gradio(port=7860):
    demo = criar_interface()
    # Tenta na porta preferencial e busca próximas se estiver em uso
    for p in range(port, port + 15):
        try:
            print(f"   🎨 Iniciando interface Gradio em http://127.0.0.1:{p}...")
            demo.launch(
                server_name='127.0.0.1',
                server_port=p,
                inbrowser=False,
                quiet=False,
                css=custom_theme_css,
                favicon_path=FAVICON_PATH,
                head=HEAD_HTML,
                theme=custom_theme
            )
            break
        except OSError as e:
            if "empty port" in str(e).lower() or "address already in use" in str(e).lower():
                print(f"   ⚠️ Porta {p} ocupada, tentando {p+1}...")
                continue
            raise e

def main():
    parser = argparse.ArgumentParser(description="StudyFlow - Gestor Acadêmico")
    parser.add_argument('--api-only', action='store_true', help='Executa apenas o servidor Flask API')
    parser.add_argument('--frontend-only', action='store_true', help='Executa apenas a interface Gradio')
    parser.add_argument('--api-port', type=int, default=5000, help='Porta da API Flask (padrão: 5000)')
    parser.add_argument('--gradio-port', type=int, default=7860, help='Porta do Gradio (padrão: 7860)')
    args = parser.parse_args()

    print("=" * 65)
    print("🎓 StudyFlow - Sistema de Gestão Acadêmica & Produtividade")
    print("=" * 65)

    if args.api_only:
        print(f"🚀 Rodando exclusivamente a API Flask em http://127.0.0.1:{args.api_port}")
        print(f"📚 Documentação Swagger: http://127.0.0.1:{args.api_port}/apidocs/")
        rodar_flask(port=args.api_port)
        return

    if args.frontend_only:
        print(f"🎨 Rodando exclusivamente o Frontend Gradio em http://127.0.0.1:{args.gradio_port}")
        rodar_gradio(port=args.gradio_port)
        return

    # Inicia Flask em thread secundária
    print(f"1️⃣ Iniciando Servidor Backend (Flask + Swagger) na porta {args.api_port}...")
    api_thread = threading.Thread(target=rodar_flask, kwargs={'port': args.api_port}, daemon=True)
    api_thread.start()

    # Aguarda Flask subir
    for _ in range(10):
        try:
            r = requests.get(f"http://127.0.0.1:{args.api_port}/", timeout=1)
            if r.status_code == 200:
                print("   ✅ Backend Flask operacional!")
                break
        except Exception:
            time.sleep(0.5)

    print(f"\n2️⃣ Links de Acesso:")
    print(f"   🌐 Frontend Gradio:      http://127.0.0.1:{args.gradio_port}")
    print(f"   📚 Swagger Documentation: http://127.0.0.1:{args.api_port}/apidocs/")
    print(f"   ⚙️ API REST Root:        http://127.0.0.1:{args.api_port}/api/dashboard")
    print("=" * 65)
    print("Pressione Ctrl+C para encerrar o sistema.\n")

    # Inicia Gradio na thread principal
    rodar_gradio(port=args.gradio_port)

if __name__ == '__main__':
    main()
