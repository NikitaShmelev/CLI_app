from logger import logger


CLOSED_FIELDS: tuple[str] = (
    "Field ID",
    "Counter",
)  # Fields restricted for modification


def get_field(file_path: str, record_index: int, field_name: str) -> str:
    # Define the field positions and their corresponding lengths (start, end)
    field_positions: dict[str, tuple[int, int]] = {
        "field_id": (0, 2),
        "name": (2, 30),
        "surname": (30, 60),
        "patronymic": (60, 90),
        "address": (90, 120),
        "counter": (2, 8),
        "amount": (8, 20),
        "currency": (20, 23),
        "total_counter": (2, 8),
        "control_sum": (8, 20),
    }

    if field_name not in field_positions:
        raise ValueError(f"Invalid field: {field_name}")

    start, end = field_positions[field_name]

    with open(file_path, "r") as file:
        lines = file.readlines()

        if field_name in ("total_counter", "control_sum"):
            record = lines[-1]
        elif field_name in ("counter", "amount", "currency") and record_index == 0:
            logger.warning("You've passed header index for transaction field")
            return
        else:
            record = lines[record_index]

        return record[start:end].strip()


def add_transaction(file_path: str, amount: int, currency: str) -> None:
    with open(file_path, "r+") as file:
        lines = file.readlines()

        # Read current footer to get the transaction count and sum
        footer = lines[-1]
        current_count = int(footer[2:8])
        current_sum = int(footer[8:20])

        new_counter = f"{current_count + 1:06}"

        # Generate new transaction line
        amount *= 100
        amount_str = f"{amount:012}"  # Ensure amount is 12 characters long
        transaction = f"02{new_counter}{amount_str}{currency}{' ' * 96}\n"

        # Insert the new transaction before the footer
        lines.insert(-1, transaction)

        # Update footer: new count and sum
        total_transactions = current_count + 1
        total_sum = current_sum + amount
        new_footer = f"03{total_transactions:06}{total_sum:012}{' ' * 97}\n"
        lines[-1] = new_footer

        # Write updated content back to the file
        file.seek(0)
        file.writelines(lines)

    logger.info(
        "Added a new transaction. Updated counter: %s, New total sum: %s",
        new_counter,
        total_sum,
    )


def set_field(file_path: str, index: int, field: str, value: str) -> None:
    if field in CLOSED_FIELDS:
        logger.warning(f"{field} field is forbidden for changes")
        return

    field_map: dict[str, tuple[int, int]] = {
        "field_id": (0, 2),
        "counter": (2, 8),
        "amount": (8, 20),
        "currency": (20, 23),
        "reserved_space": (23, 120),
        "name": (2, 30),
        "surname": (30, 60),
        "patronymic": (60, 90),
        "address": (90, 120),
    }

    if field not in field_map:
        raise ValueError(f"Invalid field: {field}")

    with open(file_path, "r") as file:
        lines = file.readlines()

    if index >= len(lines) - 2:
        raise IndexError(f"Index {index} is out of range for the file.")

    if field == "amount":
        try:
            numeric_value = float(value)
            amount = f"{int(numeric_value * 100):012}"

        except ValueError:
            raise ValueError(f"Invalid value for {field}. Expected a numeric value.")
    else:
        amount = value

    line: str = lines[index]

    # Get the field's position range
    start, end = field_map[field]
    if len(amount) > (end - start):
        raise ValueError(
            f"Value is too long for field {field}. Max length is {end - start} characters."
        )

    lines[index] = line[:start] + amount.ljust(end - start) + line[end:]

    if field == "amount":
        # Calculate the new control sum
        old_amount = int(line[8:20].strip())
        new_amount = int(amount)
        control_sum_delta = new_amount - old_amount

        # Parse the footer to update control_sum
        footer: str = lines[-1]
        current_control_sum = int(footer[8:20].strip() or "0")
        updated_control_sum = current_control_sum + control_sum_delta

        # Update the footer with the new control sum
        lines[-1] = footer[:8] + f"{updated_control_sum:012}" + footer[20:]

    with open(file_path, "w") as file:
        file.writelines(lines)

    logger.info(f"Field '{field}' updated successfully for record {index}.")
