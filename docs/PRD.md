# PRD — Agenda Cultural

## 1. Visão Geral do Produto

### 1.1 Descrição
Plataforma que agrega e divulga eventos culturais locais — shows, exposições, peças de teatro, festivais e outros — permitindo que qualquer pessoa descubra o que acontece na cidade. Acessível via aplicativo mobile (React Native) e navegador web (React + Vite). Usuários cadastrados podem submeter novos eventos, que passam por aprovação de um administrador antes de serem publicados.

### 1.2 Problema
Eventos culturais locais são divulgados de forma fragmentada em redes sociais, sites individuais e boca a boca. Não existe um ponto centralizado onde cidadãos possam descobrir tudo que acontece na cidade de forma filtrada e organizada.

### 1.3 Solução
Uma plataforma multi-cliente (mobile + web) com:
- Listagem pública de eventos culturais com filtros por tipo, data e localização.
- Busca textual server-side via endpoint dedicado (não apenas filtragem no cliente).
- Cadastro de eventos por usuários autenticados, com fluxo de aprovação por administrador.
- Dashboard administrativo (web) para gerenciar eventos e solicitações pendentes.
- Acesso ao app do usuário comum tanto via mobile (React Native) quanto via navegador web (React + Vite).

### 1.4 Público-Alvo
- **Usuários finais**: Cidadãos interessados em cultura e entretenimento local.
- **Produtores culturais**: Artistas, coletivos e produtores que desejam divulgar seus eventos.
- **Administradores**: Equipe responsável por curadoria e moderação dos eventos publicados.

---

## 2. Objetivos e Métricas de Sucesso

| Objetivo | Métrica |
|---|---|
| Centralizar eventos culturais | Número de eventos cadastrados por mês |
| Engajar a comunidade | Número de usuários ativos mensais |
| Garantir qualidade do conteúdo | Tempo médio de aprovação de eventos |
| Facilitar descoberta | Taxa de uso dos filtros de busca |

---

## 3. Requisitos Funcionais

### 3.1 Módulo Público (sem autenticação)

| ID | Requisito | Prioridade |
|---|---|---|
| RF01 | Listar eventos aprovados na tela principal com: título, imagem (thumbnail), data, local e breve descrição | Alta |
| RF02 | Visualizar detalhes completos de um evento (título, descrição completa, data, hora início/fim, local com endereço, tipo/categoria, imagem, organizador) | Alta |
| RF03 | Filtrar eventos por categoria (show, exposição, peça, festival, outro) | Alta |
| RF04 | Filtrar eventos por data (hoje, esta semana, este mês, intervalo personalizado) | Alta |
| RF05 | Filtrar eventos por localização (bairro ou raio de distância) | Média |
| RF06 | Buscar eventos por texto (título, descrição) via endpoint server-side dedicado — a busca é feita no banco de dados, não no HTML/cliente | Alta |

### 3.2 Módulo de Autenticação

| ID | Requisito | Prioridade |
|---|---|---|
| RF07 | Cadastro de usuário com nome, e-mail e senha | Alta |
| RF08 | Login com e-mail e senha | Alta |
| RF09 | Logout | Alta |
| RF10 | Recuperação de senha por e-mail | Baixa |
| RF11 | Editar perfil (nome, e-mail) | Baixa |

### 3.3 Módulo de Eventos (usuário autenticado)

| ID | Requisito | Prioridade |
|---|---|---|
| RF12 | Cadastrar novo evento com: título, descrição, data, hora início, hora fim, local (nome + endereço), categoria, imagem | Alta |
| RF13 | Visualizar meus eventos submetidos e seus status (pendente, aprovado, rejeitado) | Alta |
| RF14 | Editar evento próprio (reenvia para aprovação se já aprovado). O sistema deve exibir um aviso claro ao usuário antes da edição: "Ao editar este evento, ele voltará para a fila de aprovação" | Média |
| RF15 | Cancelar/excluir evento próprio | Média |

### 3.4 Módulo Administrativo

