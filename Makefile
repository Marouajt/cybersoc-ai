# ---------------------------------------------------------------------------
# CyberSOC AI — raccourcis de développement.
# Sous Windows sans `make`, utiliser les commandes équivalentes du README.
# ---------------------------------------------------------------------------

PYTHON ?= python

.DEFAULT_GOAL := help

.PHONY: help setup env up down logs ps reset-db test lint fmt data clean check

help:  ## Affiche cette aide
	@echo "CyberSOC AI — cibles disponibles :"
	@echo "  make setup     cree le venv et installe les dependances"
	@echo "  make env       copie .env.example vers .env si absent"
	@echo "  make up        demarre Neo4j (docker compose up -d)"
	@echo "  make down      arrete les services"
	@echo "  make logs      suit les logs Neo4j"
	@echo "  make ps        etat des services"
	@echo "  make reset-db  DETRUIT le volume Neo4j local (donnees perdues)"
	@echo "  make test      lance la suite de tests"
	@echo "  make lint      verifie le style (ruff)"
	@echo "  make fmt       formate le code (ruff format)"
	@echo "  make check     lint + test (a lancer avant chaque PR)"
	@echo "  make data      reconstruit tous les jeux de donnees (etape 1)"

setup:  ## Cree .venv et installe les dependances
	$(PYTHON) -m venv .venv
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements-dev.txt

env:  ## Cree .env a partir du modele
	@if [ -f .env ]; then echo ".env existe deja, rien a faire"; else cp .env.example .env; echo ".env cree"; fi

up:  ## Demarre Neo4j
	docker compose up -d
	@echo "Neo4j : http://localhost:7474  (bolt://localhost:7687)"

down:  ## Arrete les services
	docker compose down

logs:  ## Suit les logs Neo4j
	docker compose logs -f neo4j

ps:  ## Etat des services
	docker compose ps

reset-db:  ## DETRUIT les donnees Neo4j locales
	docker compose down -v
	@echo "Volume Neo4j supprime. Relancer 'make up' pour repartir de zero."

test:  ## Suite de tests
	$(PYTHON) -m pytest -q

lint:  ## Analyse statique
	$(PYTHON) -m ruff check .

fmt:  ## Formatage
	$(PYTHON) -m ruff format .

check: lint test  ## Verification avant PR

data:  ## Reconstruction complete des jeux de donnees (etape 1)
	@echo "Etape 1 non encore implementee : voir data/README.md"
	@$(PYTHON) -m data.build_all

clean:  ## Nettoie les caches locaux (ne touche pas aux donnees)
	@rm -rf .pytest_cache .ruff_cache .mypy_cache htmlcov .coverage
	@find . -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
	@echo "Caches nettoyes."
