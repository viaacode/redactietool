#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  app/services/rmh_mapping.py
#
#   Do mapping between redactietool form and mh target data for saving changes.
#   Similarly load json data from MediahavenApi and populate form back.
#
# from requests import Session

import json
import os
from viaa.configuration import ConfigParser
from viaa.observability import logging
from app.services.subtitle_files import get_property, get_array_property

logger = logging.get_logger(__name__, config=ConfigParser())


class RmhMapping:
    def __init__(self):
        print("RmhMapping initialized")

    def form_to_mh(self, request):
        """
        convert form metadata hash into json data
        """
        print("TODO: convert following metadata:\n", request.form)

        tp = {
            'token': request.form.get('token'),
            'pid': request.form.get('pid'),
            'department': request.form.get('department'),
            'mam_data': request.form.get('mam_data'),
            'video_url': request.form.get('video_url'),
            'subtitle_type': request.form.get('subtitle_type')
        }

        errors = None  # for now, there will however be a lot more
        # logic and checks here that can generate errors, warnings etc.

        # TODO: figure out how to turn our submitted params into the correct
        # json data or xml sidecar in order to update the wanted fields
        # for now return the template params as json
        return tp, json.dumps(tp), errors

    # TODO: also don't forget to make calls here using the suggest library from Miel.
    # we will be getting back id's from mediahaven and in order to populate
    # the dropdowns in form we will need some extra calls in order to fetch
    # the actual label and description:
    # https://github.com/viaacode/skos-scripts-redactietool

    # for the post call we don't need it as the id's will be directly pushed to mediahaven api
    # but this is something for later as Caroline needs to extend MAM structure
    # to have support for these.
    # more details in jira ticket https://meemoo.atlassian.net/browse/DEV-1821
    def mh_to_form(self, token, pid, department, errors, mam_data):
        """
        convert json metadata from MediahavenApi back into a
        python hash for populating the view
        """

        # debug data for in logs:
        print("DEBUG: mediahaven json_data:\n", mam_data)

        # Mapping expliciet aan Koen gevraagd op 1/12/2021.
        # van charlotte gelukkig al alle andere velden gehad
        # maar deze ontbreekt nog steeds!
        # avo_beschrijving = get_property(mam_data, 'dcterms_avo')

        dc_description_lang = get_property(mam_data, 'dc_description_lang')
        beschrijving_meemoo_redactie = get_property(mam_data, 'dcterms_abstract')
        ondertitels = get_property(mam_data, 'dc_description_ondertitels')
        programma_beschrijving = get_property(mam_data, 'dc_description_programma')
        cast = get_property(mam_data, 'dc_description_cast')
        transcriptie = get_property(mam_data, 'dc_description_transcriptie')

        return {
            'token': token,
            'department': department,
            'mam_data': json.dumps(mam_data),
            'original_cp': get_property(mam_data, 'Original_CP'),
            'dc_identifier_localid': get_property(mam_data, 'dc_identifier_localid'),
            'pid': pid,
            'title': mam_data.get('title'),
            'ontsluitingstitel': get_property(mam_data, 'dc_title'),

            # I'm taking some assumptions here because these fields
            # are not on my test pid. only dc_titles/serie is present
            'titel_serie': get_array_property(mam_data, 'dc_titles', 'serie'),
            'titel_episode': get_array_property(mam_data, 'dc_titles', 'episode'),
            'titel_aflevering': get_array_property(mam_data, 'dc_titles', 'aflevering'),
            'titel_alternatief': get_array_property(mam_data, 'dc_titles', 'alternatief'),
            'titel_programma': get_array_property(mam_data, 'dc_titles', 'programma'),
            'titel_serienummer': get_array_property(mam_data, 'dc_titles', 'serienummer'),
            'titel_seizoen': get_array_property(mam_data, 'dc_titles', 'seizoen'),
            'titel_seizoen_nr': get_array_property(mam_data, 'dc_titles', 'seizoen_nr'),
            'titel_archief': get_array_property(mam_data, 'dc_titles', 'archief'),
            'titel_deelarchief': get_array_property(mam_data, 'dc_titles', 'deelarchief'),
            'titel_reeks': get_array_property(mam_data, 'dc_titles', 'reeks'),
            'titel_deelreeks': get_array_property(mam_data, 'dc_titles', 'deelreeks'),
            'titel_registratie': get_array_property(mam_data, 'dc_titles', 'registratie'),

            # these are mapped and working correctly again
            'description': mam_data.get('description'),
            'beschrijving_meemoo_redactie': beschrijving_meemoo_redactie,
            'ondertitels': ondertitels,
            'programma_beschrijving': programma_beschrijving,
            'cast': cast,
            'transcriptie': transcriptie,
            'dc_description_lang': dc_description_lang,  # orig uitgebr. beschr
            'created': get_property(mam_data, 'CreationDate'),
            'dcterms_issued': get_property(mam_data, 'dcterms_issued'),
            'dcterms_created': get_property(mam_data, 'dcterms_created'),  # not used in form yet?
            'archived': get_property(mam_data, 'created_on'),
            # for v2 mam_data['Internal']['PathToVideo']
            'video_url': mam_data.get('videoPath'),
            'flowplayer_token': os.environ.get(
                'FLOWPLAYER_TOKEN', 'set_in_secrets'
            ),
            'validation_errors': errors
        }
