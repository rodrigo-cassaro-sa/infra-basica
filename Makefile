.PHONY: up down ps logs backup-dev backup-hom backup-prod health
up:
	docker compose up -d --build

down:
	docker compose down

ps:
	docker compose ps

logs:
	docker compose logs -f --tail=200

backup-dev:
	./scripts/backup.sh dev

backup-hom:
	./scripts/backup.sh hom

backup-prod:
	./scripts/backup.sh prod

health:
	./scripts/health-check.sh
