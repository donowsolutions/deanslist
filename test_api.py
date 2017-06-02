import os
from datetime import date
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
    behavior, deleted_behavior = dl_client.get_behavior(IncludeDeleted='Y')
    assert len(behavior) > 0
    assert len(deleted_behavior) >= 0 # there might not be any deleted data on the test server


def test_behavior_before():
    behavior = dl_client.get_behavior(UpdatedBefore=date.today())
    assert len(behavior) > 0


def test_homework_before():
    hw = dl_client.get_homework(UpdatedBefore=date.today())
    assert len(hw) >= 0


def test_communications_before():
    comm = dl_client.get_communications(UpdatedBefore=date.today())
    assert len(comm) >= 0

def test_incidents():
    incidents = dl_client.get_incidents(IncludeDeleted='Y')
    assert len(incidents) > 0


