.PHONY: setup dev prod stop clean logs help

# Default target
help:
	@echo "Available commands:"
	@echo "  make setup   - Set up the project for first use"
	@echo "  make dev     - Start the development environment"
	@echo "  make prod    - Start the production environment"
	@echo "  make stop    - Stop all containers"
	@echo "  make clean   - Stop and remove all containers, networks, and volumes"
	@echo "  make logs    - View logs from all containers"

setup:
	@./scripts/setup.sh

dev:
	@cp .env.dev .env
	@docker-compose -f docker-compose.dev.yml up -d
	@echo "Development environment is up and running!"
	@echo "n8n: http://localhost:$(shell grep N8N_PORT .env | cut -d '=' -f 2)"
	@echo "MoneyPrinterTurbo UI: http://localhost:$(shell grep MONEYPRINTER_UI_PORT .env | cut -d '=' -f 2)"

prod:
	@./scripts/deploy.sh

stop:
	@docker-compose -f docker-compose.dev.yml down || true
	@docker-compose -f docker-compose.prod.yml down || true
	@echo "All containers stopped"

clean:
	@docker-compose -f docker-compose.dev.yml down -v || true
	@docker-compose -f docker-compose.prod.yml down -v || true
	@echo "All containers, networks, and volumes removed"

logs:
	@docker-compose -f docker-compose.dev.yml logs -f || docker-compose -f docker-compose.prod.yml logs -f