| ID | Requisito | Prioridade |
|---|---|---|
| RF16 | Dashboard com visão geral: total de eventos, pendentes, aprovados, rejeitados, total de usuários | Alta |
| RF17 | Listar eventos pendentes de aprovação | Alta |
| RF18 | Aprovar evento pendente | Alta |
| RF19 | Rejeitar evento pendente (com motivo) | Alta |
| RF20 | Listar todos os eventos (com filtros por status) | Alta |
| RF21 | Editar qualquer evento | Média |
| RF22 | Excluir qualquer evento | Média |
| RF23 | Listar usuários cadastrados | Baixa |
| RF24 | Promover usuário a administrador | Baixa |

---

## 4. Requisitos Não Funcionais

| ID | Requisito | Detalhes |
|---|---|---|
| RNF01 | **Segurança** | Senhas armazenadas com Argon2 (via argon2-cffi). Autenticação via JWT com access token (15min) e refresh token (7 dias). |
| RNF02 | **Performance** | Listagem de eventos paginada (server-side) com resposta < 500ms. Busca textual via endpoint dedicado no backend (não no cliente). |
| RNF03 | **Multiplataforma** | App mobile (React Native/Expo) + versão web (React/Vite) para o usuário comum. Dashboard admin exclusivo via web. |
| RNF04 | **Disponibilidade** | Aplicação deve suportar deploy em ambiente single-server. |
| RNF05 | **Manutenibilidade** | Código modular com separação clara entre camadas. |
| RNF06 | **Banco de Dados** | PostgreSQL com migrações versionadas via Alembic. |
| RNF07 | **Armazenamento de Arquivos** | Upload de imagens via SeaweedFS (API compatível com S3). Imagens servidas diretamente pelo SeaweedFS via URL pública. |
| RNF08 | **Paginação** | Todos os endpoints de listagem devem ser paginados (server-side) com parâmetros `page` e `per_page`, retornando metadados de paginação (total, páginas, página atual). |

---

## 5. Regras de Negócio

| ID | Regra |
|---|---|
| RN01 | Eventos só aparecem na listagem pública após aprovação do administrador. |
| RN02 | Apenas usuários autenticados podem cadastrar eventos. |
| RN03 | Usuários comuns só podem editar/excluir seus próprios eventos. |
| RN04 | Ao editar um evento já aprovado, ele retorna ao status "pendente". O frontend deve exibir um modal/aviso explícito antes de confirmar a edição: "Atenção: ao salvar as alterações, seu evento voltará para a fila de aprovação e ficará temporariamente invisível na listagem pública." |
| RN05 | Administradores podem gerenciar qualquer evento. |
| RN06 | Um evento rejeitado deve conter o motivo da rejeição. |
| RN07 | Eventos com data passada são automaticamente marcados como "encerrado" na listagem. |
| RN08 | O primeiro usuário do sistema é criado como administrador (seed). |

---

## 6. Tecnologias

| Camada | Tecnologia | Justificativa |
|---|---|---|
| **Mobile** | React Native + Expo | Desenvolvimento cross-platform (iOS + Android) com uma única base de código |
| **Web (Usuário)** | React + Vite | Versão web do app para usuários comuns acessarem via navegador |
| **Web (Admin)** | React + Vite | Dashboard administrativo para gerenciar eventos e usuários |
| **Backend/API** | Python + FastAPI | Framework async moderno, com docs automática (Swagger/OpenAPI) |
| **ORM** | SQLAlchemy | ORM maduro com suporte completo a PostgreSQL |
| **Migrações** | Alembic | Controle de versão do schema do banco de dados |
| **Banco de Dados** | PostgreSQL | Banco relacional robusto com suporte a busca textual e dados geográficos |
| **Gerenciador de Pacotes (Python)** | UV | Gerenciador moderno e rápido para dependências Python |
| **Hash de Senhas** | Argon2 (argon2-cffi) | Algoritmo vencedor da Password Hashing Competition, mais seguro que bcrypt |
| **Autenticação** | JWT (PyJWT) | Tokens stateless para autenticação da API |
| **Upload de Imagens** | SeaweedFS | Object storage S3-compatible, self-hosted. Imagens servidas via URL pública do SeaweedFS |

---

## 7. Arquitetura

### 7.1 Visão Geral

