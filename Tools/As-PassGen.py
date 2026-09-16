import argparse
import secrets
import string
from pathlib import Path


RED = "\033[31m"
RESET = "\033[0m"
BANNER = r""" 
++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  ___  ____        ____
  / _ |/ __/_______/ __/______ ____  ___ ____
 / __ / _// __/___/\ \/ __/ _ `/ _ \/ -_) __/
/_/ |_/___/_/      /___/\__/\_,_/ .__/\__/_/
                         /_/
               As-Password Generator
                 ----------------
                 ++++++++++++++++
"""


def generate_passwords(name, numbers, special_characters, count=500):
    name = "".join(character for character in name if character.isalnum())
    name = name or "User"
    name_variants = [name, name.lower(), name.upper(), name.capitalize()]
    passwords = []
    index = 0

    while len(passwords) < count:
        name_variant = name_variants[index % len(name_variants)]
        number = numbers or "".join(secrets.choice(string.digits) for _ in range(4))
        special_character = special_characters or secrets.choice(string.punctuation)
        suffix = str(index // len(name_variants) + 1)
        password = f"{name_variant}{number}{special_character}{suffix}"

        if password not in passwords:
            passwords.append(password)
        index += 1

    return passwords


def main():
    parser = argparse.ArgumentParser(
        description="Generate 500 possible passwords"
    )
    parser.add_argument("-n", "--name", help="Name to include in passwords")
    parser.add_argument(
        "-d", "--numbers", "--number",
        help="Fixed numbers to include; random numbers are used when omitted"
    )
    parser.add_argument(
        "-s", "--special-char", "--special-characters",
        help="Fixed special character to include; a random one is used when omitted"
    )
    args = parser.parse_args()

    passwords = generate_passwords(
        args.name or "Password",
        args.numbers,
        args.special_char,
    )
    output = BANNER.lstrip("\n") + "\n".join(passwords) + "\n"
    output_path = Path.cwd() / "As-PasswordGen.txt"
    output_path.write_text(output, encoding="utf-8")

    print(f"{RED}{BANNER}{RESET}", end="")
    print("\n".join(passwords))
    print(f"\nSaved {len(passwords)} passwords to {output_path}")


if __name__ == "__main__":
    main()
