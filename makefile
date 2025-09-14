make ruff:
	uv run ruff check miscellaneous --fix
	uv run ruff format miscellaneous

make git:
	git add *
	git commit -m Updated
	git push