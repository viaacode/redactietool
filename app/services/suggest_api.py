#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  app/services/suggest_api.py
#
#   Use suggest library to get suggestions for themas, vakken given
#   onderwijsniveaus and onderwijsgraden.
#   This wraps the calls and returns json to be used in metadata edit form
#   We also allow fetching of onderwijsgraden and niveaus to dynamically populate
#   the Vue components. Furthermore we will add some endpoints to do ajax calls from
#   vue that return data here (again in json format).
#
#   ENV vars: SPARQL_ENDPOINT, SPARQL_USER, SPARQL_PASS and SPARQL_TOKEN
#

import os
import json
from app.services.suggest.Suggest import Suggest


class SuggestApi:

    SPARQL_ENDPOINT = os.environ.get(
        "SPARQL_ENDPOINT", "http://sparql_test_endpoint")
    USER = os.environ.get("SPARQL_USER", "test")
    PASSWORD = os.environ.get("SPARQL_PASS", "test")
    TOKEN = os.environ.get("SPARQL_TOKEN", "test")

    def __init__(self):
        self.suggest = Suggest(
            self.SPARQL_ENDPOINT, self.USER, self.PASSWORD, self.TOKEN
        )

    def get_onderwijsniveaus(self):
        res = []
        for r in self.suggest.get_niveaus():
            res.append(r)
        return json.dumps(res)

    def get_onderwijsgraden(self):
        res = []
        for r in self.suggest.get_graden():
            res.append(r)
        return json.dumps(res)

    def get_themas(self):
        themas = []
        for r in self.suggest.get_themas():
            themas.append(r)
        return json.dumps(themas)

    def get_vakken(self):
        vakken = []
        for r in self.suggest.get_vakken():
            vakken.append(r)
        return json.dumps(vakken)

    def get_vakken_related(self, graden, niveaus):
        concept_ids = []
        for g in graden:
            concept_ids.append(g["id"])

        for n in niveaus:
            concept_ids.append(n["id"])

        vakken = []
        for r in self.suggest.get_related_vak(concept_ids):
            vakken.append(r)
        return json.dumps(vakken)

    def get_vakken_suggesties(self, graden, themas):
        graden_ids = []
        for g in graden:
            graden_ids.append(g["id"])

        thema_ids = []
        for t in themas:
            thema_ids.append(t["id"])

        vakken = []
        for r in self.suggest.suggest(thema_ids, graden_ids):
            vakken.append(r)
        return json.dumps(vakken)
