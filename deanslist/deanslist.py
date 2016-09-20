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


API_VERSIONS = {
    'beta': 'api/beta/export/{}.php',
    'beta-bank': 'api/beta/bank/{}.php'
    'v1': 'api/v1/{}'
}

ENDPOINTS = {
    'behavior': ('beta', 'get-behavior-data'),  # sdt,edt
    'homework': ('beta', 'get-homework-data'),  # sdt,edt
    'points': ('beta-bank', 'get-bank-book'),  # rid (roster id), sid (student id), stus (student id array)
    'communications': ('beta', 'get-comm-data'),
    'users': ('beta', 'get-users'),  # show_inactive = Y/N
    'students': ('beta', 'get-students'),
    'roster_assignments': ('beta', 'get-roster-assignments'),  # rt = ALL/CL/HR/ADV
    'referrals': ('v1', 'referrals'),  # sdt, edt, sid
    'suspensions': ('v1', 'suspensions'),  # cf  (custom fields) = Y/N
    'incidents': ('v1', 'incidents'),  # cf  (custom fields) = Y/N
    'followups': ('v1', 'followups'),
    'lists': ('v1', 'lists'),  # can get single
    'terms': ('v1', 'terms'),
    'daily_attendance': ('v1', 'daily-attendance'),  # sdt,edt
    'class_attendance': ('v1', 'class-attendance'),  # sdt,edt
    'rosters': ('v1', 'rosters'),   # can get single
    'coaching_observations': ('v1', 'coaching/observation'),  # can get single
    'coaching_evidence': ('v1', 'coaching/evidence'),  # can get single
}


class DeansList(object):
    """
    """
    def __init__(self, subdomain, api_key, user_agent=None):
        self.base_url = DEANSLIST_BASE_URL.format(subdomain)
        self.session = self._establish_session(api_key, user_agent=user_agent)

        users = self.get_users()
        self.school_name = users[0]['SchoolName']
        self.school_id = users[0]['DLSchoolID']
        logger.debug('DeansList client initialized for %s!', self.school_name)

    def _establish_session(self, api_key, user_agent):
        """
        """

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

    def _get(self, relative_url, *args, **kwargs):
        """
        """
        for arg in args:
            relative_url += '/{}'.format(arg)

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

        if args:
            data = response_json
        else:
            rows = response_json['rowcount']
            data = response_json['data']
            assert len(data) == rows

        return data

    def __getattr__(self, name):
        if name.startswith('get_'):
            target = name.partition('_')[-1]
            if target in ENDPOINTS:
                api_version, endpoint = ENDPOINTS[target]
                relative_url = API_VERSIONS[api_version].format(endpoint)
                return lambda *args, **kwargs: self._get(relative_url, *args, **kwargs)
            else:
                raise AttributeError('DeansList has no "%s" API endpoint.' % target)
        else:
            return self.__getattribute__(name)

    def __dir__(self):
        base = super(DeansList, self).__dir__()
        for endpoint in ENDPOINTS:
            base.append('get_%s' % endpoint)
        return base
