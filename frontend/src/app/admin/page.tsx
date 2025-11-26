import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { UsersTable } from '@/components/admin/UsersTable';
import { LogsTable } from '@/components/admin/LogsTable';
import { PassageStats } from '@/components/admin/PassageStats';
import { AdminActions } from '@/components/admin/AdminActions';

export default function AdminPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      
      <main className="flex-1 container py-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-4">Painel Administrativo</h1>
          <p className="text-muted-foreground">
            Gerencie usuários, visualize logs e estatísticas do sistema
          </p>
        </div>

        <div className="space-y-8">
          {/* Estatísticas de Passagens */}
          <PassageStats />

          {/* Ações Administrativas */}
          <AdminActions />

          {/* Tabela de Usuários */}
          <UsersTable />

          {/* Tabela de Logs */}
          <LogsTable />
        </div>
      </main>

      <Footer />
    </div>
  );
}
