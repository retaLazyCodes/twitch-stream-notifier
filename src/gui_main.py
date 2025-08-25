#!/usr/bin/env python3
"""
Punto de entrada principal para la aplicación GUI de Twitch Notifier.
"""

import sys
import os

# Agregar el directorio src al path para importaciones
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from ui.main_window import main

if __name__ == "__main__":
    main()
