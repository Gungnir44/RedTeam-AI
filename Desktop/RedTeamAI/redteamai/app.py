"""Global application state dataclass."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from redteamai.config.settings import AppSettings


@dataclass
class AppState:
    """Singleton-like application state passed throughout the app."""
    settings: AppSettings = field(default_factory=AppSettings)
    current_project_id: Optional[int] = None
    current_session_id: Optional[int] = None
    active_module: str = "dashboard"

    # Runtime state (not persisted)
    ai_busy: bool = False
    tool_busy: bool = False

    def get_active_backend_name(self) -> str:
        return self.settings.ai_backend

    def set_project(self, project_id: int) -> None:
        self.current_project_id = project_id

    def clear_project(self) -> None:
        self.current_project_id = None
        self.current_session_id = None
