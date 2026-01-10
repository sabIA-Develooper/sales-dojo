# Arquitetura do Sales AI Dojo

## Visão Geral

Sales AI Dojo é uma aplicação full-stack dividida em backend (FastAPI) e frontend (Next.js), com integração de múltiplos serviços de IA para criar uma experiência de treinamento de vendas imersiva.

## Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Next.js 14)                   │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐ │
│  │   Login/   │  │  Vendedor  │  │  Gerente   │  │   Admin  │ │
│  │  Register  │  │    Pages   │  │   Pages    │  │   Pages  │ │
│  └────────────┘  └────────────┘  └────────────┘  └──────────┘ │
│         │                │                │              │       │
│         └────────────────┴────────────────┴──────────────┘       │
│                              │                                   │
│                      API Client (axios)                          │
└──────────────────────────────┬──────────────────────────────────┘
                               │ HTTP/REST
┌──────────────────────────────┴──────────────────────────────────┐
│                      BACKEND (FastAPI)                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                     API Routes                           │   │
│  │  /auth  /onboarding  /personas  /sessions  /feedback    │   │
│  └───────────────────────┬─────────────────────────────────┘   │
│                          │                                       │
│  ┌───────────────────────┴─────────────────────────────────┐   │
│  │                   Services Layer                         │   │
│  │  ┌─────────────┐  ┌──────────┐  ┌─────────────────┐   │   │
│  │  │   OpenAI    │  │   Vapi   │  │   Embeddings    │   │   │
│  │  │   Service   │  │  Service │  │    Service      │   │   │
│  │  └─────────────┘  └──────────┘  └─────────────────┘   │   │
│  │  ┌─────────────┐  ┌──────────┐  ┌─────────────────┐   │   │
│  │  │     RAG     │  │ Document │  │     Persona     │   │   │
│  │  │   Service   │  │ Processor│  │    Generator    │   │   │
│  │  └─────────────┘  └──────────┘  └─────────────────┘   │   │
│  └───────────────────────┬─────────────────────────────────┘   │
└──────────────────────────┼──────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼────────┐  ┌──────▼──────┐  ┌───────▼────────┐
│   Supabase     │  │   OpenAI    │  │    Vapi.ai     │
│  PostgreSQL    │  │   GPT-4o    │  │   (Voice AI)   │
│  + pgvector    │  │  Embeddings │  │                │
└────────────────┘  └─────────────┘  └────────────────┘
```

## Componentes Principais

### 1. Frontend (Next.js 14)

**Stack:**
- Next.js 14 com App Router
- TypeScript (strict mode)
- TailwindCSS + shadcn/ui
- Axios para HTTP
- Zustand para gerenciamento de estado

**Estrutura de Páginas:**

```
app/
├── (auth)/              # Grupo de rotas públicas
│   ├── login/
│   └── register/
├── (dashboard)/         # Grupo de rotas protegidas
│   ├── vendedor/
│   │   ├── cenarios/    # Escolher persona
│   │   ├── sessao/      # Chamada em andamento
│   │   └── historico/   # Ver sessões anteriores
│   └── gerente/
│       ├── equipe/      # Dashboard da equipe
│       ├── onboarding/  # Upload docs, gerar personas
│       └── cenarios/    # Gerenciar personas
├── components/
│   ├── ui/              # Componentes shadcn/ui
│   ├── VoiceCall/       # Componente de chamada de voz
│   ├── FeedbackCard/    # Exibir feedback
│   └── MetricsChart/    # Gráficos de métricas
├── lib/
│   ├── api.ts           # Cliente HTTP
│   └── utils.ts         # Utilitários
└── types/
    └── index.ts         # Type definitions
```

### 2. Backend (FastAPI)

**Stack:**
- Python 3.11+
- FastAPI (async)
- Supabase Client (PostgreSQL + Auth)
- OpenAI API
- Pydantic V2 para validação

**Arquitetura em Camadas:**

```
app/
├── main.py              # Entry point, app configuration
├── core/
│   ├── config.py        # Settings com pydantic-settings
│   ├── database.py      # Supabase client singleton
│   └── dependencies.py  # Dependency injection (auth, etc)
├── api/
│   ├── routes/          # Endpoints REST
│   └── webhooks/        # Vapi webhooks
├── services/            # Business logic
│   ├── openai_service.py
│   ├── call/
│   │   ├── vapi_orchestrator.py
│   │   └── rag_service.py
│   ├── onboarding/
│   │   ├── document_processor.py
│   │   └── embedding_service.py
│   └── persona/
│       └── generator.py
├── models/              # Pydantic schemas
└── utils/
    ├── logger.py
    └── validators.py
