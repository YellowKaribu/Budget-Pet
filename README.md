# Budget Pet

**Budget Pet** is a personal CLI tool for tracking income and expenses, created as part of my hands-on learning process with Python. It's designed to evolve alongside my understanding of programming, with a focus on solving my own real-world budgeting needs.

---

## Purpose

Most budgeting apps are either too complex, too rigid, or simply not aligned with how I want to track my finances. **Budget Pet** is a minimalist tool tailored to my workflow — distinguishing between business and personal income, automatically allocating tax reserves, and organizing spending into clear categories.

---

## Сurrent Features

- Accepts input about income or expenses via terminal prompts.
- Distinguishes between income and expenses based on input format (`+` or `-`).
- Performs basic input validation and reports errors for unrecognized responses.

---

## Requirements

- Python 3.x
- No external libraries

---

## Running the App

```bash
python3 budget_pet.py
```

Notes

This is an ongoing learning project. Features may be minimal, experimental, or change frequently. The code prioritizes clarity and gradual improvement over completeness.

Roadmap (planned)
    Data storage as .txt

    Data storage as .json

    Data storage via SQLite instead of plain text

    Summarized monthly reports

    Export to CSV

    Tag-based filtering

    CLI argument support for quick entry

File structure (planned)

    budget_pet.py — main script

    data/ — where logs or databases will be stored

    utils/ — helper functions (future)

    README.md
