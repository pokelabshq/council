.PHONY: test lint services up down health help

# Default target
help: ## Show this help
	@echo "Poke Labs Council — Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

test: ## Run pytest
	python -m pytest tests/ -x -q --timeout=30

lint: ## Run ruff
	ruff check .

services: ## List all poke-services
	@echo "Poke Labs Services:"
	@for d in poke-services/*/; do \
		name=$$(basename $$d); \
		if [ -f "$$d/server.py" ]; then \
			port=$$(grep -oP 'PORT\s*=\s*int\(os\.environ\.get\("PORT",\s*\K[0-9]+' "$$d/server.py" 2>/dev/null || echo "?"); \
			printf "  %-22s port %s\n" "$$name" "$$port"; \
		fi; \
	done

up: ## Start all services via docker compose
	docker compose up -d
	@echo "Services starting... Use 'make health' to check status."

down: ## Stop all services
	docker compose down

health: ## Check health of all services
	@echo "Checking service health..."
	@PORTS="8765 8766 8767 8768 8769 8770 8771 8772 8773 8774 8775 8776 8777 8778 8779 8780 8781 8782 8790 8791"; \
	FAILED=0; \
	for port in $$PORTS; do \
		HTTP_CODE=$$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$$port/api/health 2>/dev/null || echo "000"); \
		if [ "$$HTTP_CODE" = "200" ]; then \
			echo "  ✅ port $$port — healthy"; \
		else \
			echo "  ❌ port $$port — HTTP $$HTTP_CODE"; \
			FAILED=1; \
		fi; \
	done; \
	if [ "$$FAILED" = "1" ]; then \
		echo ""; \
		echo "One or more services failed health check"; \
		exit 1; \
	fi; \
	echo ""; \
	echo "All services healthy ✅"
