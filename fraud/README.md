# Fraud
A hypothetical payment authorization flow to demonstrate the Eventador Platform and the use of Continuous SQL to process streaming data.

Authorizations are streamed through Kafka, then they are continuously processed via SQL to find authorizations that are climbing in value over a short time window (our hypothetical fraud). The results are read via REST into a single page javascript application and a heatmap of fraud is generated.

The demo consists of:

- A generator to create hypothetical data
- SQL examples for processing the stream
- Configuration parameters for Eventador Platform
- A simple application to display the data

You will need:

- An [Eventador Account](https://eventador.cloud/register).
- Docker installed and working on your machine. If you are new to Docker or just installing it for the first time, [Docker Desktop](https://www.docker.com/products/docker-desktop) might be the easiest route.

## Setup

### Setup Eventador
Follow these steps from the Eventador Getting Started Guide.

- Create a [new environment](https://docs.eventador.io/sqlstreambuilder/ssb_getting_started/#1-create-a-cloud-environment). Name it `payment_auths`
- Create a new [virtual table source](https://docs.eventador.io/sqlstreambuilder/ssb_getting_started/#3-create-virtual-table-as-a-source). Select `Detect Schema` to create a schema from a sample of the data. Name it `authorizations` and use the Kafka topic named `authorizations`.

### Clone this repo
Open a terminal window and run the following commands from a convenient directory on your machine:

```
git clone git@github.com:Eventador/eventador_examples.git
cd eventador_examples/fraud
```

### Create an environment file
In the same terminal window and directory, create an .env file with your login credentials and some configuration information. This example uses Eventador Kafka.
```
echo "TOPIC=authorizations" > fraud.env
echo "URL=[get BASE_URL from eventador console]" >> fraud.env
echo "API_KEY=[get API key from eventador console]" >>fraud.env
```

NOTE: you can find the BASE_URL by selecting the `clusters` in the left hand pane, then `manage API keys` for the cluster you want to use, then copy `BASE URL`.

### Populate Eventador Kafka topic with data
```
docker build . -t fraud
docker run -d --env-file fraud.env fraud
```

## Create a processing job using Continuous SQL

Go to the [Eventador Console](https://eventador.cloud/streambuilder_list), and follow these steps to run a Continuous SQL job on Eventador.

- Select `SQLStreamBuilder` from the left hand menu.
- Select `None` as the virtual table sink to see results in browser only.
- Paste the below SQL into the SQL editor:

```SQL
SELECT *
FROM authorizations
MATCH_RECOGNIZE(
  PARTITION BY card
  ORDER BY eventTimestamp
  MEASURES
      A.amount AS start_amount,
      A.eventTimestamp AS first_timestamp,
      A.lat AS lat,
      A.lon AS lon,
      B.amount AS next_amount,
      B.eventTimestamp AS next_timestamp,
      C.amount AS finish_amount,
      C.eventTimestamp AS finish_timestamp
  ONE ROW PER MATCH
  AFTER MATCH SKIP PAST LAST ROW
  PATTERN (A B C)
  WITHIN INTERVAL '1' MINUTE
  DEFINE
    A AS A.amount IS NOT NULL
      AND CAST(A.amount AS integer) >= 0
      AND CAST(A.amount AS integer) <= 1000,
    B AS B.amount IS NOT NULL
      AND CAST(B.amount AS integer) >= 1001
      AND CAST(B.amount AS integer) <= 2000,
    C AS C.amount IS NOT NULL
      AND CAST(C.amount AS integer) > 2001)
```

- Select the `Materialized View` tab, select `card` as the primary key. Change `retention` to 30 seconds.
- Select `Add Query`, add `auths` as the URL pattern, select `Select All` for the columns, and `Save Changes`.
- Copy the `URL Pattern` by right clicking on it and copying the link address. You will use this in the single page application.
- Select the `SQL` tab, and `Execute` button.

Because the continuous SQL query aggregates and maintains state over a period of time, the query will not return results until the window is complete. When it does, the fraudulent activity is shown as the results arrive. It should look something like this:

![img](img/ssb_snap.png)


## Visualizing the results

You can visualize the results using any mechanism that can get data from a RESTful API. [Here is an example](https://observablehq.com/@kgorman/untitled) that utilizes an ObservableHQ notebook, D3.js and MapBox GL JS to create a simple heatmap of fraud by location.

![img2](img/heatmap.png)
