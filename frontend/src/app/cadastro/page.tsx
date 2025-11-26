import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { RegisterForm } from '@/components/cadastro/RegisterForm';

export default function CadastroPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      
      <main className="flex-1 container py-8">
        <div className="max-w-2xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold mb-4">Cadastrar Novo Usuário</h1>
            <p className="text-muted-foreground">
              Envie uma foto clara do seu rosto para cadastro no sistema
            </p>
          </div>
          
          <RegisterForm />
        </div>
      </main>

      <Footer />
    </div>
  );
}
