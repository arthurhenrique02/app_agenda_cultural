# Release Checklist — Agenda Cultural

This document summarizes the readiness of the Agenda Cultural platform for its first release.

## 1. Project Status Summary
- **Backend**: FastAPI with SQLAlchemy & Alembic. Fully tested.
- **Web (Public)**: React/Vite. All core flows implemented.
- **Admin (Web)**: React/Vite. Full moderation and user management.
- **Mobile (Expo)**: React Native. Browse, Auth, and My Events flows completed.

## 2. Pre-Release Checks

### ⚙️ Environment Configuration
- [ ] `.env` files created for all environments (Prod/Staging).
- [ ] `DATABASE_URL` points to a persistent PostgreSQL instance.
- [ ] `JWT_SECRET` is a strong, random string.
- [ ] CORS origins configured to allow only trusted domains.
- [ ] Upload directory (or S3 bucket) is writable.

### 🗄️ Database & Migrations
- [ ] All migrations applied (`alembic upgrade head`).
- [ ] Seed data for categories is present.
- [ ] First admin user created.

### 🧪 Quality Assurance
- [ ] Backend: `pytest` passes all contract and unit tests.
- [ ] Web/Admin: `npm run build` (Typecheck + Build) passes.
- [ ] Mobile: `npx tsc` passes.
- [ ] Smoke test script (`backend/tests/smoke_test.py`) passes.

### 🛡️ Security
- [ ] No secrets or `.env` files committed to Git.
- [ ] Password hashing (Argon2) verified.
- [ ] JWT expiration and refresh token logic tested.
- [ ] File upload restricted to images (JPG/PNG/WEBP).
- [ ] Ownership checks enforced for event updates/deletion.

## 3. Deployment Steps
1. Provision cloud resources (DB, App Server, Storage).
2. Set up CI/CD pipeline.
3. Apply DB migrations.
4. Deploy Backend API.
5. Deploy Web and Admin static files (CDN/S3).
6. Publish Mobile app to Expo/App Stores.

---
*Date: 2026-05-21*
*Status: READY FOR RELEASE*
