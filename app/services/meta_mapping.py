#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  app/services/meta_mapping.py
#
#   Do mapping between redactietool form and mh target data for saving changes.
#   Similarly load json data from MediahavenApi and populate form back.
#   it also has a member to create the xml sidecar data by using the
#   MetaSidecar class
#

import json
import os
from viaa.configuration import ConfigParser
from viaa.observability import logging
from app.services.mh_properties import (
    get_property, set_property,
    get_md_array,
    get_array_property, set_array_property,
    set_json_array_property
)
from app.services.xml_sidecar import XMLSidecar
from app.services.input_escaping import markdown_to_html, cleanup_markdown, escape

logger = logging.get_logger(__name__, config=ConfigParser())

# get_md_array is now deprecated. we need this instead!


def dynamic_array(mam_data, field_name):
    result = []
    field_value = mam_data.get('Dynamic').get(field_name)
    for key in field_value:
        for val in field_value[key]:
            result.append({
                'value': val,
                'attribute': key,
                'dottedKey': None  # not sure we need this
            })

    return result


def dynamic_field(mam_data, field_name, field_type):
    result = []
    for val in mam_data.get('Dynamic').get(field_name).get(field_type):
        result.append({
            'value': val,
            'attribute': field_type,
            'dottedKey': None,  # TODO: check if frontend can work without this
        })


