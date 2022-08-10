from argparse import ArgumentParser

from pysam import VariantFile, VariantHeader

from converters import SequenceAccessionConverter


def strip_quotes(string):
    return string.strip('"')


def convert_vcf(input, output, target_naming_convention):
    input_file = VariantFile(input)
    converter = SequenceAccessionConverter(target_naming_convention)

    contig_name_to_accession = {}
    # Get a new empty header
    output_header = VariantHeader()
    # Fill it with all the values from the input
    for header_rec in input_file.header.records:
        if header_rec.type != 'CONTIG':
            output_header.add_record(header_rec)
            pass
        else:
            accession = strip_quotes(header_rec['accession'])
            contig_name_to_accession[header_rec['ID']] = accession
            all_other_kwargs = dict((k, strip_quotes(v)) for k, v in header_rec.items() if k not in ('ID', 'IDX'))
            output_header.contigs.add(id=converter.convert(accession), **all_other_kwargs)
    output_file = VariantFile(output, 'w', header=output_header)

    for rec in input_file:
        # translate convert the chrom to the new sequence dictionary
        rec.translate(output_header)
        output_file.write(rec)


def main():
    argparse = ArgumentParser(description="Convert sequence/contig names from one convention to another.")
    argparse.add_argument('-i', '--input', help='Input file to convert')
    argparse.add_argument('-o', '--output', help='Output file containing convert the converted data')
    argparse.add_argument('-c', '--convention', help='Contig naming convention use the.',
                          choices=['enaSequenceName', 'genbank', 'genbankSequenceName', 'refseq', 'ucscName'],
                          default='enaSequenceName')

    args = argparse.parse_args()

    convert_vcf(args.input, args.output, target_naming_convention=args.convention)


if __name__ == "__main__":
    main()
