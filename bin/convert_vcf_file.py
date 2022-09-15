#!/bin/env python

from argparse import ArgumentParser

from ebi_eva_common_pyutils.logger import logging_config

from contig_name_converter.convert_vcf_file import convert_vcf
from contig_name_converter.converters import supported_conventions

logger = logging_config.get_logger(__name__)


def main():
    argparse = ArgumentParser(description="Convert sequence/contig names from a naming convention to another using "
                                          "stored in the accession provided in the header")
    argparse.add_argument('-i', '--input', help='Input file to convert')
    argparse.add_argument('-o', '--output', help='Output file containing the converted data')
    argparse.add_argument('-c', '--convention', help='Contig naming convention to use',
                          choices=supported_conventions,
                          default='enaSequenceName')
    argparse.add_argument('-u', '--contig_alias_url', help='URL used to contact the contig alias web service',
                          default='https://www.ebi.ac.uk/eva/webservices/contig-alias/')

    args = argparse.parse_args()
    logging_config.add_stdout_handler()

    convert_vcf(args.input, args.output, target_naming_convention=args.convention,
                contig_alias_url=args.contig_alias_url)


if __name__ == "__main__":
    main()
