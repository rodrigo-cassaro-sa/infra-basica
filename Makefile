.PHONY: up down ps logs backup health
up:
	docker compose up -d --build

down:
	docker compose down

ps:
	docker compose ps

logs:
	docker compose logs -f --tail=200

backup:
	./scripts/backup.sh

health:
	./scripts/health-check.sh
