import os
from unittest import TestCase
from unittest.mock import patch

from contig_name_converter.convert_vcf_file import convert_vcf


class TestVCFConverter(TestCase):

    def tearDown(self) -> None:
        file_to_remove = ['test_output.vcf']
        for f in file_to_remove:
            if os.path.exists(f):
               os.remove(f)

    def last_line(self, file_to_check):
        with open(file_to_check) as open_file:
            for line in open_file:
                pass
        return line

    def test_convert_to_ena(self):
        input_file = os.path.join(os.path.dirname(__file__), 'resources/test.vcf')
        target_naming_convention = 'enaSequenceName'
        output_file = 'test_output.vcf'
        convert_vcf(input_file, output_file, target_naming_convention)
        assert os.path.exists(output_file)
        assert self.last_line(output_file).split('\t')[0] == 'Y'

    def test_convert_to_refseq(self):
        input_file = os.path.join(os.path.dirname(__file__), 'resources/test.vcf')
        target_naming_convention = 'refseq'
        output_file = 'test_output.vcf'
        convert_vcf(input_file, output_file, target_naming_convention)
        assert os.path.exists(output_file)
        assert self.last_line(output_file).split('\t')[0] == 'NC_051844.1'

    def test_convert_to_no_change(self):
        input_file = os.path.join(os.path.dirname(__file__), 'resources/test.vcf')
        target_naming_convention = 'genbankSequenceName'
        output_file = 'test_output.vcf'
        with patch('convert_vcf_file.logger.warning') as mock_warn:
            convert_vcf(input_file, output_file, target_naming_convention)
        assert os.path.exists(output_file)
        assert os.path.islink(output_file)
        assert self.last_line(output_file).split('\t')[0] == 'Scaffold_70;HRSCAF=76_pilon'
        mock_warn.assert_called_once_with('There are no difference between the input file naming convention and '
                                          'genbankSequenceName. Will create a symbolic link instead.')

