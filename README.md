# 🎯 Sales AI Dojo

> Plataforma SaaS de treinamento de vendedores com simulações de voz por IA

## 📋 Visão Geral

Sales AI Dojo é uma plataforma que permite empresas treinarem seus vendedores através de simulações realistas de conversas com clientes gerados por IA. O sistema utiliza processamento de linguagem natural, síntese de voz e RAG (Retrieval-Augmented Generation) para criar experiências de treinamento personalizadas e eficazes.

### 🌟 Funcionalidades Principais

- **Onboarding Inteligente**: Upload de documentos e scraping de sites para criar knowledge base
- **Geração Automática de Personas**: IA cria perfis de clientes baseados no contexto da empresa
- **Simulações de Voz Realistas**: Conversas em tempo real com IA usando Vapi.ai
- **RAG Contextual**: Sistema busca informações relevantes durante chamadas
- **Feedback Automatizado**: GPT-4o analisa transcrições e gera insights
- **Dashboard Gerencial**: Métricas e analytics de performance da equipe

## 🏗️ Arquitetura

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Vendedor  │─────▶│   Next.js    │─────▶│   FastAPI   │
│  (Browser)  │◀─────│   Frontend   │◀─────│   Backend   │
└─────────────┘      └──────────────┘      └──────┬──────┘
                                                    │
                     ┌──────────────────────────────┼──────────────────┐
                     │                              │                  │
                ┌────▼─────┐  ┌─────────────┐  ┌──▼────────┐  ┌──────▼──────┐
                │ Supabase │  │   Vapi.ai   │  │  OpenAI   │  │  Deepgram   │
                │ (DB+Auth)│  │   (Voice)   │  │ (GPT-4o)  │  │ ElevenLabs  │
                └──────────┘  └─────────────┘  └───────────┘  └─────────────┘
```

### Fluxo de Dados

1. **Onboarding** → Empresa faz upload de docs → Sistema gera embeddings → Armazena no Supabase (pgvector)
2. **Geração de Personas** → GPT-4o analisa knowledge base → Cria perfis de clientes
3. **Sessão de Treinamento** → Vendedor inicia chamada → Vapi.ai conecta → RAG fornece contexto → Transcrição salva
4. **Feedback** → GPT-4o analisa conversa → Gera scoring e insights → Dashboard atualizado

## 🛠️ Stack Tecnológica

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: Supabase (PostgreSQL + pgvector)
- **Auth**: Supabase Auth
- **AI Services**:
  - OpenAI API (GPT-4o + embeddings)
  - Vapi.ai (orquestração de voz)
  - Deepgram (Speech-to-Text)
  - ElevenLabs (Text-to-Speech)

### Frontend
- **Framework**: Next.js 14 (App Router)
- **UI**: TailwindCSS + shadcn/ui
- **State**: React Context
- **TypeScript**: Strict mode

### DevOps
- **Containers**: Docker + Docker Compose
- **Deploy**: Railway (backend) + Vercel (frontend)
- **CI/CD**: GitHub Actions

## 🚀 Setup Local

### Pré-requisitos

- Docker & Docker Compose
- Node.js 18+ (se rodar sem Docker)
- Python 3.11+ (se rodar sem Docker)
- Contas configuradas:
  - Supabase (database + auth)
  - OpenAI API
  - Vapi.ai
  - Deepgram
  - ElevenLabs

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/sales-ai-dojo.git
cd sales-ai-dojo
```

### 2. Configure Variáveis de Ambiente

#### Backend
```bash
cp backend/.env.example backend/.env
# Edite backend/.env com suas credenciais
```

Variáveis necessárias:
```env
# API Keys
OPENAI_API_KEY=sk-...
VAPI_API_KEY=...
DEEPGRAM_API_KEY=...
ELEVENLABS_API_KEY=...

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...
SUPABASE_JWT_SECRET=your-jwt-secret

# App Config
ENVIRONMENT=development
DEBUG=true
API_V1_PREFIX=/api/v1
ALLOWED_ORIGINS=http://localhost:3000
```

#### Frontend
```bash
cp frontend/.env.local.example frontend/.env.local
# Edite frontend/.env.local
```

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
```

### 3. Rode com Docker (Recomendado)

#### Opção 1: Helper Scripts (Mais Fácil)

```bash
# Start development environment
./scripts/dev-up.sh

# View logs
./scripts/logs.sh

