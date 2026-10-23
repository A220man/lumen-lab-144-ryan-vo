# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

project-skeleton

## Roadmap

### project-skeleton — FastAPI + React project skeleton with Ziwei core engine

Status: done

Acceptance:
- Backend FastAPI app runs with /health endpoint
- Frontend Vite+React+TS builds and serves
- Ziwei core engine (calculateTrueSolarTime, generateChart) implemented in Python
- API endpoint POST /api/v1/chart generates chart from birth info
- Frontend form submits birth data and displays chart result
- Tests pass for backend and frontend

Implementation: `backend/app/main.py`, `backend/app/api/v1/chart.py`, `backend/app/services/ziwei/engine.py`, `backend/app/services/ziwei/true_solar_time.py`, `backend/app/services/ziwei/calculations.py`, `backend/app/models/chart.py`, `backend/tests/test_ziwei_engine.py`, `frontend/package.json`, `frontend/vite.config.ts`, `frontend/src/main.tsx`, `frontend/src/App.tsx`, `frontend/src/components/ChartForm.tsx`, `frontend/src/components/ChartDisplay.tsx`, `frontend/src/api/client.ts`

Tests: `backend/tests/test_ziwei_engine.py`, `backend/tests/test_api_chart.py`, `frontend/src/components/__tests__/ChartForm.test.tsx`

### true-solar-time-fix — Fix true solar time calculation - use longitude + equation of time

Status: done

Acceptance:
- calculateTrueSolarTime uses longitude offset and NOAA equation of time
- generateChart accepts longitude and uses true solar time for shichen determination
- Boundary cases (HK 2025-12-31 23:00) produce correct 亥 shichen
- Orphaned true-solar-time.ts logic ported and unified

Implementation: `backend/app/services/ziwei/true_solar_time.py`, `backend/app/services/ziwei/calculations.py`

Tests: `backend/tests/test_ziwei_engine.py::TestTrueSolarTime::test_hong_kong_boundary_case`, `backend/tests/test_ziwei_engine.py::TestGenerateChart::test_hk_boundary_chart`, `backend/tests/test_api_chart.py::TestGenerateChart::test_hk_boundary_case`

### gender-validation — Validate gender input - reject invalid values with RangeError

Status: done

Acceptance:
- generateChart throws RangeError for non-'male'/'female' gender values
- Valid 'male'/'female' inputs work correctly
- Regression tests for typo, empty string, null, undefined, number

Implementation: `backend/app/services/ziwei/calculations.py`

Tests: `backend/tests/test_ziwei_engine.py::TestGenerateChart::test_gender_validation_rejects_invalid`, `backend/tests/test_ziwei_engine.py::TestGenerateChart::test_gender_validation_accepts_valid`

### mobile-ui-fix — Fix mobile UI display issues (date picker, background colors)

Status: in_progress

Acceptance:
- Date picker works correctly on mobile
- Background colors render properly
- Responsive layout for chart display

Implementation: `frontend/src/components/ChartForm.tsx`, `frontend/src/index.css`

### auth-oidc — OIDC authentication with Keycloak (demo mode)

Status: planned

Acceptance:
- Keycloak integration with authorization code + PKCE
- Demo mode for localhost development
- Protected API endpoints
- Login/logout flow works

### docker-ci — Dockerfiles, compose, CI workflow

Status: done

Acceptance:
- Backend and frontend Dockerfiles with non-root users
- docker-compose.yml with Keycloak and volumes
- GitHub Actions CI: backend tests, frontend build/test, Docker builds
- Healthchecks configured

Implementation: `backend/Dockerfile`, `frontend/Dockerfile`, `frontend/nginx.conf`, `docker-compose.yml`, `.github/workflows/ci.yml`

