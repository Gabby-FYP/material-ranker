from typing import Any

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import InitErrorDetails, PydanticCustomError, ValidationError, core_schema


class Password(str):
    """Pydantic type for password"""

    special_chars: set[str] = {
        "$", "@", "#", "%", "!", "^", "&", "*", "(", ")", "-", "_", "+", "=", "{", "}", "[", "]"
    }

    min_length: int = 8
    includes_special_chars: bool = True
    includes_numbers: bool = True
    includes_lowercase: bool = True
    includes_uppercase: bool = True

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema(),
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        json_schema = handler(core_schema)
        json_schema.update(
            minLength=cls.min_length,
            includesNumbers=cls.includes_numbers,
            includesLowercase=cls.includes_lowercase,
            includesUppercase=cls.includes_uppercase,
            includesSpecialChars=cls.includes_special_chars,
            specialChars=list(cls.special_chars),
        )
        return json_schema

    @classmethod
    def validate(cls, value: Any) -> "Password":
        # Determine if the password meets all criteria.
        valid = isinstance(value, str)
        if valid:
            if len(value) < cls.min_length:
                valid = False
            if cls.includes_numbers and not any(char.isdigit() for char in value):
                valid = False
            if cls.includes_uppercase and not any(char.isupper() for char in value):
                valid = False
            if cls.includes_lowercase and not any(char.islower() for char in value):
                valid = False
            if cls.includes_special_chars and not any(char in cls.special_chars for char in value):
                valid = False

        if not valid:
            message = (
                f"Password must be {cls.min_length}+ characters "
                f"and include a number, an uppercase letter, a lowercase letter, and a special character."
            )
            raise ValidationError.from_exception_data(
                title="invalid_password",
                line_errors=[
                    InitErrorDetails(type=PydanticCustomError("value_error", message), input=value)
                ],
            )

        return cls(value)
