from data import Transaction

BANK_NAME = 'Revolut'
BANK_BIC = 'REVOLT21'

DEFAULT_SEQUENCE_NO = 1


class Mt940Writer:

    def __init__(self, filename, account_iban):
        self.file = open(filename, 'w')
        self.account_iban = account_iban

        self._write_header()
        self._written_starting_balance = False
        self._written_ending_balance = False

        self._balance = None
        self._date = None


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


    def write_transaction(self, transaction : Transaction):
        if not self._written_starting_balance:
            self._write_starting_balance(transaction.datetime,
                                         transaction.before_balance)

        self.file.writelines([
            Mt940.make_61(
                transaction.datetime,
                transaction.amount),
            Mt940.make_86(
                transaction.iban,
                transaction.name,
                transaction.description)
        ])

        self._balance = transaction.after_balance
        self._date = transaction.datetime


    def release(self):
        if not self.file.closed \
           and self._written_starting_balance \
           and not self._written_ending_balance:
            self._write_ending_balance()

        if not self.file.closed:
            self.file.close()


    def _write_header(self):
        self.file.write(
            Mt940.make_header(BANK_BIC))
        self.file.writelines([
            Mt940.make_20(BANK_NAME),
            Mt940.make_25(self.account_iban, CURRENCY),
            Mt940.make_28(DEFAULT_SEQUENCE_NO)
        ])


    def _write_starting_balance(self, date, balance):
        self.file.write(
            Mt940.make_60f(date, balance, CURRENCY))
        self._written_starting_balance = True


    def _write_ending_balance(self):
        self.file.write(
            Mt940.make_62f(self._date, self._balance, CURRENCY))
        self._written_ending_balance = True



CURRENCY = 'EUR'

# format identifier
TAG_940 = '940'

# header
FORMAT_HEADER = \
    '{bic}\n' + \
    TAG_940 + '\n' + \
    '{bic}\n'

# transaction ref
FORMAT_20 = ':20:{bank}\n'

# account id
FORMAT_25 = ':25:{iban} {currency}\n'

# sequence no
FORMAT_28 = ':28:{seqno}\n'

# opening balance
FORMAT_60F = ':60F:{sign}{date}{currency}{amount}\n'

# closing balance
FORMAT_62F = ':62F:{sign}{date}{currency}{amount}\n'

# transaction
FORMAT_61 = ':61:{date}{date2}{amount}{magic}\n'

# transaction 2
FORMAT_86 = ':86:/IBAN/{iban}/NAME/{name}/REMI/{description}\n'

MAGIC = 'NTRFNONREF'


class Mt940:

    @staticmethod
    def make_header(bic):
        return FORMAT_HEADER.format(
            bic=bic)

    @staticmethod
    def make_20(bank):
        return FORMAT_20.format(
            bank=bank)

    @staticmethod
    def make_25(iban, currency):
        return FORMAT_25.format(
            iban=iban,
            currency=currency)

    @staticmethod
    def make_28(seqno):
        return FORMAT_28.format(
            seqno=Mt940.pad_5(seqno))

    @staticmethod
    def make_60f(datetime, balance, currency):
        return FORMAT_60F.format(
            sign=Mt940.amount_sign(balance),
            date=Mt940.date(datetime),
            currency=currency,
            amount= Mt940.amount_val(balance))

    @staticmethod
    def make_62f(datetime, balance, currency):
        return FORMAT_62F.format(
            sign=Mt940.amount_sign(balance),
            date=Mt940.date(datetime),
            currency=currency,
            amount= Mt940.amount_val(balance))

    @staticmethod
    def make_61(datetime, amount):
        return FORMAT_61.format(
            date=Mt940.date(datetime),
            date2=Mt940.date(datetime, with_year=False),
            amount=Mt940.amount(amount),
            magic=MAGIC)

    @staticmethod
    def make_86(iban, name, description):
        return FORMAT_86.format(
            iban=iban,
            name=name,
            description=description)

    @staticmethod
    def pad_5(val):
        return str(val).zfill(5)

    @staticmethod
    def amount_sign(val):
        return 'C' if val > 0 else 'D'

    @staticmethod
    def amount_val(val):
        return '{0:.2f}'.format(abs(val)).replace('.', ',')

    @staticmethod
    def amount(val):
        return Mt940.amount_sign(val) + Mt940.amount_val(val)

    @staticmethod
    def date(val, with_year=True):
        if with_year:
            return val.strftime('%y%m%d')
        else:
            return val.strftime('%m%d')
