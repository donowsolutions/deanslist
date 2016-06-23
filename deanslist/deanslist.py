from __future__ import absolute_import, division, print_function, unicode_literals

import json
import requests
from requests.compat import urljoin
from requests.exceptions import RequestException

import logging
logger = logging.getLogger(__name__)


# API details
DEANSLIST_BASE_URL = 'https://{}.deanslistsoftware.com'

API_VERSION_BETA = 'api/beta/export'
API_VERSION_V1 = 'api/v1'


ENDPOINTS = {
    'behavior': '/api/beta/export/get-behavior-data.php',  # sdt,edt
    'homework': '/api/beta/export/get-homework-data.php',  # sdt,edt
    'points': '/api/beta/bank/get-bank-book.php',  #rid (roster id), sid (student id), stus (student id array)
    'communications': '/api/beta/export/get-comm-data.php',
    'users': '/api/beta/export/get-users.php',  # show_inactive = Y/N
    'students': '/api/beta/export/get-students.php',
    'rosters': '/api/beta/export/get-roster-assignments.php',  # rt = ALL/CL/HR/ADV
    'referrals': '/api/v1/referrals',  # sdt, edt, sid
    'suspensions': 'api/v1/suspensions',  # cf  (custom fields) = Y/N
    'incidents': '/api/v1/incidents',  # cf  (custom fields) = Y/N
    'followups': '/api/v1/followups',
    'lists': '/api/v1/lists',  # can get single
    'terms': '/api/v1/terms',
    'daily_attendance': '/api/v1/daily-attendance',  # sdt,edt
    'class_attendance': '/api/v1/class-attendance',  # sdt,edt
    'rosters': '/api/v1/rosters',   # can get single
    'coaching_observations': '/api/v1/coaching/observation',  # can get single
    'coaching_evidence': '/api/v1/coaching/evidence', # can get single
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
            logger.debug('%d rows returned', rows)

        logger.debug(response_json)
        return data


    def __getattr__(self, name):
        if name.startswith('get_'):
            target = name.partition('_')[-1]
            if target in ENDPOINTS:
                def wrapper(*args, **kwargs):
                    return self._get(ENDPOINTS[target], *args, **kwargs)
                return wrapper
            else:
                raise AttributeError('DeansList has no "%s" API endpoint.' % target)
        else:
            return self.__getattribute__(name)

    def __dir__(self):
        base = super(DeansList, self).__dir__()
        for endpoint in ENDPOINTS:
            base.append('get_%s' % endpoint)
        return base

