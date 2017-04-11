import os
import pytest
from deanslist import DeansList

API_KEY = os.environ['DEANSLIST_API_KEY']
SUBDOMAIN = os.environ['DEANSLIST_SUBDOMAIN']

dl_client = DeansList(SUBDOMAIN, API_KEY)


def test_connection():
    assert dl_client.school_id == "9"


def test_rosters():
    rosters = dl_client.get_rosters()
    assert len(rosters) > 0


def test_behavior():
    behavior, deleted_behavior = dl_client.get_behavior(IncludeDeleted = 'Y')
    assert len(behavior) > 0
    assert len(deleted_behavior) > 0




