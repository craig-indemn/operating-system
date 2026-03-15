"""Sync adapters for external systems.

Each adapter syncs records from an external system into the Hive.
Adapters are discovered by name: `hive sync <system>` imports
`sync_adapters.<system>` and calls `get_adapter().sync()`.
"""
