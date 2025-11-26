'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { 
  Home, 
  UserPlus, 
  Camera, 
  Settings,
  UserCheck
} from 'lucide-react';

const navigation = [
  { name: 'Início', href: '/', icon: Home },
  { name: 'Cadastro', href: '/cadastro', icon: UserPlus },
  { name: 'Validação', href: '/validacao', icon: Camera },
  { name: 'Admin', href: '/admin', icon: Settings },
];

export function Header() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <UserCheck className="h-8 w-8 text-primary" />
            <h1 className="text-xl font-bold">Sistema Reconhecimento Facial</h1>
          </div>
        </div>
        
        <nav className="flex items-center space-x-2">
          {navigation.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            
            return (
              <Button
                key={item.name}
                variant={isActive ? 'default' : 'ghost'}
                size="sm"
                asChild
                className={cn(
                  'transition-all duration-200',
                  isActive && 'shadow-md'
                )}
              >
                <Link href={item.href} className="flex items-center space-x-2">
                  <Icon className="h-4 w-4" />
                  <span>{item.name}</span>
                </Link>
              </Button>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
