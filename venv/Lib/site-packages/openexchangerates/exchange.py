#!/usr/bin/env python

import requests
import json
import os
import pickle
from datetime import datetime, date

SAVE_DIR = os.path.expanduser("~/.openexchangerates")
HTTP_SERVICE = "https://openexchangerates.org/api/"


########################################################################
class Exchange:
    """Open Exchange Rates API.

    The Open Exchange Rates API provides hourly-updated exchange (forex) rates,
    relative to US Dollars (USD) in JSON format.
    It's free for personal/small-scale use, and extremely cheap for apps,
    businesses and commercial projects.

    You can sign up for an App ID here: https://openexchangerates.org/signup/
    """

    #----------------------------------------------------------------------
    def __init__(self, save_dir=SAVE_DIR, app_id=None):
        """Constructor"""

        # set directory for save keys and endpoints
        self.__set_disk_dir__(save_dir)

        # if app_id is defined
        if app_id:
            # save it
            self.__save_app_id__(app_id)
        else:
            # red from local file
            app_id = self.__get_app_id__()

        # post args for API
        self.APPID = {"app_id" : app_id}

        # update endpoins if we have old (+ 1h) endpoints
        self.__update_disk_data__()


    #----------------------------------------------------------------------
    def __get_app_id__(self):
        """"""
        app_id = os.path.join(SAVE_DIR, "app_id")
        assert os.path.exists(app_id), "Missing APP_ID??"

        file_ = open(app_id, "r")
        app_id = file_.readlines()
        file_.close()
        return app_id


    #----------------------------------------------------------------------
    def __save_app_id__(self, app_id):
        """"""
        app_id_path = os.path.join(SAVE_DIR, "app_id")
        app_id_file = open(app_id_path, "w")
        app_id_file.write(app_id)
        app_id_file.close()


    #----------------------------------------------------------------------
    def __set_disk_dir__(self, path):
        """"""
        path = os.path.expanduser(path)
        path = os.path.expandvars(path)
        path = os.path.abspath(path)

        if not os.path.exists(path):
            os.mkdir(path)

        self.SAVE_DIR = path


    #----------------------------------------------------------------------
    def __update_disk_data__(self):
        """"""
        timestamp_file = os.path.join(SAVE_DIR, "timestamp")
        if not os.path.exists(timestamp_file):
            self.__save_disk_data__()

        else:
            timestamp = pickle.load(open(timestamp_file, "rb"))
            t1 = datetime.fromtimestamp(timestamp)
            t2 = datetime.now()
            delta = t2 - t1
            if (delta.seconds / (60 * 60)) >= 1:
                self.__save_disk_data__()


    #----------------------------------------------------------------------
    def __save_disk_data__(self):
        """"""
        pickle.dump(self.__currencies__(), open(os.path.join(SAVE_DIR, "currencies.json"), "wb"))
        latest = self.__latest__()
        pickle.dump(latest, open(os.path.join(SAVE_DIR, "latest.json"), "wb"))
        pickle.dump(latest["timestamp"], open(os.path.join(SAVE_DIR, "timestamp"), "wb"))


    #----------------------------------------------------------------------
    def __currencies__(self):
        """"""
        response = requests.get(HTTP_SERVICE+"currencies.json", params=self.APPID)
        return self.__handle_response__(response)


    #----------------------------------------------------------------------
    def __latest__(self):
        """"""
        response = requests.get(HTTP_SERVICE+"latest.json", params=self.APPID)
        return self.__handle_response__(response)


    #----------------------------------------------------------------------
    def historical(self, date_):
        """Get most selected date exchange rates.

        Return a dictionary with disclaimer, license, timesta, timestamp, base, rates data as keys.


        Parameters
        ----------
        date_: str, datetime
            Choice an especific date for get exchange rates.


        Returns
        -------
        latest: dict
            View https://openexchangerates.org/api/currencies.json


        Example
        -------
        >>> from datetime import date
        >>> my_date = date(2014, 10, 18)
        >>> openexchangerates.historical(my_date)

        """

        if isinstance(date_, date):
            date_ = date_.strftime("%Y-%m-%d")

        response = requests.get(HTTP_SERVICE+"historical/{}.json".format(date_), params=self.APPID)
        return self.__handle_response__(response)


    #----------------------------------------------------------------------
    def currencies(self):
        """List available currencies.

        View https://openexchangerates.org/api/currencies.json


        Returns
        -------
        currencies: dict
            Dictionary with international 3-letter codes as keys and values as full name currency.


        Example
        -------
        >>> openexchangerates.currencies()

        """

        return pickle.load(open(os.path.join(SAVE_DIR, "currencies.json"), "rb"))


    #----------------------------------------------------------------------
    def latest(self):
        """Get most up-to-date exchange rates.

        Return a dictionary with disclaimer, license, timesta, timestamp, base, rates data as keys.


        Returns
        -------
        latest: dict
            View https://openexchangerates.org/api/currencies.json


        Example
        -------
        >>> openexchangerates.latest()

        """

        return pickle.load(open(os.path.join(SAVE_DIR, "latest.json"), "rb"))


    #----------------------------------------------------------------------
    def rates(self):
        """Get most up-to-date exchange rates.

        Alias for latest()["rates"]


        Returns
        -------
        rates: dict
            Dictionary with international 3-letter codes as keys and values as exchange in USD.


        Example
        -------
        >>> openexchangerates.rates()

        """

        return self.latest()["rates"]


    #----------------------------------------------------------------------
    def historical_rates(self, date_):
        """Get most up-to-date exchange rates.

        Alias for latest()["rates"]


        Parameters
        ----------
        date_: str, datetime
            Choice an especific date for get exchange rates.


        Returns
        -------
        rates: dict
            Dictionary with international 3-letter codes as keys and values as exchange in USD.


        Example
        -------
        >>> from datetime import date
        >>> my_date = date(2011, 10, 18)
        >>> openexchangerates.rates()

        """

        return self.historical(date_)["rates"]


    #----------------------------------------------------------------------
    def BTCexchange(self, bitcoins, output_currency, satoshi=False, rates=None):
        """Convert from Bitcoins to currency.

        Return value in currency for bitcoins input.


        Parameters
        ----------

        bitcoins: int, decimal
            Bitcoins or Satoshis for convertion.

        output_currency: str
            International 3-letter codes for output currency.

        zatoshi: bool
            Is input in Satoshis?


        Returns
        -------
        value: decimal
            Value of Bitcoins in selected currency.


        Example
        -------
        >>> openexchangerates.BTCexchange(1, "USD")
        >>> openexchangerates.BTCexchange(1, "COP")
        >>> openexchangerates.BTCexchange(1, "JPY")

        """

        if rates is None:
            rates = self.rates()

        btc = 1 / rates["BTC"]
        target = rates[output_currency]
        usd = rates["USD"]

        return (bitcoins * btc) * target


    #----------------------------------------------------------------------
    def exchange(self, value, input_currency, output_currency, rates=None):
        """Convert between currencies.

        {value}{input_currency} -> {new_value}{output_currency}


        Parameters
        ----------
        value: int, decimal
            Value for input currency,

        input_currency: str
            International 3-letter codes for input currency.

        output_currency: str
            International 3-letter codes for output currency.


        Returns
        -------
        new_value: decimal
            Value in new currency.


        Example
        -------
        >>> openexchangerates.exchange(1, "USD", "COP")
        >>> openexchangerates.exchange(1, "COP", "MXN")
        >>> openexchangerates.exchange(1, "JPY", "COP")

        """

        if rates is None:
            rates = self.rates()

        target = rates[output_currency]
        current = 1 / rates[input_currency]
        usd = rates["USD"]

        return (value * current) * target


    #----------------------------------------------------------------------
    def __handle_response__(self, response):
        """"""
        if response.ok:
            try:
                return response.json()
            except json.JSONDecodeError:
                raise Exception("No JSON response.")
        else:
            raise Exception(response.reason)
