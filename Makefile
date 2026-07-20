PROJECT_NAME := hybrid-rsa-aes
SRC_PATH := src/hybrid_rsa_aes
LINT_PATHS := src tests examples
UV ?= uv

.DEFAULT_GOAL := help

.PHONY: help venv/install/main venv/install/all lint/ruff lint/mypy lint format test build clean sys/changelog sys/tag

help: ## Display this help message
	@awk 'BEGIN { FS = ":.*##"; printf "\nUsage:\n  make <target>\n\nTargets:\n" } /^[a-zA-Z0-9_./-]+:.*##/ { printf "  \033[36m%-24s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

venv/install/main: ## Install runtime dependencies
	$(UV) sync --no-group dev

venv/install/all: ## Install runtime and development dependencies
	$(UV) sync --all-groups

lint/ruff: ## Check formatting and lint with Ruff
	$(UV) run --locked ruff format --check $(LINT_PATHS)
	$(UV) run --locked ruff check $(LINT_PATHS)

lint/mypy: ## Type-check the source package
	$(UV) run --locked mypy $(SRC_PATH)

lint: lint/ruff lint/mypy ## Run all lint checks

test: ## Run tests with coverage
	$(UV) run --locked pytest --cov=hybrid_rsa_aes --cov-report=term-missing

build: ## Build source and wheel distributions
	$(UV) build

format: ## Format and auto-fix lint issues
	$(UV) run --locked ruff format $(LINT_PATHS)
	$(UV) run --locked ruff check --fix $(LINT_PATHS)

clean: ## Remove generated files and caches
	rm -rf .coverage .mypy_cache .pytest_cache .ruff_cache build dist
	find . -type d -name __pycache__ -prune -exec rm -rf {} +

sys/changelog: ## Generate CHANGELOG.md from semantic-version tags
	@tags="$$(git tag --list 'v[0-9]*' '[0-9]*' --sort=-version:refname)"; test -n "$$tags"; { printf '# Changelog\n\n'; for tag in $$tags; do printf '## %s (%s)\n\n' "$${tag#v}" "$$(git log -1 --format=%as "$$tag")"; git log --no-merges "$$tag" --format='* %s [%an]'; printf '\n'; done; } > CHANGELOG.md

sys/tag: ## Create and push a vX.Y.Z release tag matching pyproject.toml
	@read -r -p "Enter tag version (e.g., 1.0.0): " TAG; test "$$( $(UV) run --locked python -c 'import tomllib; print(tomllib.load(open("pyproject.toml", "rb"))["project"]["version"])' )" = "$$TAG"; git diff --quiet && git diff --cached --quiet; git tag -a "v$$TAG" -m "Release v$$TAG" && git push origin "v$$TAG"
