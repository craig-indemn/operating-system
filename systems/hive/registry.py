"""Type registry and ontology loader for the Hive.

Loads entity type definitions from .registry/types/ and the ontology from
.registry/ontology.yaml. Provides validation and lookup for the CLI's
two-layer routing.
"""
import os

import yaml

from config import TYPES_PATH, ONTOLOGY_PATH


class Registry:
    """Loads and validates entity types and ontology tags."""

    def __init__(self):
        self._types: dict[str, dict] = {}
        self._ontology: dict = {}
        self._tags: dict[str, dict] = {}
        self._domains: dict[str, dict] = {}
        self._statuses: list[str] = []
        self._priorities: list[str] = []
        self._loaded = False

    def load(self):
        """Load all type definitions and ontology. Idempotent."""
        if self._loaded:
            return
        self._load_types()
        self._load_ontology()
        self._validate_disjoint()
        self._loaded = True

    def _load_types(self):
        """Load entity type YAML files from .registry/types/."""
        if not TYPES_PATH.exists():
            return
        for fname in sorted(TYPES_PATH.iterdir()):
            if fname.suffix in (".yaml", ".yml"):
                with open(fname) as f:
                    schema = yaml.safe_load(f)
                if schema and "type" in schema:
                    self._types[schema["type"]] = schema

    def _load_ontology(self):
        """Load ontology.yaml for tags, domains, statuses, priorities."""
        if not ONTOLOGY_PATH.exists():
            return
        with open(ONTOLOGY_PATH) as f:
            self._ontology = yaml.safe_load(f) or {}
        self._tags = self._ontology.get("tags", {})
        self._domains = self._ontology.get("domains", {})
        self._statuses = self._ontology.get("statuses", [])
        self._priorities = self._ontology.get("priorities", [])

    def _validate_disjoint(self):
        """Ensure entity type names and tag names are disjoint sets."""
        overlap = set(self._types.keys()) & set(self._tags.keys())
        if overlap:
            raise ValueError(
                f"Entity types and tags must be disjoint. Overlap: {overlap}"
            )

    def is_entity_type(self, name: str) -> bool:
        """Check if name is a registered entity type."""
        self.load()
        return name in self._types

    def is_known_tag(self, name: str) -> bool:
        """Check if name is a registered knowledge tag."""
        self.load()
        return name in self._tags

    def get_type_schema(self, type_name: str) -> dict | None:
        """Get the schema for an entity type."""
        self.load()
        return self._types.get(type_name)

    def get_all_types(self) -> dict[str, dict]:
        """Return all entity type schemas."""
        self.load()
        return dict(self._types)

    def get_all_tags(self) -> dict[str, dict]:
        """Return all registered tags."""
        self.load()
        return dict(self._tags)

    def get_domains(self) -> dict[str, dict]:
        """Return all registered domains."""
        self.load()
        return dict(self._domains)

    def get_statuses(self) -> list[str]:
        """Return all registered statuses."""
        self.load()
        return list(self._statuses)

    def get_priorities(self) -> list[str]:
        """Return all registered priorities."""
        self.load()
        return list(self._priorities)

    def get_display_field(self, type_name: str) -> str:
        """Return the display field for an entity type (default: 'name')."""
        schema = self.get_type_schema(type_name)
        if schema:
            return schema.get("display", "name")
        return "name"

    def get_required_fields(self, type_name: str) -> list[str]:
        """Return required field names for an entity type."""
        schema = self.get_type_schema(type_name)
        if not schema:
            return []
        return [
            name
            for name, spec in schema.get("fields", {}).items()
            if isinstance(spec, dict) and spec.get("required")
        ]

    def get_ref_fields(self, type_name: str) -> dict[str, str]:
        """Return ref fields and their targets for an entity type.

        Returns dict of field_name → target_type.
        """
        schema = self.get_type_schema(type_name)
        if not schema:
            return {}
        refs = {}
        for name, spec in schema.get("fields", {}).items():
            if isinstance(spec, dict) and spec.get("type") in ("ref", "ref_list"):
                refs[name] = spec.get("target", "")
        return refs


# Singleton
_registry = Registry()


def get_registry() -> Registry:
    """Return the global registry instance."""
    return _registry
