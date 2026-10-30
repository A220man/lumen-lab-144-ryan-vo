# Changelog

## 1.1.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-10-23

### Added
- Ziwei Doushu chart generation engine based on 瞿海藩《天紀》 system
- True solar time calculation with longitude correction and NOAA equation of time
- Critical fix for HK boundary case (2025-12-31 23:00 → 亥 shichen)
- Runtime gender validation (rejects non-'male'/'female' values)
- FastAPI backend with `/api/v1/chart` and `/api/v1/chart/true-solar-time-preview` endpoints
- React + TypeScript + Vite frontend with responsive chart form and display
- 12 palaces with major/minor stars placement
- Ganzhi (stem-branch) four pillars calculation
- Ming Gong (命宫) and Shen Gong (身宮) positioning
- Comprehensive test suite: 36 backend tests, 5 frontend tests
- Docker and docker-compose configuration
- CI/CD pipeline with GitHub Actions

### Fixed
- Issue #45: `generateChart` silently ignored `longitude` - now uses true solar time
- Issue #38: Invalid gender values silently treated as female - now throws RangeError
- Equation of time calculation (removed double degrees conversion bug)
- Day pillar reference index (戊辰 = index 4, not 5)
- Hour pillar calculation per standard 五鼠遁
- Mobile date/time picker: replaced number inputs with native `type="date"` and `type="time"` for proper mobile UX
