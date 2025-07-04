# Changelog

## [0.2.0] - 2025-07-04

### Added
- `exit_program()` function for clean program termination with a farewell message.
- `wait_for_command(prompt, expected)` - a reusable input handler based on dictionary keys.
- Constants `MENU_TEXT` and `MENU_OPTIONS` to structure the main menu.
- User can now choose between: adding an operation, viewing balance, or exiting the program.

### Changed
- Menu logic now uses the `MENU_OPTIONS` dictionary to dispatch functions dynamically.
- The `main()` function has been refactored to use `wait_for_command()` and call the selected function from the dictionary.
- `input()` prompts have been standardized in both format and logic.

### Style
- Code formatted according to PEP 8: max line length, argument alignment, and clean indentation.
- Multi-line operations like `f.write()` rewritten for clarity and readability.
- Docstrings ritten using PEP 257 style with proper descriptions and type annotations.

---

## [0.1.0] - before 2025-07-04

### Added
- Core functionality:
  - logging operations 
  - reading/writing balance state in `budget_state.json`
  - handling income and expenses
  - allocating IP-related income into tax and reserve funds
- Expense category support and user comments
- Log file output to `budget_log.txt`
