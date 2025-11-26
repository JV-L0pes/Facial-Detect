/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  images: {
    domains: ['localhost'],
  },
  async rewrites() {
    // Detectar se está rodando no Docker ou localmente
    // No Docker: usar o nome do serviço 'backend:8000'
    // Localmente: usar 'localhost:8000'
    // A variável BACKEND_URL é definida no Docker durante o build
    // Se não estiver definida, assume desenvolvimento local
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    
    console.log(`[Next.js Config] Backend URL: ${backendUrl}`);
    console.log(`[Next.js Config] NODE_ENV: ${process.env.NODE_ENV}`);
    
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
}

module.exports = nextConfig
