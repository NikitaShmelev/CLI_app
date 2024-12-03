from faker import Faker
from logger import logger


def generate_example_file(file_path: str, transaction_count: int) -> None:
    """Generate an example fixed-width file with the given number of transactions."""
    if not (1 <= transaction_count <= 20000):
        raise ValueError("Transaction count must be between 1 and 20000.")

    fake = Faker()

    # Generate Header
    header: str = (
        "01"
        + f"{fake.first_name()}".ljust(28)
        + f"{fake.last_name()}".ljust(30)
        + f"{fake.first_name()}".ljust(30)
    )

    address: str = fake.address().replace("\n", ", ")
    header += address[:29].ljust(29)
    header += "\n"

    transactions: list[str] = []
    control_sum: int = 0

    # Generate transactions
    for i in range(1, transaction_count + 1):
        counter = f"{i:06}"
        amount = f"{i * 100:012}"

        control_sum += i * 100
        reserved_space: str = " " * 96  # Adjust to ensure 119 total length

        # Construct the transaction line (119 characters + \n = 120)
        transaction = f"02{counter}{amount}USD{reserved_space}\n"
        transactions.append(transaction)

    # Generate the footer
    footer: str = f"03{transaction_count:06}{control_sum:012}{' ' * 100}"

    with open(file_path, "w") as file:
        file.write(header)
        file.writelines(transactions)
        file.write(footer)

    logger.info(
        f"Example file with {transaction_count} transactions generated successfully at '{file_path}', total_amount: {control_sum}."
    )


def validate_file(file_path: str) -> None:
    with open(file_path, "r") as file:
        lines = file.readlines()

    # Validate header
    if not lines[0].startswith("01") or len(lines[0]) != 120:
        raise ValueError("Invalid header format.")

    # Validate transactions
    for line_num, line in enumerate(lines[1:-1]):
        if not line.startswith("02") or len(line) != 120:
            raise ValueError(f"Invalid transaction format, line {line_num}")

    # Validate footer
    footer = lines[-1]
    if not footer.startswith("03") or len(footer) != 120:
        raise ValueError("Invalid footer format.")

    logger.info("File validation passed.")
