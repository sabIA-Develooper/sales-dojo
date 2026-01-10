# Sales AI Dojo - API Documentation

## Base URL

```
Production: https://api.salesaidojo.com/api/v1
Development: http://localhost:8000/api/v1
```

## Authentication

Todos os endpoints (exceto `/auth/register` e `/auth/login`) requerem autenticação via JWT token.

**Header:**
```
Authorization: Bearer <your_jwt_token>
```

## Response Format

### Success Response

```json
{
  "data": { ... },
  "message": "Success message"
}
```

### Error Response

```json
{
  "detail": "Error description",
  "message": "User-friendly message"
}
```

---

## Authentication Endpoints

### POST /auth/register

Registra novo usuário no sistema.

**Request Body:**
```json
{
  "email": "joao@empresa.com",
  "password": "senha123",
  "full_name": "João Silva",
  "company_id": "uuid-da-empresa",
  "role": "salesperson"  // ou "manager", "admin"
}
```

**Response:** `201 Created`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "joao@empresa.com",
    "full_name": "João Silva",
    "role": "salesperson",
    "company_id": "uuid-da-empresa",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### POST /auth/login

Autentica usuário e retorna token.

**Request Body:**
```json
{
  "email": "joao@empresa.com",
  "password": "senha123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": { ... }
}
```

### POST /auth/logout

Invalida token do usuário.

**Response:** `200 OK`
```json
{
  "message": "Logged out successfully"
}
```

### GET /auth/me

Retorna informações do usuário autenticado.

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "email": "joao@empresa.com",
  "full_name": "João Silva",
  "role": "salesperson",
  "company_id": "uuid-da-empresa",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

## Onboarding Endpoints

### POST /onboarding/upload-documents

Upload de documentos para knowledge base.

**Request:** `multipart/form-data`
```
files: [File, File, ...]
```

**Response:** `200 OK`
```json
[
  {
    "file_id": "doc-uuid",
    "filename": "catalogo.pdf",
    "file_size_bytes": 1024000,
    "status": "success",
    "message": "File processed successfully. 15 chunks stored."
  }
]
```

### POST /onboarding/scrape-website

Inicia scraping de website.

**Request Body:**
```json
{
  "company_id": "uuid-da-empresa",
  "url": "https://empresa.com.br",
  "max_pages": 20,
  "include_subdomains": false
}
```

**Response:** `200 OK`
```json
{
  "job_id": "scrape-uuid",
  "status": "queued",
  "pages_scraped": 0,
  "entries_created": 0,
  "message": "Scraping job queued"
}
```

### GET /onboarding/status/{company_id}

Obtém status do onboarding.

**Response:** `200 OK`
```json
{
  "company_id": "uuid-da-empresa",
  "total_documents": 5,
  "total_kb_entries": 47,
  "total_embeddings": 47,
  "last_updated": "2024-01-15T14:30:00Z",
  "is_ready": true
}
```

### DELETE /onboarding/documents/{source_name}

Remove documento da knowledge base.

**Response:** `200 OK`
```json
{
  "message": "Document removed successfully",
  "source_name": "catalogo.pdf",
  "entries_deleted": 15
}
```

---

## Personas Endpoints

### POST /personas/generate

Gera personas automaticamente usando IA.

**Request Body:**
```json
{
  "company_id": "uuid-da-empresa",
  "count": 5,
  "context": "Empresa de software B2B para varejo"
}
```

**Response:** `200 OK`
```json
{
  "personas": [
    {
      "id": "persona-uuid",
      "company_id": "uuid-da-empresa",
      "name": "Carlos Oliveira",
      "role": "decision_maker",
      "personality_traits": {
        "analytical": true,
        "risk_averse": true,
        "budget_conscious": true
      },
      "pain_points": [
        "Sistema atual é lento",
        "Falta integração com ERP"
      ],
      "objections": [
        "Preço muito alto",
        "Implementação demora muito"
      ],
      "background": "CTO de rede de supermercados com 50 lojas",
      "created_at": "2024-01-15T15:00:00Z"
    }
  ],
  "total_generated": 5
}
```

### GET /personas

Lista todas as personas da empresa.

