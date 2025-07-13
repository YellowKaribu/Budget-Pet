import sys
from cli import main

def main() -> int:
    """Entry point for the module when run directly."""
    from cli import main as cli_main_entry

    return cli_main_entry()


if __name__ == "__main__":
    sys.exit(main())