#!/usr/bin/env python

from __future__ import print_function

import json
import csv
import os
import random
from random import uniform
import time
import sys
import pandas as pd


from confluent_kafka import Consumer, KafkaError, Producer
from confluent_kafka.admin import AdminClient, NewTopic

KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "fraud")
KAFKA_BROKERS = os.getenv("BOOTSTRAP_SERVERS", "localhost:9092")
SASL_USERNAME = os.getenv("SASL_USERNAME", "Nologin")
SASL_PASSWORD = os.getenv("SASL_PASSWORD", "NoPass")

REPO="https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/04-13-2020.csv"

def make_topic(t, c):
    """ attempts to make a kafka topic """
    a = AdminClient(c)
    topics = [KAFKA_TOPIC]
    fs = a.create_topics([NewTopic(topic, num_partitions=3, replication_factor=3) for topic in topics])
    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            print("Topic {} created".format(topic))
        except Exception as e:
            print("Failed to create topic, it may exist already {}: {}".format(topic, e))

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

def get_data():
    """ returns json array of data from csv source """
    try:
        df = pd.read_csv(REPO, header=0)
    except Exception as e:
        print("Something didn't work parsing csv file {}".format(e))
    return json.loads(df.to_json(orient="records"))

def main():

    conf = {
      'bootstrap.servers': KAFKA_BROKERS,
      'api.version.request': True,
      'broker.version.fallback': '0.10.0.0',
      'api.version.fallback.ms': 0,
      'sasl.mechanisms': 'PLAIN',
      'security.protocol': 'SASL_SSL',
      'sasl.username': SASL_USERNAME,
      'sasl.password': SASL_PASSWORD,
      'group.id': 'covid19',
      'default.topic.config': {'auto.offset.reset': 'smallest'}
    }
    producer = Producer(**conf)
    print("connected to {} topic {}".format(KAFKA_BROKERS, KAFKA_TOPIC))
    make_topic(KAFKA_TOPIC, conf)

    while True:
        producer.poll(0)

        for i in get_data():
            try:
                producer.produce(KAFKA_TOPIC, json.dumps(i).rstrip().encode('utf8'), callback=delivery_report)
            except Exception as ex:
                print("unable to produce {}".format(ex))
            print(i)
            producer.flush()

        time.sleep(1000)

if __name__== "__main__":
  main()
