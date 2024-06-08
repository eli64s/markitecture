COMMITS := 10
SHELL := /bin/bash
VENV := kenshi
VV := \

.PHONY: clean
clean: format ## Remove project artifacts
	@echo -e "\nFile clean up in directory: ${CURDIR}"
	./scripts/clean.sh clean

.PHONY: format
format: ## Format codebase using Ruff
	@echo -e "\nFormatting in directory: ${CURDIR}"
	ruff check --select I --fix .
	ruff format .

.PHONY: lint
lint: ## Lint codebase using Ruff
	@echo -e "\nLinting in directory: ${CURDIR}"
	ruff check . --fix

.PHONY: git-rm-cache
git-rm-cache: ## Remove all files from git cache
	git rm -r --cached .

.PHONY: git-log
git-log: ## Display git log for last ${COMMITS} commits
	git log -n ${COMMITS} --pretty=tformat: --shortstat

.PHONY: nox
nox: ## Run nox test automation against multiple Python versions
	nox -f noxfile.py

.PHONY: pytest
pytest: ## Run unit tests using pytest
	poetry run pytest ${VV} \
	--cov=. \
	--cov-branch \
	--cov-report=xml \
	--cov-report=term-missing \
	--numprocesses=auto \
	--asyncio-mode=auto \
	--durations=10

.PHONY: poetry-reqs
poetry-reqs: ## Export poetry requirements to requirements.txt
	poetry export -f requirements.txt --output setup/requirements.txt --without-hashes

.PHONY: search
search: clean ## Search for a word in the codebase
	@echo -e "\nSearching for: ${WORD} in directory: ${CURDIR}"
	grep -Ril ${WORD} kenshi tests scripts setup

.PHONY: help
help: Makefile
	@echo -e "Usage: make [target]\n"
	@awk -F: '/^[a-zA-Z0-9_-]+:.*?##/ { printf "\033[36m%-30s\033[0m %s\n", $$1, $$2 }' $<
	@echo -e "__________________________________________________________________________________________\n"
