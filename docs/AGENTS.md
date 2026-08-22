# AGENTS.md — Engineering Principles for Agentic AI Architecture

This document defines the core software engineering principles governing our enterprise agentic lead qualification system:

1. **Do not preserve backward compatibility.** Remove obsolete paths instead of adding compatibility layers, fallbacks, or migrations.
2. **Choose the simplest implementation that fully meets the current requirements.** Avoid speculative abstractions, configuration, and indirection.
3. **Grow the system in layers.** Start from the smallest version that works end to end, and add each new capability on top of a product that already works. Never trade a working product for unfinished complexity.
4. **Keep components modular and concerns clearly separated.**
5. **Prefer established, well-maintained libraries when they reduce overall complexity or improve reliability.** Do not reimplement common functionality without a clear reason.
6. **Lean on the dependencies already in the project before writing your own implementation or adding packages.** Do not assume a library lacks a capability without checking its documentation and types.
7. **Make architectural decisions for the long term.** Do not accept a stopgap that only works for now and is meant to be replaced later.
8. **Enforce a Zero-Regression Policy (MANDATORY).** Every code modification must execute and pass the automated test suite before finalization:
   ```bash
   python run_tests.py
   # or
   python -m unittest tests/test_notcrm_suite.py -v
   ```
   All 36+ test scenarios across multi-session concurrency, DAG execution, FastMCP tooling, A2A communication, Knowledge Graph memory, evals contracts, governance rules, consumption formulas, and quiz assessment must yield zero failures. Newly added endpoints or features must include an accompanying test scenario in `tests/test_notcrm_suite.py`.
