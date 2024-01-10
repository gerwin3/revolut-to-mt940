#!/usr/bin/python3

import argparse

from revolut import RevolutCsvReader
from mt940 import Mt940Writer


def main():
    parser = argparse.ArgumentParser(
        prog='oddity-revolut-to-mt940',
        description='Convert Revolut CSV-files to MT940 format.')

    parser.add_argument('--in',
                        dest='input_file',
                        help='path to Revolut csv-file',
                        required=True)

    parser.add_argument('--account-iban',
                        dest='account_iban',
                        help='Revolut account IBAN',
                        required=True)

    parser.add_argument('--out',
                        dest='output_file',
                        help='path to MT940 output path',
                        required=True)

    args = parser.parse_args()

    reader = RevolutCsvReader(args.input_file)

    with Mt940Writer(args.output_file, args.account_iban) as writer:
        transactions = reader.get_all_transactions()
        for transaction in transactions:
            writer.write_transaction(transaction)

        print('Wrote {} transactions to file: {}.'.format(len(transactions), args.output_file))


if __name__ == "__main__":
    main()
