#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers and integrated
#           code from python-saml3 flask demo for SAML authorization
#
#           Thanks to 'suggest library' from Miel Vander Sande that will
#           be used to populate the dropdowns in the metadata
#           form's LOM sections. Suggest is part of the KnowledeGraph project.
#
#  app/redactietool.py
#
#   Micro service to supply the wanted mocked responses that come back from mediahaven and
#   from the suggest library. It allows working offline without an internet connection
#
#   example export when connected:
#     export MEDIAHAVEN_API = https://example-qas.meemoo.be/mediahaven-rest-api
#
#   for the mocked server just change the export like so:
#     export MEDIAHAVEN_API = http://localhost:5000
#
#   Running the mock/dev server just do following:
#       cd mocked_metadata
#       ./start_mock_api.sh
#

import json
from flask import Flask, render_template, request, send_from_directory
from flask_cors import CORS, cross_origin

app = Flask(
    __name__,
    static_url_path='',
    static_folder='items',
    template_folder='templates'
)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


# export MEDIAHAVEN_API=http://localhost:5000
@app.route('/resources/media')
@cross_origin()
def send_json_file():
    search_qry = request.args.get('q')
    print("q=", search_qry)
    # start_index = request.args.get('startIndex')
    # nr_of_results = request.args.get('nrOfResults')
    # print("start_index=", start_index)
    # print("nr results=", nr_of_results)

    json_data = '{}'
    result_count = 0

    # verwant_aan for subs:
    if (len(search_qry.split('dc_relationsis_verwant_aan:')) > 1):
        json_file = search_qry.split('dc_relationsis_verwant_aan:')[
            1].split(')')[0].strip() + '.json'
        print("json file to fetch in sub_items=", json_file)
        result_count = 0

    # check if we search pid:
    if (len(search_qry.split('ExternalId:')) > 1):
        result_count = 1
        json_file = search_qry.split('ExternalId:')[1].split(')')[
            0].strip() + '.json'
        json_data = open('./items/'+json_file).read()

    return {
        'totalNrOfResults': result_count,
        'mediaDataList': [json.loads(json_data)]
    }


@app.route('/onderwijsniveaus')
@cross_origin()
def onderwijsniveaus_json():
    return send_from_directory('suggest', 'onderwijsniveaus.json')


@app.route('/onderwijsgraden')
@cross_origin()
def onderwijsgraden_json():
    return send_from_directory('suggest', 'onderwijsgraden.json')


@app.route('/themas')
@cross_origin()
def themas_json():
    return send_from_directory('themas', 'themas.json')


@app.route('/vakken')
@cross_origin()
def vakken_json():
    return send_from_directory('vakken', 'vakken.json')


@app.route('/vakken_suggest', methods=['POST'])
@cross_origin()
def get_vakken_suggesties():
    json_data = json.loads(request.data)
    print("graden=", json_data['graden'])
    print("themas=", json_data['themas'])
    return send_from_directory('vakken', 'vakken_suggest.json')


@app.route('/vakken_related', methods=['POST'])
@cross_origin()
def get_vakken_related():
    json_data = json.loads(request.data)
    print("graden=", json_data['graden'])
    print("niveaus=", json_data['niveaus'])
    return send_from_directory('vakken', 'vakken_related.json')


@app.route('/keyword_search', methods=['POST'])
@cross_origin()
def keyword_search():
    json_data = json.loads(request.data)
    print("search qry=", json_data['qry'])

    # simulate ES search response:
    return json.dumps([
        {
            'text': 'strik',
            '_id': '_strik',
            '_score': 1.0
        },
        {
            'text': 'strijk',
            '_id': '_strijk',
            '_score': 1.0
        },
        {
            'text': 'straf',
            '_id': '_straf',
            '_score': 1.0
        },
        {
            'text': 'strop',
            '_id': '_strop',
            '_score': 1.0
        },
        {
            'text': 'stroop',
            '_id': '_stroop',
            '_score': 1.0
        },
        {
            'text': 'stramien',
            '_id': '_stramien',
            '_score': 1.0
        },

    ])


@app.route('/publicatie_status', methods=['GET'])
@cross_origin()
def mock_pub_status():
    # request.form.pid and request.form.department are passed
    return {
        'publish_item': True
    }


@app.route('/')
def api_docs():
    return render_template('api.html')


if __name__ == '__main__':
    app.run()
