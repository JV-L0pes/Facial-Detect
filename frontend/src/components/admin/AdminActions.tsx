'use client';

import { useState } from 'react';
import { useDeleteAllUsers, useDeleteUser } from '@/lib/hooks/useUsers';
import { adminApi } from '@/lib/api/admin';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  AlertTriangle, 
  Users, 
  History, 
  Database,
  Trash2,
  UserX,
  Brush
} from 'lucide-react';
import { motion } from 'framer-motion';
import { toast } from 'sonner';

export function AdminActions() {
  const [isLoading, setIsLoading] = useState(false);
  const deleteAllUsers = useDeleteAllUsers();
  const deleteUser = useDeleteUser();

  const handleClearLogs = async () => {
    if (!confirm('ATENÇÃO: Esta ação irá remover TODOS os logs de acesso!\n\nTem certeza que deseja continuar?')) {
      return;
    }

    setIsLoading(true);
    try {
      const response = await adminApi.clearLogs();
      toast.success('Logs limpos com sucesso!');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erro ao limpar logs');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearDatabase = async () => {
    if (!confirm('⚠️ ATENÇÃO: Esta ação irá LIMPAR COMPLETAMENTE o banco de dados!\n\nIsso inclui:\n• Todos os usuários cadastrados\n• Todos os logs de acesso\n• Todos os embeddings do sistema\n\nEsta ação NÃO PODE ser desfeita!\n\nTem certeza que deseja continuar?')) {
      return;
    }

    if (!confirm('Última chance! Tem certeza absoluta que deseja limpar o banco?')) {
      return;
    }

    setIsLoading(true);
    try {
      const response = await adminApi.clearDatabase();
      toast.success('Banco limpo com sucesso!');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erro ao limpar banco');
    } finally {
      setIsLoading(false);
    }
  };

  const actionGroups = [
    {
      title: 'Gerenciar Usuários',
      icon: Users,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
      actions: [
        {
          title: 'Remover Todos os Usuários',
          description: 'Remove todos os usuários cadastrados do sistema',
          icon: UserX,
          variant: 'destructive' as const,
          onClick: () => deleteAllUsers.mutate(),
          isLoading: deleteAllUsers.isPending,
        },
      ],
    },
    {
      title: 'Gerenciar Logs',
      icon: History,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      actions: [
        {
          title: 'Limpar Todos os Logs',
          description: 'Remove todos os logs de acesso do sistema',
          icon: Brush,
          variant: 'default' as const,
          onClick: handleClearLogs,
          isLoading: isLoading,
        },
      ],
    },
    {
      title: 'Gerenciar Banco de Dados',
      icon: Database,
      color: 'text-red-600',
      bgColor: 'bg-red-50',
      actions: [
        {
          title: 'Limpar Banco Completamente',
          description: 'Remove todos os dados do sistema (usuários, logs, embeddings)',
          icon: Trash2,
          variant: 'destructive' as const,
          onClick: handleClearDatabase,
          isLoading: isLoading,
        },
      ],
    },
  ];

  return (
    <Card className="border-red-200 bg-red-50/50">
      <CardHeader>
        <div className="flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-red-600" />
          <CardTitle className="text-red-800">Ações Administrativas</CardTitle>
        </div>
        <CardDescription className="text-red-700">
          Ações que afetam permanentemente os dados do sistema
        </CardDescription>
      </CardHeader>
      
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {actionGroups.map((group, groupIndex) => {
            const GroupIcon = group.icon;
            
            return (
              <motion.div
                key={group.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: groupIndex * 0.1 }}
                className="bg-white rounded-lg border p-6"
              >
                <div className="flex items-center gap-2 mb-4">
                  <div className={`p-2 rounded-lg ${group.bgColor}`}>
                    <GroupIcon className={`h-5 w-5 ${group.color}`} />
                  </div>
                  <h3 className="font-semibold">{group.title}</h3>
                </div>
                
                <div className="space-y-3">
                  {group.actions.map((action, actionIndex) => {
                    const ActionIcon = action.icon;
                    
                    return (
                      <motion.div
                        key={action.title}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: (groupIndex * 0.1) + (actionIndex * 0.05) }}
                      >
                        <Button
                          variant={action.variant}
                          className="w-full justify-start"
                          onClick={action.onClick}
                          disabled={action.isLoading}
                        >
                          {action.isLoading ? (
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                          ) : (
                            <ActionIcon className="h-4 w-4 mr-2" />
                          )}
                          {action.title}
                        </Button>
                        <p className="text-xs text-muted-foreground mt-1">
                          {action.description}
                        </p>
                      </motion.div>
                    );
                  })}
                </div>
              </motion.div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
