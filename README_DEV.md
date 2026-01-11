# 🚀 Guia de Desenvolvimento - Sales AI Dojo

> **Desenvolva localmente SEM precisar de API keys pagas!**

Este guia mostra como começar a desenvolver o Sales AI Dojo **incrementalmente**, sem precisar de todas as integrações externas configuradas.

---

## 📋 O que funciona SEM API keys externas?

✅ **Funciona sem configurar:**
- ✅ Backend FastAPI
- ✅ Frontend Next.js
- ✅ PostgreSQL com pgvector
- ✅ Autenticação JWT local
- ✅ CRUD de empresas, usuários, personas
- ✅ Upload de documentos
- ✅ Sessões de treinamento (mock)
- ✅ Dashboard e métricas

❌ **Precisa configurar para funcionar:**
- ❌ Geração de embeddings (OpenAI)
- ❌ Análise de transcrições com GPT-4 (OpenAI)
- ❌ Chamadas de voz real (Vapi.ai)
- ❌ Speech-to-Text (Deepgram)
- ❌ Text-to-Speech (ElevenLabs)

---

## 🎯 Quick Start (Sem API Keys)

### 1. **Configuração Mínima**

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/sales-ai-dojo.git
cd sales-ai-dojo

# Crie o .env do backend (apenas com configs locais)
cat > backend/.env << 'EOF'
# Database (já configurado no docker-compose)
DATABASE_URL=postgresql://sales_user:sales_password_dev@postgres:5432/sales_dojo

# App config
ENVIRONMENT=development
DEBUG=true
JWT_SECRET=dev-secret-change-in-production

# API Keys (OPCIONAL - deixe comentado por enquanto)
# OPENAI_API_KEY=sk-...
# VAPI_API_KEY=...
EOF

# Crie o .env do frontend
cat > frontend/.env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost/api/v1
EOF
```

### 2. **Inicie o Ambiente**

```bash
# Usando scripts helper
./scripts/dev-up.sh

# Ou manualmente
docker-compose up --build
```

### 3. **Acesse a Aplicação**

- **Frontend**: http://localhost
- **Backend API**: http://localhost/api/v1
- **API Docs (Swagger)**: http://localhost/docs
- **PostgreSQL**: localhost:5432 (user: sales_user, pass: sales_password_dev, db: sales_dojo)

---

## 🗄️ Database Setup

### Conectar no PostgreSQL

```bash
# Via Docker
docker exec -it sales-dojo-postgres psql -U sales_user -d sales_dojo

# Via cliente local (se tiver psql instalado)
psql -h localhost -U sales_user -d sales_dojo
```

### Criar Tabelas (Migrations)

```bash
# Entrar no container do backend
docker-compose exec backend bash

# Inicializar Alembic (primeira vez)
alembic init alembic

# Criar uma migration
alembic revision --autogenerate -m "create initial tables"

# Aplicar migrations
alembic upgrade head

# Ver status
alembic current
```

---

## 🛠️ Desenvolvimento Incremental

### Fase 1: Backend Básico (SEM APIs externas)

**Objetivo**: CRUD funcional de empresas, usuários e personas

```python
# Endpoints que funcionam SEM OpenAI:
POST /api/v1/auth/register       # ✅ Criar usuário
POST /api/v1/auth/login          # ✅ Login
GET  /api/v1/auth/me             # ✅ Ver perfil

POST /api/v1/companies           # ✅ Criar empresa
GET  /api/v1/companies/{id}      # ✅ Ver empresa

POST /api/v1/personas            # ✅ Criar persona manualmente
GET  /api/v1/personas            # ✅ Listar personas
PUT  /api/v1/personas/{id}       # ✅ Editar persona
```

**Como testar**:
```bash
# Veja os endpoints no Swagger
open http://localhost/docs

# Ou use curl
curl -X POST http://localhost/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@example.com",
    "password": "senha123",
    "full_name": "João Teste"
  }'
```

### Fase 2: Frontend Básico

**Objetivo**: Telas de login, dashboard e CRUD

- ✅ Tela de login/registro
- ✅ Dashboard do vendedor
- ✅ Lista de personas
- ✅ Criar/editar personas manualmente

### Fase 3: Features com Mocks

**Objetivo**: Simular features de IA

```python
# backend/app/services/openai_service.py

