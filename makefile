make ruff:
	uv run ruff check src --fix
	uv run ruff format src

make git:
	git add *
	git commit -m Updated
	git push