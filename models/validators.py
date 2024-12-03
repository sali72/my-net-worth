from mongoengine import ValidationError

from models.enums import TransactionTypeEnum as T


class PredefinedEntityValidator:
    @staticmethod
    def validate(entity) -> None:
        if not entity.is_predefined and not entity.user_id:
            raise ValidationError(
                f"user_id is required for non-predefined {entity.__class__.__name__}."
            )

        if not entity.is_predefined:
            existing_predefined = entity.__class__.objects(
                name=entity.name, is_predefined=True
            ).first()
            if existing_predefined:
                raise ValidationError(
                    f"A predefined {entity.__class__.__name__} with the name '{entity.name}' already exists."
                )


class TransactionValidator:
    @staticmethod
    def validate(transaction) -> None:
        if transaction.type == T.TRANSFER.value:
            TransactionValidator._validate_transfer(transaction)
        elif transaction.type == T.EXPENSE.value:
            TransactionValidator._validate_expense(transaction)
        elif transaction.type == T.INCOME.value:
            TransactionValidator._validate_income(transaction)
        else:
            raise ValidationError(f"Unknown transaction type: {transaction.type}")

    @staticmethod
    def _validate_transfer(transaction) -> None:
        if not transaction.from_wallet_id or not transaction.to_wallet_id:
            raise ValidationError(
                "Both 'from_wallet_id' and 'to_wallet_id' are required for transfers."
            )
        if transaction.from_wallet_id == transaction.to_wallet_id:
            raise ValidationError(
                "'from_wallet_id' and 'to_wallet_id' cannot be the same for transfers."
            )

    @staticmethod
    def _validate_expense(transaction) -> None:
        if not transaction.from_wallet_id:
            raise ValidationError("'from_wallet_id' is required for expenses.")
        if transaction.to_wallet_id:
            raise ValidationError("'to_wallet_id' should not be provided for expenses.")

    @staticmethod
    def _validate_income(transaction) -> None:
        if not transaction.to_wallet_id:
            raise ValidationError("'to_wallet_id' is required for incomes.")
        if transaction.from_wallet_id:
            raise ValidationError(
                "'from_wallet_id' should not be provided for incomes."
            )


class CurrencyValidator:
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


class CurrencyExchangeValidator:
    @staticmethod
    def validate(exchange) -> None:
        CurrencyExchangeValidator.validate_reverse_pair(exchange)

    @staticmethod
    def validate_reverse_pair(exchange) -> None:
        reverse_pair_exists = exchange.__class__.objects(
            user_id=exchange.user_id,
            from_currency_id=exchange.to_currency_id,
            to_currency_id=exchange.from_currency_id,
        ).first()
        if reverse_pair_exists:
            raise ValidationError(
                "A reverse currency exchange pair already exists for this user."
            )

    @staticmethod
    def validate_input_currency_ids(exchange) -> None:
        if exchange.from_currency_id == exchange.to_currency_id:
            raise ValidationError(
                "from_currency_id can't be same as to_currency_id."
            )