Arquitetura **monolítica modular** com separação clara entre frontend e backend. O backend expõe uma API REST consumida por três clientes: app mobile, web do usuário e dashboard admin web.

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  React Native   │  │  React + Vite   │  │  React + Vite   │
│  (App Mobile)   │  │  (Web Usuário)  │  │  (Web Admin)    │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                     │
         └────────────────────┼─────────────────────┘
                              │ HTTP/REST
                       ┌──────▼──────┐
                       │   FastAPI   │
                       │  (Backend)  │
                       └──┬───────┬──┘
                          │       │
                ┌─────────▼──┐  ┌─▼───────────┐
                │ PostgreSQL │  │  SeaweedFS   │
                │  (Dados)   │  │  (Imagens)   │
                └────────────┘  └──────────────┘
```

### 7.2 Estrutura de Pastas

```
agenda-cultural/
├── frontend/
│   ├── mobile/                  # React Native (Expo)
│   │   ├── src/
│   │   │   ├── components/      # Componentes reutilizáveis
│   │   │   ├── screens/         # Telas do app
│   │   │   │   ├── HomeScreen.tsx
│   │   │   │   ├── EventDetailScreen.tsx
│   │   │   │   ├── LoginScreen.tsx
│   │   │   │   ├── RegisterScreen.tsx
│   │   │   │   ├── CreateEventScreen.tsx
│   │   │   │   ├── EditEventScreen.tsx
│   │   │   │   └── MyEventsScreen.tsx
│   │   │   ├── navigation/      # Configuração de rotas
│   │   │   ├── services/        # Chamadas à API
│   │   │   ├── hooks/           # Custom hooks
│   │   │   ├── contexts/        # Context API (auth, etc.)
│   │   │   ├── types/           # Tipagens TypeScript
│   │   │   └── utils/           # Funções utilitárias
│   │   ├── assets/
│   │   ├── app.json
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── web/                     # React + Vite (App Web Usuário)
│   │   ├── src/
│   │   │   ├── components/
│   │   │   ├── pages/
│   │   │   │   ├── HomePage.tsx
│   │   │   │   ├── EventDetailPage.tsx
│   │   │   │   ├── LoginPage.tsx
│   │   │   │   ├── RegisterPage.tsx
│   │   │   │   ├── CreateEventPage.tsx
│   │   │   │   ├── EditEventPage.tsx
│   │   │   │   └── MyEventsPage.tsx
│   │   │   ├── services/
│   │   │   ├── hooks/
│   │   │   ├── contexts/
│   │   │   ├── types/
│   │   │   └── utils/
│   │   ├── index.html
│   │   ├── package.json
│   │   ├── vite.config.ts
│   │   └── tsconfig.json
│   │
│   └── admin/                   # React + Vite (Dashboard Admin)
│       ├── src/
│       │   ├── components/
│       │   ├── pages/
│       │   │   ├── DashboardPage.tsx
│       │   │   ├── PendingEventsPage.tsx
│       │   │   ├── AllEventsPage.tsx
│       │   │   ├── UsersPage.tsx
│       │   │   └── LoginPage.tsx
│       │   ├── services/
│       │   ├── hooks/
│       │   ├── contexts/
│       │   ├── types/
│       │   └── utils/
│       ├── index.html
│       ├── package.json
│       ├── vite.config.ts
│       └── tsconfig.json
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # Ponto de entrada FastAPI
│   │   ├── config.py            # Configurações (env vars)
│   │   ├── database.py          # Conexão e sessão do banco
│   │   │
│   │   ├── models/              # Modelos SQLAlchemy (tabelas)
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── event.py
│   │   │   └── category.py
│   │   │
│   │   ├── schemas/             # Schemas Pydantic (request/response)
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── event.py
│   │   │   ├── category.py
│   │   │   └── auth.py
│   │   │
│   │   ├── routers/             # Endpoints agrupados por domínio
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── events.py
│   │   │   ├── users.py
│   │   │   ├── categories.py
│   │   │   ├── upload.py
│   │   │   └── admin.py
│   │   │
│   │   ├── services/            # Lógica de negócio
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── event_service.py
│   │   │   ├── user_service.py
│   │   │   └── storage_service.py  # Upload/download de imagens via SeaweedFS
│   │   │
│   │   └── dependencies/        # Dependências FastAPI (auth, db session)
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       └── database.py
│   │
│   ├── alembic/                 # Migrações do banco
│   │   ├── versions/
│   │   ├── env.py
│   │   └── alembic.ini
│   │
│   ├── tests/
│   │   ├── test_auth.py
│   │   ├── test_events.py
│   │   └── test_admin.py
│   │
│   ├── pyproject.toml           # Configuração do projeto (UV)
│   └── .env.example
│
├── docs/
│   └── PRD.md
│
└── README.md
```

### 7.3 Camadas do Backend

```
Routers (endpoints)  →  Services (lógica de negócio)  →  Models (banco de dados)
       ↕                        ↕
   Schemas                Dependencies
