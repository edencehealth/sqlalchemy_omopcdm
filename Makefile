.PHONY: clean

clean:
	find src '(' -name '*.egg-info' -or -name '__pycache__' ')' -print0  |xargs -r -0 rm -rfv --
	rm -rfv dist .pytest_cache .mypy_cache
	pre-commit clean && pre-commit gc