```

### 3. Banco de Dados (Supabase)

**PostgreSQL com pgvector:**

```sql
-- Tabelas principais:
companies               # Empresas
users                   # Usuários (vinculados ao Supabase Auth)
knowledge_base          # Documentos com embeddings (vector column)
personas                # Personas de clientes geradas
training_sessions       # Sessões de treinamento
feedback                # Feedback e scoring das sessões

-- Índice vetorial para busca de similaridade:
CREATE INDEX ON knowledge_base USING ivfflat (embedding vector_cosine_ops);

-- Função RPC para busca vetorial:
match_documents(query_embedding, match_threshold, match_count, company_id)
```

## Fluxos de Dados

### Fluxo 1: Onboarding

1. **Gerente faz upload de documentos** → `/api/v1/onboarding/upload-documents`
2. **Backend processa arquivos:**
   - `DocumentProcessor` extrai texto (PDF, DOCX, etc)
   - Divide em chunks de ~1000 caracteres
3. **Gera embeddings:**
   - `EmbeddingService` chama OpenAI embeddings API
   - Armazena no `knowledge_base` com vector column
4. **Status atualizado:**
   - Gerente pode ver quantos documentos e embeddings foram criados

### Fluxo 2: Geração de Personas

1. **Gerente solicita geração** → `/api/v1/personas/generate`
2. **Backend busca contexto:**
   - Pega amostra do knowledge_base da empresa
3. **OpenAI gera personas:**
   - GPT-4o recebe contexto e gera 5-10 personas diferentes
   - Cada uma com nome, role, traços, objeções, etc
4. **Armazena no banco:**
   - Personas salvas na tabela `personas`

### Fluxo 3: Sessão de Treinamento

1. **Vendedor inicia sessão** → `/api/v1/sessions/start`
2. **Backend seleciona persona:**
   - Aleatória ou específica
3. **Cria chamada no Vapi.ai:**
   - `VapiOrchestratorService.create_training_call()`
   - Configura assistente com:
     - Instructions baseadas na persona
     - Voice (ElevenLabs)
     - Transcriber (Deepgram)
4. **Chamada em tempo real:**
   - Frontend conecta via WebRTC
   - Durante conversa, Vapi pode chamar nosso backend via webhook para RAG
5. **RAG em tempo real (opcional):**
   - Vapi envia pergunta do cliente → nosso webhook
   - `RAGService.search()` busca contexto relevante
   - Retorna para Vapi incluir na resposta
6. **Fim da chamada:**
   - Vendedor encerra → `/api/v1/sessions/{id}/end`
   - Transcrição salva no banco

### Fluxo 4: Feedback e Análise

1. **Backend analisa transcrição:**
   - `OpenAIService.analyze_transcript()`
   - GPT-4o avalia:
     - Rapport (construção de relacionamento)
     - Discovery (perguntas de descoberta)
     - Objection Handling (tratamento de objeções)
     - Closing (fechamento)
2. **Gera feedback estruturado:**
   - Score geral (0-100)
   - Scores por categoria
   - Pontos fortes
   - Áreas de melhoria
   - Recomendações
3. **Armazena no banco:**
   - Tabela `feedback`
4. **Frontend exibe:**
   - Cards com scores
   - Gráficos de evolução
   - Comparação com média da equipe

## Decisões Arquiteturais

### Por que Supabase?

- **PostgreSQL robusto** com pgvector para embeddings
- **Auth nativo** (JWT, RLS)
- **Storage** para documentos
- **Webhooks** e real-time (futuro)
- **Managed service** (menos overhead operacional)

### Por que FastAPI?

- **Async nativo** (importante para I/O com IA)
- **Type hints** e validação automática (Pydantic)
- **Docs auto-geradas** (OpenAPI)
- **Performance** comparável a Node.js
- **Ecossistema Python** para IA (OpenAI, ML libs)

### Por que Next.js 14?

- **App Router** moderno (Server Components)
- **TypeScript** first-class
- **Performance** excelente (SSR, ISR, streaming)
- **Deploy fácil** (Vercel)
- **Ecossistema** rico (shadcn/ui, etc)

### Por que RAG?

- **Conhecimento específico** da empresa sem re-treinar modelo
- **Respostas mais precisas** baseadas em docs reais
- **Escalável** (apenas adiciona embeddings)
- **Atualização fácil** (upload novo doc = novos embeddings)

## Integrações Externas

### OpenAI

**Uso:**
- **GPT-4o:** Análise de transcrições, geração de personas, instruções para Vapi
- **text-embedding-3-small:** Geração de embeddings (1536 dimensões)

**Rate Limits:**
- Monitora tokens por minuto (TPM)
- Implementa retry com exponential backoff

### Vapi.ai

**Uso:**
- Orquestração de chamadas de voz
- Integra TTS (ElevenLabs) + STT (Deepgram) + LLM (OpenAI)
- Webhooks para eventos (call started, ended, etc)

**Config:**
- Assistant customizado por persona
- Recording habilitado
- Timeout de 10 minutos

### Deepgram

**Uso:**
- Speech-to-Text em português (BR)
- Modelo: nova-2
- Integrado via Vapi

### ElevenLabs

**Uso:**
- Text-to-Speech de alta qualidade
- Voz configurável por persona
- Integrado via Vapi

## Segurança

### Autenticação

- **Supabase Auth:** JWT tokens
- **Backend:** Valida JWT em cada request
- **Middleware:** `get_current_user` dependency

### Autorização

- **Role-based:** salesperson, manager, admin
- **Company isolation:** Usuário só acessa dados da própria empresa
- **Verificação:** `get_current_company_id` dependency

### Dados Sensíveis

- **API keys:** Nunca no código, sempre em `.env`
- **Passwords:** Hash com bcrypt (gerenciado pelo Supabase)
- **Tokens:** Expira em 1 hora (configurável)

## Escalabilidade

### Backend

- **Stateless:** Pode rodar múltiplas instâncias
- **Async I/O:** Suporta muitas conexões simultâneas
- **Connection pooling:** Supabase gerencia
- **Caching:** Pode adicionar Redis para sessions, embeddings frequentes

### Frontend

- **Static Generation:** Páginas públicas pré-renderizadas
- **CDN:** Vercel Edge Network
- **Code splitting:** Automático no Next.js
- **Lazy loading:** Componentes sob demanda

### Banco de Dados

- **Índice vetorial:** ivfflat para busca rápida
- **Partitioning:** Por company_id (futuro)
- **Backups:** Gerenciados pelo Supabase
- **Read replicas:** Disponível no Supabase Pro

## Monitoramento e Observabilidade

### Logs

- **Backend:** Python logging (estruturado)
- **Frontend:** Console + error boundaries
- **Agregação:** Pode integrar com Sentry, LogRocket

### Métricas

- **API:** Response time, error rate
- **Vapi:** Call duration, completion rate
- **OpenAI:** Tokens usage, cost tracking

### Health Checks

- **Backend:** `/health` e `/health/db`
- **Docker:** Healthcheck configurado
- **Monitoramento:** Pode integrar com UptimeRobot, Pingdom

## Deploy

### Railway (Backend)

```bash
railway up
# Auto-deploy on git push
```

### Vercel (Frontend)

```bash
vercel --prod
# Auto-deploy on git push to main
```

### Variáveis de Ambiente

**Backend:**
- Configurar no Railway dashboard
- Secrets seguros (nunca em logs)

**Frontend:**
- Configurar no Vercel dashboard
- `NEXT_PUBLIC_*` expostas ao browser

## Testes

### Backend

```bash
pytest tests/ -v
```

**Cobertura:**
- Unit tests para services
- Integration tests para API routes
- Mocks para OpenAI, Vapi

### Frontend

```bash
npm run test
```

**Cobertura:**
- Component tests (React Testing Library)
- E2E tests (Playwright - futuro)
- Integration tests para API client

## Roadmap Técnico

### Curto Prazo (MVP)

- [x] Setup completo do projeto
- [ ] Implementar todas as rotas críticas
- [ ] Frontend com componentes principais
- [ ] Integração completa Vapi
- [ ] Deploy em staging

### Médio Prazo

- [ ] Webhooks do Vapi para RAG em tempo real
- [ ] Dashboard analytics avançado
- [ ] Notificações em tempo real
- [ ] Exportação de relatórios (PDF)
- [ ] Testes automatizados completos

### Longo Prazo

- [ ] Multi-idioma
- [ ] Mobile app (React Native)
- [ ] Coaching IA personalizado
- [ ] Integração com CRMs
- [ ] Marketplace de personas

## Referências

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Next.js Docs](https://nextjs.org/docs)
- [Supabase Docs](https://supabase.com/docs)
- [OpenAI API](https://platform.openai.com/docs)
- [Vapi.ai Docs](https://docs.vapi.ai/)
