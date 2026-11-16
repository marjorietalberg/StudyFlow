import os
import sys
import time
import subprocess
import threading

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")


def start_backend():
    print("=================================================================")
    print("1️⃣ Iniciando Backend FastAPI (Porta 8000)...")
    print("=================================================================")
    backend_main = os.path.join(BACKEND_DIR, "main.py")
    subprocess.run([sys.executable, backend_main], cwd=BACKEND_DIR)


def start_frontend():
    print("=================================================================")
    print("2️⃣ Aguardando backend e iniciando Frontend Flet (Porta 8550)...")
    print("=================================================================")
    time.sleep(2)
    frontend_main = os.path.join(FRONTEND_DIR, "main.py")
    subprocess.run([sys.executable, frontend_main], cwd=FRONTEND_DIR)


if __name__ == "__main__":
    print("\n" + "="*65)
    print("✨ DAYFLOW — GERENCIADOR INTELIGENTE DE ATIVIDADES ✨")
    print("=================================================================")
    print("🌐 Documentação Swagger: http://127.0.0.1:8000/docs")
    print("🎨 Interface Flet Web:   http://127.0.0.1:8550")
    print("=================================================================\n")

    t_backend = threading.Thread(target=start_backend, daemon=True)
    t_backend.start()

    time.sleep(1.5)
    start_frontend()
