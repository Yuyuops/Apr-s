.PHONY: test audit check

test:
	pytest -q

audit:
	python audit_programs.py

check: test audit