**Response:** `200 OK`
```json
[
  {
    "id": "persona-uuid",
    "company_id": "uuid-da-empresa",
    "name": "Carlos Oliveira",
    "role": "decision_maker",
    ...
  }
]
```

### GET /personas/random

Retorna persona aleatória.

**Response:** `200 OK`
```json
{
  "id": "persona-uuid",
  "name": "Carlos Oliveira",
  ...
}
```

### GET /personas/{persona_id}

Obtém detalhes de persona específica.

**Response:** `200 OK`
```json
{
  "id": "persona-uuid",
  "name": "Carlos Oliveira",
  ...
}
```

### POST /personas

Cria persona manualmente.

**Request Body:**
```json
{
  "company_id": "uuid-da-empresa",
  "name": "Maria Santos",
  "role": "influencer",
  "personality_traits": { ... },
  "pain_points": [ ... ],
  "objections": [ ... ],
  "background": "Gerente de TI"
}
```

**Response:** `201 Created`
```json
{
  "id": "persona-uuid",
  "name": "Maria Santos",
  ...
}
```

### PUT /personas/{persona_id}

Atualiza persona existente.

**Request Body:**
```json
{
  "name": "Maria Santos Silva",
  "objections": ["Novo valor"]
}
```

**Response:** `200 OK`
```json
{
  "id": "persona-uuid",
  "name": "Maria Santos Silva",
  ...
}
```

### DELETE /personas/{persona_id}

Remove persona.

**Response:** `200 OK`
```json
{
  "message": "Persona deleted successfully",
  "persona_id": "persona-uuid"
}
```

---

## Training Sessions Endpoints

### POST /sessions/start

Inicia nova sessão de treinamento.

**Request Body:**
```json
{
  "persona_id": "persona-uuid"  // opcional, se não enviado seleciona aleatória
}
```

**Response:** `200 OK`
```json
{
  "session_id": "session-uuid",
  "persona_id": "persona-uuid",
  "vapi_call_id": "vapi-call-uuid",
  "call_url": "https://vapi.ai/call/..."
}
```

### POST /sessions/{session_id}/end

Finaliza sessão de treinamento.

**Request Body:**
```json
{
  "duration_seconds": 420,
  "transcript": {
    "messages": [
      {"role": "assistant", "content": "Olá, aqui é Carlos..."},
      {"role": "user", "content": "Oi Carlos, tudo bem?"}
    ]
  }
}
```

**Response:** `200 OK`
```json
{
  "message": "Session ended successfully",
  "session_id": "session-uuid"
}
```

### GET /sessions/{session_id}

Obtém detalhes de sessão.

**Response:** `200 OK`
```json
{
  "id": "session-uuid",
  "user_id": "user-uuid",
  "company_id": "company-uuid",
  "persona_id": "persona-uuid",
  "vapi_call_id": "vapi-call-uuid",
  "transcript": { ... },
  "duration_seconds": 420,
  "status": "completed",
  "created_at": "2024-01-15T16:00:00Z"
}
```

### GET /sessions

Lista sessões do usuário.

**Query Parameters:**
- `limit` (int, default 20): Máximo de resultados
- `offset` (int, default 0): Paginação

**Response:** `200 OK`
```json
[
  {
    "id": "session-uuid",
    "persona_id": "persona-uuid",
    "duration_seconds": 420,
    "status": "completed",
    "created_at": "2024-01-15T16:00:00Z"
  }
]
```

### GET /sessions/stats/me

Estatísticas das sessões do usuário.

**Response:** `200 OK`
```json
{
  "total_sessions": 15,
  "completed_sessions": 12,
  "abandoned_sessions": 3,
  "total_duration_seconds": 6300,
  "average_duration_seconds": 420,
  "average_score": 78.5
}
```

---

## Feedback Endpoints

### GET /feedback/{session_id}

Obtém feedback de uma sessão.

