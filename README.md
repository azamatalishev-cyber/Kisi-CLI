# kisi-python
Re-engineered version of Jesse Joes script 

https://github.com/jessejoe/kisi-python

**NOTE: Secrets for this script are stored in AWS Parameter Store (boto3).Some functions were made specific to my work environment. Feel free to adjust accordingly to your convenience *

# Requirements
```bash pip install -r requirements.txt```

## `kisi.py`
`kisi.py` is a wrapper for `api.py`, from here you will be able to access functions in api.py via argparse .

### Example
```bash
$usage: kisi.py [-h] [-v] [-printUser] [-getPlaces] [-createUser] [-deleteUser]
               [-bulkAddUsers] [-bulkRemoveUsers] [-getMembers]
               [-getDenverMembers] [-getAllEmails] [-name NAME] [-csv, CSV]
               [-place, PLACE]

Command line interface to interact with Kisi

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         verbose logging
  -printUser, --printUser
  -getPlaces, --places  Will print out the places in Greenhouse and the member
                        count E.G (kisi.py -getPlaces)
  -createUser, --createUser
                        Creates a user in New York and added to to the General
                        Staff Group E.G ( kisi.py -createUser -name
                        user@greenhouse.io)
  -deleteUser, --deleteUser
                        Deletes a user in all of Kisi instance.It will also
                        disable and de-assign the card for the user.
                        E.G(kisi.py -deleteUser -name user@greenouse.io)
  -bulkAddUsers, -bulkAddUsers
                        Bulk adds users via csv to New York and adds them to
                        General Staff group E.G(kisi.py -bulkAddUsers -csv
                        test.csv
  -bulkRemoveUsers, -bulkRemoveUsers
                        Bulk removes users via csv E.G(kisi.py
                        -bulkRemoveUsers -csv test.csv
  -getMembers, -getMembers
                        Gets users for a place csv E.G(kisi.py -getMembers
                        -place DEN)
  -getDenverMembers, -getDenverMembers
                        Gets emails for everyone in Denver
  -getAllEmails, -getAllEmails
                        Gets emails for everyone and store CSV on desktop
  -name NAME, --name NAME
  -csv, CSV, --csv CSV
  -place, PLACE, --place PLACE}
```

## `api.py`
`api.py` can be imported and used from outside scripts, for example:
```python
In [1]: from api import KisiApi

In [2]: api = KisiApi('foo@bar.com', 'PASSWORD')

In  [3]: api.getAllEmails()
Out [3]: {u'JSON OUTPUT'}
```

