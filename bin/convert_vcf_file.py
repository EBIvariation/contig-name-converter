#!/bin/env python

from argparse import ArgumentParser

from ebi_eva_common_pyutils.logger import logging_config

from contig_name_converter.convert_vcf_file import convert_vcf

logger = logging_config.get_logger(__name__)


def main():
    argparse = ArgumentParser(description="Convert sequence/contig names from one convention to another.")
    argparse.add_argument('-i', '--input', help='Input file to convert')
    argparse.add_argument('-o', '--output', help='Output file containing convert the converted data')
    argparse.add_argument('-c', '--convention', help='Contig naming convention use the.',
                          choices=['enaSequenceName', 'genbank', 'genbankSequenceName', 'refseq', 'ucscName'],
                          default='enaSequenceName')

    args = argparse.parse_args()
    logging_config.add_stdout_handler()

    convert_vcf(args.input, args.output, target_naming_convention=args.convention)


if __name__ == "__main__":
    main()
