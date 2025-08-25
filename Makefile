.PHONY: run run-gui install lint format

install:
	poetry install

run:
	poetry run python -m src.main

run-gui:
	poetry run python src/gui_main.py

# Testing commands


# Development commands
lint:
	poetry run ruff check .

format:
	poetry run ruff format .

# Help
help:
	@echo "Comandos disponibles:"
	@echo "  install      - Instalar dependencias"
	@echo "  run          - Ejecutar aplicación de consola"
	@echo "  run-gui      - Ejecutar aplicación GUI"
	@echo "  lint         - Verificar código"
	@echo "  format       - Formatear código"
	@echo "  help         - Mostrar esta ayuda"