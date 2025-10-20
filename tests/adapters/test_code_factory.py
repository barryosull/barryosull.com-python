import pytest

from backend.adapters.api.rest.code_factory import CodeFactory


def test_int_to_code_returns_four_character_string():
    code = CodeFactory.int_to_code(1)
    assert len(code) == 4
    assert isinstance(code, str)


def test_int_to_code_uses_valid_characters():
    for i in range(100):
        code = CodeFactory.int_to_code(i)
        assert all(c in CodeFactory.CHARS for c in code)


def test_sequential_inputs_produce_different_codes():
    codes = [CodeFactory.int_to_code(i) for i in range(10)]
    assert len(codes) == len(set(codes))


def test_sequential_inputs_are_scrambled():
    code1 = CodeFactory.int_to_code(1)
    code2 = CodeFactory.int_to_code(2)
    code3 = CodeFactory.int_to_code(3)

    assert code1 != code2
    assert code2 != code3
    assert code1 != "0001"
    assert code2 != "0002"


def test_code_to_int_reverses_encoding():
    original = 42
    code = CodeFactory.int_to_code(original)
    decoded = CodeFactory.code_to_int(code)
    assert decoded == original


def test_round_trip_for_various_numbers():
    test_values = [0, 1, 2, 100, 1000, 10000, 100000, 999999]

    for n in test_values:
        code = CodeFactory.int_to_code(n)
        decoded = CodeFactory.code_to_int(code)
        assert decoded == n


def test_wraparound_at_max_codes():
    max_codes = CodeFactory.MAX_CODES

    code_at_max = CodeFactory.int_to_code(max_codes)
    code_at_zero = CodeFactory.int_to_code(0)

    assert code_at_max == code_at_zero


def test_wraparound_beyond_max_codes():
    max_codes = CodeFactory.MAX_CODES

    code_before_wrap = CodeFactory.int_to_code(max_codes - 1)
    code_after_wrap = CodeFactory.int_to_code(max_codes + 1)
    code_at_one = CodeFactory.int_to_code(1)

    assert code_after_wrap == code_at_one
    assert code_before_wrap != code_after_wrap


def test_zero_produces_valid_code():
    code = CodeFactory.int_to_code(0)
    assert code == "0000"


def test_negative_numbers_wrap_around():
    code_negative = CodeFactory.int_to_code(-1)
    code_max_minus_one = CodeFactory.int_to_code(CodeFactory.MAX_CODES - 1)

    assert code_negative == code_max_minus_one


def test_same_input_produces_same_code():
    code1 = CodeFactory.int_to_code(42)
    code2 = CodeFactory.int_to_code(42)

    assert code1 == code2


def test_deterministic_encoding():
    expected_codes = {
        1: "QGLJ",
        2: "GX72",
        3: "7DSL",
        100: "I3SS",
        1000: "11ZS",
    }

    for n, expected_code in expected_codes.items():
        assert CodeFactory.int_to_code(n) == expected_code


def test_code_to_int_with_known_codes():
    known_mappings = {
        "QGLJ": 1,
        "GX72": 2,
        "7DSL": 3,
        "0000": 0,
    }

    for code, expected_int in known_mappings.items():
        assert CodeFactory.code_to_int(code) == expected_int


def test_all_codes_in_range_are_unique():
    sample_size = 1000
    codes = [CodeFactory.int_to_code(i) for i in range(sample_size)]

    assert len(codes) == len(set(codes))


def test_large_numbers():
    large_number = 1000000
    code = CodeFactory.int_to_code(large_number)
    decoded = CodeFactory.code_to_int(code)

    assert len(code) == 4
    assert decoded == large_number % CodeFactory.MAX_CODES
