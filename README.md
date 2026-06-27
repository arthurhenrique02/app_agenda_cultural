# Agenda Cultural

Plataforma multi-cliente que agrega e divulga eventos culturais locais — shows, exposições, peças de teatro, festivais e mais. Qualquer pessoa descobre o que acontece na cidade; usuários autenticados submetem eventos, que passam por aprovação de um administrador antes de serem publicados.

Acessível via **mobile** (React Native/Expo), **web** (React + Vite) e **dashboard administrativo** (web + build desktop Electron). Backend em **FastAPI** com **PostgreSQL** e armazenamento de imagens em **SeaweedFS** (S3-compatible).

> Documento de requisitos completo: [`docs/PRD.md`](docs/PRD.md) · [`PRD.pdf`](PRD.pdf)

---

## Arquitetura

Monólito modular: backend REST consumido por três clientes.

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ React Native│  │ React + Vite│  │ React + Vite│
│  (mobile)   │  │   (web)     │  │   (admin)   │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       └────────────────┼────────────────┘
                        │ HTTP/REST
                  ┌─────▼─────┐
                  │  FastAPI  │
                  └──┬─────┬──┘
            ┌────────▼─┐  ┌─▼──────────┐
            │PostgreSQL│  │ SeaweedFS  │
            │ (dados)  │  │ (imagens)  │
            └──────────┘  └────────────┘
```

Camadas do backend: **Routers** (HTTP) → **Services** (regra de negócio) → **Models** (ORM), com **Schemas** (Pydantic, validação I/O) e **Dependencies** (auth, sessão DB).

## Stack

| Camada | Tecnologia |
|---|---|
| Mobile | React Native + Expo + TypeScript |
| Web (usuário) | React 18 + Vite + TypeScript |
| Web (admin) | React 18 + Vite + TypeScript |
| Desktop (admin) | Electron (build do admin) |
| API | Python 3.12 + FastAPI (async) |
| ORM / Migrações | SQLAlchemy 2 (asyncio) + Alembic |
| Banco | PostgreSQL 16 |
| Storage | SeaweedFS (S3-compatible, via boto3) |
| Auth | JWT (PyJWT) — access 15min / refresh 7 dias |
| Hash de senha | Argon2 (argon2-cffi) |
| Gerenciador Python | uv |

## Estrutura do repositório

```
app_agenda_cultural/
├── backend/            # FastAPI + SQLAlchemy + Alembic
│   ├── app/
│   │   ├── models/         # tabelas (user, event, category)
│   │   ├── schemas/        # Pydantic
│   │   ├── repositories/   # acesso a dados
│   │   ├── services/       # regra de negócio (+ storage SeaweedFS)
│   │   ├── routers/        # auth, events, users, categories, upload, admin
│   │   ├── dependencies/   # auth, db session
│   │   ├── security/       # jwt, password (argon2)
│   │   ├── seed.py         # categorias + admin inicial
│   │   └── main.py
│   ├── alembic/        # migrações versionadas
│   └── tests/          # pytest
├── frontend/
│   ├── mobile/         # React Native (Expo)
│   ├── web/            # app web do usuário
│   ├── admin/          # dashboard admin (web)
│   └── desktop/        # admin empacotado em Electron
├── infra/              # Dockerfile, docker-compose, s3.json
└── docs/               # PRD
```

---

## Como rodar

### Opção A — Docker (backend + DB + storage)

Sobe API, PostgreSQL e SeaweedFS de uma vez. Roda migrações e seed automaticamente.

```bash
cd infra
cp ../backend/.env.example .env   # ajuste valores se quiser
docker compose up --build
```

- API: http://localhost:8000 · Docs (Swagger): http://localhost:8000/docs
- PostgreSQL: porta `5450`
- SeaweedFS (S3): porta `8333`

### Opção B — Backend local (uv)

Requer Python 3.12+, [uv](https://docs.astral.sh/uv/), e PostgreSQL + SeaweedFS acessíveis (ex.: subindo só esses serviços via compose).

```bash
cd backend
cp .env.example .env
uv sync                          # instala dependências
uv run alembic upgrade head      # migrações
uv run python -m app.seed        # seed de categorias + admin
uv run uvicorn app.main:app --reload --port 8000
```

### Frontends

```bash
# Web usuário
cd frontend/web && npm install && npm run dev

# Admin (web)
cd frontend/admin && npm install && npm run dev

# Admin desktop (Electron)
cd frontend/desktop && npm install && npm run dev
npm run package                  # gera instalador (electron-builder)

# Mobile (Expo)
cd frontend/mobile && npm install && npm start
```

## Variáveis de ambiente (backend)

Definidas em `backend/.env` (veja `.env.example`):

| Variável | Descrição |
|---|---|
| `SECRET_KEY` | Chave de assinatura JWT |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | Credenciais e nome do banco (lidos pelo container `db` no compose) |
| `DATABASE_URL` | Conexão Postgres (asyncpg) — deve bater com usuário/senha/banco acima |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Validade do access token (padrão 15) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Validade do refresh token (padrão 7) |
| `STORAGE_ENDPOINT` / `STORAGE_PUBLIC_URL` | Endpoint interno e URL pública do SeaweedFS |
| `STORAGE_ACCESS_KEY` / `STORAGE_SECRET_KEY` / `STORAGE_BUCKET` | Credenciais e bucket S3 |
| `ADMIN_DEFAULT_PASSWORD` | Senha do admin criado no seed |

### Login padrão do admin

Criado automaticamente pelo seed na primeira execução:

| Campo | Valor |
|---|---|
| E-mail | `admin@agendacultural.com` |
| Senha | valor de `ADMIN_DEFAULT_PASSWORD` (padrão do `.env.example`: `admin123`) |
| Role | `admin` |

> Troque `ADMIN_DEFAULT_PASSWORD` antes de qualquer deploy.

## Testes

```bash
cd backend
uv run pytest
```

---

## Modelo de dados

Três tabelas: `users`, `categories`, `events`.

- `events.created_by → users.id` (autor)
- `events.reviewed_by → users.id` (admin revisor, nullable)
- `events.category_id → categories.id`

**Status do evento** (`pendente` → `aprovado` / `rejeitado` / `cancelado`). Evento rejeitado carrega `rejection_reason`. Eventos só aparecem na listagem pública após aprovação; ao editar um evento aprovado, ele volta para `pendente`.

## API (resumo)

Base: `/api`. Docs interativas em `/docs`.

| Grupo | Rotas principais | Auth |
|---|---|---|
| Auth | `POST /auth/register`, `/auth/login`, `/auth/refresh` | público / token |
| Eventos públicos | `GET /events`, `GET /events/search?q=`, `GET /events/{id}` | público |
| Eventos do usuário | `GET /events/me`, `POST /events`, `PUT /events/{id}`, `DELETE /events/{id}` | user / owner |
| Upload | `POST /upload/image` (multipart, max 5MB: jpg/png/webp) | user |
| Categorias | `GET /categories` | público |
| Admin | `GET /admin/dashboard`, `/admin/events`, `/admin/events/pending`, `PATCH /admin/events/{id}/approve`, `/admin/events/{id}/reject`, `GET /admin/users`, `PATCH /admin/users/{id}/promote` | admin |

Listagens são **paginadas server-side** (`page`, `per_page`) e retornam metadados:

```json
{ "items": [...], "total": 150, "page": 1, "per_page": 20, "pages": 8 }
```

A busca textual (`/events/search`) é feita no banco, não no cliente.
