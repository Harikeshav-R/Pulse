.PHONY: help up down test lint seed

help:
	@echo "TrialPulse Makefile Commands:"
	@echo "  make up      - Start the full dockerized stack in the background"
	@echo "  make down    - Stop the dockerized stack"
	@echo "  make test    - Run backend pytest suite"
	@echo "  make lint    - Run ruff linter on the backend"
	@echo "  make seed    - Seed the database with demo data"

up:
	docker compose up -d --build

down:
	docker compose down

test:
	cd backend && uv run pytest tests/

lint:
	cd backend && uv run ruff check .

seed:
	cd backend && uv run python scripts/seed_demo_data.py
	cd backend && uv run python scripts/generate_wearable_data.py
