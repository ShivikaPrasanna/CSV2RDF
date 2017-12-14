#!/usr/bin/env python3
#  -*- coding: UTF-8 -*-
'''
Create an RDF vocabulary from literal RDF values
'''
import argparse

import logging

from rdflib import *
from rdflib.namespace import SKOS
from slugify import slugify

logging.basicConfig(filename='vocab.log', filemode='a', level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

log = logging.getLogger(__name__)


def vocabularize(graph, namespace):
    """
    Transform literal values into a RDF flat RDF vocabulary. Splits values by '/'.

    :return:
    """
    output = Graph()
    vocab = Graph()

    log.debug('Starting vocabulary creation')

    for (sub, obj) in graph.subject_objects(URIRef(args.property)):
        for value in [occ.strip().lower() for occ in str(obj).split('/')]:

            new_obj = namespace[slugify(value)]  # TODO: Take into account slugified duplicates
            output.add((sub, URIRef(args.tproperty), new_obj))
            vocab.add((new_obj, RDF.type, URIRef(args.tclass)))
            vocab.add((new_obj, SKOS.prefLabel, Literal(value, lang="fi")))

    log.debug('Vocabulary creation finished')
    return output, vocab


if __name__ == '__main__':

    argparser = argparse.ArgumentParser(description="Create flat ontology based on input file and property",
                                        fromfile_prefix_chars='@')

    argparser.add_argument("input", help="Input RDF data file")
    argparser.add_argument("output", help="Output RDF data file")
    argparser.add_argument("output_schema", help="Output RDF schema file")
    argparser.add_argument("property", metavar="SOURCE_PROPERTY", help="Property used in input file")
    argparser.add_argument("tproperty", metavar="TARGET_PROPERTY", help="Target property for output file")
    argparser.add_argument("tclass", metavar="TARGET_CLASS", help="Target class for target property values")
    argparser.add_argument("tnamespace", metavar="TARGET_NAMESPACE", help="Namespace for target values")

    argparser.add_argument("--remove", dest='remove', action='store_true', default=False,
                           help="Remove original property triples")

    argparser.add_argument("--format", default='turtle', type=str, help="Format of RDF files [default: turtle]")

    argparser.add_argument("--mapping", metavar='FILE', type=str,
                           help="File containing value mappings (Not implemented)")

    args = argparser.parse_args()

    ns_target = Namespace(args.tnamespace)
    input_graph = Graph().parse(args.input, format=args.format)

    log.debug('Parsed input file')

    annotations, vocabulary = vocabularize(input_graph, ns_target)

    annotations.serialize(format=args.format, destination=args.output)
    vocabulary.serialize(format=args.format, destination=args.output_schema)

    log.debug('Serialized output files')
