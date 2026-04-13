"""
Clarion — Module Registry
Core extensibility framework. Modules self-register their routes, tasks,
chatbot tools, and permissions. New features are added without modifying
existing code.

Usage:
    # In a module's __init__.py:
    from app.registry import ModuleManifest, registry

    manifest = ModuleManifest(
        id="cases",
        name="Case Management",
        version="1.0.0",
        dependencies=["sync"],
        required_permissions=["cases:read"],
        chatbot_tools=["query_cases", "get_case_detail"],
    )

    def register(app):
        from .routes import router
        app.include_router(router, prefix="/api/v1/cases", tags=["Cases"])
"""

from __future__ import annotations

import importlib
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from fastapi import FastAPI

logger = logging.getLogger("clarion.registry")


@dataclass
class ModuleManifest:
    """Declaration of a module's metadata and capabilities."""

    id: str
    name: str
    version: str
    description: str = ""
    dependencies: list[str] = field(default_factory=list)
    required_permissions: list[str] = field(default_factory=list)
    admin_configurable: bool = False
    chatbot_tools: list[str] = field(default_factory=list)
    health_check: Callable | None = None


@dataclass
class RegisteredModule:
    """A module that has been discovered and registered."""

    manifest: ModuleManifest
    register_fn: Callable
    enabled: bool = True
    healthy: bool = True
    error: str | None = None


class ModuleRegistry:
    """
    Discovers, validates, and activates feature modules.

    Lifecycle:
    1. discover() — scans modules/ directory for manifests
    2. resolve_dependencies() — validates dependency graph
    3. activate() — calls register() on each enabled module in dependency order
    """

    def __init__(self):
        self._modules: dict[str, RegisteredModule] = {}
        self._activation_order: list[str] = []

    @property
    def modules(self) -> dict[str, RegisteredModule]:
        return self._modules.copy()

    @property
    def enabled_modules(self) -> dict[str, RegisteredModule]:
        return {k: v for k, v in self._modules.items() if v.enabled}

    @property
    def chatbot_tools(self) -> dict[str, str]:
        """Returns {tool_name: module_id} for all enabled modules."""
        tools = {}
        for mod in self._modules.values():
            if mod.enabled:
                for tool in mod.manifest.chatbot_tools:
                    tools[tool] = mod.manifest.id
        return tools

    def discover(self, modules_path: Path) -> None:
        """Scan the modules directory and load manifests."""
        if not modules_path.exists():
            logger.warning(f"Modules path does not exist: {modules_path}")
            return

        for module_dir in sorted(modules_path.iterdir()):
            if not module_dir.is_dir() or module_dir.name.startswith("_"):
                continue

            init_file = module_dir / "__init__.py"
            if not init_file.exists():
                logger.warning(f"Module {module_dir.name} has no __init__.py, skipping")
                continue

            try:
                module_name = f"app.modules.{module_dir.name}"
                mod = importlib.import_module(module_name)

                if not hasattr(mod, "manifest") or not hasattr(mod, "register"):
                    logger.warning(f"Module {module_dir.name} missing 'manifest' or 'register', skipping")
                    continue

                manifest: ModuleManifest = mod.manifest
                self._modules[manifest.id] = RegisteredModule(
                    manifest=manifest,
                    register_fn=mod.register,
                )
                logger.info(f"Discovered module: {manifest.id} v{manifest.version}")

            except Exception as e:
                logger.error(f"Failed to discover module {module_dir.name}: {e}")
                self._modules[module_dir.name] = RegisteredModule(
                    manifest=ModuleManifest(
                        id=module_dir.name,
                        name=module_dir.name,
                        version="0.0.0",
                    ),
                    register_fn=lambda app: None,
                    enabled=False,
                    healthy=False,
                    error=str(e),
                )

    def resolve_dependencies(self) -> list[str]:
        """
        Topological sort of modules by dependencies.
        Disables modules whose dependencies are missing or disabled.
        """
        resolved: list[str] = []
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(module_id: str) -> bool:
            if module_id in visited:
                return True
            if module_id in visiting:
                logger.error(f"Circular dependency detected involving: {module_id}")
                return False

            mod = self._modules.get(module_id)
            if not mod or not mod.enabled:
                return False

            visiting.add(module_id)

            for dep_id in mod.manifest.dependencies:
                dep = self._modules.get(dep_id)
                if not dep or not dep.enabled:
                    logger.warning(
                        f"Module {module_id} depends on {dep_id} which is "
                        f"{'disabled' if dep else 'not found'}. Disabling {module_id}."
                    )
                    mod.enabled = False
                    mod.error = f"Missing dependency: {dep_id}"
                    visiting.discard(module_id)
                    return False

                if not visit(dep_id):
                    mod.enabled = False
                    mod.error = f"Dependency {dep_id} could not be resolved"
                    visiting.discard(module_id)
                    return False

            visiting.discard(module_id)
            visited.add(module_id)
            resolved.append(module_id)
            return True

        for module_id in list(self._modules.keys()):
            visit(module_id)

        self._activation_order = resolved
        return resolved

    async def check_feature_flags(self, get_flags_fn: Callable) -> None:
        """
        Check feature flags from database and disable modules accordingly.
        get_flags_fn should return a dict of {module_id: enabled}.
        """
        try:
            flags = await get_flags_fn()
            for module_id, enabled in flags.items():
                if module_id in self._modules:
                    self._modules[module_id].enabled = enabled
                    if not enabled:
                        logger.info(f"Module {module_id} disabled by feature flag")
        except Exception as e:
            logger.warning(f"Could not load feature flags: {e}. All discovered modules enabled.")

    def activate(self, app: FastAPI) -> None:
        """Register all enabled modules with the FastAPI app in dependency order."""
        for module_id in self._activation_order:
            mod = self._modules.get(module_id)
            if not mod or not mod.enabled:
                continue

            try:
                mod.register_fn(app)
                logger.info(f"Activated module: {module_id}")
            except Exception as e:
                logger.error(f"Failed to activate module {module_id}: {e}")
                mod.healthy = False
                mod.error = str(e)

    def get_health_status(self) -> dict[str, Any]:
        """Return health status for all modules (used by admin health dashboard)."""
        return {
            mod_id: {
                "name": mod.manifest.name,
                "version": mod.manifest.version,
                "enabled": mod.enabled,
                "healthy": mod.healthy,
                "error": mod.error,
            }
            for mod_id, mod in self._modules.items()
        }

    def get_permissions(self) -> list[str]:
        """Return all permissions declared across enabled modules."""
        perms = set()
        for mod in self._modules.values():
            if mod.enabled:
                perms.update(mod.manifest.required_permissions)
        return sorted(perms)


# Singleton registry instance
registry = ModuleRegistry()
