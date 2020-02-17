from collections import namedtuple

Transaction = namedtuple(
    'Transaction', [
        'amount',
        'name',
        'iban',
        'description',
        'datetime',
        'after_balance',
        'before_balance'
    ])