**Response:** `200 OK`
```json
{
  "id": "feedback-uuid",
  "session_id": "session-uuid",
  "overall_score": 78.5,
  "strengths": [
    "Boa construção de rapport",
    "Perguntas de descoberta eficazes"
  ],
  "areas_for_improvement": [
    "Tratar objeções com mais empatia",
    "Melhorar técnica de fechamento"
  ],
  "detailed_analysis": {
    "rapport": {
      "score": 85,
      "feedback": "Excelente abertura, criou conexão rápida"
    },
    "discovery": {
      "score": 80,
      "feedback": "Boas perguntas, poderia aprofundar mais"
    },
    "objection_handling": {
      "score": 70,
      "feedback": "Respondeu objeções mas faltou empatia"
    },
    "closing": {
      "score": 75,
      "feedback": "Tentou fechar mas não foi assertivo"
    }
  },
  "created_at": "2024-01-15T16:10:00Z"
}
```

### POST /feedback/regenerate

Regenera feedback de uma sessão.

**Request Body:**
```json
{
  "session_id": "session-uuid",
  "focus_areas": ["objection_handling", "closing"]
}
```

**Response:** `200 OK`
```json
{
  "id": "feedback-uuid",
  "overall_score": 80.0,
  ...
}
```

---

## Dashboard Endpoints

### GET /dashboard/metrics

Métricas gerais da equipe.

**Query Parameters:**
- `start_date` (ISO 8601): Data início
- `end_date` (ISO 8601): Data fim

**Response:** `200 OK`
```json
{
  "total_sessions": 150,
  "average_score": 76.8,
  "total_duration_minutes": 1050,
  "top_performers": [
    {
      "user_id": "user-uuid",
      "user_name": "João Silva",
      "average_score": 88.5,
      "total_sessions": 20
    }
  ],
  "score_distribution": {
    "0-50": 5,
    "50-70": 30,
    "70-85": 80,
    "85-100": 35
  },
  "sessions_over_time": [
    {"date": "2024-01-10", "count": 15},
    {"date": "2024-01-11", "count": 18}
  ]
}
```

### GET /dashboard/leaderboard

Ranking da equipe.

**Query Parameters:**
- `limit` (int, default 10): Quantos usuários mostrar

**Response:** `200 OK`
```json
[
  {
    "rank": 1,
    "user_id": "user-uuid",
    "user_name": "João Silva",
    "average_score": 88.5,
    "total_sessions": 20,
    "best_category": "rapport"
  }
]
```

---

## Error Codes

| Code | Description |
|------|-------------|
| 400  | Bad Request - Dados inválidos |
| 401  | Unauthorized - Token inválido ou expirado |
| 403  | Forbidden - Sem permissão para acessar recurso |
| 404  | Not Found - Recurso não encontrado |
| 422  | Unprocessable Entity - Erro de validação Pydantic |
| 500  | Internal Server Error - Erro no servidor |

---

## Rate Limiting

- **Default:** 60 requests/minuto por usuário
- **Headers de resposta:**
  - `X-RateLimit-Limit`: Limite de requests
  - `X-RateLimit-Remaining`: Requests restantes
  - `X-RateLimit-Reset`: Timestamp do reset

---

## Webhooks (Vapi)

### POST /webhooks/vapi

Recebe eventos do Vapi.ai.

**Events:**
- `call.started`: Chamada iniciada
- `call.ended`: Chamada finalizada
- `call.transcript`: Atualização de transcrição
- `assistant.request`: IA precisa de contexto (RAG)

**Request Body (exemplo assistant.request):**
```json
{
  "event": "assistant.request",
  "call_id": "vapi-call-uuid",
  "message": "Qual o prazo de entrega?",
  "metadata": {
    "session_id": "session-uuid",
    "company_id": "company-uuid"
  }
}
```

**Response:** `200 OK`
```json
{
  "context": "Prazo de entrega padrão é 15 dias úteis..."
}
```

---

## Testing

Use o **Swagger UI** para testar endpoints:
```
http://localhost:8000/docs
```

Ou **ReDoc:**
```
http://localhost:8000/redoc
```

---

## SDKs

### JavaScript/TypeScript

```typescript
import api from '@/lib/api';

// Login
const response = await api.authAPI.login({
  email: 'joao@empresa.com',
  password: 'senha123'
});

// Start session
const session = await api.sessionsAPI.start({
  persona_id: 'persona-uuid'
});
```

### Python (futuro)

```python
from sales_dojo_sdk import SalesDojo

client = SalesDojo(api_key="your-api-key")

# Start session
session = client.sessions.start(persona_id="persona-uuid")
```