(validação I/O)          (auth, db session)
```

- **Routers**: Recebem requisições HTTP, validam entrada via Schemas, delegam para Services.
- **Services**: Contêm toda a lógica de negócio. Não conhecem HTTP.
- **Models**: Mapeamento ORM das tabelas do banco.
- **Schemas**: Validação e serialização de dados (Pydantic).
- **Dependencies**: Injeção de dependências do FastAPI (usuário autenticado, sessão do banco).

---

## 8. Modelagem de Dados

### 8.1 Diagrama de Tabelas (ER)

```
┌──────────────────────────┐       ┌──────────────────────────────────┐
│         users            │       │            categories            │
├──────────────────────────┤       ├──────────────────────────────────┤
│ id          UUID    [PK] │       │ id            UUID          [PK] │
│ name        VARCHAR(150) │       │ name          VARCHAR(100)       │
│ email       VARCHAR(255) │       │ description   TEXT               │
│ password    VARCHAR(255) │       │ created_at    TIMESTAMP          │
│ role        VARCHAR(20)  │       └──────────────┬───────────────────┘
│ is_active   BOOLEAN      │                      │
│ created_at  TIMESTAMP    │                      │
│ updated_at  TIMESTAMP    │                      │
└────────────┬─────────────┘                      │
             │                                    │
             │ 1:N                                │ 1:N
             │                                    │
┌────────────▼────────────────────────────────────▼───┐
│                       events                        │
├─────────────────────────────────────────────────────┤
│ id              UUID          [PK]                  │
│ title           VARCHAR(200)                        │
│ description     TEXT                                │
│ date            DATE                                │
│ start_time      TIME                                │
│ end_time        TIME (nullable)                     │
│ venue_name      VARCHAR(200)                        │
│ address         VARCHAR(300)                        │
│ neighborhood    VARCHAR(100)                        │
│ city            VARCHAR(100)                        │
│ image_url       VARCHAR(500) (nullable)             │
│ status          VARCHAR(20) [pendente|aprovado|     │
│                              rejeitado|cancelado]   │
│ rejection_reason TEXT (nullable)                    │
│ category_id     UUID [FK → categories.id]           │
│ created_by      UUID [FK → users.id]                │
│ reviewed_by     UUID [FK → users.id] (nullable)     │
│ reviewed_at     TIMESTAMP (nullable)                │
│ created_at      TIMESTAMP                           │
│ updated_at      TIMESTAMP                           │
└─────────────────────────────────────────────────────┘
```

### 8.2 Relacionamentos

| Origem | Destino | Tipo | Descrição |
|---|---|---|---|
| `events.created_by` | `users.id` | N:1 | Usuário que criou o evento |
| `events.reviewed_by` | `users.id` | N:1 | Admin que revisou o evento |
| `events.category_id` | `categories.id` | N:1 | Categoria do evento |

### 8.3 Índices Recomendados

- `events.status` — filtro frequente na listagem pública e admin.
- `events.date` — ordenação e filtro por data.
- `events.category_id` — filtro por categoria.
- `events.created_by` — listar "meus eventos".
- `users.email` — login e unicidade.

---

## 9. Diagrama de Classes

```
┌─────────────────────────────┐
│           User              │
├─────────────────────────────┤
│ - id: UUID                  │
│ - name: str                 │
│ - email: str                │
│ - password: str             │
│ - role: UserRole            │
│ - is_active: bool           │
│ - created_at: datetime      │
│ - updated_at: datetime      │
├─────────────────────────────┤
│ + events: list[Event]       │
│ + reviewed_events: list[Event]│
│ + is_admin(): bool          │
└──────────────┬──────────────┘
               │
               │ cria / revisa
               ▼
