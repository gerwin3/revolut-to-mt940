# Convert Revolut export file to MT940 format

This small Python script converts Revolut export files (in CSV) to MT940. You can use the MT940 to import statements in some bookkeeping software like SnelStart (which it was built for).

## Disclaimer
This script comes without any warranty whatsoever. Do not use it in production. Do not use it if you are not familiar with how banks work, how bookkeeping software works, and if you do not have the technical know-how to make changes to this script yourself if something breaks. If you do use this script it might kill your cat or start World War 3. Don't come to me, I warned you.

## Features

* It is specifically built for getting Revolut transactions into SnelStart. 
* Parses the Revolut CSV file and extracts: timestamp, transaction type, transaction description, transaction reference, transaction amount, fee amount, balance after transaction, counterparty IBAN.
* This information is converted into a valid MT940 file.
* Revolut charges fees for transactions. These are included in the transaction (as Revolut sees it). This could cause problems when importing into bookkeeping software as the amounts do not match up. This script will not include fees in transactions but insert "fake" transactions for each deducted fee. You will see those transactions separately in your bookkeeping software but in Revolut they are included in the transaction.

## Limitations

* Apart from loading transactions into SnelStart, it has not been tested on any other tasks. It might or might not work for your use case.
* Revolut does not export the counterparty IBAN for transactions that you *receive*. As such, the IBAN field in MT940 for credit transactions are usually empty.
* The export files from Revolut are missing some key data fields when the transaction is still pending (status is not *COMPLETED*). Only export completed transactions.

## Usage

1. Clone the repository.
2. Make sure you have Python 3.
3. Run the following command:

```
python3 main.py \
	--in /path/to/revolut.csv \
	--out /path/to/mt.940 \
	--account-iban <your revolut account IBAN>
```

## License

MIT
