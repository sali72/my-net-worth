from mongoengine import ValidationError

from models.models import Transaction


class TransactionValidator:
    @staticmethod
    def validate(transaction: Transaction) -> None:
        if transaction.type == "transfer":
            TransactionValidator._validate_transfer(transaction)
        elif transaction.type == "expense":
            TransactionValidator._validate_expense(transaction)
        elif transaction.type == "income":
            TransactionValidator._validate_income(transaction)
        else:
            raise ValidationError(f"Unknown transaction type: {transaction.type}")

    @staticmethod
    def _validate_transfer(transaction: Transaction) -> None:
        if not transaction.from_wallet_id or not transaction.to_wallet_id:
            raise ValidationError(
                "Both 'from_wallet_id' and 'to_wallet_id' are required for transfers."
            )
        if transaction.from_wallet_id == transaction.to_wallet_id:
            raise ValidationError(
                "'from_wallet_id' and 'to_wallet_id' cannot be the same for transfers."
            )

    @staticmethod
    def _validate_expense(transaction: Transaction) -> None:
        if not transaction.from_wallet_id:
            raise ValidationError("'from_wallet_id' is required for expenses.")
        if transaction.to_wallet_id:
            raise ValidationError("'to_wallet_id' should not be provided for expenses.")

    @staticmethod
    def _validate_income(transaction: Transaction) -> None:
        if not transaction.to_wallet_id:
            raise ValidationError("'to_wallet_id' is required for incomes.")
        if transaction.from_wallet_id:
            raise ValidationError(
                "'from_wallet_id' should not be provided for incomes."
            )