class MetaMapping:
    def __init__(self):
        self.MAKER_OPTIONS = [
            'Maker', 'Archiefvormer', 'Auteur', 'Acteur',
            'Cineast', 'Componist', 'Choreograaf', 'Danser',
            'Documentairemaker', 'Fotograaf', 'Interviewer',
            'Kunstenaar', 'Muzikant', 'Performer', 'Producer',
            'Productiehuis', 'Regisseur', 'Schrijver',
            'Opdrachtgever',
        ]

        self.CONTRIBUTOR_OPTIONS = [
            'Aanwezig', 'Adviseur', 'Afwezig', 'Archivaris',
            'Arrangeur', 'ArtistiekDirecteur', 'Assistent',
            'Auteur', 'Belichting', 'Bijdrager', 'Cameraman',
            'Co-producer', 'Commentator', 'Componist', 'DecorOntwerper',
            'Digitaliseringspartner', 'Dirigent', 'Dramaturg',
            'Fotografie', 'Geluid', 'Geluidsman', 'GrafischOntwerper',
            'KostuumOntwerper', 'Kunstenaar', 'Make-up', 'Muzikant',
            'Nieuwsanker', 'Omroeper', 'Onderzoeker', 'Post-productie',
            'Producer', 'Presenter', 'Reporter', 'Scenarist',
            'Soundtrack', 'Sponsor', 'TechnischAdviseur', 'Uitvoerder',
            'Verontschuldigd', 'Vertaler', 'Verteller', 'Voorzitter'
        ]

        self.PUBLISHER_OPTIONS = [
            'Distributeur', 'Exposant',
            'Persagentschap', 'Publisher'
        ]

    def frontend_metadata(self, pid, department, mam_data):
        item_type = mam_data.get('type')
        item_type_lom = dynamic_array(mam_data, 'lom_learningresourcetype')
        if item_type_lom and len(item_type_lom) > 0:
            item_type = item_type_lom[0]['value']

        return {
            'pid': pid,
            'department': department,
            'item_type': item_type,
            'item_languages': dynamic_field(mam_data, 'lom_languages', 'multiselect'),
            'item_eindgebruikers': dynamic_field(mam_data, 'lom_intendedenduserrole', 'multiselect'),
            'item_themas': dynamic_field(mam_data, 'lom_thema', 'Thema'),
            'item_vakken': dynamic_field(mam_data, 'lom_vak', 'Vak'),
            'item_vakken_legacy': dynamic_field(mam_data, 'lom_classification', 'multiselect'),
            'item_onderwijsniveaus': dynamic_field(mam_data, 'lom_onderwijsniveau', 'Onderwijsniveau'),
            'item_onderwijsgraden': dynamic_field(mam_data, 'lom_onderwijsgraad', 'Onderwijsgraad'),
            'tiem_onderwijsgraden_legacy': [],  # TODO: how does this work in v2???
            'item_onderwijsniveaus_legacy': [],  # TODO: how does this work in v2???
            # 'item_onderwijsniveaus_legacy': get_md_array(
            #     mam_data, 'lom_context'),
            #     mam_data,
            #     'lom_onderwijsgraad',
            #     legacy_fallback=True
            # ),
            # 'item_onderwijsgraden_legacy': get_md_array(
            #    mam_data,
            #    'lom_typicalagerange'
            # ),
            'item_keywords': dynamic_field(mam_data, 'lom_keywords', 'Sleutelwoord'),
            # 'item_keywords_cp': get_md_array(mam_data, 'dc_subjects'),
            # this is just an educated guess TODO: check if this is now correct
            'item_keywords_cp': mam_data.get('Descriptive').get('Keywords').get('Keyword'),
            'publish_item': 'ajax'  # signal ajax request to frontend
        }

    def form_params(self, pid, department, mam_data, errors=[]):
        keyframe_edit_url = '{}{}'.format(
            os.environ.get('KEYFRAME_EDITING_LINK',
                           'https://set_in_secrets?id='),
            mam_data['Internal']['FragmentId']
        )

        item_type = mam_data.get('type')
        item_type_lom = dynamic_array(mam_data, 'lom_learningresourcetype')
        if item_type_lom and len(item_type_lom) > 0:
            item_type = item_type_lom[0]['value']

        # get_property(mam_data, 'dcterms_abstract')
        dcterms_abstract = mam_data.get('Dynamic').get('dcterms_abstract')
        avo_beschrijving = markdown_to_html(dcterms_abstract)

        result = {
            'department': department,
            'mam_data': json.dumps(mam_data),
            'publish_item': False,
            'original_cp': mam_data.get('Dynamic').get('Original_CP'),
            'makers': dynamic_array(mam_data, 'dc_creators'),
            'maker_options': self.MAKER_OPTIONS,
            'contributors': dynamic_array(mam_data, 'dc_contributors'),
            'contributor_options': self.CONTRIBUTOR_OPTIONS,
            'publishers': dynamic_array(mam_data, 'dc_publishers'),
            'publisher_options': self.PUBLISHER_OPTIONS,
            'item_type': item_type,
            'frontend_metadata': self.frontend_metadata(pid, department, mam_data),
            'dc_identifier_localid': mam_data.get('Dynamic').get('dc_identifier_localid'),
            'pid': pid,
            'title': mam_data.get('Descriptive').get('Title'),
            'ontsluitingstitel': mam_data.get('Dynamic').get('dc_title'),
            # get_array_property(mam_data, 'dc_titles', 'serie'),
            # array now???
            'titel_serie': mam_data.get('Dynamic').get('dc_titles').get('serie', ''),
            'titel_episode': mam_data.get('Dynamic').get('dc_titles').get('episode', ''),
            'titel_aflevering': mam_data.get('Dynamic').get('dc_titles').get('aflevering', ''),
            'titel_alternatief': mam_data.get('Dynamic').get('dc_titles').get('alternatief', ''),
            'titel_programma': mam_data.get('Dynamic').get('dc_titles').get('programma', ''),
            'titel_serienummer': mam_data.get('Dynamic').get('dc_titles').get('serienummer', ''),
            'titel_seizoen': mam_data.get('Dynamic').get('dc_titles').get('seizoen', ''),
            'titel_seizoen_nr': mam_data.get('Dynamic').get('dc_titles').get('seizoen_nr', ''),
            'titel_archief': mam_data.get('Dynamic').get('dc_titles').get('archief', ''),
            'titel_deelarchief': mam_data.get('Dynamic').get('dc_titles').get('deelarchief', ''),
            'titel_reeks': mam_data.get('Dynamic').get('dc_titles').get('reeks', ''),
            'titel_deelreeks': mam_data.get('Dynamic').get('dc_titles').get('deelreeks', ''),
            'titel_registratie': mam_data.get('Dynamic').get('dc_titles').get('registratie', ''),
            'description': mam_data.get('Descriptive').get('Description'),
            'avo_beschrijving': avo_beschrijving,
            'ondertitels': mam_data.get('Dynamic').get('dc_description_ondertitels', ''),
            'programma_beschrijving': mam_data.get('Dynamic').get('dc_description_programma', ''),
            'cast': mam_data.get('Dynamic').get('dc_description_cast', ''),
            'transcriptie': mam_data.get('Dynamic').get('dc_description_transcriptie', ''),
            'dc_description_lang': mam_data.get('Dynamic').get('dc_description_lang', ''),
            # is now isodate!
            'created': mam_data.get('Descriptive').get('CreationDate'),
            'dcterms_issued': mam_data.get('Dynamic').get('dcterms_issued'),
            'dcterms_created': mam_data.get('Dynamic').get('dcterms_created'),
            # is now isodate!
            'archived': mam_data.get('Administrative').get('ArchiveDate'),
            'keyframe_edit_url': keyframe_edit_url,
            'video_url': mam_data.get('Internal').get('PathToVideo'),
            'keyframe': mam_data.get('Internal').get('PathToKeyframe'),
            'flowplayer_token': os.environ.get(
                'FLOWPLAYER_TOKEN', 'set_in_secrets'
            ),
            'validation_errors': errors
        }

        print(">>>>>> MAM DATA=", json.dumps(mam_data, indent=2))
        print(">>>>>> MAP RESULT=", json.dumps(result, indent=2))
        return result

    def get_productie_field(self, request_form, field_name, field):
        if f'{field_name}_attribute_' in field:
            fid = field.replace(f'{field_name}_attribute_', '')
            select_val = request_form.get(f'{field_name}_attribute_{fid}')
            input_val = request_form.get(f'{field_name}_value_{fid}')

            return {
                'value': input_val,
                'attribute': select_val,
                'dottedKey': None
            }

    def update_legacy_flag(self, request, mam_data):
        # default waarde voor lom_legacy
        lom_legacy = "true"

        themas = dynamic_array(mam_data, 'lom_thema')
        vakken = dynamic_array(mam_data, 'lom_vak')

        if (themas and vakken and len(themas) > 0 and len(vakken) > 0):
            lom_legacy = "false"

        mam_data = set_property(
            mam_data, 'lom_legacy',
            lom_legacy
        )

        return mam_data

    def form_to_mh(self, request, mam_data):
        """
        convert form metadata hash into json data
        """
        pid = escape(request.form.get('pid'))
        department = escape(escape(request.form.get('department')))

        # fields we can alter+save:
        mam_data = set_property(
            mam_data, 'dc_title',
            request.form.get('ontsluitingstitel')
        )

        mam_data = set_property(
            mam_data, 'dcterms_issued',
            request.form.get('uitzenddatum')
        )

        # deze nog eventjes un-escaped
        mam_data = set_property(
            mam_data, 'dcterms_abstract',
            cleanup_markdown(request.form.get('avo_beschrijving'))
        )

        # array value serie in subsection dc_titles
        mam_data = set_array_property(
            mam_data, 'dc_titles',
            'serie', request.form.get('serie')
        )

        # single select item_type -> lom_learningresourcetype
        mam_data = set_json_array_property(
            mam_data, 'lom_learningresourcetype', 'code',
            request.form.get('lom_type'),
        )

        # multiselect talen -> lom_languages
        mam_data = set_json_array_property(
            mam_data, 'lom_languages', 'code',
            request.form.get('talen'),
        )

        # multiselect item_eindgebruikers -> lom_intendedenduserrole
        mam_data = set_json_array_property(
            mam_data, 'lom_intendedenduserrole', 'code',
            request.form.get('lom1_beoogde_eindgebruiker'),
        )

        # multiselect item_onderwijsniveaus of
        # item_onderwijsnivaus_legacy -> lom_onderwijsniveau
        mam_data = set_json_array_property(
            mam_data, 'lom_onderwijsniveau', 'id',
            request.form.get('lom1_onderwijsniveaus'),
            'Onderwijsniveau'
        )

        # multiselect item_onderwijsgraden of
        # item_onderwijsgraden_legacy -> lom_onderwijsgraad
        mam_data = set_json_array_property(
            mam_data, 'lom_onderwijsgraad', 'id',
            request.form.get('lom1_onderwijsgraden'),
            'Onderwijsgraad'
        )

        # multiselect themas -> lom_thema
        mam_data = set_json_array_property(
            mam_data, 'lom_thema', 'id',
            request.form.get('themas'),
            'Thema'
        )

        # multiselect vakken -> lom_vak
        mam_data = set_json_array_property(
            mam_data, 'lom_vak', 'id',
            request.form.get('vakken'),
            'Vak'
        )

        mam_data = self.update_legacy_flag(request, mam_data)

        # Sleutelwoord(en) trefwoorden -> lom_keywords
        mam_data = set_json_array_property(
            mam_data, 'lom_keywords', 'name',
            request.form.get('trefwoorden'),
            'Sleutelwoord'
        )

        dc_creators = []
        dc_contributors = []
        dc_publishers = []

        for f in request.form:
            creator = self.get_productie_field(request.form, 'prd_maker', f)
            if creator:
                dc_creators.append(creator)

            contributor = self.get_productie_field(
                request.form, 'prd_bijdrager', f)
            if contributor:
                dc_contributors.append(contributor)

            publisher = self.get_productie_field(
                request.form, 'prd_publisher', f)
            if publisher:
                dc_publishers.append(publisher)

        mam_data = set_property(mam_data, 'dc_creators', dc_creators)
        mam_data = set_property(
            mam_data, 'dc_contributors', dc_contributors)
        mam_data = set_property(mam_data, 'dc_publishers', dc_publishers)

        tp = self.form_params(pid, department, mam_data)

        # update publish_item, no extra ajax call needed here
        if request.form.get('publicatiestatus_checked'):
            tp['frontend_metadata']['publish_item'] = True
        else:
            tp['frontend_metadata']['publish_item'] = False

        return tp

    def mh_to_form(self, pid, department, mam_data, validation_errors):
        """
        convert json metadata from MediahavenApi back into a
        python hash for populating the view and do the mapping from mh names to
        wanted names in metadata/edit.html
        """
        # print("DEBUG: mediahaven json_data:\n")
        # print(json.dumps(mam_data, indent=2))

        return self.form_params(pid, department, mam_data, validation_errors)

    def xml_sidecar(self, metadata, tp):
        xml_data = XMLSidecar().metadata_sidecar(metadata, tp)
        fragment_id = metadata['fragmentId']
        external_id = metadata['externalId']

        return fragment_id, external_id, xml_data
