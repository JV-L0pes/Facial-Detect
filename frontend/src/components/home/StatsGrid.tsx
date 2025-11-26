'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useStats } from '@/lib/hooks/useStats';
import { Users, CheckCircle, History, Cpu } from 'lucide-react';
import { motion } from 'framer-motion';

const statsData = [
  {
    key: 'total_users',
    icon: Users,
    title: 'Usuários Cadastrados',
    color: 'text-blue-600',
    bgColor: 'bg-blue-50',
  },
  {
    key: 'success_rate',
    icon: CheckCircle,
    title: 'Taxa de Sucesso',
    color: 'text-green-600',
    bgColor: 'bg-green-50',
    suffix: '%',
  },
  {
    key: 'total_logs',
    icon: History,
    title: 'Tentativas de Acesso',
    color: 'text-purple-600',
    bgColor: 'bg-purple-50',
  },
  {
    key: 'device',
    icon: Cpu,
    title: 'Dispositivo',
    color: 'text-orange-600',
    bgColor: 'bg-orange-50',
  },
];

export function StatsGrid() {
  const { data: stats, isLoading, error } = useStats();

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <div className="h-4 w-24 bg-muted rounded"></div>
              <div className="h-8 w-8 bg-muted rounded"></div>
            </CardHeader>
            <CardContent>
              <div className="h-8 w-16 bg-muted rounded mb-2"></div>
              <div className="h-3 w-32 bg-muted rounded"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <Card className="text-center py-8">
        <CardContent>
          <p className="text-muted-foreground">Erro ao carregar estatísticas</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {statsData.map((stat, index) => {
        const Icon = stat.icon;
        let value = '-';
        
        if (stats) {
          switch (stat.key) {
            case 'total_users':
              value = stats.total_users.toString();
              break;
            case 'success_rate':
              value = stats.success_rate.toFixed(1);
              break;
            case 'total_logs':
              value = stats.total_logs.toString();
              break;
            case 'device':
              value = stats.face_recognition.device.toUpperCase();
              break;
          }
        }

        return (
          <motion.div
            key={stat.key}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card className="hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {stat.title}
                </CardTitle>
                <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                  <Icon className={`h-4 w-4 ${stat.color}`} />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {value}{stat.suffix}
                </div>
                <Badge variant="outline" className="mt-2">
                  {stats?.face_recognition.model_loaded ? 'Modelo Carregado' : 'Carregando...'}
                </Badge>
              </CardContent>
            </Card>
          </motion.div>
        );
      })}
    </div>
  );
}
