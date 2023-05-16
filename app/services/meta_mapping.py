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
        item_type_lom = get_md_array(mam_data, 'lom_learningresourcetype')
        if item_type_lom and len(item_type_lom) > 0:
            item_type = item_type_lom[0]['value']

        return {
            'pid': pid,
            'department': department,
            'item_type': item_type,
            'item_languages': get_md_array(mam_data, 'lom_languages'),
            'item_eindgebruikers': get_md_array(mam_data, 'lom_intendedenduserrole'),
            'item_themas': get_md_array(mam_data, 'lom_thema'),
            'item_vakken': get_md_array(mam_data, 'lom_vak'),
            'item_vakken_legacy': get_md_array(mam_data, 'lom_classification'),
            'item_onderwijsniveaus': get_md_array(
                mam_data,
                'lom_onderwijsniveau',
                legacy_fallback=True
            ),
            'item_onderwijsniveaus_legacy': get_md_array(
                mam_data, 'lom_context'),
            'item_onderwijsgraden': get_md_array(
                mam_data,
                'lom_onderwijsgraad',
                legacy_fallback=True
            ),
            'item_onderwijsgraden_legacy': get_md_array(
                mam_data,
                'lom_typicalagerange'
            ),
            'item_keywords': get_md_array(mam_data, 'lom_keywords'),
            'item_keywords_cp': get_md_array(mam_data, 'dc_subjects'),
            # TODO: later fetch directly after v2 refactor
            'publish_item': 'ajax'  # signal ajax request to frontend
        }

    def form_params(self, pid, department, mam_data, errors=[]):
        dc_description_lang = get_property(mam_data, 'dc_description_lang')
        ondertitels = get_property(mam_data, 'dc_description_ondertitels')
        cast = get_property(mam_data, 'dc_description_cast')
        transcriptie = get_property(mam_data, 'dc_description_transcriptie')

        keyframe_edit_url = '{}{}'.format(
            os.environ.get('KEYFRAME_EDITING_LINK',
                           'https://set_in_secrets?id='),
            mam_data['Internal']['FragmentId']
        )

        item_type = mam_data.get('type')
        item_type_lom = get_md_array(mam_data, 'lom_learningresourcetype')
        if item_type_lom and len(item_type_lom) > 0:
            item_type = item_type_lom[0]['value']

        dcterms_abstract = get_property(mam_data, 'dcterms_abstract')
        avo_beschrijving = markdown_to_html(dcterms_abstract)

        return {
            'department': department,
            'mam_data': json.dumps(mam_data),
            'publish_item': False,
            'original_cp': get_property(mam_data, 'Original_CP'),
            'makers': get_md_array(mam_data, 'dc_creators'),
            'maker_options': self.MAKER_OPTIONS,
            'contributors': get_md_array(mam_data, 'dc_contributors'),
            'contributor_options': self.CONTRIBUTOR_OPTIONS,
            'publishers': get_md_array(mam_data, 'dc_publishers'),
            'publisher_options': self.PUBLISHER_OPTIONS,
            'item_type': item_type,
            'frontend_metadata': self.frontend_metadata(pid, department, mam_data),
            'dc_identifier_localid': get_property(mam_data, 'dc_identifier_localid'),
            'keyframe': mam_data.get('previewImagePath'),
            'pid': pid,
            'title': mam_data.get('title'),
            'ontsluitingstitel': get_property(mam_data, 'dc_title'),

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
            'description': mam_data.get('description'),
            'avo_beschrijving': avo_beschrijving,
            'ondertitels': ondertitels,
            'programma_beschrijving': get_property(mam_data, 'dc_description_programma'),
            'cast': cast,
            'transcriptie': transcriptie,
            'dc_description_lang': dc_description_lang,  # orig uitgebr. beschr
            'created': get_property(mam_data, 'CreationDate'),
            'dcterms_issued': get_property(mam_data, 'dcterms_issued'),
            # not used in form yet?
            'dcterms_created': get_property(mam_data, 'dcterms_created'),
            'archived': get_property(mam_data, 'created_on'),
            'keyframe_edit_url': keyframe_edit_url,
            # for v2 mam_data['Internal']['PathToVideo']
            'video_url': mam_data.get('videoPath'),
            'flowplayer_token': os.environ.get(
                'FLOWPLAYER_TOKEN', 'set_in_secrets'
            ),
            'validation_errors': errors
        }

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

        themas = get_md_array(mam_data, 'lom_thema')
        vakken = get_md_array(mam_data, 'lom_vak')

        if(themas and vakken and len(themas) > 0 and len(vakken) > 0):
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
