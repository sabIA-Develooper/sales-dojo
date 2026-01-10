# Deployment Guide - Sales AI Dojo

Este guia detalha como fazer deploy da aplicação em produção.

## Pré-requisitos

- Conta no [Railway](https://railway.app/) (backend)
- Conta no [Vercel](https://vercel.com/) (frontend)
- Conta no [Supabase](https://supabase.com/) (banco de dados)
- Chaves de API configuradas:
  - OpenAI API Key
  - Vapi.ai API Key
  - Deepgram API Key
  - ElevenLabs API Key

---

## 1. Setup do Supabase

### 1.1 Criar Projeto

1. Acesse [Supabase Dashboard](https://app.supabase.com/)
2. Clique em "New Project"
3. Preencha:
   - Name: `sales-ai-dojo-prod`
   - Database Password: (senha forte)
   - Region: escolha mais próxima

### 1.2 Habilitar pgvector

No SQL Editor, execute:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 1.3 Criar Tabelas

Execute o script SQL completo (disponível em `docs/sql/schema.sql`):

```sql
-- Companies
CREATE TABLE companies (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  website TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Users
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  full_name TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('salesperson', 'manager', 'admin')),
  company_id UUID REFERENCES companies(id),
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Knowledge Base
CREATE TABLE knowledge_base (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID REFERENCES companies(id),
  content TEXT NOT NULL,
  source_type TEXT,
  source_name TEXT,
  embedding vector(1536),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX ON knowledge_base USING ivfflat (embedding vector_cosine_ops);

-- Personas
CREATE TABLE personas (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID REFERENCES companies(id),
  name TEXT NOT NULL,
  role TEXT NOT NULL,
  personality_traits JSONB,
  pain_points TEXT[],
  objections TEXT[],
  background TEXT,
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
  status TEXT DEFAULT 'ongoing',
  created_at TIMESTAMP DEFAULT NOW()
);

-- Feedback
CREATE TABLE feedback (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  session_id UUID REFERENCES training_sessions(id),
  overall_score FLOAT,
  strengths TEXT[],
  areas_for_improvement TEXT[],
  detailed_analysis JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### 1.4 Criar Função de Busca Vetorial

```sql
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding vector(1536),
    match_threshold float,
    match_count int,
    company_id uuid
)
RETURNS TABLE (
    id uuid,
    content text,
    source_type text,
    source_name text,
    similarity float
)
LANGUAGE sql STABLE
AS $$
    SELECT
        knowledge_base.id,
        knowledge_base.content,
        knowledge_base.source_type,
        knowledge_base.source_name,
        1 - (knowledge_base.embedding <=> query_embedding) as similarity
    FROM knowledge_base
    WHERE knowledge_base.company_id = match_documents.company_id
        AND 1 - (knowledge_base.embedding <=> query_embedding) > match_threshold
    ORDER BY similarity DESC
    LIMIT match_count;
$$;
```

### 1.5 Configurar Row Level Security (RLS)

```sql
-- Habilita RLS
ALTER TABLE knowledge_base ENABLE ROW LEVEL SECURITY;
ALTER TABLE personas ENABLE ROW LEVEL SECURITY;
ALTER TABLE training_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;

-- Policies (exemplos)
CREATE POLICY "Users can view their company's knowledge"
  ON knowledge_base FOR SELECT
  USING (company_id = (SELECT company_id FROM users WHERE id = auth.uid()));
```

### 1.6 Obter Credenciais

No Supabase Dashboard → Settings → API:
- `SUPABASE_URL`: Project URL
- `SUPABASE_KEY`: anon/public key
- `SUPABASE_JWT_SECRET`: JWT Secret (em Settings → API → JWT Settings)

---

## 2. Deploy Backend (Railway)

### 2.1 Conectar Repositório

1. Acesse [Railway Dashboard](https://railway.app/dashboard)
2. Clique em "New Project"
3. Escolha "Deploy from GitHub repo"
4. Selecione o repositório `sales-ai-dojo`
5. Configure:
   - Root Directory: `backend`
   - Build Command: (Railway detecta automaticamente)
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 2.2 Configurar Variáveis de Ambiente

Em Settings → Variables, adicione:

```
OPENAI_API_KEY=sk-...
VAPI_API_KEY=...
DEEPGRAM_API_KEY=...
ELEVENLABS_API_KEY=...

SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...
SUPABASE_JWT_SECRET=your-jwt-secret

ENVIRONMENT=production
DEBUG=false
API_V1_PREFIX=/api/v1
ALLOWED_ORIGINS=https://sales-ai-dojo.vercel.app,https://www.salesaidojo.com
```

### 2.3 Deploy

- Railway faz deploy automático quando você faz push para `main`
- URL gerada: `https://sales-ai-dojo-production.up.railway.app`

### 2.4 Configurar Domínio Customizado (opcional)

1. Em Settings → Networking
2. Adicione domínio: `api.salesaidojo.com`
3. Configure DNS no seu provedor:
   ```
   CNAME api railway.app
   ```

---

## 3. Deploy Frontend (Vercel)

### 3.1 Conectar Repositório

1. Acesse [Vercel Dashboard](https://vercel.com/dashboard)
2. Clique em "Add New Project"
3. Import do GitHub: `sales-ai-dojo`
4. Configure:
   - Framework Preset: Next.js
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: (padrão)

### 3.2 Configurar Variáveis de Ambiente

Em Settings → Environment Variables:

```
NEXT_PUBLIC_API_URL=https://sales-ai-dojo-production.up.railway.app/api/v1
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
```

### 3.3 Deploy

- Vercel faz deploy automático em cada push para `main`
- URL gerada: `https://sales-ai-dojo.vercel.app`

### 3.4 Configurar Domínio Customizado

1. Em Settings → Domains
2. Adicione: `www.salesaidojo.com`
3. Configure DNS:
   ```
   CNAME www cname.vercel-dns.com
   ```

---

## 4. Configurar APIs Externas

### 4.1 OpenAI

1. Acesse [OpenAI Platform](https://platform.openai.com/)
2. Crie API Key
3. Configure billing
4. Monitore usage em Dashboard

### 4.2 Vapi.ai

1. Acesse [Vapi.ai Dashboard](https://dashboard.vapi.ai/)
2. Crie API Key
3. Configure webhooks:
   - Endpoint: `https://api.salesaidojo.com/webhooks/vapi`
   - Events: `call.started`, `call.ended`, `assistant.request`
4. (Opcional) Configure phone number para outbound calls

### 4.3 Deepgram

1. Acesse [Deepgram Console](https://console.deepgram.com/)
2. Crie API Key
3. Habilita modelo `nova-2` para português

### 4.4 ElevenLabs

1. Acesse [ElevenLabs](https://elevenlabs.io/)
2. Crie API Key
3. Escolha vozes para usar nas personas

---

## 5. Monitoramento

### 5.1 Logs

**Railway (Backend):**
- Acesse Deployments → View Logs
- Filtre por nível (INFO, ERROR, etc)

**Vercel (Frontend):**
- Acesse Deployments → Function Logs
- Veja erros de runtime

### 5.2 Uptime Monitoring

Configure um serviço como [UptimeRobot](https://uptimerobot.com/):

- Backend: `https://api.salesaidojo.com/health`
- Frontend: `https://www.salesaidojo.com`

### 5.3 Error Tracking

Recomendado integrar [Sentry](https://sentry.io/):

**Backend:**
```python
import sentry_sdk
sentry_sdk.init(dsn="your-dsn")
```

**Frontend:**
```typescript
import * as Sentry from '@sentry/nextjs';
Sentry.init({ dsn: 'your-dsn' });
```

### 5.4 Analytics

Para OpenAI usage:
- Dashboard → Usage → View details
- Configure billing alerts

Para Vapi:
- Dashboard → Analytics
- Monitore call duration, costs

---

## 6. CI/CD

Os workflows do GitHub Actions já estão configurados em `.github/workflows/`.

### 6.1 Secrets do GitHub

Configure em Settings → Secrets and variables → Actions:

```
OPENAI_API_KEY_TEST
SUPABASE_URL_TEST
SUPABASE_KEY_TEST
```

### 6.2 Auto-Deploy

- **Main branch:** Deploy automático para produção
- **Develop branch:** Deploy para staging (configurar separadamente)
- **Pull Requests:** Preview deploy no Vercel

---

## 7. Backups

### 7.1 Banco de Dados

Supabase faz backup automático diário (retenção de 7 dias no free tier).

**Manual backup:**
```bash
pg_dump "postgresql://user:pass@host:5432/db" > backup.sql
```

### 7.2 Documentos Uploaded

Configure backup do Supabase Storage:
- Em Storage → Buckets → Configure
- Habilita Automatic Backup (planos pagos)

---

## 8. Escalabilidade

### 8.1 Backend

**Railway:**
- Escala verticalmente até 8GB RAM
- Para mais, migre para AWS/GCP com Docker

**Otimizações:**
- Use Redis para cache de embeddings
- Connection pooling no Supabase
- Rate limiting por usuário

### 8.2 Frontend

**Vercel:**
- Escala automaticamente (serverless)
- CDN global
- Edge Functions para latência baixa

### 8.3 Banco de Dados

**Supabase:**
- Upgrade para plano Pro (8GB RAM, 2 CPUs)
- Read replicas para analytics
- Connection pooler (Supavisor)

---

## 9. Custos Estimados (MVP)

| Serviço | Plano | Custo/mês |
|---------|-------|-----------|
| Railway | Hobby | $5 |
| Vercel | Free | $0 |
| Supabase | Free | $0 |
| OpenAI | Pay-as-you-go | $50-200 |
| Vapi.ai | Pay-as-you-go | $100-300 |
| Deepgram | Free tier | $0 |
| ElevenLabs | Starter | $5 |
| **Total** | | **$160-510** |

**Após escalar (100 usuários ativos):**
- Railway: $20
- Supabase Pro: $25
- OpenAI: $500-1000
- Vapi: $500-1000
- **Total: ~$1500-2500/mês**

---

## 10. Checklist de Deploy

- [ ] Supabase configurado com todas as tabelas
- [ ] Função `match_documents` criada
- [ ] RLS policies aplicadas
- [ ] Backend no Railway com variáveis configuradas
- [ ] Frontend no Vercel com variáveis configuradas
- [ ] Domínios customizados configurados
- [ ] Webhooks do Vapi apontando para backend
- [ ] OpenAI API key com billing configurado
- [ ] Monitoring configurado (UptimeRobot)
- [ ] Error tracking configurado (Sentry)
- [ ] GitHub Actions rodando sem erros
- [ ] Teste end-to-end funcionando
- [ ] Documentação atualizada

---

## 11. Troubleshooting

### Backend não inicia

```bash
# Verificar logs
railway logs

# Testar localmente
docker-compose up backend
```

### Frontend não conecta na API

- Verifique CORS no backend (ALLOWED_ORIGINS)
- Confirme NEXT_PUBLIC_API_URL correto
- Teste endpoint: `curl https://api.salesaidojo.com/health`

### Embeddings não funcionam

- Confirme OpenAI API key válida
- Verifique pgvector instalado: `SELECT * FROM pg_extension WHERE extname = 'vector';`
- Teste busca vetorial: `SELECT match_documents(...)`

### Chamadas Vapi falhando

- Verifique Vapi API key
- Confirme webhooks configurados
- Tente chamada de teste no Dashboard do Vapi

---

## Suporte

- **Issues:** [GitHub Issues](https://github.com/seu-usuario/sales-ai-dojo/issues)
- **Docs:** [docs/](../docs/)
- **Email:** suporte@salesaidojo.com
