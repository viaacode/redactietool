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


# THESE ARE SOON TO BE DEPRECATED:
def get_property(mam_data, attribute):
    props = mam_data.get('mdProperties', [])
    result = ''
    for prop in props:
        if prop.get('attribute') == attribute:
            return prop.get('value', '')

    return result


def get_array_property(mam_data, attribute, array_attribute):
    props = mam_data.get('mdProperties', [])
    result = ''
    for prop in props:
        if prop.get('attribute') == attribute:
            array_values = prop.get('value', '')
            for att in array_values:
                if att.get('attribute') == array_attribute:
                    return att.get('value', '')

    return result


#
# def set_property(mam_data, propkey, propvalue):
#     for prop in mam_data['mdProperties']:
#         if prop.get('attribute') == propkey:
#             prop['value'] = propvalue
#             return mam_data
#
#     # if we get here. we need to add a new property as it was cleared and
#     # is not present anymore
#     mam_data['mdProperties'].append({
#         'value': propvalue,
#         'attribute': propkey,
#         'dottedKey': None
#     })
#
#     return mam_data
#
#
# def get_md_array(mam_data, attribute, legacy_fallback=False):
#     props = mam_data.get('mdProperties', [])
#     for prop in props:
#         if prop.get('attribute') == attribute:
#             return prop.get('value', [])
#
#     if legacy_fallback:
#         return {'show_legacy': True}
#     else:
#         return []
#
#

#
# def set_array_property(mam_data, attribute, array_attribute, propvalue):
#     props = mam_data.get('mdProperties', [])
#     array_attrib_exists = False
#     array_prop = None
#     for prop in props:
#         if prop.get('attribute') == attribute:
#             array_prop = prop
#             array_values = prop.get('value', '')
#             for att in array_values:
#                 if att.get('attribute') == array_attribute:
#                     array_attrib_exists = True
#                     att['value'] = propvalue
#                     return mam_data
#
#     if not array_prop:
#         array_val = [{
#             'value': propvalue,
#             'attribute': array_attribute,
#             'dottedKey': None
#         }]
#         array_prop = {
#             'attribute': attribute,
#             'dottedKey': None,
#             'value': array_val
#         }
#         mam_data['mdProperties'].append(array_prop)
#         return mam_data
#
#     if array_prop and not array_attrib_exists:
#         array_prop['value'].append({
#             'value': propvalue,
#             'attribute': array_attribute,
#             'dottedKey': None
#         })
#         return mam_data
#
#     # in case it's new array prop (bail out for now):
#     print(
#         "ERROR in set_array_property: {}/{} with value {} not saved!".format(
#             attribute,
#             array_attribute,
#             propvalue
#         )
#     )
#
#     return mam_data
#
#
# def set_json_array_property(mam_data, propkey, jkey, jvalue, prop_name="multiselect"):
#     values = json.loads(jvalue)
#     array_values = []
#     for v in values:
#         array_values.append({
#             'value': v[jkey],
#             'attribute': prop_name,
#             'dottedKey': None
#         })
#
#     # print("set_json_array values=", array_values, "prop_name", prop_name)
#
#     for prop in mam_data['mdProperties']:
#         if prop.get('attribute') == propkey:
#             prop['value'] = array_values
#             return mam_data
#
#     mh_prop = {
#         'value': array_values,
#         'attribute': propkey,
#         'dottedKey': None
#     }
#
#     # extra subKey to set here
#     if prop_name == 'multiselect':
#         mh_prop['subKey'] = 'multiselect'
#
#     mam_data['mdProperties'].append(mh_prop)
#     return mam_data
