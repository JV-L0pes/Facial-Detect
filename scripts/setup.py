#!/usr/bin/env python3
"""
Script de inicialização do Sistema de Reconhecimento Facial
Verifica dependências e inicializa o sistema
"""

import sys
import subprocess
import os
import venv
from pathlib import Path

def check_python_version():
    """Verifica versão do Python"""
    if sys.version_info < (3, 8):
        print("ERRO: Python 3.8+ e necessario")
        print(f"Versao atual: {sys.version}")
        return False
    print(f"OK: Python {sys.version.split()[0]}")
    return True

def create_virtual_environment():
    """Cria ambiente virtual"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("OK: Ambiente virtual ja existe")
        return True
    
    print("Criando ambiente virtual...")
    try:
        venv.create(venv_path, with_pip=True)
        print("OK: Ambiente virtual criado")
        return True
    except Exception as e:
        print(f"ERRO: Falha ao criar ambiente virtual: {e}")
        return False

def get_python_executable():
    """Retorna o executável Python do ambiente virtual"""
    if os.name == 'nt':  # Windows
        return Path("venv/Scripts/python.exe")
    else:  # Linux/Mac
        return Path("venv/bin/python")

def install_dependencies():
    """Instala dependências no ambiente virtual"""
    python_exe = get_python_executable()
    
    if not python_exe.exists():
        print("ERRO: Ambiente virtual nao encontrado")
        return False
    
    print("Instalando dependencias...")
    try:
        subprocess.check_call([str(python_exe), '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("OK: Dependencias instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERRO: Falha ao instalar dependencias: {e}")
        return False

def check_cuda():
    """Verifica disponibilidade do CUDA"""
    python_exe = get_python_executable()
    
    try:
        result = subprocess.run([str(python_exe), '-c', 'import torch; print(torch.cuda.is_available())'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            cuda_available = result.stdout.strip() == 'True'
            if cuda_available:
                # Obter nome da GPU
                gpu_result = subprocess.run([str(python_exe), '-c', 'import torch; print(torch.cuda.get_device_name(0))'], 
                                          capture_output=True, text=True)
                if gpu_result.returncode == 0:
                    gpu_name = gpu_result.stdout.strip()
                    print(f"OK: CUDA disponivel: {gpu_name}")
                else:
                    print("OK: CUDA disponivel")
                return True
            else:
                print("AVISO: CUDA nao disponivel, usando CPU")
                return False
        else:
            print("AVISO: PyTorch nao instalado")
            return False
    except Exception as e:
        print(f"AVISO: Erro ao verificar CUDA: {e}")
        return False

def create_directories():
    """Cria diretórios necessários"""
    directories = ['data', 'data/logs', 'data/faiss_index', 'models', 'frontend/css', 'frontend/js']
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"OK: Diretorio {directory} criado/verificado")

def initialize_database():
    """Inicializa banco de dados"""
    python_exe = get_python_executable()
    
    try:
        result = subprocess.run([str(python_exe), '-c', 
                               'from backend.app.database import init_database; print(init_database())'], 
                              capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip() == 'True':
            print("OK: Banco de dados inicializado")
            return True
        else:
            print("ERRO: Erro ao inicializar banco de dados")
            return False
    except Exception as e:
        print(f"ERRO: Erro ao inicializar banco: {e}")
        return False

def test_face_recognition():
    """Testa sistema de reconhecimento facial"""
    python_exe = get_python_executable()
    
    try:
        result = subprocess.run([str(python_exe), '-c', 
                               'from backend.app.face_recognition import face_recognition; '
                               'stats = face_recognition.get_stats(); '
                               'print(f"Device: {stats[\"device\"]}"); '
                               'print(f"Threshold: {stats[\"threshold\"]}")'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("OK: Sistema de reconhecimento facial")
            print(result.stdout.strip())
            return True
        else:
            print(f"AVISO: Sistema de reconhecimento com problemas: {result.stderr}")
            return False
    except Exception as e:
        print(f"AVISO: Erro no sistema de reconhecimento: {e}")
        return False

def main():
    """Função principal"""
    print("Inicializando Sistema de Reconhecimento Facial")
    print("=" * 50)
    
    # Verificações básicas
    if not check_python_version():
        sys.exit(1)
    
    # Criar ambiente virtual
    if not create_virtual_environment():
        sys.exit(1)
    
    # Instalar dependências
    if not install_dependencies():
        sys.exit(1)
    
    # Verificar CUDA
    check_cuda()
    
    # Configuração
    print("\nConfigurando diretorios...")
    create_directories()
    
    print("\nInicializando banco de dados...")
    if not initialize_database():
        sys.exit(1)
    
    print("\nTestando sistema de reconhecimento...")
    if not test_face_recognition():
        print("AVISO: Sistema de reconhecimento com problemas, mas continuando...")
    
    print("\nOK: Sistema inicializado com sucesso!")
    print("\nPara ativar o ambiente virtual:")
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\activate")
    else:  # Linux/Mac
        print("   source venv/bin/activate")
    print("\nPara iniciar o servidor:")
    print("   python backend/app/main.py")
    print("\nAcesse: http://localhost:8000")
    print("\nConsulte o README.md para mais informacoes")

if __name__ == "__main__":
    main()