# Stop environment
./scripts/dev-down.sh
```

#### Opção 2: Docker Compose Manual

```bash
docker-compose up --build
```

Serviços disponíveis:
- **Application**: http://localhost (Nginx reverse proxy)
- **Backend API**: http://localhost/api/v1
- **API Docs**: http://localhost/docs

**Arquitetura:**
- 🔵 **Nginx** (port 80) - Reverse proxy + rate limiting
- 🟢 **Backend** (internal) - FastAPI com hot reload
- 🟡 **Frontend** (internal) - Next.js com hot reload

📖 **Documentação completa**: [docs/DOCKER.md](docs/DOCKER.md)

### 4. Rode Manualmente (Alternativa)

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 📚 Endpoints Principais

### Autenticação
- `POST /api/v1/auth/register` - Criar conta
- `POST /api/v1/auth/login` - Login

### Onboarding
- `POST /api/v1/onboarding/upload-documents` - Upload de documentos
- `POST /api/v1/onboarding/scrape-website` - Scraping de site
- `GET /api/v1/onboarding/status/{company_id}` - Status do processamento

### Personas
- `GET /api/v1/personas` - Listar personas
- `POST /api/v1/personas/generate` - Gerar novas personas
- `GET /api/v1/personas/random` - Selecionar persona aleatória

### Sessões de Treinamento
- `POST /api/v1/sessions/start` - Iniciar chamada com Vapi
- `POST /api/v1/sessions/{id}/end` - Finalizar sessão
- `GET /api/v1/sessions/{id}` - Detalhes da sessão

### Feedback
- `GET /api/v1/feedback/{session_id}` - Obter feedback da sessão
- `POST /api/v1/feedback/regenerate` - Regenerar análise

### Dashboard
- `GET /api/v1/dashboard/metrics` - Métricas da equipe
- `GET /api/v1/dashboard/leaderboard` - Ranking de vendedores

## 🗄️ Schema do Banco (Supabase)

```sql
-- Companies
CREATE TABLE companies (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  website TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Knowledge Base (com suporte a embeddings)
CREATE TABLE knowledge_base (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID REFERENCES companies(id),
  content TEXT NOT NULL,
  source_type TEXT, -- 'document', 'website', 'manual'
  source_name TEXT,
  embedding vector(1536), -- OpenAI embedding dimension
  created_at TIMESTAMP DEFAULT NOW()
);

-- Índice para busca vetorial
CREATE INDEX ON knowledge_base USING ivfflat (embedding vector_cosine_ops);

-- Personas
CREATE TABLE personas (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID REFERENCES companies(id),
  name TEXT NOT NULL,
  role TEXT, -- 'decision_maker', 'influencer', 'gatekeeper'
  personality_traits JSONB,
  pain_points TEXT[],
  objections TEXT[],
  created_at TIMESTAMP DEFAULT NOW()
);

-- Training Sessions
CREATE TABLE training_sessions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,
  company_id UUID REFERENCES companies(id),
  persona_id UUID REFERENCES personas(id),
  vapi_call_id TEXT,
  transcript JSONB,
  duration_seconds INTEGER,
  status TEXT, -- 'ongoing', 'completed', 'abandoned'
  created_at TIMESTAMP DEFAULT NOW()
);

-- Feedback
CREATE TABLE feedback (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  session_id UUID REFERENCES training_sessions(id),
  overall_score FLOAT, -- 0-100
  strengths TEXT[],
  areas_for_improvement TEXT[],
  detailed_analysis JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
```

## 🧪 Testes

```bash
# Backend
cd backend
pytest tests/ -v

# Frontend
cd frontend
npm run test
```

## 📦 Deploy

### Backend (Railway)

1. Conecte repositório ao Railway
2. Configure variáveis de ambiente
3. Deploy automático via GitHub

```bash
# Ou via CLI
railway login
railway up
```

### Frontend (Vercel)

1. Conecte repositório ao Vercel
2. Configure variáveis de ambiente
3. Deploy automático via GitHub

```bash
# Ou via CLI
vercel --prod
```

## 🗺️ Roadmap MVP

### Fase 1: Fundação (Semanas 1-2)
- [x] Setup inicial do projeto
- [ ] Configuração Supabase (schema + auth)
- [ ] Integração OpenAI (embeddings + chat)
- [ ] Sistema de upload de documentos

### Fase 2: Onboarding & Knowledge Base (Semanas 3-4)
- [ ] Parser de documentos (PDF, Excel, TXT)
- [ ] Web scraper básico
- [ ] Pipeline de embeddings
- [ ] Sistema RAG funcional

### Fase 3: Personas & IA (Semanas 5-6)
- [ ] Gerador automático de personas
- [ ] Integração Vapi.ai
- [ ] Sistema de chamadas de voz
- [ ] RAG em tempo real durante chamadas

### Fase 4: Feedback & Analytics (Semanas 7-8)
- [ ] Analisador de transcrições
- [ ] Engine de scoring
- [ ] Dashboard gerencial
- [ ] Gráficos de performance

### Fase 5: Polish & Deploy (Semana 9-10)
- [ ] Testes end-to-end
- [ ] Otimizações de performance
- [ ] Documentação completa
- [ ] Deploy em produção

## 🤝 Contribuindo

```bash
# 1. Fork o projeto
# 2. Crie uma branch para sua feature
git checkout -b feature/nova-funcionalidade

# 3. Commit suas mudanças (use Conventional Commits)
git commit -m "feat: adiciona gerador de personas"

# 4. Push para a branch
git push origin feature/nova-funcionalidade

# 5. Abra um Pull Request
```

### Conventional Commits

- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Documentação
- `refactor:` Refatoração de código
- `test:` Testes
- `chore:` Tarefas gerais (build, configs, etc)

## 📚 Documentação

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Arquitetura completa do sistema
- **[API.md](docs/API.md)** - Documentação de todos os endpoints
- **[DOCKER.md](docs/DOCKER.md)** - Guia completo de Docker (dev + prod)
- **[DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Deploy em produção (Railway + Vercel)

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

## 📞 Suporte

- **Documentação**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/seu-usuario/sales-ai-dojo/issues)
- **Email**: suporte@salesaidojo.com

---

Feito com ❤️ para revolucionar o treinamento de vendas
