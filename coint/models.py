from django.db import models
from tempodb import TempoDB, pdseries2tbdseries
import datetime
from intradata import get_google_data
from celery.contrib.methods import task_method
from coint_site.celery import app
import logging

logger = logging.getLogger(__name__)


class Company(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150)
    symbol = models.CharField(max_length=20)
    hq = models.CharField(max_length=150)
    industry = models.CharField(max_length=150)
    sector = models.CharField(max_length=150)
    tempodb = models.IntegerField()

    def get_prices(self):
        logger.info('Fetching prices for: ' + self.symbol)
        tdb = TempoDB()
        return tdb.db[self.tempodb].read_key(self.symbol, datetime.datetime(2000, 1, 1), datetime.datetime.now())

    @app.task(filter=task_method)
    def update_prices(self):
        logger.info('Updating prices for: ' + self.symbol)
        tdb = TempoDB()
        df = get_google_data(self.symbol, lookback=15)
        series = df['close']
        tbd_series = pdseries2tbdseries(series)
        tdb.db[self.tempodb].write_key(self.symbol, tbd_series)
        return None


class Pair(models.Model):
    id = models.AutoField(primary_key=True)
    symbol = models.CharField(max_length=40)
