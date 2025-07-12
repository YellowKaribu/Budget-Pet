from abc import ABC, abstractmethod

@abstractmethod 
class TransactionInputPort(ABC):
    @abstractmethod
    def prompt_transaction_type(self) -> str:
        pass

    @abstractmethod
    def prompt_transaction_amount(self) -> str:
        pass

    @abstractmethod
    def prompt_transaction_category(self) -> str:
        pass

    @abstractmethod
    def prompt_transaction_comment(self) -> str:
        pass

    @abstractmethod
    def prompt_tax_status(self) -> str:
        pass


