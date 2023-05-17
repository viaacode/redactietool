#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  app/services/mh_properties.py
#
#   Setting, getting properties and array properties in v2 json of Mediahaven.
#

import json


def dynamic_array(mam_data, field_name):
    field_value = mam_data.get('Dynamic').get(field_name)

    if field_value is None:
        return []

    result = []
    for key in field_value:
        for val in field_value[key]:
            result.append({
                'value': val,
                'attribute': key,
            })

    return result


def dynamic_field(mam_data, field_name, field_type):
    field_values = mam_data.get('Dynamic').get(field_name)
    if field_values is None:
        return []

    result = []
    for val in field_values.get(field_type):
        result.append({
            'value': val,
            'attribute': field_type,
        })

    return result


def save_json_value(field_type, json_value, value_key):
    result = {}
    result[field_type] = []
    values = json.loads(json_value)
    for val in values:
        result[field_type].append(val[value_key])

    return result


def save_array_field(mam_data, field_name, values):
    mam_data['Dynamic'][field_name] = {}

    # first clear out all fields
    for val in values:
        mam_data['Dynamic'][field_name][val['attribute']] = []

    # now fill up arrays with the values
    for val in values:
        mam_data['Dynamic'][field_name][val['attribute']].append(val['value'])

    return mam_data


def get_title(mam_data, title_name):
    # TODO: ask if this is ok to return first element of list here.
    # in v1 we had 1 value, here we have an array with 1 value so we just return the first
    # title string to make it compatible
    if mam_data.get('Dynamic') is None:
        return ''

    dc_titles = mam_data.get('Dynamic').get('dc_titles')
    if dc_titles:
        titles = dc_titles.get(title_name, '')
        if len(titles) > 0:
            return titles[0]

    return ''
