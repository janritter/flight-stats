from pyflightdata import FlightData
from peewee import *
from datetime import datetime
import logging
import os
import time

log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.basicConfig(level=log_level)

# Set Timezone
time.tzset()

database = PostgresqlDatabase(
    'flightstats',
    user='flightstats',
    password=os.environ['DB_PASSWORD'],
    host=os.environ['DB_HOST'],
)

f = FlightData()

originAirport = os.environ['ORIGIN_AIRPORT']

logging.info("Using origin airport: {}".format(originAirport))


class BaseModel(Model):
    """A base model that will use our Postgresql database"""
    class Meta:
        database = database


class Airline(BaseModel):
    code = CharField()
    name = CharField()


class Flight(BaseModel):
    number = CharField()
    statusText = CharField()
    statusColor = CharField()
    createdAt = DateTimeField()
    updatedAt = DateTimeField()
    airline = ForeignKeyField(Airline, backref='flights')
    originAirport = CharField()
    destinationAirport = CharField()
    timeScheduled = DateTimeField()
    timeEstimated = DateTimeField(null=True)


def create_tables():
    with database:
        database.create_tables([Airline, Flight])


def get_time_scheduled(flight):
    return datetime.fromtimestamp(
        flight['time']['scheduled']['departure_millis']/1000.0)


def get_time_estimated_or_none(flight):
    if 'departure_millis' in flight['time']['estimated']:
        return datetime.fromtimestamp(
            flight['time']['estimated']['departure_millis']/1000.0)
    return None


if __name__ == '__main__':
    create_tables()

    while True:
        logging.info("Fetching flights at {}".format(datetime.now()))

        departures = f.get_airport_departures(originAirport)

        for departure in departures:
            logging.debug(departure)

            apiFlight = departure['flight']
            status = apiFlight['status']

            logging.debug("Flight info from API: %s", apiFlight)

            if 'code' not in apiFlight['airline']:
                logging.warning(
                    "No airline code in API flight, skipping: %s", apiFlight)
                continue

            airline, created = Airline.get_or_create(
                code=apiFlight['airline']['code']['iata'],
                name=apiFlight['airline']['name'],
            )

            timeScheduled = get_time_scheduled(apiFlight)
            timeEstimated = get_time_estimated_or_none(apiFlight)

            flight = Flight.get_or_none(
                number=apiFlight['identification']['number']['default'],
                timeScheduled=timeScheduled,
            )

            now = datetime.now()

            if not flight:
                flight = Flight.create(
                    number=apiFlight['identification']['number']['default'],
                    statusText=status['generic']['status']['text'],
                    statusColor=status['generic']['status']['color'],
                    createdAt=now,
                    updatedAt=now,
                    airline=airline,
                    originAirport=originAirport,
                    destinationAirport=apiFlight['airport']['destination']['code']['iata'],
                    timeScheduled=timeScheduled,
                    timeEstimated=timeEstimated,
                )
                logging.info("Created flight %s",
                            apiFlight['identification']['number']['default'],)
                logging.debug("Created flight object: %s", flight)
            else:
                flight.statusText = status['generic']['status']['text']
                flight.statusColor = status['generic']['status']['color']
                flight.updatedAt = now
                flight.timeEstimated = timeEstimated
                flight.timeScheduled = timeScheduled
                flight.save()

                logging.info("Updated flight %s",
                            apiFlight['identification']['number']['default'],)
                logging.debug("Updated flight object: %s", flight)

        logging.info("Sleeping for 5 minutes")
        time.sleep(300)
