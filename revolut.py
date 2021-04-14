import os
import string
import csv
import math

from datetime import datetime, timedelta

from data import Transaction

EXCPECT_HEADERS = [
    'Date started (UTC)', 'Date completed (UTC)', 'Date started (Europe/Amsterdam)',
    'Date completed (Europe/Amsterdam)', 'ID', 'Type', 'Description', 'Reference',
    'Payer', 'Card number', 'Orig currency', 'Orig amount', 'Payment currency',
    'Amount', 'Fee', 'Balance', 'Account', 'Beneficiary account number',
    'Beneficiary sort code or routing number', 'Beneficiary IBAN', 'Beneficiary BIC'
]

NAME_REMOVE_PREFIXES = [
    'Payment from ',
    'To '
]

DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%H:%M:%S'
DATETIME_FORMAT = DATE_FORMAT + TIME_FORMAT

FEE_NAME = 'Revolut'
FEE_IBAN = ''
FEE_DESCRIPTION_FORMAT = 'Bank transaction fee {}'
FEE_DATETIME_DELTA = timedelta(seconds=1)

class RevolutCsvReader:

    def __init__(self, filename):
        if not os.path.isfile(filename):
            raise ValueError('File does not exist: {}'.format(filename))

        self.filename = filename

        self.file = open(self.filename, 'r')
        self.reader = csv.reader(self.file)

        self._validate()


    def __del__(self):
        if not self.file.closed:
            self.file.close()


    def _validate(self):
        def _santize_header(header):
            header = ''.join([c for c in header
                              if c in string.printable])
            header = header.strip()
            return header

        headers = [_santize_header(h) for h in next(self.reader)]
        if headers != EXCPECT_HEADERS:
            raise ValueError('Headers do not match expected Revolut CSV format.')


    def get_all_transactions(self):
        transactions = []
        for row in self.reader:
            transactions = self._parse_transaction(row) + transactions

        return transactions


    def _parse_transaction(self, row):

        def _santize_name(name_):
            for remove_prefix in NAME_REMOVE_PREFIXES:
                if name_.startswith(remove_prefix):
                    name_ = name_[len(remove_prefix):]

            return name_

        def _parse_datetime(date_str, time_str):
            return datetime.strptime(date_str + time_str, DATETIME_FORMAT)


        _0, _1, completed_date_str, completed_time_str, _4, _5, name, description, _8, _9, \
        _10, _11, _12, amount_str, fee_str, balance_str, _16, _17, _18, iban, _20 \
            = row

        completed_datetime = _parse_datetime(completed_date_str, "00:00:00")
        amount, fee, balance = \
            float(amount_str), float(fee_str), float(balance_str)

        transaction_without_fee = Transaction(
            amount=amount,
            name=_santize_name(name),
            iban=iban,
            description=description,
            datetime=completed_datetime,
            before_balance=balance - amount - fee,
            after_balance=balance - fee)

        batch = [transaction_without_fee]

        if not math.isclose(fee, 0.00):
            fee_transaction = self._make_fee_transaction(
                completed_datetime,
                balance,
                fee)

            batch.append(fee_transaction)

        return batch


    def _make_fee_transaction(self, completed_datetime, balance, fee):
        return Transaction(
            amount=fee,
            name=FEE_NAME,
            iban=FEE_IBAN,
            # include timestamp of transaction to make sure that SnelStart
            # does not detect similar transactions as the same one
            description=FEE_DESCRIPTION_FORMAT.format(int(completed_datetime.timestamp())),
            datetime=completed_datetime + FEE_DATETIME_DELTA,
            before_balance=balance - fee,
            after_balance=balance)
