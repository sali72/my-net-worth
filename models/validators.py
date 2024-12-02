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


class CurrencyValidator:
    @staticmethod
    def validate(currency) -> None:
        # Validate user_id for non-predefined currencies
        if not currency.is_predefined and not currency.user_id:
            raise ValidationError("user_id is required for non-predefined currencies.")

        # Validate code length based on currency_type
        CurrencyValidator.validate_code_length(currency.code, currency.currency_type)

    @staticmethod
    def validate_code_length(code: str, currency_type: str) -> None:
        if currency_type == "fiat":
            if len(code) != 3:
                raise ValidationError(
                    "Code must be exactly 3 characters for fiat currencies."
                )
        elif currency_type == "crypto":
            if not (3 <= len(code) <= 10):
                raise ValidationError(
                    "Code must be between 3 and 10 characters for crypto currencies."
                )
        else:
            raise ValidationError(f"Invalid currency_type: {currency_type}")
