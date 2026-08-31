PY ?= python3
export PYTHONPATH := src

.PHONY: help test demo run prereg prereg-verify lint typecheck all

help:
	@echo "make test           - run the property/control suite (165 checks)"
	@echo "make demo           - offline end-to-end walkthrough (no API key)"
	@echo "make run            - run the FULL study; writes a self-verifying report"
	@echo "make prereg         - freeze a Phase-0 preregistration into preregistrations/"
	@echo "make prereg-verify  - recompute a preregistration's self-digest"
	@echo "make lint typecheck - ruff + mypy (dev extras)"
	@echo "make all            - test + run"

test:
	$(PY) -m gradia_wind_tunnel.tests

demo:
	$(PY) -m gradia_wind_tunnel.cli demo

run:
	$(PY) -m gradia_wind_tunnel.cli run --benchmark gsm8k --cycles 6

phase0:
	$(PY) -m gradia_wind_tunnel.cli phase0 --benchmark gsm8k   # offline rehearsal

figures:
	$(PY) -m gradia_wind_tunnel.figures --out paper/figures

prereg:
	$(PY) -m gradia_wind_tunnel.cli prereg-freeze --max-cost-usd 300

prereg-verify:
	@test -n "$(FILE)" || (echo "usage: make prereg-verify FILE=preregistrations/<id>.json" && exit 2)
	$(PY) -m gradia_wind_tunnel.cli prereg-verify $(FILE)

lint:
	ruff check src

typecheck:
	mypy src/gradia_wind_tunnel

all: test run
