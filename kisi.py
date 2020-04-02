#!/usr/bin/env python
import logging
import argparse
import getpass

from api import KisiApi
import boto3

def main():

    ssm = boto3.client('ssm', region_name='us-east-1')

    parameter1 = ssm.get_parameter(Name='kisiApiUser', WithDecryption=True)
    parameter2 = ssm.get_parameter(Name='kisiAPIPassword', WithDecryption=True)
    kisiApiUser = parameter1['Parameter']['Value']
    kisiPassword = parameter2['Parameter']['Value']

    parser = argparse.ArgumentParser(description='Command line interface to interact with Kisi')
    parser.add_argument('-v',
                        '--verbose',
                        action='store_true',
                        help='verbose logging')
    parser.add_argument('-printUser',
                        '--printUser',
                        dest='printUser',
                        action='store_true',
                        help='')
    parser.add_argument('-getPlaces',
                        '--places',
                        dest='places',
                        action='store_true',
                        help='Will print out the places in Greenhouse and the member count E.G (kisi.py -getPlaces)'
                        )
    parser.add_argument('-createUser',
                        '--createUser',
                        dest='createUser',
                        action='store_true',
                        help='Creates a user in New York and added to to the General Staff Group E.G ( kisi.py -createUser -name user@greenhouse.io)'
                        )
    parser.add_argument('-deleteUser',
                        '--deleteUser',
                        dest='deleteUser',
                        action='store_true',
                        help='Deletes a user in all of Kisi instance.It will also disable and de-assign the card for the user. E.G(kisi.py -deleteUser -name user@greenouse.io)'
                        )
    parser.add_argument('-bulkAddUsers',
                        '-bulkAddUsers',
                         dest='bulkAddUsers',
                         action='store_true',
                        help='Bulk adds users via csv to New York and adds them to General Staff group E.G(kisi.py -bulkAddUsers -csv test.csv'
                        )
    parser.add_argument('-name',
                        '--name',
                        required=False
                        )
    parser.add_argument('-csv,',
                       '--csv',
                       required=False
                      )
    args = parser.parse_args()

    api = KisiApi(kisiApiUser, kisiPassword)

    if args.printUser:
        api.getUserInstancesById(args.name)
    if args.places:
        api.getAllPlaces()
    if args.createUser:
        api.provisionUser(args.name,'NY','nygen')
    if args.deleteUser:
        api.deleteUser(args.name)
    if args.bulkAddUsers:
        api.bulkAddUsers(args.csv)

if __name__ == "__main__":
    main()
