from __future__ import absolute_import, division, print_function, unicode_literals

import json
import requests
from requests.compat import urljoin
from requests.exceptions import RequestException
try:
    from exceptions import ConnectionError
except ImportError:
    class ConnectionError(OSError):
        pass

import logging
logger = logging.getLogger(__name__)


# API details
DEANSLIST_BASE_URL = 'https://{}.deanslistsoftware.com'


BETA = 'B'
BETA_BANK = 'BB'
V1 = 'V1'

API_VERSIONS = {
    BETA: 'api/beta/export/{}.php',
    BETA_BANK: 'api/beta/bank/{}.php',
    V1: 'api/v1/{}'
}

RESOURCE = 'R'
COLLECTION = 'C'

ENDPOINTS = {
    'behavior': (BETA, 'get-behavior-data', COLLECTION, {'sdt': 'Start Date (YYYY-MM-DD)', 'edt': 'End Date (YYYY-MM-DD)'}),
    'homework': (BETA, 'get-homework-data', COLLECTION, {'sdt': 'Start Date (YYYY-MM-DD)', 'edt': 'End Date (YYYY-MM-DD)'}),
    'points': (BETA_BANK, 'get-bank-book', COLLECTION, {'rid': 'Roster ID', 'sid': 'Student ID', 'stus': 'Array of Student IDs'}),
    'communications': (BETA, 'get-comm-data', COLLECTION, {}),
    'users': (BETA, 'get-users', COLLECTION, {'show_inactive': 'Include inactive users (Y/N)'}),
    'students': (V1, 'students', COLLECTION, {'StudentID': 'Array of Student IDs', 'IncludeParents': 'Include parent contact data (Y/N)', 'IncludeUnenrolled': 'Include unenrolled students (Y/N)'}),
    'roster_assignments': (BETA, 'get-roster-assignments', COLLECTION, {'rt': 'Roster type identifier (ALL/CL/HR/ADV)'}),
    'referrals': (V1, 'referrals', COLLECTION, {'sdt': 'Start Date (YYYY-MM-DD)', 'edt': 'End Date (YYYY-MM-DD)', 'sid': 'Student ID'}),
    'suspensions': (V1, 'suspensions', COLLECTION, {'cf': 'Include custom fields (Y/N)'}),
    'incidents': (V1, 'incidents', COLLECTION, {'cf': 'Include custom fields (Y/N)'}),
    'followups': (V1, 'followups', COLLECTION, {'iuid': 'Initiated by User ID', 'cuid': 'Created by User ID', 'sid': 'Student ID', 'out': 'Outstanding (Y/N)', 'type': 'Type (REF/COMM/SUSP)'}),
    'lists': (V1, 'lists', COLLECTION, {}),
    'list': (V1, 'lists', RESOURCE, {}),
    'terms': (V1, 'terms', COLLECTION, {}),
    'daily_attendance': (V1, 'daily-attendance', COLLECTION, {'sdt': 'Start Date (YYYY-MM-DD)', 'edt': 'End Date (YYYY-MM-DD)'}),
    'class_attendance': (V1, 'class-attendance', COLLECTION, {'sdt': 'Start Date (YYYY-MM-DD)', 'edt': 'End Date (YYYY-MM-DD)'}),
    'rosters': (V1, 'rosters', COLLECTION, {'show_inactive': 'Include inactive rosters (Y/N)'}),
    'roster': (V1, 'rosters', RESOURCE, {}),
    'coaching_observations': (V1, 'coaching/observation', COLLECTION, {}),
    'coaching_observation': (V1, 'coaching/observation', RESOURCE, {}),
    'all_coaching_evidence': (V1, 'coaching/evidence', COLLECTION, {}),
    'coaching_evidence': (V1, 'coaching/evidence', RESOURCE, {}),
}


class DeansList(object):

    def __init__(self, subdomain, api_key, user_agent=None):
        self.base_url = DEANSLIST_BASE_URL.format(subdomain)
        self.session = self._establish_session(api_key, user_agent=user_agent)

        users = self.get_users()
        self.school_name = users[0]['SchoolName']
        self.school_id = users[0]['DLSchoolID']
        logger.debug('DeansList client initialized for %s!', self.school_name)

    def _establish_session(self, api_key, user_agent):

        headers = {}
        if user_agent:
            headers['User-Agent'] = user_agent
        headers['Accept'] = 'application/json'

        params = {}
        params['apikey'] = api_key

        s = requests.Session()
        s.params = params
        s.headers.update(headers)
        return s

    def _get(self, relative_url, **kwargs):

        url = urljoin(self.base_url, relative_url)

        logger.debug('Hitting url: %s with params: %s', url, kwargs)

        try:
            response = self.session.get(url, params=kwargs)
        except requests.ConnectionError:
            raise ConnectionError('Unable to connect to %s - are you sure the subdomain is correct?' % self.base_url)

        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            if response.status_code == 401:
                raise ConnectionError('Unable to authenticate - are you sure the API key is correct?')
            elif response.status_code == 404:
                raise ConnectionError('No such resource %s - are you sure the endpoints were configured correctly?' % relative_url)
            else:
                raise(e)

        try:
            response_json = response.json()
        except ValueError:
            logger.exception('Response was not valid JSON!')
            return None

        if 'rowcount' in response_json and 'data' in response_json:
            rows = response_json['rowcount']
            data = response_json['data']
            assert len(data) == rows
        else:
            data = response_json

        return data

    def _handle_endpoint(self, endpoint, *args, **kwargs):
        api_version, endpoint, endpoint_type, parameters = ENDPOINTS[endpoint]
        relative_url = API_VERSIONS[api_version].format(endpoint)
        if endpoint_type == RESOURCE:
            if len(args) == 1:
                relative_url += '/{}'.format(*args)
            else:
                raise ValueError('The %s endpoint returns a single resource and requires a single ID as an argument.' % endpoint)

        for kwarg in kwargs:
            if kwarg not in parameters:
                raise ValueError('Unknown parameter %s for endpoint %s.  Valid parameters are: %s' % (kwarg, endpoint, parameters))

        return self._get(relative_url, **kwargs)

    def __getattr__(self, name):
        if name.startswith('get_'):
            target = name.partition('_')[-1]
            if target in ENDPOINTS:
                return lambda *args, **kwargs: self._handle_endpoint(target, *args, **kwargs)
            else:
                raise AttributeError('DeansList has no "%s" API endpoint.' % target)
        else:
            return self.__getattribute__(name)

    def __dir__(self):
        base = super(DeansList, self).__dir__()
        for endpoint in ENDPOINTS:
            base.append('get_%s' % endpoint)
        return base
