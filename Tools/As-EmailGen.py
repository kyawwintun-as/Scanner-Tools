
import argparse
import random
from pathlib import Path


RED = "\033[31m"
RESET = "\033[0m"
BANNER = r"""   ___  ____        ____
  / _ |/ __/_______/ __/______ ____  ___ ____
 / __ / _// __/___/\ \/ __/ _ `/ _ \/ -_) __/
/_/ |_/___/_/      /___/\__/\_,_/ .__/\__/_/
                         /_/
               As-EmailGen by Mr-Loser
                 ----------------
"""


def generate_email_accounts(name, mail_domains, starting_number, count=100):
    name_parts = name.lower().split()
    first_name = name_parts[0]
    last_name = name_parts[-1]
    account_formats = [
        f"{first_name}.{last_name}",
        f"{first_name}{last_name}",
        f"{first_name[0]}{last_name}",
        f"{first_name}{last_name[0]}",
    ]

    accounts = []
    number = starting_number
    while len(accounts) < count:
        for domain in mail_domains:
            for account in account_formats:
                accounts.append(f"{account}{number}@{domain}")
                if len(accounts) == count:
                    return accounts
        number += 1
    return accounts

def main():
    parser = argparse.ArgumentParser(description='Generate possible email accounts')
    parser.add_argument('-n', '--name', help='Specify the full name')
    parser.add_argument('-m', '--mail-domain', help='Specify the email domain')
    parser.add_argument('-d', '--number', type=int, default=1195,
                        help='Starting number to append to accounts (default: 1195)')
    args = parser.parse_args()

    if args.name:
        name = args.name
    else:
        names = ["John Smith", "Jane Doe", "Jim Brown", "Jill White", "Jack Taylor"]
        name = random.choice(names)

    if args.mail_domain:
        mail_domains = [args.mail_domain]
    else:
        mail_domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]

    accounts = generate_email_accounts(name, mail_domains, args.number)
    output = BANNER + "\n".join(accounts) + "\n"
    output_path = Path.cwd() / "As-EmailGen.txt"
    output_path.write_text(output, encoding="utf-8")

    print(f"{RED}{BANNER}{RESET}", end="")
    for account in accounts:
        print(account)
    print(f"\nSaved {len(accounts)} accounts to {output_path}")

if __name__ == "__main__":
    main()
