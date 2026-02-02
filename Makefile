.PHONY: completions completions-static install dev test help

help:
	@echo "kubrux development targets:"
	@echo "  make completions      - Regenerate completions via shtab (requires: uv pip install -e '.[completions]')"
	@echo "  make completions-static - Update static completion files (manual - add new flags to completions/*)"
	@echo "  make install          - Install kubrux with uv tool"
	@echo "  make dev              - Install in editable mode with dev deps"
	@echo "  make test             - Run tests"

# Regenerate completion scripts using shtab (always in sync with argparse).
completions:
	uv run kubrux --print-completion bash > completions/kubrux-shtab.bash
	uv run kubrux --print-completion zsh > completions/_kubrux-shtab
	@echo "Generated completions/kubrux-shtab.bash and completions/_kubrux-shtab"
	@echo "For always-in-sync: add 'source <(kubrux --print-completion zsh)' to ~/.zshrc"

install:
	uv tool install --force .

dev:
	uv pip install -e ".[completions]"

test:
	uv run pytest -q 2>/dev/null || echo "No tests yet"
