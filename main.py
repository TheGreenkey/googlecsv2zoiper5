import csv
from pypika import Query, Table
import phonenumbers
import re
import argparse
import sys

whitespace_pattern = re.compile(r'\s+')
contact_tbl = Table('Contact')
name_tbl = Table('Name')
phone_tbl = Table('Phone')


def output(output_file, queries):
    with open(output_file, mode='w') as fd:
        for contact in queries:
            for stmt in contact:
                fd.write(stmt + ';\n')
            fd.write('\n')


def read_csv(input_file, account_id, current_contact_id, current_name_id, current_phone_id):
    queries = []

    with open(input_file, mode='r') as fd:
        reader = csv.DictReader(fd)

        for row in reader:
            # skip entries which don't have any names
            if not row['Given Name'].strip() \
                and not row['Additional Name'].strip() \
                    and not row['Family Name'].strip():
                continue

            # skip entries which don't have a phone number
            if not row['Phone 1 - Value'].strip():
                continue

            contact = []

            number = re.sub(whitespace_pattern, '', row['Phone 1 - Value'])
            number = phonenumbers.parse(number, 'DE')
            number = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)

            current_name_id = current_name_id + 1
            current_contact_id = current_contact_id + 1
            current_phone_id = current_phone_id + 1

            contact.append(Query.into(contact_tbl).insert(None).get_sql())
            contact.append(Query
                           .into(name_tbl)
                           .columns('ID', 'Contact', 'First', 'Middle', 'Last')
                           .insert(current_name_id, current_contact_id, row['Given Name'] or None, row['Additional Name'] or None, row['Family Name'] or None)
                           .get_sql())
            contact.append(Query
                           .into(phone_tbl)
                           .columns('ID', 'Contact', 'Type', 'Phone', 'Normal', 'AccountMappingType', 'Account', 'Presence', 'CustomType')
                           .insert(current_phone_id, current_contact_id, 8, number, number, 2, account_id, 1, 1)
                           .get_sql())

            queries.append(contact)

    return queries


def parse_command_line():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('input', type=int,
                        help='The input csv file exported from Google Contacts.')
    parser.add_argument('account_id', type=int,
                        help='The account to add all parsed contacts to.')
    parser.add_argument('current_contact_id', type=int,
                        help='The currently largest contact id found in the db table "Contact".')
    parser.add_argument('current_name_id', type=int,
                        help='The currently largest name id found in the db table "Name".')
    parser.add_argument('current_phone_id', type=int,
                        help='The currently largest phone id found in the db table "Phone".')
    parser.add_argument('--output', type=str, default='statements.sql',
                        help='The output destination for the generated sql statements.')

    try:
        return parser.parse_args()
    except SystemExit as e:
        if e.code == 2:
            parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    args = parse_command_line()

    stmts = read_csv(args.input, args.account_id, args.current_contact_id, args.current_name_id, args.current_phone_id)
    output(args.output, stmts)
