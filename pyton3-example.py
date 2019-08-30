#!/usr/bin/env python

from __future__ import print_function

__author__ = "Luka Paulic <luka.paulic@sartura.hr>"

import sysrepo as sr
import sys
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def weather_report_state_data(xpath, holder, request_id, original_xpath, private_ctx):
    print("\n\n ========== GET STATE DATA ========== \n\n")
    
    print("Original XPATH: " + original_xpath)
    print("Current XPATH: " + xpath)

    last_node = xpath.split(":")[-1].split("/")[-1]
    print(last_node)

    if (last_node == "status"):
        try:
            out_values = holder.allocate(2)
            out_values.val(0).set("/weather-report:weather-report/status/city", "Zagreb", sr.SR_STRING_T)
            out_values.val(1).set("/weather-report:weather-report/status/temperature", 32, sr.SR_INT32_T)
        except Exception as e:
            logger.exception(e)

    
try:
    module = "weather-report"

    print("\n\n ========== PLUGIN SCRITP STARTED  ==========")

    connection = sr.Connection("python-example-application")
    session = sr.Session(connection)
    subscribe = sr.Subscribe(session)

    subscribe.dp_get_items_subscribe("/"+module+":weather-report", weather_report_state_data, sr.SR_SUBSCR_DEFAULT)

    sr.global_loop()

    print("Application exit requested, exiting.\n")

except Exception as ex:
    print(e)