┌─────────────────────────────┐       ┌─────────────────────────┐
│           Event             │       │       Category          │
├─────────────────────────────┤       ├─────────────────────────┤
│ - id: UUID                  │       │ - id: UUID              │
│ - title: str                │       │ - name: str             │
│ - description: str          │       │ - description: str      │
│ - date: date                │       │ - created_at: datetime  │
│ - start_time: time          │       ├─────────────────────────┤
│ - end_time: time | None     │       │ + events: list[Event]   │
│ - venue_name: str           │       └────────────┬────────────┘
│ - address: str              │                    │
│ - neighborhood: str         │                    │
│ - city: str                 │◄───────────────────┘
│ - image_url: str | None     │       pertence a
│ - status: EventStatus       │
│ - rejection_reason: str|None│
│ - category_id: UUID         │
│ - created_by: UUID          │
│ - reviewed_by: UUID | None  │
│ - reviewed_at: datetime|None│
│ - created_at: datetime      │
│ - updated_at: datetime      │
├─────────────────────────────┤
│ + creator: User             │
│ + reviewer: User | None     │
│ + category: Category        │
│ + is_past(): bool           │
│ + is_approved(): bool       │
└─────────────────────────────┘

┌─────────────────────────────┐
│     <<enumeration>>         │
│        UserRole             │
├─────────────────────────────┤
│ USER = "user"               │
│ ADMIN = "admin"             │
└─────────────────────────────┘

┌─────────────────────────────┐
│     <<enumeration>>         │
│       EventStatus           │
├─────────────────────────────┤
│ PENDING = "pendente"        │
│ APPROVED = "aprovado"       │
│ REJECTED = "rejeitado"      │
│ CANCELLED = "cancelado"     │
└─────────────────────────────┘
```

### Classes de Serviço

```
┌─────────────────────────────────┐
│         AuthService             │
├─────────────────────────────────┤
│ + register(data): User          │
│ + login(email, password): Token │
│ + refresh_token(token): Token   │
│ + hash_password(pwd): str       │
│ + verify_password(pwd, hash): bool │
└─────────────────────────────────┘

