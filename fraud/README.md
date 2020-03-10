# Fraud
A hypothetical payment authorization flow to demonstrate the Eventador Platform and the use of Continuous SQL to process streaming data.

The demo consists of:

- A generator to create hypothetical data
- SQL examples for processing the stream
- Configuration parameters for Eventador Platform

You will need:

- A kafka provider or your own cluster. The example uses [CC](https://confluent.cloud/login).
- An [Eventador Account](https://eventador.cloud/register).
- Docker installed and working on your machine. If you are new to Docker or just installing it for the first time, [Docker Desktop](https://www.docker.com/products/docker-desktop) might be the easiest route.

## Setup

Open a terminal window and run the following commands from a convenient directory on your machine:

### Clone this repo
```
git clone git@github.com:Eventador/eventador_examples.git
cd eventador_examples/fraud
```

### Create an environment file
In the same directory create an .env file with your login credentials and some configuration information. This example uses Confluent Cloud, if you are using a different Kafka service or your own then specify credentials that match your specific configuration. Replace the variables surrounded by `[ ]` with your own values, including the brackets.
```
echo "BOOTSTRAP_SERVERS=[yourCCkafkaserver:9092]" >> fraud.env
echo "SASL_USERNAME=[get from confluent cloud]" >> fraud.env
echo "SASL_PASSWORD=[get from confluent cloud]" >> fraud.env
echo "KAFKA_TOPIC=payment_auths" >> fraud.env
```

### Populate Kafka with data
```
docker build . -t fraud
docker run -d --env-file fraud.env fraud
```

### Setup Eventador
Follow the steps from the Eventador Getting Started Guide.

- Create a [new environment](https://docs.eventador.io/sqlstreambuilder/ssb_getting_started/#1-create-a-cloud-environment). Name it `kickflips`
- Create a [datasource](https://docs.eventador.io/sqlstreambuilder/ssb_getting_started/#2-create-a-data-source). Name it `kickflips`. Connect it to any Kafka cluster you want to use for this purpose. The example code assumes CC.
- Create a new [virtual table source](https://docs.eventador.io/sqlstreambuilder/ssb_getting_started/#3-create-virtual-table-as-a-source), use [this JSON schema definition](/kickflips.json).

- Create the following [Virtual Table Sinks](https://docs.eventador.io/sqlstreambuilder/ssb_getting_started/#4-create-virtual-table-as-a-sink):
```
fraud_output
```
