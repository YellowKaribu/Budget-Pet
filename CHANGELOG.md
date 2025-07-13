# Changelog

## [0.2.1] -

### Add
- Monthly event processing logic via `check_monthly_events`


---

## [0.2.0] - 

### Fix
- Fixed extra text in user messages caused by incorrect argument type passed to notify()
- Fixed non-working cancel command when entered as transaction amount

## Add
- Users can now enter transaction amounts using either the European format (1,2) or the Russian format (1.2).
- Support for transaction input cancellation by user: "отмена"
- Implemented CLI option to display transaction log via notifier port.
- Added CLI menu option for exiting the program.
- Added labeled display of `BudgetState` fields in CLI output for improved readability.

### Refactored
- Transitioned to a monolithic hexagonal architecture to isolate core logic and enabling easier addition of new modules in the future (e.g., MySQL as a database, web servers, etc.).

---

## [0.1.1] - 08-07-2025

### Added
- `exit_program()` function for clean program termination with a farewell message.
- User can now choose between: adding an operation, viewing balance, or exiting the program.
- Introduced a centralized `collect_transaction_details()` function to gather all user input for transactions.
- Added UserCancelledError exception and implemented support for graceful cancellation via cancel/menu/отмена inputs.
- Added `user_input()` wrapper to standardize input handling and detect cancellation.
- Introduced TypedDict (UserMessages) and Literal-based type alias (MessageKey) for message keys to improve IDE autocomplete and key validation (but this will be replaced in the next updates)

### Changed
- Refactored most functions to better adhere to the single-responsibility principle (one function - one action).
- Menu logic now uses the `MENU_OPTIONS` dictionary to dispatch functions dynamically.
- The `main()` function has been refactored to use `wait_for_command()` and call the selected function from the dictionary.
- Replaced all `input()` calls with `user_input()`, enabling unified cancellation handling and returning to the main menu when "cancel" is entered.
- Replaced all inline user messages with centralized `notify()` function using the USER_MESSAGES dictionary.
- Added helper functions and decorators for reading and writing state file.
- Replaced raw "+" / "-" input parsing with TransactionType enum usage.
- Rewrote `log_transaction()` for cleaner formatting and added operation type as a column.

### Style
- Code formatted according to PEP 8: max line length, argument alignment, and clean indentation.
- Docstrings ritten using PEP 257 style with proper descriptions and type annotations.
- Multi-line/multitask functions and names rewritten for clarity and readability.
- Dubpicate code replaced with decorators and dataclasses


---

## [0.1.0] - before 04-07-2025

### Added
- Core functionality:
  - logging operations 
  - reading/writing balance state in `budget_state.json`
  - handling income and expenses
  - allocating IP-related income into tax and reserve funds
- Expense category support and user comments
- Log file output to `budget_log.txt`
