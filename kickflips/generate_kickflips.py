#!/usr/bin/env python
from __future__ import print_function

import json
import os
import random
import time
import sys
import uuid
import gpxpy.gpx
from confluent_kafka import Consumer, KafkaError, Producer
from confluent_kafka.admin import AdminClient, NewTopic

KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "kickflipstest")
KAFKA_BROKERS = os.getenv("BOOTSTRAP_SERVERS", "localhost:9092")
SASL_USERNAME = os.getenv("SASL_USERNAME", "")
SASL_PASSWORD = os.getenv("SASL_PASSWORD", "")
BOARDID=os.getenv("BOARDID","09")
PROCESSING_DIR = "tracks/"+BOARDID+"/"

def main():
    try:
        conf = {
          'bootstrap.servers': KAFKA_BROKERS,
          'api.version.request': True,
          'broker.version.fallback': '0.10.0.0',
          'api.version.fallback.ms': 0,
          'sasl.mechanisms': 'PLAIN',
          'security.protocol': 'SASL_SSL',
          'sasl.username': SASL_USERNAME,
          'sasl.password': SASL_PASSWORD,
          'group.id': 'kickflip_group',
          'default.topic.config': {'auto.offset.reset': 'smallest'}
        }
        producer = Producer(**conf)
        print("connected to {} topic {}".format(KAFKA_BROKERS, KAFKA_TOPIC))

        make_topic(KAFKA_TOPIC, conf)

    except:
        print("ERROR: unable to create a producer to {}".format(KAFKA_BROKERS))
        sys.exit(1)

    for file in os.listdir(PROCESSING_DIR):
        if file.endswith(".gpx"):
            gpx_file = open(PROCESSING_DIR+file, 'r')
            gpx = gpxpy.parse(gpx_file)
            userid = generate_userid()
            batt_pct = 100
            temperature = 82
            tripid = str(uuid.uuid4())
            speed = (100 * 1000) / 3600
            previous_point = None
            trip_distance = 0
            trip_start_time = time.time()

            for track in gpx.tracks:
                for segment in track.segments:
                    for i, point in enumerate(segment.points):
                        if previous_point is not None:
                            time.sleep(3)   # speed constant
                            batt_pct = generate_battery_usage(batt_pct)
                            temperature = generate_temperature(temperature)
                            distance = point.distance_2d(previous_point)
                            trip_distance = trip_distance + distance
                            trip_duration = time.time()-trip_start_time
                            duration = distance / speed

                            payload = {"userid":userid,
                                       "boardid": BOARDID,
                                       "tripid": tripid,
                                       "battery_level": batt_pct,
                                       "temperature": temperature,
                                       "trip_distance": trip_distance,
                                       "trip_start_time": trip_start_time,
                                       "trip_duration": trip_duration,
                                       "location": {"latitude":point.latitude, "longitude": point.longitude }
                                       }

                            try:
                                producer.produce(KAFKA_TOPIC,
                                        json.dumps(payload).rstrip().encode('utf8'),
                                        key=BOARDID,
                                        callback=delivery_report)
                                producer.flush()
                            except Exception as ex:
                                print("unable to produce {}".format(ex))
                        previous_point = point
                    producer.flush()



def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

def generate_userid():
    return random.randrange(100, 120)

def generate_battery_usage(pct):
    return round(pct-.012, 3)

def generate_temperature(t):
    return round(t+.03, 3)

def make_topic(t, c):
    a = AdminClient(c)
    topics = [KAFKA_TOPIC]
    fs = a.create_topics([NewTopic(topic, num_partitions=3, replication_factor=3) for topic in topics])
    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            print("Topic {} created".format(topic))
        except Exception as e:
            print("Failed to create topic {}: {}".format(topic, e))

if __name__== "__main__":
  main()
