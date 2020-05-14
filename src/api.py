import logging
import requests
from pprint import pprint
import json
import pandas

try:
    # python2
    from urlparse import urljoin
except ImportError:
    # python3
    from urllib.parse import urljoin


class KisiApi:
    """ TWO DICTIONARIES TO USE WITH FUNCTIONS """
    places = {}
    groups = {}

    def __init__(self, email, password):
        self.session = requests.Session()
        self.base_url = 'https://api.kisi.io'
        self.auth_token = ''
        self.login(email, password)

    def __del__(self):
        if not self.auth_token:
            logging.debug('Logging out')

    """AUTHENTICATION FUNCTIONS"""

    def login(self, email, password):
        """
        Login to API

        :return: Authentication token from KISI API
        """
        auth_json = {'user': {'email': email, 'password': password}}
        resp = self.send_api('POST', 'users/sign_in', json=auth_json)
        self.auth_token = resp.json()['authentication_token']
        logging.debug('Got authentication token {}'.format(self.auth_token))
        return self.auth_token

    def logout(self):
        """
        Logout of session

        KISI API returns 204 empty response on success
        """
        resp = self.send_api('DELETE', 'users/sign_out')
        resp.raise_for_status()
        self.auth_token = ''

    def send_api(self, method, endpoint, **kwargs):
        """ Send call to API

        :param method: HTTP method ('GET', 'POST', etc.)
        :param endpoint: API endpoint to join to the base url
        :kwargs: keyword arguments that will be added to API request, e.g.
        json={'key', 'value}
        """
        url = urljoin(self.base_url, endpoint)
        req = requests.Request(method,
                               url,
                               headers=self.get_headers(),
                               **kwargs)
        logging.debug('Sending {} request to {}'.format(req.method, req.url))
        prepped = req.prepare()
        resp = self.session.send(prepped)
        resp.raise_for_status()
        return resp

    def get_headers(self):
        return {
            'Accept': 'application/json',
            'X-Authentication-Token': self.auth_token
        }

    def exportJsonList(self, data):

        with open('data.json', 'w') as f:
            json.dump(data, f, indent=4, sort_keys=True)

    """"FUNCTIONS FOR PLACES AND CARDS"""

    def printCardToken(self, id):
        user = self.send_api('GET', 'members/{}'.format(id)).json()
        cardToken = user['card']['token']
        userName = user['name']
        pprint('Card Token for {} is {}'.format(userName, cardToken))

    """De-assigns and Disables card from user"""

    def deassignCard(self, user_id):
        try:
            self.send_api('POST', '/members/{}/deassign_card'.format(user_id))
            print("Successfully de-assigned card")
        except requests.exceptions.HTTPError:
            print('Card does not exist or is already de-assigned')

    def disableCard(self, user_id):
        try:
            self.send_api('POST', '/members/{}/disable_card'.format(user_id))
            print("Successfully disabled card")
        except requests.exceptions.HTTPError:
            print('Card does not exist or is already disabled')

    """FUNCTIONS FOR USERS
    This function will get all the ID's a user has
    IF A USER IS IN MULTIPLE PLACES, THEY WILL HAVE A DIFFERENT ID FOR EACH PLACE
    It will get all the Kisi members in Kisi
    We use a list comprehension here to create a list with the ID's a user might have
    Lastly, this function will return a list of ids for that user."""

    def getUserInstancesById(self, name):
        allUsers = self.getAllMembers()
        userIds = [(i['id']) for i in allUsers if name.lower() in i['name'].lower()]
        return userIds

    def getUserIds(self, name):
        allUsers = self.getAllMembers()
        userIds = [(i['id'], i['place']['name']) for i in allUsers if name.lower() in i['name'].lower()]
        return userIds

    def getUserInstances(self, name):
        allUsers = self.getAllMembers()
        user = [i for i in allUsers if name.lower() in i['name'].lower()]
        if user == []:
            print('There are no users by that name')
        else:
            return user

    def deleteUser(self, name):
        ids = self.getUserInstancesById(name)
        count = len(ids)
        print("There are {} occurrences of {} in Greenhouse Kisi".format(count, name))
        for i in ids:
            self.disableCard(i)
            self.deassignCard(i)
            self.send_api('DELETE', '/members/{}'.format(i))
            print('Successfully deleted {}'.format(name))

    def printUser(self, userId):
        resp = self.send_api('GET', '/members/{}'.format(userId))
        user = resp.json()
        pprint(user)

    def provisionUser(self, email, place, group):
        placeID = self.getPlaceId(place)
        groupID = self.getGroupId(group)
        user_to_create = {
            "member": {"card_enabled": True, "link_enabled": False, "login_enabled": False, "name": email, "image": "",
                       "backup_card_enabled": True, "place_id": placeID, "role_id": "basic", "email": email}}
        resp = self.send_api('POST', '/members', json=user_to_create)
        self.createShare(groupID, placeID, email)
        pprint(resp.json())

    """GETTER FUNCTIONS"""

    def getAllMembers(self):
        offset = 0
        limit = 100
        allUsers = []
        users = self.send_api('GET', '/members?limit={}&offset={}'.format(limit, offset)).json()
        allUsers.extend(users)
        while len(users) >= limit:
            offset = offset + limit
            resp = self.send_api('GET', '/members?limit={}&offset={}'.format(limit, offset))
            users = resp.json()
            allUsers.extend(users)
        print('There are {} users in Greenhouse Kisi'.format(len(allUsers)))
        return allUsers

    def getMembers(self, place):
        offset = 0
        limit = 50
        allUsers = []
        placeID = self.getPlaceId(place)
        users = self.send_api('GET', '/members?place_id={}&limit={}&offset={}'.format(placeID, limit, offset)).json()
        allUsers.extend(users)
        while len(users) >= limit:
            offset = offset + limit
            resp = self.send_api('GET', '/members?place_id={}&limit={}&offset={}'.format(placeID, limit, offset))
            users = resp.json()
            allUsers.extend(users)
        print('There are {} users in {}'.format(len(allUsers), place))
        return allUsers

    def getAllPlaces(self):
        places = self.send_api('GET', '/places').json()
        all_places = [(i['name'], i['members_count']) for i in places]
        print(all_places)

    def getPlaceId(self, city):
        return self.places[city]

    def getGroupId(self, group):
        return self.groups[group]

    """ ADHOC FUNCTIONS TO SOLVE PROBLEMS. FUR THE LULZ"""

    def getDenverUsersWithAppAccess(self):
        users = self.getMembers('DEN')
        # user_ids = [(i['name'],i['id']) for i in users if not i['login_enabled']]
        user_ids = [i for i in users if i['login_enabled']]
        print('{} users in Denver have app access'.format(len(user_ids)))

    def disableAppAccess(self, list):
        self.exportJsonList(list)
        data = {"login_enabled": False}
        for i in list:
            self.send_api('PATCH', '/members/{}'.format(i['id']), json=data)
            print(i['id'])
            print('Disabled App access for {}'.format(i['name']))

    def appAccessEnabledOTPRequiredDenver(self):
        users = self.getMembers('DEN')
        user_ids = [i['id'] for i in users if i['login_enabled'] and not i['user']['otp_required_for_login']]
        pprint('There are {} users with App access on and 2FA not enabled '.format(len(user_ids)))

    """Shares Access to a group E.G "General Staff Access"""

    def createShare(self, group_id, place_id, email):

        data = {"share": {
            "card_enabled": True, "link_enabled": False, "login_enabled": False, "apply_to_place": False,
            "valid_from": "", "valid_until": "", "notify": False,
            "role": "basic", "email": email, "group_id": group_id, "place_id": place_id}}

        resp = self.send_api('POST', '/shares', json=data)
        pprint(resp.json())

    def bulkAddUsers(self, file):
        emails = self.convertCSVtoList(file)
        for email in emails:
            self.provisionUser(email, 'NY', 'nygen')
        print('Done Creating users')

    def convertCSVtoList(self, file):
        reader = pandas.read_csv(file)
        emails = [i for i in reader['Email']]
        return emails
