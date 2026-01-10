# Docker Setup - Sales AI Dojo

Guia completo de dockerização do projeto com containers separados, multi-stage builds e configurações otimizadas para desenvolvimento e produção.

---

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Quick Start](#quick-start)
- [Desenvolvimento](#desenvolvimento)
- [Produção](#produção)
- [Scripts Helper](#scripts-helper)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

O projeto utiliza Docker com múltiplos containers:

- **Backend** (FastAPI) - Container Python com hot reload
- **Frontend** (Next.js) - Container Node.js com hot reload
- **Nginx** - Reverse proxy e balanceador de carga

### Características

✅ **Multi-stage builds** - Images otimizadas para dev e prod
✅ **Hot reload** - Mudanças no código refletem instantaneamente
✅ **Nginx** - Reverse proxy com rate limiting e SSL ready
✅ **Health checks** - Monitoramento automático de containers
✅ **Resource limits** - Limites de CPU e memória (produção)
✅ **Scripts helper** - Comandos simplificados para operações comuns

---

## 🏗️ Arquitetura

### Desenvolvimento

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  http://localhost (port 80)                    │
│                                                 │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
        ┌────────────────┐
        │     Nginx      │  Rate limiting
        │  Reverse Proxy │  CORS headers
        └───┬────────┬───┘  Access logs
            │        │
    ┌───────▼──┐  ┌──▼────────┐
    │ Backend  │  │ Frontend  │
    │ FastAPI  │  │  Next.js  │
    │ :8000    │  │  :3000    │
    └──────────┘  └───────────┘
    Hot Reload     Hot Reload
```

### Produção

```
┌─────────────────────────────────────────────────┐
│ http://localhost or https://domain.com          │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
        ┌────────────────┐
        │     Nginx      │  SSL/TLS
        │  Reverse Proxy │  Rate limiting
        └───┬────────┬───┘  Load balancing
            │        │
    ┌───────▼──┐  ┌──▼────────┐
    │ Backend  │  │ Frontend  │
    │ FastAPI  │  │  Next.js  │
    │ 4 workers│  │ Optimized │
    └──────────┘  └───────────┘
   Non-root user  Non-root user
```

---

## 🚀 Quick Start

### Pré-requisitos

- Docker 20.10+
- Docker Compose 2.0+

### 1. Clone e Configure

```bash
git clone https://github.com/seu-usuario/sales-ai-dojo.git
cd sales-ai-dojo

# Configure environment variables
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local

# Edit with your API keys
nano backend/.env
nano frontend/.env.local
```

### 2. Start Development Environment

```bash
# Using helper script (recommended)
./scripts/dev-up.sh

# Or manually
docker-compose up --build
```

### 3. Access Application

- **Frontend**: http://localhost
- **Backend API**: http://localhost/api/v1
- **API Docs**: http://localhost/docs

---

## 💻 Desenvolvimento

### Comandos Básicos

```bash
# Start all services
./scripts/dev-up.sh

# Stop all services
./scripts/dev-down.sh

# View logs
./scripts/logs.sh

# View logs of specific service
./scripts/logs.sh dev backend

# Rebuild containers
./scripts/rebuild.sh
```

### Manual Commands

```bash
# Start in detached mode
docker-compose up -d

# Start with build
docker-compose up --build

# Stop services
docker-compose down

# View logs (all services)
docker-compose logs -f

# View logs (specific service)
docker-compose logs -f backend

# Rebuild specific service
docker-compose build backend
docker-compose up -d backend

# Execute command in running container
docker-compose exec backend python -m pytest
docker-compose exec frontend npm run lint

# Access container shell
docker-compose exec backend bash
docker-compose exec frontend sh
```

### File Structure

```
sales-ai-dojo/
├── backend/
│   ├── Dockerfile                # Multi-stage (dev/prod)
│   ├── .dockerignore
│   └── ...
├── frontend/
│   ├── Dockerfile                # Multi-stage (dev/prod)
│   ├── .dockerignore
│   └── ...
├── nginx/
│   ├── Dockerfile
│   └── nginx.conf                # Reverse proxy config
├── docker-compose.yml            # Development
├── docker-compose.prod.yml       # Production
└── scripts/
    ├── dev-up.sh
    ├── dev-down.sh
    ├── prod-up.sh
    ├── prod-down.sh
    ├── logs.sh
    ├── rebuild.sh
    └── clean.sh
```

### Hot Reload

Mudanças no código são automaticamente refletidas:

**Backend:**
- Modificações em `.py` → Uvicorn recarrega automaticamente
- Volume montado: `./backend:/app`

**Frontend:**
- Modificações em `.tsx`, `.ts`, `.css` → Next.js hot reload
- Volume montado: `./frontend:/app`

**Nginx:**
- Modificações em `nginx.conf` → Recarrega config
- Volume montado (read-only): `./nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro`

### Environment Variables

**Backend** (`.env`):
```env
OPENAI_API_KEY=sk-...
VAPI_API_KEY=...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...
# ... etc
```

**Frontend** (`.env.local`):
```env
NEXT_PUBLIC_API_URL=http://localhost/api/v1
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
```

### Ports

| Service  | Internal Port | External Port | Access              |
|----------|---------------|---------------|---------------------|
| Nginx    | 80            | 80            | http://localhost    |
| Backend  | 8000          | -             | Via Nginx           |
| Frontend | 3000          | -             | Via Nginx           |

---

## 🚢 Produção

### Build Production Images

```bash
# Using helper script
./scripts/prod-up.sh

# Or manually
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

### Production Optimizations

**Backend:**
- ✅ Multi-stage build (smaller image)
- ✅ Non-root user (security)
- ✅ 4 workers (uvicorn)
- ✅ Resource limits (2 CPU, 2GB RAM)
- ✅ Log rotation (max 10MB, 3 files)

**Frontend:**
- ✅ Standalone output (Next.js)
- ✅ Multi-stage build
- ✅ Non-root user
- ✅ Resource limits (1 CPU, 1GB RAM)
- ✅ Static assets optimization

**Nginx:**
- ✅ Rate limiting (60 req/min API, 100 req/min general)
- ✅ Gzip compression
- ✅ SSL/TLS ready
- ✅ Security headers
- ✅ Access logs

### SSL/HTTPS Setup

1. **Obtain SSL certificates** (Let's Encrypt, CloudFlare, etc)

2. **Add certificates to nginx directory:**
```bash
mkdir -p nginx/ssl
cp cert.pem nginx/ssl/
cp key.pem nginx/ssl/
```

3. **Uncomment SSL section in `nginx/nginx.conf`:**
```nginx
server {
    listen 443 ssl http2;
    server_name salesaidojo.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    # ...
}
```

4. **Update docker-compose.prod.yml:**
```yaml
nginx:
  volumes:
    - ./nginx/ssl:/etc/nginx/ssl:ro  # Uncomment this line
```

5. **Rebuild:**
```bash
./scripts/rebuild.sh prod
```

### Resource Limits

Default limits in `docker-compose.prod.yml`:

| Service  | CPU Limit | CPU Reserve | Memory Limit | Memory Reserve |
|----------|-----------|-------------|--------------|----------------|
| Backend  | 2 cores   | 1 core      | 2GB          | 1GB            |
| Frontend | 1 core    | 0.5 core    | 1GB          | 512MB          |
| Nginx    | 0.5 core  | 0.25 core   | 256MB        | 128MB          |

Adjust based on your needs in `docker-compose.prod.yml`:

```yaml
backend:
  deploy:
    resources:
      limits:
        cpus: '4'      # Increase for more load
        memory: 4G
```

### Monitoring

**View container stats:**
```bash
docker stats
```

**Check health:**
```bash
docker-compose -f docker-compose.prod.yml ps
```

**View logs:**
```bash
./scripts/logs.sh prod

# Specific service
./scripts/logs.sh prod backend

# Nginx access logs
docker-compose -f docker-compose.prod.yml exec nginx tail -f /var/log/nginx/access.log
```

---

## 🛠️ Scripts Helper

### `./scripts/dev-up.sh`

Inicia ambiente de desenvolvimento.

```bash
./scripts/dev-up.sh
```

- Cria `.env` files se não existirem
- Builda images
- Inicia containers em detached mode
- Mostra URLs de acesso

### `./scripts/dev-down.sh`

Para ambiente de desenvolvimento.

```bash
./scripts/dev-down.sh
```

### `./scripts/prod-up.sh`

Inicia ambiente de produção.

```bash
./scripts/prod-up.sh
```

- Valida se `.env` files existem
- Builda production images (otimizadas)
- Inicia containers com resource limits
- Confirma antes de iniciar

### `./scripts/prod-down.sh`

Para ambiente de produção.

```bash
./scripts/prod-down.sh
```

- Pede confirmação antes de parar
- Para todos os containers

### `./scripts/logs.sh`

Visualiza logs.

```bash
# Development logs
./scripts/logs.sh

# Production logs
./scripts/logs.sh prod

# Specific service (dev)
./scripts/logs.sh dev backend

# Specific service (prod)
./scripts/logs.sh prod frontend
```

### `./scripts/rebuild.sh`

Rebuilda containers (sem cache).

```bash
# Development
./scripts/rebuild.sh

# Production
./scripts/rebuild.sh prod
```

Use quando:
- Mudou dependências (`requirements.txt`, `package.json`)
- Quer forçar rebuild completo
- Resolvendo problemas de cache

### `./scripts/clean.sh`

Limpa recursos Docker não utilizados.

```bash
./scripts/clean.sh
```

Remove:
- Containers parados
- Networks não utilizadas
- Images dangling (sem tag)

---

## 🔧 Troubleshooting

### Container não inicia

**Sintoma:** Container reinicia continuamente

**Debug:**
```bash
# Ver logs
docker-compose logs backend

# Ver status
docker-compose ps

# Inspecionar container
docker inspect sales-dojo-backend-dev
```

**Soluções:**
- Verificar `.env` files estão configurados
- Verificar portas não estão em uso
- Verificar health check está passando

### Port already in use

**Sintoma:** `Bind for 0.0.0.0:80 failed: port is already allocated`

**Solução:**
```bash
# Descobrir processo usando porta 80
sudo lsof -i :80

# Parar processo
sudo kill -9 <PID>

# Ou mudar porta no docker-compose.yml
ports:
  - "8080:80"  # Use porta 8080 ao invés de 80
```

### Out of disk space

**Sintoma:** `no space left on device`

**Solução:**
```bash
# Ver uso de disco
docker system df

# Limpar tudo (⚠️ cuidado)
docker system prune -a --volumes

# Ou limpar seletivamente
./scripts/clean.sh
```

### Hot reload não funciona

**Sintoma:** Mudanças no código não refletem

**Backend:**
```bash
# Verificar se volume está montado
docker-compose exec backend ls -la /app

# Restart container
docker-compose restart backend
```

**Frontend:**
```bash
# Verificar se node_modules é um volume
docker-compose ps -a

# Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend
```

### Permission denied

**Sintoma:** `Permission denied` ao acessar arquivos

**Solução:**
```bash
# Verificar ownership dos volumes
ls -la backend/

# Ajustar permissions
sudo chown -R $USER:$USER backend/ frontend/

# Ou rodar como root (não recomendado em prod)
docker-compose exec -u root backend bash
```

### Cannot connect to backend from frontend

**Sintoma:** Frontend não consegue chamar API

**Debug:**
```bash
# Verificar network
docker network inspect sales-dojo-network

# Teste de conectividade
docker-compose exec frontend ping backend

# Ver se backend está acessível
docker-compose exec frontend curl http://backend:8000/health
```

**Solução:**
- Verificar containers estão na mesma network
- Verificar `NEXT_PUBLIC_API_URL` no frontend
- Em desenvolvimento, use `http://backend:8000` internamente
- Externamente (browser), use `http://localhost/api/v1`

### Database connection fails

**Sintoma:** Backend não conecta no Supabase

**Debug:**
```bash
# Ver logs do backend
docker-compose logs backend | grep -i supabase

# Testar conectividade
docker-compose exec backend python -c "from app.core.database import verify_connection; print(verify_connection())"
```

**Solução:**
- Verificar `SUPABASE_URL` e `SUPABASE_KEY` no `.env`
- Verificar Supabase está acessível (não está bloqueado por firewall)
- Verificar API key está correta

---

## 📊 Comparação Dev vs Prod

| Aspecto           | Development                | Production                |
|-------------------|----------------------------|---------------------------|
| Build stage       | `development`              | `production`              |
| Hot reload        | ✅ Sim                     | ❌ Não                    |
| Source mounted    | ✅ Sim                     | ❌ Não                    |
| User              | root                       | non-root (appuser)        |
| Workers (backend) | 1 (auto-reload)            | 4 (multi-process)         |
| Image size        | ~1.5GB                     | ~500MB                    |
| Resource limits   | ❌ Não                     | ✅ Sim (CPU, RAM)         |
| Log rotation      | ❌ Não                     | ✅ Sim (10MB, 3 files)    |
| Health checks     | ✅ Sim                     | ✅ Sim                    |
| SSL/TLS           | ❌ Não                     | ✅ Configurável           |

---

## 🔐 Security Best Practices

### Development

- ✅ Não commitar `.env` files (use `.env.example`)
- ✅ Usar `.dockerignore` para evitar secrets em images
- ✅ Manter Docker atualizado

### Production

- ✅ Usar non-root user nos containers
- ✅ Habilitar SSL/TLS (HTTPS)
- ✅ Configurar rate limiting no Nginx
- ✅ Usar secrets manager (Railway Secrets, AWS Secrets Manager)
- ✅ Scan de vulnerabilidades em images:
  ```bash
  docker scan sales-dojo-backend:latest
  ```
- ✅ Limitar resource usage (CPU, RAM)
- ✅ Rotação de logs para evitar disk full
- ✅ Network isolation (usar Docker networks)

---

## 📚 Referências

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Next.js Docker Deployment](https://nextjs.org/docs/deployment#docker-image)
- [FastAPI in Containers](https://fastapi.tiangolo.com/deployment/docker/)
- [Nginx Configuration](https://nginx.org/en/docs/)

---

## 💡 Tips & Tricks

### Faster Rebuilds

Use `--build` only when dependencies changed:

```bash
# Quick restart (no rebuild)
docker-compose restart

# Rebuild specific service
docker-compose build backend
docker-compose up -d backend
```

### Debug Inside Container

```bash
# Access backend shell
docker-compose exec backend bash

# Run Python REPL
docker-compose exec backend python

# Run tests
docker-compose exec backend pytest

# Access frontend shell
docker-compose exec frontend sh

# Run npm commands
docker-compose exec frontend npm run lint
```

### Prune Old Images

```bash
# See disk usage
docker system df

# Remove unused images
docker image prune -a

# Remove specific image
docker rmi sales-dojo-backend:latest
```

### Copy Files From Container

```bash
# Copy logs
docker cp sales-dojo-backend-dev:/var/log/app.log ./logs/

# Copy uploads
docker cp sales-dojo-backend-dev:/tmp/uploads ./backup/
```

---

**Precisa de ajuda?** Abra uma issue no GitHub ou consulte a [documentação completa](../README.md).
