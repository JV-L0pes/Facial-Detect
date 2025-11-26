#!/usr/bin/env python3
"""
Script para verificar configuração GPU ONLY do sistema de reconhecimento facial
"""

import sys
import os
import torch
import numpy as np
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

def check_gpu_availability():
    """Verifica disponibilidade e configuração da GPU"""
    print("Verificando configuração GPU...")
    print("=" * 50)
    
    # Verificar CUDA
    cuda_available = torch.cuda.is_available()
    print(f"CUDA disponível: {cuda_available}")
    
    if cuda_available:
        print(f"Versão CUDA: {torch.version.cuda}")
        print(f"Número de GPUs: {torch.cuda.device_count()}")
        
        for i in range(torch.cuda.device_count()):
            gpu_name = torch.cuda.get_device_name(i)
            gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
            print(f"GPU {i}: {gpu_name} ({gpu_memory:.1f} GB)")
    else:
        print("CUDA não disponível!")
        return False
    
    return True

def test_insightface_gpu():
    """Testa InsightFace com 100% GPU ONLY"""
    print("\nTestando InsightFace 100% GPU ONLY...")
    print("=" * 50)
    
    try:
        import insightface
        from insightface.app import FaceAnalysis
        
        # Configurar InsightFace para 100% GPU ONLY
        print("Configurando InsightFace para 100% GPU ONLY...")
        face_app = FaceAnalysis(
            name='buffalo_l',
            providers=['CUDAExecutionProvider']  # 100% GPU, ZERO fallback
        )
        
        # Preparar modelo
        face_app.prepare(ctx_id=0, det_size=(1920, 1920))
        
        # Verificar se realmente está usando GPU
        providers = face_app.models['detection'].session.get_providers()
        print(f"Providers ativos: {providers}")
        
        if 'CUDAExecutionProvider' not in providers:
            print("ERRO: InsightFace não está usando GPU!")
            return False
        
        print("InsightFace configurado com 100% GPU ONLY!")
        
        # Testar com imagem aleatória
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        print("Testando detecção de faces...")
        faces = face_app.get(test_image)
        print(f"Detecção funcionando! Faces detectadas: {len(faces)}")
        
        return True
        
    except Exception as e:
        print(f"Erro no teste InsightFace: {e}")
        return False

def test_onnxruntime_gpu():
    """Testa ONNX Runtime com GPU"""
    print("\nTestando ONNX Runtime GPU...")
    print("=" * 50)
    
    try:
        import onnxruntime as ort
        
        # Verificar providers disponíveis
        available_providers = ort.get_available_providers()
        print(f"Providers disponíveis: {available_providers}")
        
        # Verificar se CUDA está disponível
        cuda_available = 'CUDAExecutionProvider' in available_providers
        print(f"CUDA Provider disponível: {cuda_available}")
        
        if cuda_available:
            print("ONNX Runtime com CUDA funcionando!")
        else:
            print("CUDA Provider não disponível no ONNX Runtime")
            
        return cuda_available
        
    except Exception as e:
        print(f"Erro no teste ONNX Runtime: {e}")
        return False

def main():
    """Função principal de verificação"""
    print("100% GPU ONLY - Sistema de Reconhecimento Facial")
    print("=" * 60)
    
    # Verificar GPU
    gpu_ok = check_gpu_availability()
    
    if not gpu_ok:
        print("\nGPU não disponível! Sistema requer GPU.")
        print("   Para usar CPU, altere DEVICE='cpu' em config.py")
        return False
    
    # Testar ONNX Runtime
    onnx_ok = test_onnxruntime_gpu()
    
    # Testar InsightFace
    insightface_ok = test_insightface_gpu()
    
    # Resumo
    print("\nRESUMO DA VERIFICAÇÃO:")
    print("=" * 60)
    print(f"GPU disponível: {gpu_ok}")
    print(f"ONNX Runtime CUDA: {onnx_ok}")
    print(f"InsightFace GPU: {insightface_ok}")
    
    if gpu_ok and onnx_ok and insightface_ok:
        print("\nSistema GPU ONLY configurado corretamente!")
        print("   Todos os componentes estão funcionando com GPU.")
        return True
    else:
        print("\nProblemas detectados na configuração GPU.")
        print("   Verifique a instalação do CUDA e ONNX Runtime.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
