# Dockerfile para o frontend (nginx)
FROM nginx:alpine

# Copiar arquivos do frontend
COPY . /usr/share/nginx/html/

# Copiar configuração do nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Instalar wget para healthcheck do docker-compose
RUN apk add --no-cache wget

# Expor porta 80
EXPOSE 80

# Comando padrão
CMD ["nginx", "-g", "daemon off;"]
