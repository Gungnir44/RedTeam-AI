#!/usr/bin/env python3
"""
RedTeam AI — Entry point.
Launch: python main.py
"""
import sys
import os

# Ensure the project root is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt

    # High DPI support
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("RedTeam AI")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("RedTeam AI Project")

    # Apply theme before any widgets are created
    from redteamai.gui.theme import apply_theme
    apply_theme(app)

    # Initialize database
    from redteamai.data.database import init_db
    init_db()

    # Load config
    from redteamai.config.manager import load_config
    settings = load_config()

    # Setup logging
    from redteamai.utils.logger import setup_logging
    setup_logging(log_level="INFO")

    # Build app state
    from redteamai.app import AppState
    state = AppState(settings=settings)

    # Create and show main window
    from redteamai.gui.main_window import MainWindow
    window = MainWindow(state)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
