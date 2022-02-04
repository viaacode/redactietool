#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  app/services/meta_mapping.py
#
#   Do mapping between redactietool form and mh target data for saving changes.
#   Similarly load json data from MediahavenApi and populate form back.
#   it also has a member to create the xml sidecar data by using the MetaSidecar class
#
import json
import os
import markdown2
from viaa.configuration import ConfigParser
from viaa.observability import logging
from app.services.subtitle_files import get_property, get_array_property, get_md_array
from app.services.meta_sidecar import MetaSidecar
from markupsafe import escape

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

    def set_property(self, mam_data, propkey, propvalue):
        for prop in mam_data['mdProperties']:
            if prop.get('attribute') == propkey:
                prop['value'] = propvalue
                return mam_data

        # if we get here. we need to add a new property as it was cleared and
        # is not present anymore
        mam_data['mdProperties'].append({
            'value': propvalue,
            'attribute': propkey,
            'dottedKey': None
        })

        return mam_data

    def set_json_array_property(self, mam_data, propkey, jkey, jvalue, prop_name="multiselect"):
        values = json.loads(jvalue)
        array_values = []
        for v in values:
            array_values.append({
                'value': v[jkey],
                'attribute': prop_name,
                'dottedKey': None
            })

        # print("set_json_array values=", array_values, "prop_name", prop_name)

        for prop in mam_data['mdProperties']:
            if prop.get('attribute') == propkey:
                prop['value'] = array_values
                return mam_data

        mh_prop = {
            'value': array_values,
            'attribute': propkey,
            'dottedKey': None
        }

        # extra subKey to set here
        if prop_name == 'multiselect':
            mh_prop['subKey'] = 'multiselect'

        mam_data['mdProperties'].append(mh_prop)
        return mam_data

    def set_array_property(self, mam_data, attribute, array_attribute, propvalue):
        props = mam_data.get('mdProperties', [])
        array_attrib_exists = False
        array_prop = None
        for prop in props:
            if prop.get('attribute') == attribute:
                array_prop = prop
                array_values = prop.get('value', '')
                for att in array_values:
                    if att.get('attribute') == array_attribute:
                        array_attrib_exists = True
                        att['value'] = propvalue
                        return mam_data

        if not array_prop:
            array_val = [{
                'value': propvalue,
                'attribute': array_attribute,
                'dottedKey': None
            }]
            array_prop = {
                'attribute': attribute,
                'dottedKey': None,
                'value': array_val
            }
            mam_data['mdProperties'].append(array_prop)
            return mam_data

        if array_prop and not array_attrib_exists:
            array_prop['value'].append({
                'value': propvalue,
                'attribute': array_attribute,
                'dottedKey': None
            })
            return mam_data

        # in case it's new array prop (bail out for now):
        print(
            "ERROR in set_array_property: {}/{} with value {} not saved!".format(
                attribute,
                array_attribute,
                propvalue
            )
        )

        return mam_data

    def unescape_tag(self, content, tag):
        content = content.replace(f'&lt;{tag}&gt;', f'<{tag}>')
        content = content.replace(f'&lt;/{tag}&gt;', f'</{tag}>')
        return content

    def secure_unescape(self, html_content):
        safe_content = str(escape(html_content))
        safe_content = self.unescape_tag(safe_content, 'p')
        safe_content = self.unescape_tag(safe_content, 'h2')
        safe_content = self.unescape_tag(safe_content, 'br')
        safe_content = self.unescape_tag(safe_content, 'strong')
        safe_content = self.unescape_tag(safe_content, 'em')
        safe_content = self.unescape_tag(safe_content, 'u')

        # editor also supports lists
        safe_content = self.unescape_tag(safe_content, 'ol')
        safe_content = self.unescape_tag(safe_content, 'ul')
        safe_content = self.unescape_tag(safe_content, 'li')

        # sanitize a href tags and add target = _blank
        safe_content = safe_content.replace("&lt;a href=&#34;", '<a href="')

        # href tag escaping in case of html edit mode:
        # safe_content = safe_content.replace(
        #     '&#34; target=&#34;_blank&#34;&gt;',
        #     '" target="_blank">'
        # )

        # href tags in markdown mode:
        safe_content = safe_content.replace("&lt;a href=&#34;", '<a href="')
        safe_content = safe_content.replace(
            '&#34;&gt;',
            '" target="_blank">'
        )
        safe_content = safe_content.replace('&lt;/a&gt;', '</a>')

        # allow regular < and > to still work
        safe_content = safe_content.replace("&amp;lt;", "&lt;")
        safe_content = safe_content.replace("&amp;gt;", "&gt;")
        safe_content = safe_content.replace("&lt;br&gt;", "<br>")

        return safe_content

    def markdown_to_html(self, markdown_content):
        markdown_text = self.cleanup_markdown(markdown_content)
        html_content = markdown2.markdown(markdown_text)
        html_content = html_content.replace("\n\n", "<br>")
        html_content = html_content.replace("\n", "")
        return self.secure_unescape(html_content)

    def cleanup_markdown(self, markdown_text):
        markdown_text = markdown_text.replace("&#13;\n", "").replace("\r", "")
        return markdown_text

    def form_params(self, token, pid, department, mam_data, errors=[]):
        dc_description_lang = get_property(mam_data, 'dc_description_lang')
        ondertitels = get_property(mam_data, 'dc_description_ondertitels')
        cast = get_property(mam_data, 'dc_description_cast')
        transcriptie = get_property(mam_data, 'dc_description_transcriptie')

        keyframe_edit_url = '{}{}'.format(
            os.environ.get('KEYFRAME_EDITING_LINK',
                           'https://set_in_secrets?id='),
            mam_data['fragmentId']
        )

        item_type = mam_data.get('type')
        item_type_lom = get_md_array(mam_data, 'lom_learningresourcetype')
        if item_type_lom and len(item_type_lom) > 0:
            item_type = item_type_lom[0]['value']

        dcterms_abstract = get_property(mam_data, 'dcterms_abstract')
        avo_beschrijving = self.markdown_to_html(dcterms_abstract)

        return {
            'token': token,
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
            'item_themas': json.dumps(get_md_array(mam_data, 'lom_thema')),
            'item_vakken': json.dumps(get_md_array(mam_data, 'lom_vak')),
            'item_vakken_legacy': json.dumps(get_md_array(mam_data, 'lom_classification')),
            'item_languages': json.dumps(get_md_array(mam_data, 'lom_languages')),
            'item_eindgebruikers': json.dumps(get_md_array(mam_data, 'lom_intendedenduserrole')),
            'item_onderwijsniveaus': json.dumps(
                get_md_array(
                    mam_data,
                    'lom_onderwijsniveau',
                    legacy_fallback=True
                )
            ),
            'item_onderwijsniveaus_legacy': json.dumps(get_md_array(mam_data, 'lom_context')),
            'item_onderwijsgraden': json.dumps(
                get_md_array(
                    mam_data,
                    'lom_onderwijsgraad',
                    legacy_fallback=True
                )
            ),
            'item_onderwijsgraden_legacy': json.dumps(get_md_array(mam_data, 'lom_typicalagerange')),
            'item_keywords_cp': json.dumps(get_md_array(mam_data, 'dc_subjects')),
            'item_keywords': json.dumps(get_md_array(mam_data, 'lom_keywords')),
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
        # na optimalisatie is momenteel
        # legacy vakken ( lom_classification )
        # niet nodig voor deze check zie DEV-1881
        # default waarde voor lom_legacy
        lom_legacy = "true"

        themas = get_md_array(mam_data, 'lom_thema')
        vakken = get_md_array(mam_data, 'lom_vak')

        if(themas and vakken and len(themas) > 0 and len(vakken) > 0):
            lom_legacy = "false"

        mam_data = self.set_property(
            mam_data, 'lom_legacy',
            lom_legacy
        )

        return mam_data

    def form_to_mh(self, request, mam_data):
        """
        convert form metadata hash into json data
        """
        # print("DEBUG form metadata:\n", request.form)
        # logic and checks here that can generate errors, warnings etc.

        pid = escape(request.form.get('pid'))
        token = escape(request.form.get('token'))
        department = escape(escape(request.form.get('department')))

        # fields we can alter+save:
        mam_data = self.set_property(
            mam_data, 'dc_title',
            request.form.get('ontsluitingstitel')
        )

        mam_data = self.set_property(
            mam_data, 'dcterms_issued',
            request.form.get('uitzenddatum')
        )

        # deze nog eventjes un-escaped
        mam_data = self.set_property(
            mam_data, 'dcterms_abstract',
            self.cleanup_markdown(request.form.get('avo_beschrijving'))
        )

        # array value serie in subsection dc_titles
        # (this is also how we need to save our productie section values soon!!!)
        mam_data = self.set_array_property(
            mam_data, 'dc_titles',
            'serie', request.form.get('serie')
        )

        # single select item_type -> lom_learningresourcetype
        mam_data = self.set_json_array_property(
            mam_data, 'lom_learningresourcetype', 'code',
            request.form.get('lom_type'),
        )

        # multiselect talen -> lom_languages
        mam_data = self.set_json_array_property(
            mam_data, 'lom_languages', 'code',
            request.form.get('talen'),
        )

        # multiselect item_eindgebruikers -> lom_intendedenduserrole
        mam_data = self.set_json_array_property(
            mam_data, 'lom_intendedenduserrole', 'code',
            request.form.get('lom1_beoogde_eindgebruiker'),
        )

        # multiselect item_onderwijsniveaus of item_onderwijsnivaus_legacy -> lom_onderwijsniveau
        mam_data = self.set_json_array_property(
            mam_data, 'lom_onderwijsniveau', 'id',
            request.form.get('lom1_onderwijsniveaus'),
            'Onderwijsniveau'
        )

        # multiselect item_onderwijsgraden of item_onderwijsgraden_legacy -> lom_onderwijsgraad
        mam_data = self.set_json_array_property(
            mam_data, 'lom_onderwijsgraad', 'id',
            request.form.get('lom1_onderwijsgraden'),
            'Onderwijsgraad'
        )

        # multiselect themas -> lom_thema
        mam_data = self.set_json_array_property(
            mam_data, 'lom_thema', 'id',
            request.form.get('themas'),
            'Thema'
        )

        # multiselect vakken -> lom_vak
        mam_data = self.set_json_array_property(
            mam_data, 'lom_vak', 'id',
            request.form.get('vakken'),
            'Vak'
        )

        mam_data = self.update_legacy_flag(request, mam_data)

        # Sleutelwoord(en) trefwoorden -> lom_keywords
        mam_data = self.set_json_array_property(
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

        mam_data = self.set_property(mam_data, 'dc_creators', dc_creators)
        mam_data = self.set_property(
            mam_data, 'dc_contributors', dc_contributors)
        mam_data = self.set_property(mam_data, 'dc_publishers', dc_publishers)

        tp = self.form_params(token, pid, department, mam_data)

        if request.form.get('publicatiestatus_checked'):
            tp['publish_item'] = True
        else:
            tp['publish_item'] = False

        return tp

    def mh_to_form(self, token, pid, department, mam_data, validation_errors):
        """
        convert json metadata from MediahavenApi back into a
        python hash for populating the view and do the mapping from mh names to
        wanted names in metadata/edit.html
        """
        # print("DEBUG: mediahaven json_data:\n")
        # print(json.dumps(mam_data, indent=2))

        return self.form_params(token, pid, department, mam_data, validation_errors)

    def xml_sidecar(self, metadata, tp):
        sidecar = MetaSidecar()
        xml_data = sidecar.generate(metadata, tp)
        fragment_id = metadata['fragmentId']
        external_id = metadata['externalId']

        return fragment_id, external_id, xml_data