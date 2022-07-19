# Flight Stats Collector

> Tool to collect departure flight information for a given airport from Flightradar24

The collected data can then be used for further analysis, e.g. number of canceled flights per airline

## Development

### Install dependencies

```bash
poetry install
```

### Run script

```bash
poetry shell
python3 app.py
```

## Setup

Start docker-compose setup with postgres and metabase

```bash
docker-compose up -d --build
```

After starting the docker-compose environment you can connect to the postgres database with your DB client of choice on port 5432 and access metabase via [http://localhost:3000/](http://localhost:3000/)

### Required Environment Variables

| Nmae           | Description                                    |
|----------------|------------------------------------------------|
| DB_USER        | Username of the PostgreSQL user                |
| DB_PASSWORD    | Password for the PostgreSQL user               |
| DB_HOST        | Hostname of the PostgreSQL                     |
| ORIGIN_AIRPORT | IATA code of the airport to be tracked         |
| LOG_LEVEL      | Log level for the collector, must be uppercase |
| TZ             | Timezone for date times stored in PostgreSQL   |
