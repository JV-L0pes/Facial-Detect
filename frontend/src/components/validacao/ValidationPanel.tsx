'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { validationApi } from '@/lib/api/validation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Shield, User, Activity, CheckCircle, XCircle, Clock } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import type { ValidationResponse } from '@/types';

interface ValidationStatus {
  status: 'waiting' | 'processing' | 'success' | 'error';
  user?: string;
  confidence?: number;
  liveness?: boolean;
  passageCount?: number;
  message?: string;
}

interface ValidationPanelProps {
  videoRef: React.RefObject<HTMLVideoElement>;
  canvasRef: React.RefObject<HTMLCanvasElement>;
  webcam: any;
}

export function ValidationPanel({ videoRef, canvasRef, webcam }: ValidationPanelProps) {
  // Canvas separado para captura que não interfere no vídeo principal
  const captureCanvasRef = useRef<HTMLCanvasElement | null>(null);
  
  // Criar canvas separado para captura
  useEffect(() => {
    if (!captureCanvasRef.current) {
      captureCanvasRef.current = document.createElement('canvas');
    }
  }, []);

  // Função de captura que NÃO interfere no stream principal
  const captureFrame = useCallback((): string | null => {
    if (!videoRef.current || !captureCanvasRef.current) return null;

    const video = videoRef.current;
    const captureCanvas = captureCanvasRef.current;
    const ctx = captureCanvas.getContext('2d');

    if (!ctx) return null;

    // Verificar se o vídeo está pronto e reproduzindo
    if (video.videoWidth === 0 || video.videoHeight === 0 || video.paused || video.ended) {
      return null;
    }

    // Usar dimensões equilibradas para captura eficiente
    const captureWidth = 480;
    const captureHeight = 360;
    
    captureCanvas.width = captureWidth;
    captureCanvas.height = captureHeight;

    // Captura com qualidade adequada para reconhecimento
    ctx.drawImage(video, 0, 0, captureWidth, captureHeight);
    return captureCanvas.toDataURL('image/jpeg', 0.8); // Qualidade melhor para reconhecimento
  }, [videoRef]);
  
  const [validationStatus, setValidationStatus] = useState<ValidationStatus>({
    status: 'waiting',
  });
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const isProcessingRef = useRef(false);
  const lastValidationRef = useRef<number>(0);

  // Função de validação ultra-otimizada para não interferir na câmera
  const validateContinuously = useCallback(() => {
    // Evitar múltiplas validações simultâneas
    if (isProcessingRef.current) {
      return; // Silencioso - não logar para não poluir console
    }

    // Throttling equilibrado: não validar mais de uma vez a cada 3 segundos
    const now = Date.now();
    if (now - lastValidationRef.current < 3000) {
      return;
    }

    // Verificar se o vídeo está realmente pronto antes de capturar
    if (!videoRef.current || videoRef.current.paused || videoRef.current.ended) {
      return;
    }

    // Usar setTimeout para garantir que não interfira no ciclo de renderização do vídeo
    setTimeout(() => {
      const imageData = captureFrame();
      if (!imageData) {
        console.log('Nenhuma imagem capturada');
        return;
      }

      console.log('Iniciando validação...');
      isProcessingRef.current = true;
      lastValidationRef.current = now;

      // Usar fetch diretamente para melhor controle
      fetch('/api/validate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ image: imageData }),
      })
        .then(response => response.json())
        .then(response => {
          if (response.success) {
            setValidationStatus({
              status: response.access_granted ? 'success' : 'error',
              user: response.user_name || 'Desconhecido',
              confidence: response.confidence,
              liveness: response.liveness_passed,
              passageCount: response.passage_count,
              message: response.message,
            });
            
            if (response.access_granted) {
              setTimeout(() => {
                setValidationStatus(prev => ({
                  ...prev,
                  status: 'waiting',
                  message: 'Detecção contínua ativa'
                }));
              }, 3000);
            }
          } else {
            setValidationStatus({
              status: 'error',
              message: response.message || 'Erro na validação',
            });
          }
        })
        .catch(error => {
          console.error('Validation error:', error);
          setValidationStatus({
            status: 'error',
            message: 'Erro de conexão',
          });
        })
        .finally(() => {
          isProcessingRef.current = false;
        });
    }, 50); // Delay mínimo para não interferir na renderização
  }, [captureFrame, videoRef]);

  // Controlar intervalo baseado no estado da webcam
  useEffect(() => {
    if (webcam.isActive) {
      // Iniciar detecção contínua - intervalo equilibrado para fluidez e reconhecimento
      intervalRef.current = setInterval(validateContinuously, 5000); // Reduzir para 5 segundos
    } else {
      // Parar detecção
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      // Resetar flags
      isProcessingRef.current = false;
      lastValidationRef.current = 0;
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      isProcessingRef.current = false;
    };
  }, [webcam.isActive, validateContinuously]);

  const getStatusIcon = () => {
    switch (validationStatus.status) {
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'error':
        return <XCircle className="h-5 w-5 text-red-600" />;
      case 'processing':
        return <Clock className="h-5 w-5 text-yellow-600 animate-spin" />;
      default:
        return <Shield className="h-5 w-5 text-muted-foreground" />;
    }
  };

  const getStatusColor = () => {
    switch (validationStatus.status) {
      case 'success':
        return 'border-green-200 bg-green-50';
      case 'error':
        return 'border-red-200 bg-red-50';
      case 'processing':
        return 'border-yellow-200 bg-yellow-50';
      default:
        return 'border-muted-foreground/25';
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center gap-2">
          <Shield className="h-5 w-5" />
          <CardTitle>Status da Validação</CardTitle>
        </div>
        <CardDescription>
          Informações em tempo real sobre o reconhecimento facial
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Status Principal */}
        <div className={`p-4 rounded-lg border ${getStatusColor()}`}>
          <div className="flex items-center gap-2 mb-2">
            {getStatusIcon()}
            <span className="font-medium">
              {validationStatus.status === 'waiting' && 'Aguardando'}
              {validationStatus.status === 'processing' && 'Processando...'}
              {validationStatus.status === 'success' && 'Acesso Liberado'}
              {validationStatus.status === 'error' && 'Acesso Negado'}
            </span>
          </div>
          {validationStatus.message && (
            <p className="text-sm text-muted-foreground">
              {validationStatus.message}
            </p>
          )}
        </div>

        {/* Informações do Usuário */}
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium">Usuário</span>
            <Badge variant="outline">
              {validationStatus.user || 'Desconhecido'}
            </Badge>
          </div>

          {/* Contador de Passagens */}
          <AnimatePresence>
            {validationStatus.passageCount !== undefined && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="flex justify-between items-center"
              >
                <span className="text-sm font-medium">Passagens</span>
                <Badge variant="default" className="bg-green-600">
                  {validationStatus.passageCount}
                </Badge>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Confiança */}
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">Confiança</span>
              <span className="text-sm font-mono">
                {validationStatus.confidence 
                  ? `${(validationStatus.confidence * 100).toFixed(1)}%`
                  : '0%'
                }
              </span>
            </div>
            <Progress 
              value={validationStatus.confidence ? validationStatus.confidence * 100 : 0}
              className="h-2"
            />
          </div>

          {/* Liveness */}
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium">Liveness</span>
            <Badge 
              variant={validationStatus.liveness ? 'default' : 'destructive'}
              className={validationStatus.liveness ? 'bg-green-600' : ''}
            >
              {validationStatus.liveness ? 'Aprovado' : 'Em análise'}
            </Badge>
          </div>
        </div>

        {/* Dicas */}
        <div className="p-4 bg-muted/50 rounded-lg">
          <div className="flex items-start gap-2">
            <Activity className="h-4 w-4 text-muted-foreground mt-0.5" />
            <div className="text-sm text-muted-foreground">
              <p className="font-medium mb-1">Dicas para melhor reconhecimento:</p>
              <ul className="space-y-1 text-xs">
                <li>• Fique de frente para a câmera</li>
                <li>• Mantenha boa iluminação</li>
                <li>• Movimente-se levemente para liveness</li>
                <li>• Mantenha o rosto centralizado</li>
              </ul>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
