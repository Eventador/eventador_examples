# kickflip
A hypothetical boosted board mobility service to demonstrate the Eventador Platform and the use of Continuous SQL to process streaming data. Kickflip is a hypothetical company that provides ride-sharing skateboards - this demo shows the streaming data workflows under the covers that make the service possible.

The demo consists of:

- A generator to create hypothetical data
- SQL examples for processing the stream
- Configuration parameters for Eventador Platform

You will need:

- A kafka provider or your own cluster. The example uses [CC](https://confluent.cloud/login).
- An [Eventador Account](https://eventador.cloud/register).
- Docker installed and working on your machine. If you are new to Docker or just installing it for the first time, [Docker Desktop](https://www.docker.com/products/docker-desktop) might be the easiest route.

## Setup

### Clone this repo
```
git clone git@github.com:Eventador/eventador_examples.git
cd eventador_examples/kickflips
```

### Create an environment file
In the same directory create an .env file with your login credentials. Name it kickflips.env with the following variables defined. This example uses CC, if you are using a different service or your own then specify creds that match it.
```
BOOTSTRAP_SERVERS=yourCCkafkaserver:9092
SASL_USERNAME=<get from confluent cloud>
SASL_PASSWORD=<get from confluent cloud>
KAFKA_TOPIC=kickflips
```

### Populate Kafka with data
```
docker build . -t kickflips
docker run -d --env-file kickflip01.env kickflips
docker run -d --env-file kickflip02.env kickflips
```

### Setup Eventador
Follow the steps from the Eventador Getting Started Guide.

- Create a [new environment](https://docs.eventador.io/sqlstreambuilder/ssb_getting_started/#1-create-a-cloud-environment). Name it `kickflips`
- Create a [datasource](https://docs.eventador.io/sqlstreambuilder/ssb_getting_started/#2-create-a-data-source). Name it `kickflips`. Connect it to any Kafka cluster you want to use for this purpose. The example code assumes CC.
- Create a new [virtual table source](https://docs.eventador.io/sqlstreambuilder/ssb_getting_started/#3-create-virtual-table-as-a-source), use [this JSON schema definition](/kickflips.json).

- Create the following [Virtual Table Sinks](https://docs.eventador.io/sqlstreambuilder/ssb_getting_started/#4-create-virtual-table-as-a-sink):
```
kickflips_app
kickflips_dashboard
```

You should be all setup and ready to run continuous SQL queries

## Run Continuous Queries

Follow [these steps](https://docs.eventador.io/sqlstreambuilder/ssb_getting_started/#5-running-sql) to run Continuous SQL on Eventador.

Create two jobs:

#### Job 1 - Mobile App

This is a simple computation that aggregates the data over a sliding 15 minute interval and constantly computing the range of the board based on battery consumption. This is to be displayed in a mobile app so customers can see how far they can travel.

- Name: kickflips_app
- Sink Virtual Table: kickflips_app
- SQL: Copy/paste this SQL into the SQL window.

```sql
-- display range remaining every 15 seconds
SELECT boardid,
tumble_end(eventTimestamp, interval '15' second) as TS,
CAST(ROUND(MIN(CAST(battery_level as numeric)),2) AS varchar)||'%' as state_of_charge,
MIN(CAST(trip_distance AS numeric)) AS distance_covered,
100-MIN(CAST(battery_level as numeric)) AS battery_pct_used,
MIN(CAST(trip_distance AS numeric))/(100-MIN(CAST(battery_level as numeric))) AS foot_per_battery_pct,
MIN(CAST(battery_level as numeric))*(MIN(CAST(trip_distance AS numeric))/(100-MIN(CAST(battery_level as numeric)))) as range_in_feet
FROM kickflips
GROUP by boardid, tumble(eventTimestamp, interval '15' second)
```

Select the execute button. The job will start and data will be continuously queried and saved into the output topic `kickflips_app`.

#### Job 2 - Dashboard

This job aggregates all trips and shows the overall usage of the service to compute ridership in real time.

- Name: kickflips_dashboard
- Sink Virtual Table: kickflips_dashboard
- SQL: Copy/paste the below SQL into the SQL window.

```SQL
-- display average trip distance over a 1 minute period
SELECT
boardid, tumble_end(eventTimestamp, interval '1' minute) as ts,
avg(trip_distance) as distance
FROM kickflips
WHERE boardid IS NOT NULL
GROUP BY boardid, tumble(eventTimestamp, interval '1' minute)
```

Select the execute button. The job will start and data will be continuously queried and saved into the output topic `kickflips_dashboard`.
