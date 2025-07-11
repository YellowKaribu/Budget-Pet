from ports.output_port import NotifierPort

class CliNotifierAdapter(NotifierPort):
    def notify_success(self, message: str) -> None:
        print(f"{message}")