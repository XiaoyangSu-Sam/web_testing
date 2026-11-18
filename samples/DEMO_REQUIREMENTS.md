# Sample README

## Async report

The report page has a ready heading and a Run report button. Each submission accepts a new job with a unique ID. A successful job publishes the three fixture rows for that same ID. A documented failed job displays failure and preserves the earlier result. The fixture can inject stalled jobs, mismatched IDs or incorrect row counts to demonstrate diagnostic reporting.

## Synthetic CSV

The input generator creates sequential IDs and cycles through amounts -1.25, 0.00 and 3.75. It supplies exact byte count, row count and decimal total. The local readback example starts with four rows and then reads increasing sizes, verifying count, ID order and exact total at each step.
