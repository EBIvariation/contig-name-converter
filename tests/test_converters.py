from unittest import TestCase

from converters import AssemblyAccessionConverter, SequenceAccessionConverter


class TestSequenceAccessionConverter(TestCase):

    def setUp(self) -> None:
        self.converter = SequenceAccessionConverter(target_naming_convention='enaSequenceName')

    def test_convert(self):
        assert self.converter.convert('CM025139.1') == 'Y'


class TestAssemblyAccessionConverter(TestCase):

    def test_convert(self):
        converter = AssemblyAccessionConverter(source_assembly='GCA_014441545.1',
                                               source_naming_convention='genbankSequenceName',
                                               target_naming_convention='enaSequenceName')
        assert converter.convert('Scaffold_70;HRSCAF=76_pilon') == 'Y'
