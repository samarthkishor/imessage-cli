#!/usr/bin/env python3

import subprocess
import sys

from typing import List, Optional

SEND_MESSAGE_SCRIPT_PATH = "send_text.applescript"
GET_CONTACT_NUMBER_SCRIPT_PATH = "get_contact_number.applescript"


def format_number(num: str) -> str:
    """
    Returns a string containing just the numbers
    """
    return "".join([char for char in num if char.isdigit()])


def get_numbers(name: List[str], number=None) -> Optional[List[int]]:
    """
    Returns a list of numbers associated with a specific contact.
    If the parameter `number` is specified, returns a list with just the number
    only if it is in the contact.
    """
    args = ["osascript", GET_CONTACT_NUMBER_SCRIPT_PATH]
    for n in name:
        args.append(n)
    name = " ".join(name)
    try:
        output = subprocess.check_output(args).decode("utf-8")
    except subprocess.CalledProcessError:
        print("Error: no contact with name", name)
        return None
    output = output.split(",")

    if len(output) == 0:
        print("Error: no numbers for contact", name)
        return None

    output = [format_number(n) for n in output]

    if number is not None:
        number_str = format_number(number)
        if number_str not in output:
            print(f"Error: contact {name} does not have number {number}")
            return None
        return [int(number_str)]

    return [int(n) for n in output]


def send_message(number: int, message=None):
    """
    Sends an iMessage to the number.
    If `message` is not provided, send the contents of stdin.
    """
    message_count = 0
    if message is None:
        for line in sys.stdin:
            line = line.rstrip()
            # skip blank lines
            if line == "":
                continue
            print("message:", line)
            try:
                subprocess.run(
                    ["osascript", SEND_MESSAGE_SCRIPT_PATH, str(number), line]
                )
                message_count += 1
            except subprocess.CalledProcessError:
                print("There was an error sending a message to", number)
    else:
        # message is a list of strings because of argparse
        message = " ".join(message)
        print("message:", message)
        try:
            subprocess.run(
                ["osascript", SEND_MESSAGE_SCRIPT_PATH, str(number), message]
            )
            message_count += 1
        except subprocess.CalledProcessError:
            print("There was an error sending a message to", number)

    print(f"Sent {message_count} message(s) to {number}")


def choose_number(name: List[str], numbers: List[int]) -> int:
    """
    Prompts the user to pick a number from a list of numbers.
    Returns the number that was picked.

    If there is only one number in the list, returns that number.
    """
    if len(numbers) == 1:
        return numbers[0]

    name = " ".join(name)
    print(f"Contact {name} has more than one number.")
    for i, number in enumerate(numbers):
        print(f"({i + 1}): {number}")
    while True:
        try:
            print("Which one would you like to send a message to?")
            choice = int(input("Enter a number (1, 2, etc.): "))
            # subtract 1 because choice starts from 1
            return numbers[choice - 1]
        except ValueError:
            print(
                (
                    "Error: type a number (1, 2, etc.) corresponding to "
                    "the number you want to send a message to."
                )
            )
            continue


def main(**kwargs):
    print(kwargs)
    message = kwargs["message"]
    if kwargs["name"] is not None:
        if kwargs["number"] is not None:
            numbers = get_numbers(kwargs["name"], number=kwargs["number"])
            if numbers is None:
                return
            # numbers should only have 1 element
            assert len(numbers) == 1
            send_message(numbers[0], message)
            return
        else:
            numbers = get_numbers(kwargs["name"])
            if numbers is None:
                return
            name = " ".join(kwargs["name"])
            if len(numbers) > 1 and message is None:
                print(
                    "Error: If a contact has more than one number and the"
                    " message is from stdin, you must specify the number"
                    " with --number"
                )
                return
            number = choose_number(name, numbers)
            send_message(number, message)
            return
    elif kwargs["number"] is not None:
        number = format_number(kwargs["number"])
        send_message(number)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="iMessage utility")
    parser.add_argument(
        "--name",
        type=str,
        nargs="+",
        help="First name and optional last name (separated with spaces)",
    )
    parser.add_argument(
        "--number", help="Phone number"
    )  # the script handles formatting
    parser.add_argument(
        "--message", type=str, nargs="*", help="The message you want to send"
    )
    args = parser.parse_args()
    main(name=args.name, number=args.number, message=args.message)
