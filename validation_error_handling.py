from typing import Any
from enum import Enum
from pydantic_core import ErrorDetails


def str_error(error_type: str, field: str, msg: str, input_raw: str,
              expected: int | None) -> None:

    input_processed = len(input_raw)

    if error_type == "string_too_short":
        if not input_processed:
            print(f"'{field}' cannot be empty.")
        else:
            print(
                f"'{field}' should be larger than or equal to {expected}",
                f"char. Got {input_processed}")
    elif error_type == "string_too_long":
        print(
            f"'{field}' should be smaller than or equal to {expected} char.",
            f"Got {input_processed}")
    else:
        print("Unknown Error:", msg)


def int_error(error_type: str, field: str, msg: str, input_raw: int,
              expected: int | None) -> None:

    input_processed = input_raw

    if error_type == "int_parsing":
        print(f"'{field}' must an integer. Got {input_processed}")
    elif error_type == "less_than_equal":
        if expected == 0:
            print(
                f"'{field}' must be positive. Got {input_processed}")
        else:
            print(
                f"'{field}' should be less than or equal to {expected}.",
                f"Got {input_processed}")
    elif error_type == "greater_than_equal":
        if expected == 0:
            print(
                f"'{field}' must be negative. Got {input_processed}")
        else:
            print(
                f"'{field}' should be greater than or equal to {expected}.",
                f"Got {input_processed}")
    else:
        print("Unknown Error:", msg)


def float_error(error_type: str, field: str, msg: str, input_raw: float,
                expected: float | None) -> None:

    input_processed = input_raw

    if error_type == "float_parsing":
        print(f"'{field}' must an integer. Got {input_processed}")
    elif error_type == "less_than_equal":
        if expected == 0:
            print(
                f"'{field}' must be positive. Got {input_processed}")
        else:
            print(
                f"'{field}' should be less than or equal to {expected}.",
                f"Got {input_processed}")
    elif error_type == "greater_than_equal":
        if expected == 0:
            print(
                f"'{field}' must be negative. Got {input_processed}")
        else:
            print(f"'{field}' should be greater than or equal to {expected}.",
                  f"Got {input_processed}")
    else:
        print("Unknown Error:", msg)


#    if (min == 0 and max == 100
#            and field_float < min and field_float > max):
#        print("SpaceStation Oxygen Level be a percentage.")


def bool_error(error_type: str, field: str, msg: str, input_raw: bool) -> None:

    input_processed = input_raw

    if error_type == "bool_parsing":
        print(f"'{field}' must a valid boolean. Got {input_processed}")
    else:
        print("Unknown Error:", msg)


# def date_error(error_type: str, field: str, msg: str, input_raw: date,
#                expected: str | None) -> None:

#     input_processed = input_raw

#     if error_type == "date_from_datetime_parsing":
#         print(f"'{field}' must be a valid date. Got {input_processed}")
#     else:
#         print("Unknown Error:", msg)


def enum_error(error_type: str, field: str, msg: str, input_raw: Enum,
               expected: str | None) -> None:

    # print(type(input_raw))
    # print(input_raw)

    input_processed = input_raw

    if error_type == "enum":
        print(f"'{field}' must {msg[len('Input should '):]}.",
              f"Got {input_processed}")
    else:
        print("Unknown Error:", msg)


def missing_error(error_type: str, field: str, msg: str, input_raw: Any,
                  expected: str | None) -> None:

    # print(type(input_raw))
    # print(input_raw)

    input_processed = input_raw

    if error_type == "date_from_datetime_parsing":
        print(f"'{field}' must be a valid date. Got {input_processed}")
    else:
        print("Unknown Error:", msg)


def error_processing(error_details: list[ErrorDetails]) -> None:

    # print()
    # print()
    # print("\n".join(error_details))
    # print("ALL:", error_details, sep="\n")
    # print()
    # print()

    for error in error_details:

        # print()
        # print("current:", error)
        # print()

        error_type = error["type"]
        if not len(error["loc"]):
            field = None
        else:
            field = str(error["loc"][0])
        msg: str = error["msg"]
        input: Any = error["input"]
        get_expected: Any = error.get("ctx")
        # print("get expected:", get_expected)
        # print()
        expected: list[Any] = (list(get_expected.values())[0]
                               if get_expected else get_expected)

        # print()
        # print("unpacked:", error_type, field, msg, input, expected)
        # print()
        if field is None:
            print(msg[len("Value error, "):])
        elif field in ["name", "start", "end"]:
            str_error(error_type, field, msg, input, expected)  # type: ignore
        elif field in ["duration_minutes", "witness_count"]:
            int_error(error_type, field, msg, input, expected)  # type: ignore
        elif field in ["signal_strength", "oxygen_level"]:
            float_error(
                error_type, field, msg, input, expected)  # type: ignore
        # elif field in ["timestamp"]:
        #     date_error(error_type, field, msg, input, expected)
        elif field in ["is_verified"]:
            bool_error(error_type, field, msg, input)
        elif field in ["zone"]:
            enum_error(error_type, field, msg, input, expected)  # type: ignore
        elif error_type in ["missing"]:
            missing_error(
                error_type, field, msg, input, expected)  # type: ignore

        else:
            print("Unknown error:", error)