class OpenAIService:
    def __init__(self):
        self.has_api_key = settings.has_openai

    async def generate_personas(self, context: str, count: int):
        if not self.has_api_key:
            # Retorna personas mockadas
            return self._generate_mock_personas(count)

        # Código real com OpenAI
        ...

    def _generate_mock_personas(self, count: int):
        """Gera personas fake para desenvolvimento"""
        return [
            {
                "name": f"Cliente Mock {i}",
                "role": "decision_maker",
                "personality_traits": {"analytical": True},
                "pain_points": ["Custo alto", "Falta de tempo"],
                "objections": ["Preço", "Implementação"],
                "background": "Gerente de TI em empresa média"
            }
            for i in range(count)
        ]
```

### Fase 4: Adicionar APIs Reais (quando tiver keys)

```bash
# Edite backend/.env e descomente:
OPENAI_API_KEY=sk-your-real-key-here

# Reinicie apenas o backend
docker-compose restart backend

# Agora os endpoints com IA funcionam!
POST /api/v1/personas/generate   # ✅ Usa GPT-4 real
POST /api/v1/feedback/analyze    # ✅ Usa GPT-4 real
```

---

## 📚 Estrutura do Banco de Dados

### Tabelas Principais

```sql
-- Empresas
companies (
  id UUID PRIMARY KEY,
  name TEXT,
  website TEXT,
  created_at TIMESTAMP
)

-- Usuários
users (
  id UUID PRIMARY KEY,
  email TEXT UNIQUE,
  password_hash TEXT,
  full_name TEXT,
  role TEXT,  -- 'salesperson', 'manager', 'admin'
  company_id UUID REFERENCES companies(id),
  created_at TIMESTAMP
)

-- Personas
personas (
  id UUID PRIMARY KEY,
  company_id UUID REFERENCES companies(id),
  name TEXT,
  role TEXT,
  personality_traits JSONB,
  pain_points TEXT[],
  objections TEXT[],
  background TEXT,
  created_at TIMESTAMP
)

-- Knowledge Base (com embeddings)
knowledge_base (
  id UUID PRIMARY KEY,
  company_id UUID REFERENCES companies(id),
  content TEXT,
  source_type TEXT,
  source_name TEXT,
  embedding vector(1536),  -- pgvector
  created_at TIMESTAMP
)

-- Sessões de Treinamento
training_sessions (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  company_id UUID REFERENCES companies(id),
  persona_id UUID REFERENCES personas(id),
  transcript JSONB,
  duration_seconds INTEGER,
  status TEXT,
  created_at TIMESTAMP
)

-- Feedback
feedback (
  id UUID PRIMARY KEY,
  session_id UUID REFERENCES training_sessions(id),
  overall_score FLOAT,
  strengths TEXT[],
  areas_for_improvement TEXT[],
  detailed_analysis JSONB,
  created_at TIMESTAMP
)
```

---

## 🧪 Testando sem APIs Externas

### Criar Dados de Teste

```bash
# Entre no container do backend
docker-compose exec backend python

# Crie dados de teste
from app.core.database import SessionLocal
from app.models import *

db = SessionLocal()

# Criar empresa
company = Company(name="Empresa Teste", website="https://example.com")
db.add(company)
db.commit()

# Criar usuário
user = User(
    email="joao@teste.com",
    password_hash="...",  # Use bcrypt
    full_name="João Silva",
    role="salesperson",
    company_id=company.id
)
db.add(user)
db.commit()

# Criar persona
persona = Persona(
    company_id=company.id,
    name="Carlos Oliveira",
    role="decision_maker",
    personality_traits={"analytical": True, "risk_averse": True},
    pain_points=["Sistema lento", "Falta integração"],
    objections=["Preço alto", "Implementação longa"],
    background="CTO de rede de supermercados"
)
db.add(persona)
db.commit()
```

### Usar Endpoints

```bash
# Registrar usuário
curl -X POST http://localhost/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "joao@teste.com",
    "password": "senha123",
    "full_name": "João Silva",
    "company_id": "uuid-da-empresa",
    "role": "salesperson"
  }'

# Login
curl -X POST http://localhost/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "joao@teste.com",
    "password": "senha123"
  }'

# Listar personas (precisa do token)
curl -X GET http://localhost/api/v1/personas \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

