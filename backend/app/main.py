from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional
import cv2
import numpy as np
import base64
import io
from PIL import Image
import json
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Imports locais
from backend.app.database import get_db, init_database
from backend.app.models import User, AccessLog
from backend.app.face_recognition import face_recognition
from backend.app.liveness_detection import advanced_liveness_detector
from backend.app.encryption import encryption_manager
from config import API_TITLE, API_VERSION, MAX_FILE_SIZE, ALLOWED_EXTENSIONS

# Inicializar FastAPI
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description="Sistema de Reconhecimento Facial para Controle de Acesso"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar arquivos estáticos
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Inicializar banco de dados
init_database()

@app.get("/", response_class=HTMLResponse)
async def root():
    """Página principal"""
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/cadastro", response_class=HTMLResponse)
async def cadastro_page():
    """Página de cadastro"""
    with open("frontend/cadastro.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/validacao", response_class=HTMLResponse)
async def validacao_page():
    """Página de validação"""
    with open("frontend/validacao.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/admin", response_class=HTMLResponse)
async def admin_page():
    """Página administrativa"""
    with open("frontend/admin.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.post("/api/register")
async def register_user(
    name: str = Form(...),
    email: str = Form(...),
    photo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Cadastra novo usuário"""
    try:
        # Validar arquivo
        if not photo.filename:
            raise HTTPException(status_code=400, detail="Arquivo não fornecido")
        
        # Verificar extensão
        file_ext = "." + photo.filename.split(".")[-1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Formato de arquivo não suportado")
        
        # Verificar tamanho
        content = await photo.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="Arquivo muito grande")
        
        # Converter para imagem OpenCV
        image = Image.open(io.BytesIO(content))
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Extrair embedding
        embedding = face_recognition.extract_embedding(image_cv)
        if embedding is None:
            raise HTTPException(status_code=400, detail="Nenhuma face detectada na imagem")
        
        # Verificar se email já existe
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email já cadastrado")
        
        # Criptografar embedding
        encrypted_embedding = encryption_manager.encrypt_embedding(embedding)
        
        # Criar usuário no banco
        user = User(
            name=name,
            email=email,
            embedding_hash=encrypted_embedding,
            faiss_id=0  # Será atualizado após adicionar ao FAISS
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Adicionar embedding ao índice FAISS
        faiss_id = face_recognition.add_user_embedding(embedding, user.id)
        
        # Atualizar faiss_id no banco
        user.faiss_id = faiss_id
        db.commit()
        
        return {
            "success": True,
            "message": "Usuário cadastrado com sucesso!",
            "user_id": user.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.post("/api/validate")
async def validate_face(
    request: Request,
    db: Session = Depends(get_db)
):
    """Valida face em tempo real"""
    try:
        # Obter dados da requisição
        data = await request.json()
        image_data = data.get("image")
        
        if not image_data:
            raise HTTPException(status_code=400, detail="Imagem não fornecida")
        
        # Decodificar imagem base64
        image_bytes = base64.b64decode(image_data.split(",")[1])
        image = Image.open(io.BytesIO(image_bytes))
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Detectar faces
        faces = face_recognition.detect_faces(image_cv)
        
        if not faces:
            # Log tentativa sem face detectada
            log = AccessLog(
                access_granted=False,
                liveness_passed=False,
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent"),
                error_message="Nenhuma face detectada"
            )
            db.add(log)
            db.commit()
            
            return {
                "success": False,
                "message": "Nenhuma face detectada",
                "access_granted": False,
                "liveness_passed": False,
                "confidence": 0.0,
                "user_id": None
            }
        
        # Pegar melhor face
        best_face = max(faces, key=lambda x: x['det_score'])
        embedding = best_face['embedding']
        bbox = best_face['bbox']
        
        # Verificar liveness (incluindo landmarks se disponíveis)
        landmarks = best_face.get('landmarks')
        liveness_passed = advanced_liveness_detector.add_frame(image_cv, bbox, landmarks)
        
        # Reconhecer face
        user_id, distance = face_recognition.recognize_face(embedding)
        
        # Determinar se acesso foi concedido
        access_granted = user_id is not None and liveness_passed
        
        # Log da tentativa
        log = AccessLog(
            user_id=user_id,
            confidence=1.0 - distance if user_id else None,
            access_granted=access_granted,
            liveness_passed=liveness_passed,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        db.add(log)
        db.commit()
        
        # Resposta - converter tipos NumPy para Python nativos
        response = {
            "success": True,
            "access_granted": bool(access_granted),
            "liveness_passed": bool(liveness_passed),
            "confidence": float(1.0 - distance) if user_id else 0.0,
            "user_id": int(user_id) if user_id else None
        }
        
        if access_granted:
            user = db.query(User).filter(User.id == user_id).first()
            response["message"] = f"Acesso liberado para {user.name}!"
        else:
            if not liveness_passed:
                response["message"] = "Falha na verificação de liveness"
            else:
                response["message"] = "Usuário não reconhecido"
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/api/users")
async def get_users(db: Session = Depends(get_db)):
    """Lista todos os usuários"""
    try:
        users = db.query(User).filter(User.is_active == True).all()
        
        return {
            "success": True,
            "users": [
                {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "created_at": user.created_at.isoformat()
                }
                for user in users
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/api/logs")
async def get_logs(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Lista logs de acesso"""
    try:
        logs = db.query(AccessLog).order_by(AccessLog.timestamp.desc()).limit(limit).all()
        
        return {
            "success": True,
            "logs": [
                {
                    "id": log.id,
                    "user_id": log.user_id,
                    "confidence": log.confidence,
                    "access_granted": log.access_granted,
                    "liveness_passed": log.liveness_passed,
                    "timestamp": log.timestamp.isoformat(),
                    "ip_address": log.ip_address,
                    "error_message": log.error_message
                }
                for log in logs
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Retorna estatísticas do sistema"""
    try:
        # Estatísticas do banco
        total_users = db.query(User).filter(User.is_active == True).count()
        total_logs = db.query(AccessLog).count()
        successful_access = db.query(AccessLog).filter(AccessLog.access_granted == True).count()
        
        # Estatísticas do sistema de reconhecimento
        face_stats = face_recognition.get_stats()
        
        return {
            "success": True,
            "stats": {
                "total_users": total_users,
                "total_logs": total_logs,
                "successful_access": successful_access,
                "success_rate": (successful_access / total_logs * 100) if total_logs > 0 else 0,
                "face_recognition": face_stats
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.delete("/api/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Remove usuário"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        # Remover do índice FAISS
        face_recognition.remove_user_embedding(user.faiss_id)
        
        # Marcar como inativo no banco
        user.is_active = False
        db.commit()
        
        return {
            "success": True,
            "message": "Usuário removido com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.delete("/api/users")
async def delete_all_users(db: Session = Depends(get_db)):
    """Remove todos os usuários"""
    try:
        # Obter todos os usuários ativos
        users = db.query(User).filter(User.is_active == True).all()
        
        if not users:
            return {
                "success": True,
                "message": "Nenhum usuário encontrado",
                "deleted_count": 0
            }
        
        # Remover todos do índice FAISS
        for user in users:
            if user.faiss_id > 0:
                face_recognition.remove_user_embedding(user.faiss_id)
        
        # Marcar todos como inativos
        for user in users:
            user.is_active = False
        
        db.commit()
        
        return {
            "success": True,
            "message": f"{len(users)} usuários removidos com sucesso",
            "deleted_count": len(users)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.delete("/api/logs/clear")
async def clear_logs(db: Session = Depends(get_db)):
    """Limpa todos os logs de acesso"""
    try:
        # Contar logs antes da limpeza
        logs_count = db.query(AccessLog).count()
        
        if logs_count == 0:
            return {
                "success": True,
                "message": "Nenhum log encontrado",
                "deleted_logs": 0
            }
        
        # Limpar logs
        db.query(AccessLog).delete()
        db.commit()
        
        return {
            "success": True,
            "message": f"{logs_count} logs removidos com sucesso",
            "deleted_logs": logs_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.delete("/api/database/clear")
async def clear_database(db: Session = Depends(get_db)):
    """Limpa completamente o banco de dados"""
    try:
        # Contar registros antes da limpeza
        users_count = db.query(User).count()
        logs_count = db.query(AccessLog).count()
        
        # Limpar tabelas
        db.query(AccessLog).delete()
        db.query(User).delete()
        db.commit()
        
        # Limpar índice FAISS
        face_recognition.clear_index()
        
        return {
            "success": True,
            "message": "Banco de dados limpo com sucesso",
            "deleted_users": users_count,
            "deleted_logs": logs_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    from config import API_HOST, API_PORT
    
    print(f"Iniciando servidor em http://{API_HOST}:{API_PORT}")
    uvicorn.run(app, host=API_HOST, port=API_PORT)
