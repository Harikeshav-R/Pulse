.PHONY: help up down test lint seed voice-worker

help:
	@echo "TrialPulse Makefile Commands:"
	@echo "  make up      - Start the full dockerized stack in the background"
	@echo "  make down    - Stop the dockerized stack"
	@echo "  make test    - Run backend pytest suite"
	@echo "  make lint    - Run linters on the backend and frontend"
	@echo "  make seed    - Seed the database with demo data"

up:
	docker compose up -d --build

down:
	docker compose down

test:
	cd backend && uv run pytest tests/

lint:
	cd backend && uv run ruff check .
	cd apps/dashboard && pnpm run lint && pnpm tsc -b

seed:
	cd backend && uv run python scripts/seed_demo_data.py
	cd backend && uv run python scripts/generate_wearable_data.py

voice-worker:
	cd backend && uv run python scripts/run_voice_worker.py dev