# -*- coding: utf-8 -*-
""" Module to create tasks of project """
import requests


def covid_data_getter():
    """ Getting Covid information from https://github.com/CSSEGISandData/COVID-19"""
    github_base = 'https://api.github.com'
    headers = {
        'Accept': 'application/vnd.github.v3+json',
    }