make ruff:
	uv run ruff check src --fix
	uv run ruff format src
	@rm -rf .python-version .ruff_cache src/__pycache__

make git:
	git add *
	git commit -m Updated
	git push