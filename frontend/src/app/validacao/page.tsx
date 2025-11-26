'use client';

import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { WebcamCapture } from '@/components/validacao/WebcamCapture';
import { ValidationPanel } from '@/components/validacao/ValidationPanel';
import { useWebcam } from '@/lib/hooks/useWebcam';

export default function ValidacaoPage() {
  const { videoRef, canvasRef, webcam, startWebcam, stopWebcam } = useWebcam();

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      
      <main className="flex-1 container py-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-4">Validação Facial</h1>
          <p className="text-muted-foreground">
            Posicione-se em frente à câmera para validação de acesso
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <WebcamCapture 
              videoRef={videoRef}
              canvasRef={canvasRef}
              webcam={webcam}
              startWebcam={startWebcam}
              stopWebcam={stopWebcam}
            />
          </div>
          <div className="lg:col-span-1">
            <ValidationPanel 
              videoRef={videoRef}
              canvasRef={canvasRef}
              webcam={webcam}
            />
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
