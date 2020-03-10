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
echo "KAFKA_TOPIC=paymentauths" >> fraud.env
```

### Populate Kafka with data
```
docker build . -t fraud
docker run -d --env-file fraud.env fraud
```

### Setup Eventador
Follow the steps from the Eventador Getting Started Guide.

- Create a [new environment](https://docs.eventador.io/sqlstreambuilder/ssb_getting_started/#1-create-a-cloud-environment). Name it `payment_auths`
- Create a [datasource](https://docs.eventador.io/sqlstreambuilder/ssb_getting_started/#2-create-a-data-source). Name it `payment_auths`. Connect it to the Kafka cluster you configured above.
- Create a new [virtual table source](https://docs.eventador.io/sqlstreambuilder/ssb_getting_started/#3-create-virtual-table-as-a-source), use this JSON schema definition:

```json
{
  "name": "paymentauths",
  "type": "record",
  "namespace": "com.eventador.payments",
  "fields": [
    {
      "name": "amount",
      "type": "int"
    },
    {
      "name": "userid",
      "type": "int"
    },
    {
      "name": "card",
      "type": "string"
    }
  ]
}
```

## Run Continuous Queries

Follow [these steps](https://docs.eventador.io/sqlstreambuilder/ssb_getting_started/#5-running-sql) to run Continuous SQL on Eventador.

Create a job with the following SQL, and select `results in browser` as the virtual table sink. Select `Execute`.

```SQL
--production fraud job, identify cards that have move than 2 auths in a 10 minute window
select card,
count(*) as thecount,
max(amount) as max_amount,
tumble_end(eventTimestamp, interval '20' second) as ts_end
from paymentauths
group by card, tumble(eventTimestamp, interval '20' second)
having count(*) > 2;
```

Because the continuous SQL query aggregates and maintains state over a 20 second period, the query will not return results until the window is complete. When it does, the fraudulent activity is shown as the results arrive. It should look something like this:

![img](img/ssb_snap.png)


## Taking it further

### Input transforms

You can utilize an input transform to read Kafka header information. You will need to add two pieces of information to the above example:

1. Input Transform.

In the `source virtual table` configuration, select `Transformations`, and paste the following code into the editor box:
```javascript
var out = JSON.parse(record);
var header = JSON.parse(message.headers);
var interested_keys = ['DC'];
out['topic'] = message.topic;
out['partition'] = message.partition;


Object.keys(header).forEach(function(key) {
    if (interested_keys.indexOf(key) > -1){
        out[key] = header[key];
    }
});

JSON.stringify(out);
```

2. Edit the schema to have new fields to hold the data - select the `Schema` tab and **Add** the following to your schema definition in the editor box:

```JSON
    {
      "name": "topic",
      "type": "string"
    },
    {
      "name": "partition",
      "type": "string"
    },
    {
      "name": "DC",
      "type": "string"
    }
```

Restart the job, you will now get Kafka header information in the results.
