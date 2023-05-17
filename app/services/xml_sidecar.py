#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  app/services/xml_sidecar.py
#
#   This class can generate a xml sidecar for doing updates on metadata for items in
#   mediahaven. With API v2 this class could become deprecated if we have the possibility
#   to do all the wanted updates with json directly.
#

import os
from lxml import etree
from app.services.mh_properties import get_title, dynamic_array


class XMLSidecar:
    def __init__(self):
        self.TESTBEELD_PERM_ID = os.environ.get(
            'TESTBEELD_PERM_ID', 'config_testbeeld_uuid')
        self.ONDERWIJS_PERM_ID = os.environ.get(
            'ONDERWIJS_PERM_ID', 'config_onderwijs_uuid')
        self.ADMIN_PERM_ID = os.environ.get(
            'ADMIN_PERM_ID', 'config_admin_uuid')

    def save_array_field(self, metadata, fieldname, mdprops, field_attrib="multiselect"):
        array_values = metadata['Dynamic'][fieldname]
        array_elem = etree.SubElement(mdprops, fieldname)
        array_elem.set('strategy', 'OVERWRITE')

        # TODO: iterate a different structure like this here:
        # array_values = {
        # 'Onderwijsniveau': [
        #   'https://w3id.org/onderwijs-vlaanderen/id/structuur/volwassenenonderwijs',
        #   'https://w3id.org/onderwijs-vlaanderen/id/structuur/lager-onderwijs',
        #   'https://w3id.org/onderwijs-vlaanderen/id/structuur/secundair-onderwijs'
        # ]
        # }
        return

        if array_values and len(array_values) > 0:
            for kw in array_values:
                etree.SubElement(
                    array_elem, kw['attribute']).text = kw['value']
        else:
            etree.SubElement(array_elem, field_attrib).text = ''

    def sidecar_root(self):
        MH_NS = 'https://zeticon.mediahaven.com/metadata/20.3/mh/'
        MHS_NS = 'https://zeticon.mediahaven.com/metadata/20.3/mhs/'
        XSI_NS = 'http://www.w3.org/2001/XMLSchema-instance'  # version="20.3"

        schema_loc = etree.QName(
            "http://www.w3.org/2001/XMLSchema-instance", "schemaLocation")
        zeticon_mhs = 'https://zeticon.mediahaven.com/metadata/20.3/mhs/'
        zeticon_mhs_xsd = 'https://zeticon.mediahaven.com/metadata/20.3/mhs.xsd'
        zeticon_mh = 'https://zeticon.mediahaven.com/metadata/20.3/mh/'
        zeticon_mh_xsd = 'https://zeticon.mediahaven.com/metadata/20.3/mh.xsd'
        XSI_LOC = f"{zeticon_mhs} {zeticon_mhs_xsd} {zeticon_mh} {zeticon_mh_xsd}"

        NSMAP = {
            'mh': MH_NS,
            'mhs': MHS_NS,
            'xsi': XSI_NS
        }

        root = etree.Element(
            "{%s}Sidecar" % MHS_NS,
            {
                'version': '20.3',
                schema_loc: XSI_LOC
            },
            nsmap=NSMAP
        )

        return root, MH_NS, MHS_NS, XSI_NS

    def metadata_sidecar(self, metadata, tp):
        root, MH_NS, MHS_NS, XSI_NS = self.sidecar_root()
        rights = etree.SubElement(root, '{%s}RightsManagement' % MHS_NS)

        perms = etree.SubElement(rights, '{%s}Permissions' % MH_NS)
        perms.set('strategy', 'OVERWRITE')

        # now set our permissions and exclude the ONDERWIJS_PERM_ID
        # when publish_item is not set
        etree.SubElement(perms, '{%s}Read' %
                         MH_NS).text = self.TESTBEELD_PERM_ID
        etree.SubElement(perms, '{%s}Read' % MH_NS).text = self.ADMIN_PERM_ID

        if tp.get('frontend_metadata').get('publish_item'):
            etree.SubElement(perms, '{%s}Read' %
                             MH_NS).text = self.ONDERWIJS_PERM_ID
            print(
                "publicatiestatus == TRUE, added read permission =",
                self.ONDERWIJS_PERM_ID
            )

        else:
            print("publicatiestatus== FALSE")

        etree.SubElement(perms, '{%s}Write' %
                         MH_NS).text = self.TESTBEELD_PERM_ID
        etree.SubElement(perms, '{%s}Write' % MH_NS).text = self.ADMIN_PERM_ID
        etree.SubElement(perms, '{%s}Export' %
                         MH_NS).text = self.TESTBEELD_PERM_ID
        etree.SubElement(perms, '{%s}Export' % MH_NS).text = self.ADMIN_PERM_ID

        mdprops = etree.SubElement(root, "{%s}Dynamic" % MHS_NS)

        # Alemene fields:
        # ===============
        # ontsluitingstitel
        etree.SubElement(
            mdprops, "dc_title").text = metadata['Dynamic']['dc_title']

        # uizenddatum
        etree.SubElement(
            mdprops, "dcterms_issued").text = metadata['Dynamic']['dcterms_issued']

        # serie
        dc_titles = etree.SubElement(mdprops, "dc_titles")
        dc_titles.set('strategy', 'OVERWRITE')
        etree.SubElement(dc_titles, "serie").text = get_title(
            metadata, 'serie')

        # Inhoud fields:
        # ==============
        # avo_beschrijving
        etree.SubElement(
            mdprops, "dcterms_abstract").text = metadata['Dynamic']['dcterms_abstract']

        # Productie fields:
        # =================
        # dc_creators
        dc_creators = etree.SubElement(mdprops, "dc_creators")
        dc_creators.set('strategy', 'OVERWRITE')
        for entry in dynamic_array(metadata, 'dc_creators'):
            etree.SubElement(
                dc_creators, entry['attribute']).text = entry['value']

        # dc_contributors
        dc_creators = etree.SubElement(mdprops, "dc_contributors")
        dc_creators.set('strategy', 'OVERWRITE')
        for entry in dynamic_array(metadata, 'dc_contributors'):
            etree.SubElement(
                dc_creators, entry['attribute']).text = entry['value']

        # dc_publishers
        dc_creators = etree.SubElement(mdprops, "dc_publishers")
        dc_creators.set('strategy', 'OVERWRITE')
        for entry in dynamic_array(metadata, 'dc_publishers'):
            etree.SubElement(
                dc_creators, entry['attribute']).text = entry['value']

        # Leerobject fields:
        # ==================
        # lom_type -> lom_learningresourcetype (Audio/Video)
        lom_type = etree.SubElement(mdprops, "lom_learningresourcetype")
        lom_type.set('strategy', 'OVERWRITE')
        for kw in dynamic_array(metadata, 'lom_learningresourcetype'):
            etree.SubElement(lom_type, kw['attribute']).text = kw['value']

        # eindgebruiker is multiselect
        lom_languages = etree.SubElement(mdprops, "lom_intendedenduserrole")
        lom_languages.set('strategy', 'OVERWRITE')
        for kw in dynamic_array(metadata, 'lom_intendedenduserrole'):
            etree.SubElement(lom_languages, kw['attribute']).text = kw['value']

        # talen are multiselect
        lom_languages = etree.SubElement(mdprops, "lom_languages")
        lom_languages.set('strategy', 'OVERWRITE')
        for kw in dynamic_array(metadata, 'lom_languages'):
            etree.SubElement(lom_languages, kw['attribute']).text = kw['value']

        # TODO: save_array_field needs refactor here!
        # lom_onderwijsniveau is like keywords (onderwijsniveau)
        self.save_array_field(
            metadata, "lom_onderwijsniveau", mdprops, "Onderwijsniveau")

        # lom_onderwijsgraad is like keywords
        self.save_array_field(
            metadata, "lom_onderwijsgraad", mdprops, "Onderwijsgraad")

        # themas are like keywords (in future might be multiselect)
        self.save_array_field(metadata, "lom_thema", mdprops, "Thema")

        # vakken are multiselect but like keywords
        self.save_array_field(metadata, "lom_vak", mdprops, "Vak")

        # lom_legacy "false" indien vakken + themas ingevuld
        etree.SubElement(
            mdprops, "lom_legacy").text = metadata['Dynamic']['lom_legacy']

        # trefwoorden / keywords are 'Sleutelwoord'
        self.save_array_field(metadata, "lom_keywords",
                              mdprops, "Sleutelwoord")

        xml_data = etree.tostring(
            root, pretty_print=True, encoding="UTF-8", xml_declaration=True
        ).decode()

        return xml_data

    def subtitle_sidecar(self, metadata, tp):
        cp_id = metadata['Dynamic']['CP_id']
        cp = metadata['Dynamic']['CP']
        xml_pid = f"{tp['pid']}_{tp['subtitle_type']}"

        root, MH_NS, MHS_NS, XSI_NS = self.sidecar_root()

        descriptive = etree.SubElement(root, '{%s}Descriptive' % MHS_NS)
        etree.SubElement(descriptive, '{%s}Title' %
                         MH_NS).text = tp['srt_file']
        description = f"Subtitles for item {tp['pid']}"
        etree.SubElement(
            descriptive, '{%s}Description' % MH_NS).text = description

        rights = etree.SubElement(
            root, '{%s}RightsManagement' % MHS_NS)  # of Structural?
        permissions = etree.SubElement(rights, '{%s}Permissions' % MH_NS)
        etree.SubElement(permissions, '{%s}Read' %
                         MH_NS).text = self.TESTBEELD_PERM_ID
        etree.SubElement(permissions, '{%s}Read' %
                         MH_NS).text = self.ONDERWIJS_PERM_ID
        etree.SubElement(permissions, '{%s}Read' %
                         MH_NS).text = self.ADMIN_PERM_ID
        etree.SubElement(permissions, '{%s}Write' %
                         MH_NS).text = self.TESTBEELD_PERM_ID
        etree.SubElement(permissions, '{%s}Write' %
                         MH_NS).text = self.ADMIN_PERM_ID
        etree.SubElement(permissions, '{%s}Export' %
                         MH_NS).text = self.TESTBEELD_PERM_ID
        etree.SubElement(permissions, '{%s}Export' %
                         MH_NS).text = self.ADMIN_PERM_ID

        mdprops = etree.SubElement(root, "{%s}Dynamic" % MHS_NS)

        # set is_verwant_aan needs overwrite strategy and is needed for new items
        relations = etree.SubElement(mdprops, "dc_relations")
        relations.set('strategy', 'OVERWRITE')
        etree.SubElement(relations, "is_verwant_aan").text = tp['pid']

        etree.SubElement(mdprops, "CP_id").text = cp_id
        # mediahaven computes external_id for us.
        # etree.SubElement(mdprops, "external_id").text = xml_pid
        etree.SubElement(mdprops, "PID").text = xml_pid
        etree.SubElement(mdprops, "CP").text = cp
        etree.SubElement(mdprops, "sp_name").text = 'borndigital'

        xml_data = etree.tostring(
            root, pretty_print=True, encoding="UTF-8", xml_declaration=True
        ).decode()

        return xml_data
