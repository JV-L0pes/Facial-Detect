#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para verificar se o reconhecimento facial está funcionando
"""

import sys
import os
# Adicionar o diretório raiz do projeto ao path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.face_recognition import face_recognition
from app.database import get_db
from app.models import User
import cv2
import numpy as np
from PIL import Image
import base64
import io

def test_face_recognition():
    """Testa o sistema de reconhecimento facial"""
    print("Testando sistema de reconhecimento facial...")
    
    try:
        # Verificar se há usuários cadastrados
        db = next(get_db())
        users = db.query(User).all()
        print(f"Usuarios cadastrados: {len(users)}")
        
        if len(users) == 0:
            print("ERRO: Nenhum usuario cadastrado! Cadastre um usuario primeiro.")
            return False
        
        # Verificar estatísticas do sistema
        stats = face_recognition.get_stats()
        print(f"Estatisticas do sistema:")
        print(f"   - Total de embeddings: {stats['total_embeddings']}")
        print(f"   - Usuarios registrados: {stats['registered_users']}")
        print(f"   - Dispositivo: {stats['device']}")
        print(f"   - Threshold: {stats['threshold']}")
        
        if stats['total_embeddings'] == 0:
            print("ERRO: Nenhum embedding encontrado! O sistema nao foi inicializado corretamente.")
            return False
        
        print("OK: Sistema de reconhecimento facial esta funcionando!")
        return True
        
    except Exception as e:
        print(f"ERRO ao testar reconhecimento facial: {e}")
        return False

def test_api_endpoint():
    """Testa o endpoint da API"""
    print("\nTestando endpoint da API...")
    
    try:
        import requests
        
        # Testar endpoint raiz
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("OK: Endpoint raiz funcionando")
        else:
            print(f"ERRO: Endpoint raiz retornou status {response.status_code}")
            return False
        
        # Testar endpoint de validação com imagem de teste
        test_image_data = create_test_image()
        
        payload = {
            "image": test_image_data
        }
        
        response = requests.post(
            "http://localhost:8000/api/validate",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("OK: Endpoint de validacao funcionando")
            print(f"   - Sucesso: {result.get('success', False)}")
            print(f"   - Mensagem: {result.get('message', 'N/A')}")
            return True
        else:
            print(f"ERRO: Endpoint de validacao retornou status {response.status_code}")
            print(f"   - Resposta: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("ERRO: Nao foi possivel conectar a API. Verifique se o backend esta rodando.")
        return False
    except Exception as e:
        print(f"ERRO ao testar API: {e}")
        return False

def create_test_image():
    """Cria uma imagem de teste simples"""
    # Criar uma imagem simples de teste (640x480, fundo cinza)
    img = np.ones((480, 640, 3), dtype=np.uint8) * 128  # Cinza médio
    
    # Adicionar um retângulo para simular uma face
    cv2.rectangle(img, (200, 150), (440, 350), (255, 255, 255), -1)
    cv2.rectangle(img, (200, 150), (440, 350), (0, 0, 0), 2)
    
    # Converter para PIL Image
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    
    # Converter para base64
    buffer = io.BytesIO()
    pil_img.save(buffer, format='JPEG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/jpeg;base64,{img_str}"

if __name__ == "__main__":
    print("Iniciando testes do sistema de reconhecimento facial...\n")
    
    # Testar reconhecimento facial
    face_recognition_ok = test_face_recognition()
    
    # Testar API
    api_ok = test_api_endpoint()
    
    print(f"\nResumo dos testes:")
    print(f"   - Reconhecimento facial: {'OK' if face_recognition_ok else 'FALHOU'}")
    print(f"   - API: {'OK' if api_ok else 'FALHOU'}")
    
    if face_recognition_ok and api_ok:
        print("\nTodos os testes passaram! O sistema esta funcionando corretamente.")
    else:
        print("\nAlguns testes falharam. Verifique os problemas acima.")
