#!/usr/bin/env python
'''
Takes a PREMIS CSV file, as generated by premiscsv.py, and transform into XML.
'''
import sys
import argparse
from lxml import etree
import ififuncs


def write_premis(doc, premisxml):
    '''
    Writes the PREMIS object to a file.
    '''
    with open(premisxml, 'w') as out_file:
        doc.write(out_file, pretty_print=True)


def create_unit(index, parent, unitname):
    '''
    Helper function that adds an XML element.
    '''
    premis_namespace = "http://www.loc.gov/premis/v3"
    unitname = etree.Element("{%s}%s" % (premis_namespace, unitname))
    parent.insert(index, unitname)
    return unitname


def setup_xml():
    '''
    This should just create the PREMIS lxml object.
    Actual metadata generation should be moved to other functions.
    '''
    namespace = '<premis:premis xmlns:premis="http://www.loc.gov/premis/v3" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.loc.gov/premis/v3 https://www.loc.gov/standards/premis/premis.xsd" version="3.0"></premis:premis>'
    premis = etree.fromstring(namespace)
    return premis


def describe_objects(premis, object_dictionaries):
    '''
    Converts the CSV object metadata into PREMIS XML.
    '''
    xsi_namespace = "http://www.w3.org/2001/XMLSchema-instance"
    for objects in object_dictionaries:
        id_list = objects['objectIdentifier'].replace(
            '[', ''
        ).replace(']', '').replace('\'', '').split(', ')
        object_parent = create_unit(
            0, premis, 'object'
        )
        object_parent.attrib[
            "{%s}type" % xsi_namespace
        ] = "premis:%s" % objects['objectCategory']
        object_identifier_uuid = create_unit(
            2, object_parent, 'objectIdentifier'
        )
        object_identifier_uuid_type = create_unit(
            1, object_identifier_uuid, 'objectIdentifierType'
        )
        object_identifier_uuid_value = create_unit(
            2, object_identifier_uuid, 'objectIdentifierValue'
        )
        object_identifier_uuid_type.text = id_list[0]
        object_identifier_uuid_value.text = id_list[1]
        if objects['objectCategory'] == 'file':
            object_characteristics = create_unit(
                5, object_parent, 'objectCharacteristics'
            )
            storage = create_unit(
                7, object_parent, 'storage'
            )
            content_location = create_unit(
                0, storage, 'contentLocation'
            )
            content_location_type = create_unit(
                0, content_location, 'contentLocationType'
            )
            content_location_value = create_unit(
                1, content_location, 'contentLocationValue'
            )
            fixity = create_unit(
                0, object_characteristics, 'fixity'
            )
            size = create_unit(
                1, object_characteristics, 'size'
            )
            format_ = create_unit(
                2, object_characteristics, 'format'
            )
            format_registry = create_unit(
                1, format_, 'formatRegistry'
            )
            format_registry_name = create_unit(
                0, format_registry, 'formatRegistryName'
            )
            format_registry_key = create_unit(
                1, format_registry, 'formatRegistryKey'
            )
            format_registry_role = create_unit(
                2, format_registry, 'formatRegistryRole'
            )
            size.text = objects['size']
            message_digest_algorithm = create_unit(
                0, fixity, 'messageDigestAlgorithm'
            )
            message_digest = create_unit(
                1, fixity, 'messageDigest'
            )
            message_digest_originator = create_unit(
                2, fixity, 'messageDigestOriginator'
            )
            message_digest_originator.text = objects['messageDigestOriginator']
            message_digest.text = objects['messageDigest']
            message_digest_algorithm.text = objects['messageDigestAlgorithm']
            format_registry_name.text = objects['formatRegistryName']
            format_registry_key.text = objects['formatRegistryKey']
            format_registry_role.text = objects['formatRegistryRole']
            content_location_type.text = objects['contentLocationType']
            content_location_value.text = objects['contentLocationValue']
        linked_events = objects['linkingEventIdentifierValue'].split('|')
        for event in linked_events:
            if event != '':
                linking_event_identifier = create_unit(
                    99, object_parent, 'linkingEventIdentifier'
                )
                linking_event_identifier_type = create_unit(
                    1, linking_event_identifier, 'linkingEventIdentifierType'
                )
                linking_event_identifier_value = create_unit(
                    2, linking_event_identifier, 'linkingEventIdentifierValue'
                )
                linking_event_identifier_type.text = 'UUID'
                linking_event_identifier_value.text = event
    return premis


def describe_events(premis, event_dictionaries):
    '''
    Converts the CSV object metadata into PREMIS XML.
    '''
    for x in event_dictionaries:
        event_parent = create_unit(
            99, premis, 'event'
        )
        event_identifier_uuid = create_unit(
            1, event_parent, 'eventIdentifier'
        )
        event_identifier_uuid_type = create_unit(
            1, event_identifier_uuid, 'eventIdentifierType'
        )
        event_identifier_uuid_value = create_unit(
            2, event_identifier_uuid, 'eventIdentifierValue'
        )
        event_type = create_unit(
            1, event_parent, 'eventType'
        )
        event_date_time = create_unit(
            2, event_parent, 'eventDateTime'
        )
        event_detail_information = create_unit(
            3, event_parent, 'eventDetailInformation'
        )
        event_detail = create_unit(
            1, event_detail_information, 'eventDetail'
        )
        event_outcome_information = create_unit(
            4, event_parent, 'eventOutcomeInformation'
        )
        event_outcome = create_unit(
            1, event_outcome_information, 'eventOutcome'
        )
        event_outcome_detail = create_unit(
            2, event_outcome_information, 'eventOutcomeDetail'
        )
        event_outcome_detail_note = create_unit(
            1, event_outcome_detail, 'eventOutcomeDetailNote'
        )
        event_identifier_uuid_type.text = x['eventIdentifierType']
        event_identifier_uuid_value.text = x['eventIdentifierValue']
        event_type.text = x['eventType']
        event_date_time.text = x['eventDateTime']
        event_detail.text = x['eventDetail']
        event_outcome.text = x['eventOutcome']
        event_outcome_detail_note.text = x['eventOutcomeDetailNote']
    print(etree.tostring(premis, pretty_print=True))


def parse_args(args_):
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Converts PREMIS CSV to XML'
        ' Written by Kieran O\'Leary.'
    )
    parser.add_argument(
        '-i',
        help='full path of objects csv', required=True
    )
    parser.add_argument(
        '-ev',
        help='full path of events csv', required=True
    )
    parser.add_argument(
        '-user',
        help='Declare who you are. If this is not set, you will be prompted.'
    )
    parsed_args = parser.parse_args(args_)
    return parsed_args


def main(args_):
    '''
    Launches all the other functions when run from the command line.
    For debugging purposes, the contents of the CSV is printed to screen.
    '''
    args = parse_args(args_)
    csv_file = args.i
    events_csv = args.ev
    object_dictionaries = ififuncs.extract_metadata(csv_file)
    event_dictionaries = ififuncs.extract_metadata(events_csv)
    premis = setup_xml()
    premis = describe_objects(premis, object_dictionaries)
    describe_events(premis, event_dictionaries)


if __name__ == '__main__':
    main(sys.argv[1:])