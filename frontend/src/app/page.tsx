import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { StatsGrid } from '@/components/home/StatsGrid';
import { FeaturesSection } from '@/components/home/FeaturesSection';
import { ConnectionTest } from '@/components/ConnectionTest';

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      
      <main className="flex-1 container py-8">
        {/* Hero Section */}
        <section className="text-center py-12">
          <div className="max-w-4xl mx-auto">
            <h1 className="text-4xl font-bold tracking-tight text-foreground sm:text-6xl mb-6">
              Sistema de Controle de Acesso
            </h1>
            <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              Reconhecimento facial com detecção de liveness para controle de acesso seguro
            </p>
          </div>
        </section>

        {/* Features Section */}
        <FeaturesSection />

        {/* Stats Section */}
        <section className="py-12">
          <h2 className="text-3xl font-bold text-center mb-8">
            Estatísticas do Sistema
          </h2>
          <StatsGrid />
        </section>

        {/* Connection Test Section */}
        <section className="py-12">
          <div className="flex justify-center">
            <ConnectionTest />
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
