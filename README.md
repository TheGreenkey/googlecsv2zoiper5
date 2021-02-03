# googlecsv2zoiper5

This python script converts an exported Google Contacts CSV (`Google Contacts -> Export -> Export as Google CSV`) to sql
statements ready to insert into the internal contacts db (`ContactsV2.db`) of the VOIP application Zoiper 5
without requiring you to buy a pro license.

It currently only exports the `Phone 1 - Value`-Field with the corresponding names.

## Usage

Because I only wrote it for myself it's quite rudimentary. You need to find out what your current auto increment values
in your db for the following tables are:

- `Contact`
- `Name`
- `Phone`

You also need the account id for which the contacts should be added. You can find it in the `Account`-Table