---

## 🔧 Ferramentas Úteis

### Acessar PostgreSQL

```bash
# Via psql
docker exec -it sales-dojo-postgres psql -U sales_user -d sales_dojo

# Ver tabelas
\dt

# Ver dados
SELECT * FROM companies;
SELECT * FROM users;
SELECT * FROM personas;
```

### Ver Logs

```bash
# Todos os serviços
./scripts/logs.sh

# Apenas backend
docker-compose logs -f backend

# Apenas postgres
docker-compose logs -f postgres
```

### Resetar Banco de Dados

```bash
# Para tudo
./scripts/dev-down.sh

# Remove volumes (⚠️ apaga dados)
docker-compose down -v

# Sobe novamente (banco zerado)
./scripts/dev-up.sh
```

---

## ⚙️ Variáveis de Ambiente

### Backend (.env)

```bash
# === CONFIGURAÇÃO MÍNIMA (sem APIs externas) ===

# Database
DATABASE_URL=postgresql://sales_user:sales_password_dev@postgres:5432/sales_dojo

# App
ENVIRONMENT=development
DEBUG=true
JWT_SECRET=dev-secret-change-in-production

# === OPCIONAL: Descomente quando tiver as keys ===

# OpenAI (para embeddings e GPT-4)
# OPENAI_API_KEY=sk-...

# Vapi.ai (para chamadas de voz)
# VAPI_API_KEY=...

# Deepgram (Speech-to-Text)
# DEEPGRAM_API_KEY=...

# ElevenLabs (Text-to-Speech)
# ELEVENLABS_API_KEY=...
```

### Frontend (.env.local)

```bash
# URL da API (via nginx)
NEXT_PUBLIC_API_URL=http://localhost/api/v1
```

---

## 🎓 Próximos Passos

### 1. **Familiarize-se com o código**
```bash
# Backend
backend/app/
├── main.py              # Entry point
├── core/
│   ├── config.py        # Configurações
│   └── database.py      # SQLAlchemy setup
├── models/              # Pydantic schemas
├── api/routes/          # Endpoints
└── services/            # Lógica de negócio
```

### 2. **Crie suas primeiras rotas**
```python
# backend/app/api/routes/test.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/hello")
async def hello():
    return {"message": "Hello World!"}
```

### 3. **Adicione ao main.py**
```python
from app.api.routes import test

app.include_router(test.router, prefix="/api/v1/test", tags=["Test"])
```

### 4. **Teste**
```bash
curl http://localhost/api/v1/test/hello
```

---

## 💡 Dicas

### Hot Reload Funciona!
- Mude código Python → backend recarrega automaticamente
- Mude código TypeScript → frontend recarrega automaticamente

### Debug no VSCode
```json
// .vscode/launch.json
{
  "configurations": [
    {
      "name": "Attach to Backend",
      "type": "python",
      "request": "attach",
      "connect": {
        "host": "localhost",
        "port": 5678
      }
    }
  ]
}
```

### Comandos Úteis
```bash
# Rebuild sem cache
./scripts/rebuild.sh

# Ver uso de recursos
docker stats

# Limpar tudo
./scripts/clean.sh
```

---

## 🐛 Troubleshooting

### Backend não inicia
```bash
# Ver logs
docker-compose logs backend

# Entrar no container
docker-compose exec backend bash

# Testar Python
python -c "from app.core.config import settings; print(settings.DATABASE_URL)"
```

### Banco não conecta
```bash
# Testar conexão
docker-compose exec postgres pg_isready -U sales_user

# Ver logs do postgres
docker-compose logs postgres
```

### Port 5432 já em uso
```bash
# Ver quem está usando
sudo lsof -i :5432

# Parar postgres local
sudo systemctl stop postgresql

# Ou mudar porta no docker-compose.yml
ports:
  - "5433:5432"  # Usa 5433 externamente
```

---

## 📖 Documentação Adicional

- **[README.md](README.md)** - Overview do projeto
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Arquitetura completa
- **[DOCKER.md](docs/DOCKER.md)** - Guia completo de Docker
- **[API.md](docs/API.md)** - Documentação de endpoints

---

**Dúvidas?** Abra uma issue no GitHub ou consulte a documentação!

**Bons estudos e bom desenvolvimento! 🚀**
