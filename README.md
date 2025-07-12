# Budget Pet

**Budget Pet** is a CLI-based personal finance tracker, designed and built as a part of my practical Python learning. Its architecture is hexagonal (ports and adapters), allowing easy evolution and integration of new features as my skills grow.

---

## Purpose

Most budgeting tools are either bloated, too rigid, or disconnected from how I want to manage money. **Budget Pet** is intentionally minimalist, focused on:

- clean distinction between personal and business income,
- automatic tax reserve allocation,
- category-based spending,
- and now, extensibility for future technologies (e.g., MySQL, web interfaces).

---

## Current Features

- CLI menu for income/expense tracking, log viewing, and balance display.
- Separation of logic into core + adapters via hexagonal architecture.
- Transaction logs stored in `.jsonl` format.
- Expense categories mapped to human-readable labels.

---

## Architecture

Budget Pet now follows a **monolithic hexagonal architecture**, with:

- clear separation of core logic and infrastructure,
- pure business logic in the core layer,
- adapters for CLI input/output and JSONL storage,
- easy future extension for MySQL, web servers, or automated imports.

---

## Requirements

- Python 3.11+
- No external dependencies (yet)

---

## Running the App

```bash
python3 main.py