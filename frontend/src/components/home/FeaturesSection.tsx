'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Shield, Zap, Eye } from 'lucide-react';
import { motion } from 'framer-motion';

const features = [
  {
    icon: Shield,
    title: 'Seguro',
    description: 'Criptografia AES-256 e compliance LGPD',
    gradient: 'from-blue-500 to-blue-600',
  },
  {
    icon: Zap,
    title: 'Rápido',
    description: 'Processamento em tempo real',
    gradient: 'from-yellow-500 to-orange-500',
  },
  {
    icon: Eye,
    title: 'Anti-Spoofing',
    description: 'Detecção de liveness integrada',
    gradient: 'from-green-500 to-emerald-500',
  },
];

export function FeaturesSection() {
  return (
    <section className="py-12">
      <div className="text-center mb-12">
        <h2 className="text-3xl font-bold mb-4">Recursos Principais</h2>
        <p className="text-muted-foreground max-w-2xl mx-auto">
          Tecnologia avançada para garantir segurança e eficiência no controle de acesso
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {features.map((feature, index) => {
          const Icon = feature.icon;
          
          return (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.2 }}
              whileHover={{ y: -5 }}
            >
              <Card className="h-full hover:shadow-xl transition-all duration-300 border-0 bg-gradient-to-br from-background to-muted/20">
                <CardHeader className="text-center">
                  <div className="mx-auto mb-4 p-4 rounded-full bg-gradient-to-r from-primary/10 to-primary/5">
                    <Icon className="h-8 w-8 text-primary" />
                  </div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                  <CardDescription className="text-base">
                    {feature.description}
                  </CardDescription>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className={`h-1 w-full rounded-full bg-gradient-to-r ${feature.gradient}`} />
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </div>
    </section>
  );
}
