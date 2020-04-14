# JHU CSSE Covid19 REST endpoint

This is a repository for tooling to fetch data on the Covid19 outbreak from the John Hopkins CSSE [github repo](https://github.com/CSSEGISandData/COVID-19) and continuously process it to a RESTful endpoint. If updates are made to the data, the changes are reflected by querying the endpoint.

The purpose of providing the data via REST is so that developers, data scientists, data engineers and tinkerers can easily reference the latest data and not have to write any processing tooling in order to help the fight. This hopefully eliminates services, cost, development time, and aids in the goal of fighting Covid19 in an academic and/or research setting.

This is built using the [Eventador Platform](https://www.eventador.io) for continuous ingest, processing and materialization of results.

## The URL for the REST endpoint.

The software used to create this feed is contained in this repository but you do not need to deploy this software to use the data.

The public URL of the RESTful endpoint is:

```
https://snapper-2058733b.b83e87f22c1e0e3d.ssb.evstreams.net/api/v1/query/3804/covid19
```

## Freshness of data

While the JHU dataset is only appended to daily, continous edits are made to existing data. The freshest data is pulled continuously and processed in real time to a view.

## Using the REST API

This is a public read only API. You can create analytics, reports, applications or whatever you want using this data. Because of it being public, the REST endpoint queries are not configurable, if you need a specific query [ping us at Eventador](mailto:hello@eventador.io) and we will whip one up for you as long as it's public and others can make use of it.

Using this endpoint, it's simple, for instance, to populate a python datatable with the latest data like:

```python
import pandas as pd

REPO = "https://snapper-2058733b.b83e87f22c1e0e3d.ssb.evstreams.net/api/v1/query/3804/covid19"
df = pd.read_json(REPO, header=0)
print(df)
```

Or perhaps you just want to see the data on the command line:
```bash
curl https://snapper-2058733b.b83e87f22c1e0e3d.ssb.evstreams.net/api/v1/query/3804/covid19
```

## Optional: Using the software to pull data.

You **do not** need to run this software to use the data, you can use the REST endpoint above without doing anything below. If you want to run this yourself - you will need your own Apache Kafka cluster, and an [Eventador Account](https://www.eventador.io) to use this software effectively.

### Clone this repo
```
git clone git@github.com:Eventador/eventador_examples.git
cd eventador_examples/covid19
```

### Create an environment file
In the same directory create an .env file with your login credentials and some configuration information. Replace the variables surrounded by `[ ]` with your own values, including the brackets.
```
echo "BOOTSTRAP_SERVERS=[yourkafkaserver:9092]" > covid19.env
echo "SASL_USERNAME=[get from cloud provider]" >> covid19.env
echo "SASL_PASSWORD=[get from cloud provider]" >> covid19.env
echo "KAFKA_TOPIC=covid19" >> covid19.env
```

### Populate Kafka with data
```
docker build . -t covid19
docker run -d --env-file covid19.env covid19
```

### Setup Eventador
Follow these steps from the Eventador Getting Started Guide.

- Create a [new environment](https://docs.eventador.io/sqlstreambuilder/ssb_getting_started/#1-create-a-cloud-environment). Name it `covid19`
- Create a [datasource](https://docs.eventador.io/sqlstreambuilder/ssb_getting_started/#2-create-a-data-source). Name it `covid19`. Connect it to the Kafka cluster you configured above.
- Create a new [virtual table source](https://docs.eventador.io/sqlstreambuilder/ssb_getting_started/#3-create-virtual-table-as-a-source). Select `Detect Schema` to create a schema from a sample of the data.

### Create a processing job using Continuous SQL

Follow these steps to run a Continuous SQL job on Eventador.

- Select `SQLStreamBuilder` from the left hand menu.
- Select `results in browser` as the virtual table sink.
- Paste the below SQL into the SQL editor:

```SQL
-- the more simplistic query you can run
SELECT * FROM covid19;
```

- Select the `Materialized View` tab, select `Combined_Key` as the primary key. Change `retention` to 30 seconds.
- Select `Add Query`, add `covid19` as the URL pattern, select `Select All` for the columns, and `Save Changes`.
- Copy the `URL Pattern` by right clicking on it and copying the link address. You will use this in the single page application.
- Select the `SQL` tab, and `Execute` button.

# Terms of Use
## Software License

The software code in this repository is covered under [this License](LICENSE.MD).

## Data copyright

Data is copyright 2020 Johns Hopkins University, all rights reserved, is provided to the public strictly for educational and academic research purposes. The Website relies upon publicly available data from multiple sources, that do not always agree. The Johns Hopkins University hereby disclaims any and all representations and warranties with respect to the Website, including accuracy, fitness for use, and merchantability. Reliance on the Website for medical guidance or use of the Website in commerce is strictly prohibited.
