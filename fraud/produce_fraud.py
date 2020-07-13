#!/usr/bin/env python

from __future__ import print_function

import json
import os
import random
from random import uniform
import time
import sys
import eventador as ev

from card_generator import generate_card
from geopoint import create_geopoint

CITIES = [
    {"lat": 30.2672, "lon": -97.7430608, "city": "austin"},
    {"lat": 34.0522, "lon": -118.2437, "city": "los angeles"},
    {"lat": 39.7392, "lon": -104.9903, "city": "denver"},
    {"lat": 32.7767, "lon": -96.7970, "city": "dallas"}
]

def get_latlon():
    geo = random.choice(CITIES)
    return create_geopoint(geo['lat'], geo['lon'])

def purchase():
    """Return a random amount in cents """
    return random.randrange(1000, 90000)

def get_user():
    """ return a random user """
    return random.randrange(0, 999)

def make_fraud(seed, card, user, latlon):
    """ return a fraudulent transaction """
    amount = (seed+1)*1000
    payload = {"userid": user,
               "amount": amount,
	           "lat": latlon[0],
	           "lon": latlon[1],
               "card": card
              }
    return payload

def fraud_loop(session):

    payload = {}
    fraud_trigger = 15
    i = 1

    while True:

        if i % fraud_trigger == 0:
            # fraud
            print("fraud..")
            card = generate_card("visa16")
            user = get_user()
            latlon = get_latlon()
            for r in range(3):
                payload = make_fraud(r, card, user, latlon)
                try:
                    ev.produce(session, payload)
                except Exception as ex:
                    print("unable to produce {}".format(ex))
        else:
            # not fraud
            latlon = get_latlon()
            payload = {
                "userid": get_user(),
                "amount": purchase(),
    	        "lat": latlon[0],
		        "lon": latlon[1],
                "card": generate_card("visa16")
            }

        try:
            ev.produce(session, payload)
            i += 1
        except Exception as ex:
            print("unable to produce {}".format(ex))



if __name__== "__main__":
    try:
        session  = ev.create_session()
        response = ev.create_topic(session)
        fraud_loop(session)
    except Exception as e:
        print(e)