┌──────────────────────────────────────────┐
│           EventService                   │
├──────────────────────────────────────────┤
│ + list_approved(filters, page): PaginatedResult[Event] │
│ + search(query, filters, page): PaginatedResult[Event] │
│ + get_by_id(id): Event                   │
│ + create(data, user): Event              │
│ + update(id, data, user): Event          │
│ + delete(id, user): void                 │
│ + list_by_user(user_id): list[Event]     │
│ + list_pending(): list[Event]            │
│ + approve(id, admin): Event              │
│ + reject(id, admin, reason): Event       │
│ + get_dashboard_stats(): DashboardStats  │
└──────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│           UserService                   │
├─────────────────────────────────────────┤
│ + get_by_id(id): User                   │
│ + get_by_email(email): User             │
│ + list_all(): list[User]                │
│ + update_profile(id, data): User        │
│ + promote_to_admin(id): User            │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│         StorageService                  │
├─────────────────────────────────────────┤
│ + upload_image(file): str (URL)         │
│ + delete_image(url): void               │
└─────────────────────────────────────────┘
```

---

## 10. API — Endpoints

### 10.1 Autenticação (`/api/auth`)

| Método | Rota | Descrição | Auth |
|---|---|---|---|
| POST | `/api/auth/register` | Cadastrar novo usuário | Não |
| POST | `/api/auth/login` | Login (retorna tokens JWT) | Não |
| POST | `/api/auth/refresh` | Renovar access token | Sim |

### 10.2 Eventos Públicos (`/api/events`)

| Método | Rota | Descrição | Auth |
|---|---|---|---|
| GET | `/api/events` | Listar eventos aprovados (paginado, com filtros) | Não |
| GET | `/api/events/search` | Busca textual server-side por título e descrição (paginado) | Não |
| GET | `/api/events/{id}` | Detalhes de um evento | Não |

**Query params para GET `/api/events`:**
- `category_id` — filtrar por categoria
- `date_from`, `date_to` — intervalo de datas
- `neighborhood` — filtrar por bairro
- `page`, `per_page` — paginação (padrão: page=1, per_page=20)

**Query params para GET `/api/events/search`:**
- `q` — texto de busca (obrigatório, mínimo 2 caracteres)
- `category_id` — filtrar por categoria (opcional)
- `page`, `per_page` — paginação

**Formato de resposta paginada (padrão para todos os endpoints de listagem):**
```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "per_page": 20,
  "pages": 8
}
```

### 10.3 Eventos do Usuário (`/api/events/me`)

| Método | Rota | Descrição | Auth |
|---|---|---|---|
| GET | `/api/events/me` | Meus eventos submetidos | Sim (user) |
| POST | `/api/events` | Cadastrar novo evento | Sim (user) |
| PUT | `/api/events/{id}` | Editar meu evento | Sim (owner) |
| DELETE | `/api/events/{id}` | Cancelar meu evento | Sim (owner) |

### 10.4 Upload (`/api/upload`)

| Método | Rota | Descrição | Auth |
|---|---|---|---|
| POST | `/api/upload/image` | Upload de imagem para o SeaweedFS. Retorna a URL pública da imagem. Aceita multipart/form-data (max 5MB, formatos: jpg, png, webp) | Sim (user) |

### 10.5 Categorias (`/api/categories`)

| Método | Rota | Descrição | Auth |
|---|---|---|---|
| GET | `/api/categories` | Listar categorias | Não |

### 10.6 Admin (`/api/admin`)

| Método | Rota | Descrição | Auth |
|---|---|---|---|
| GET | `/api/admin/dashboard` | Estatísticas do dashboard | Sim (admin) |
| GET | `/api/admin/events` | Listar todos os eventos (com filtro de status) | Sim (admin) |
| GET | `/api/admin/events/pending` | Listar eventos pendentes | Sim (admin) |
| PATCH | `/api/admin/events/{id}/approve` | Aprovar evento | Sim (admin) |
| PATCH | `/api/admin/events/{id}/reject` | Rejeitar evento (body: reason) | Sim (admin) |
| PUT | `/api/admin/events/{id}` | Editar qualquer evento | Sim (admin) |
| DELETE | `/api/admin/events/{id}` | Excluir qualquer evento | Sim (admin) |
| GET | `/api/admin/users` | Listar usuários | Sim (admin) |
| PATCH | `/api/admin/users/{id}/promote` | Promover a admin | Sim (admin) |

---

## 11. Fluxos Principais

### 11.1 Fluxo: Submissão e Aprovação de Evento

```
Usuário                          Backend                        Admin
   │                                │                              │
   │── POST /api/events ──────────►│                              │
   │                                │── Salva com status           │
   │                                │   "pendente"                 │
   │◄── 201 Created ──────────────│                              │
   │                                │                              │
   │                                │   (Admin acessa dashboard)   │
   │                                │◄──── GET /admin/events/pending
   │                                │────► Lista pendentes ───────►│
   │                                │                              │
   │                                │◄── PATCH /admin/events/{id}/approve
   │                                │── Atualiza status            │
   │                                │   "aprovado"                 │
   │                                │────► 200 OK ────────────────►│
   │                                │                              │
   │  (Evento aparece na listagem pública)                        │
```

### 11.2 Fluxo: Visualização de Eventos (Público)

```
Qualquer Usuário                 Backend
      │                             │
      │── GET /api/events ─────────►│
      │   ?category_id=X            │── Filtra eventos aprovados
      │   &date_from=Y              │   aplica filtros
      │                             │
      │◄── 200 [{título, data,     │
      │     local, thumbnail}] ─────│
      │                             │
      │── GET /api/events/{id} ────►│
      │                             │── Retorna detalhes completos
      │◄── 200 {evento completo} ──│
```

---

## 12. Telas do Aplicativo

### 12.1 Mapa de Navegação

```
                    ┌──────────────┐
                    │  Splash /    │
                    │  Loading     │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
              ┌─────│  Home Screen │─────┐
              │     │ (Lista de    │     │
              │     │  Eventos)    │     │
              │     └──────┬───────┘     │
              │            │             │
     ┌────────▼──┐  ┌──────▼───────┐  ┌──▼─────────┐
     │  Filtros  │  │  Detalhes do │  │   Login /   │
     │           │  │    Evento    │  │  Registro   │
     └───────────┘  └──────────────┘  └──────┬──────┘
                                             │
                                      ┌──────▼──────┐
                                      │ Área Logada │
                                      └──┬──────┬───┘
                                         │      │
                               ┌─────────▼┐  ┌──▼──────────┐
                               │ Criar    │  │ Meus        │
                               │ Evento   │  │ Eventos     │
                               └──────────┘  └─────────────┘
