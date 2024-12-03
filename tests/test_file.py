import pytest
from file_parser import set_field, add_transaction, get_field
from utils import generate_example_file, validate_file


@pytest.fixture
def setup_test_file(tmpdir: str):
    test_file = tmpdir.join("test_file.txt")
    transaction_count = 5
    generate_example_file(str(test_file), transaction_count)

    return test_file


def test_get_field_valid(setup_test_file):
    value = get_field(setup_test_file, 1, "amount")

    assert len(value) == 12
    assert value == "000000000100"


def test_get_field_invalid(setup_test_file):
    with pytest.raises(ValueError):
        get_field(setup_test_file, 1, "invalid_field")


def test_set_field_valid(setup_test_file):
    set_field(setup_test_file, 1, "amount", "1500")

    with open(setup_test_file, "r") as file:
        amount: str = file.readlines()[1][8:20]

        assert len(amount) == 12
        assert amount == "000000150000"


def test_set_field_invalid_format(setup_test_file):
    with pytest.raises(ValueError):
        set_field(setup_test_file, 1, "amount", "abc")  # non-numeric


def test_set_field_invalid_type(setup_test_file):
    with pytest.raises(ValueError):
        set_field(
            setup_test_file, 1, "amount", "invalid_value"
        )  # Non-numeric value for amount


def test_add_transaction(setup_test_file):
    add_transaction(setup_test_file, 100, "PLN")
    with open(setup_test_file, "r") as file:
        lines = file.readlines()

        transaction = lines[-2]
        assert len(transaction) == 120
        assert transaction.strip()[-3:] == "PLN"
        assert transaction.strip()[8:-3] == "000000010000"

        assert len(lines) == 8  # 6 original lines + 1 new transaction + 1 footer line


def test_generate_example_file(tmpdir):
    file_path = tmpdir.join("generated_file.txt")
    transactions_count = 5
    generate_example_file(file_path, transactions_count)

    with open(file_path, "r") as file:
        lines = file.readlines()
        assert len(lines) == 7  # 1 header + 5 transactions + 1 footer

    # transactions
    for ind, line in enumerate(lines[1:-1]):
        assert line.startswith("02")
        assert line[2:8] == f"{(ind+1):06}"  # Counter should be 00000X
        assert line[8:20] == f"{(ind+1)*100:012}"

    # footer
    footer_line = lines[-1]
    total_count = footer_line[2:8]
    control_sum = footer_line[8:20]

    assert total_count == f"00000{transactions_count}"
    assert control_sum == "000000001500"  # 100 + 200 + 300 + 400 + 500


def test_control_amount_update(setup_test_file):
    with open(setup_test_file, "r") as file:
        lines = file.readlines()
        initial_control_sum = int(lines[-1][8:20].strip())

    set_field(setup_test_file, 1, "amount", "200.00")  # Update amount to 200.00

    # Calculate the expected new control sum
    old_amount = int(lines[1][8:20].strip())
    new_amount = 20000
    control_sum_delta = new_amount - old_amount
    expected_control_sum = initial_control_sum + control_sum_delta

    with open(setup_test_file, "r") as file:
        updated_lines = file.readlines()
        updated_control_sum = int(updated_lines[-1][8:20].strip())

    assert updated_control_sum == expected_control_sum, (
        f"Expected control sum {expected_control_sum}, "
        f"but got {updated_control_sum}."
    )


def test_validate_file(setup_test_file):
    assert validate_file(setup_test_file) is None