```

### 12.2 Descrição das Telas

| Tela | Descrição |
|---|---|
| **Home (Lista de Eventos)** | Grid/lista de cards com eventos aprovados (paginados). Cada card mostra: imagem (thumbnail), título, data, horário e local. Barra de busca no topo (busca server-side via endpoint `/api/events/search`). Filtros acessíveis (categoria, data, bairro). Botão flutuante "+" para criar evento (visível se logado). Paginação no rodapé ou scroll infinito. |
| **Detalhes do Evento** | Imagem em destaque no topo. Título, descrição completa, data e horário, local com endereço completo, categoria, nome do organizador. Botão de compartilhar. |
| **Login** | Campos: e-mail, senha. Botão "Entrar". Link "Não tem conta? Cadastre-se". |
| **Registro** | Campos: nome, e-mail, senha, confirmar senha. Botão "Cadastrar". |
| **Criar Evento** | Formulário: título, descrição, data, hora início, hora fim, nome do local, endereço, bairro, cidade, categoria (dropdown), upload de imagem (via SeaweedFS). Botão "Enviar para aprovação". |
| **Editar Evento** | Mesmo formulário de criação, preenchido com dados atuais. Se o evento estiver aprovado, exibe banner de aviso amarelo: "Ao salvar, o evento volta para fila de aprovação". Modal de confirmação antes de salvar. |
| **Meus Eventos** | Lista dos eventos do usuário com badge de status (pendente/amarelo, aprovado/verde, rejeitado/vermelho). Ao clicar, mostra detalhes + motivo de rejeição se aplicável. Botão de editar em cada card. |

### 12.3 Telas do Dashboard Admin (Web)

| Tela | Descrição |
|---|---|
| **Dashboard** | Cards com métricas: total de eventos, pendentes, aprovados, rejeitados, total de usuários. Gráfico simples de eventos por mês. Lista rápida dos últimos eventos pendentes. |
| **Eventos Pendentes** | Tabela com: título, categoria, data, criado por, data de submissão. Ações: ver detalhes, aprovar, rejeitar. Modal de rejeição com campo de motivo. |
| **Todos os Eventos** | Tabela completa com filtro por status. Ações: editar, excluir. |
| **Usuários** | Tabela com: nome, e-mail, role, data de cadastro, qtd eventos. Ação: promover a admin. |

---

## 13. Protótipo

Protótipo interativo disponível no Figma: https://relax-beaver-81335956.figma.site/

---

## 14. Seed de Dados Iniciais

### 14.1 Categorias Padrão

| Nome | Descrição |
|---|---|
| Show | Shows musicais, concertos e apresentações ao vivo |
| Exposição | Exposições de arte, fotografia e instalações |
| Teatro | Peças de teatro, espetáculos e performances |
| Festival | Festivais culturais, gastronômicos e temáticos |
| Cinema | Sessões de cinema, exibições e mostras audiovisuais |
| Oficina | Workshops, oficinas culturais e aulas abertas |
| Outro | Outros eventos culturais |

### 14.2 Usuário Admin Inicial

- **Nome**: Administrador
- **E-mail**: admin@agendacultural.com
- **Senha**: (definida via variável de ambiente `ADMIN_DEFAULT_PASSWORD`)
- **Role**: admin

---

## 15. Riscos e Mitigações

| Risco | Impacto | Mitigação |
|---|---|---|
| Upload de imagens pesadas | Lentidão no app | Limitar tamanho (5MB), comprimir no backend, servir via SeaweedFS (CDN-like) |
| Spam de eventos falsos | Poluição da plataforma | Fluxo de aprovação por admin |
| Único ponto de falha (monolito) | Indisponibilidade total | Aceitável para escopo acadêmico; monitorar logs |
| Complexidade do React Native | Atraso na entrega | Usar Expo para simplificar build e testes |

---

## 16. Glossário

| Termo | Definição |
|---|---|
| **Evento** | Atividade cultural com data, local e descrição, cadastrada na plataforma |
| **Status** | Estado do evento no fluxo de aprovação: pendente, aprovado, rejeitado ou cancelado |
| **Admin** | Usuário com permissão de moderação e gerenciamento da plataforma |
| **Dashboard** | Painel web administrativo com visão geral e ferramentas de gestão |
| **Seed** | Dados iniciais inseridos no banco de dados na primeira execução |
