import requests
from retry import retry


supported_conventions = {'insdc', 'refseq', 'enaSequenceName', 'genbankSequenceName', 'ucscName'}


class SequenceAccessionConverter:
    """Converter that needs to receive the INSDC contig accession that can uniquely identify the sequence to
    translate the contig name"""
    _contig_alias_url = 'https://www.ebi.ac.uk/eva/webservices/contig-alias/'

    def __init__(self, target_naming_convention, contig_alias_url=None):
        assert target_naming_convention in supported_conventions, \
            f'The target naming convention {target_naming_convention} is not on of the supported ones ' \
            f'{", ".join(sorted(supported_conventions))}'
        self.target_naming_convention = target_naming_convention
        if contig_alias_url:
            self.contig_alias_url = contig_alias_url
        else:
            self.contig_alias_url = self._contig_alias_url
        self._cache = {}

    @retry(tries=3, delay=2, backoff=1.2, jitter=(1, 3))
    def _retrieve_from_contig_alias(self, contig_name):
        url = self.contig_alias_url + 'v1/chromosomes/genbank/' + contig_name
        response = requests.get(url, headers={'accept': 'application/json'})
        response.raise_for_status()
        chromosome_entities = response.json().get('_embedded').get('chromosomeEntities')
        assert len(chromosome_entities) == 1, 'Multiple option found for ' + contig_name
        return chromosome_entities[0].get(self.target_naming_convention)

    def convert(self, contig_accession):
        if contig_accession not in self._cache:
            self._cache[contig_accession] = self._retrieve_from_contig_alias(contig_accession)
        return self._cache[contig_accession]


class AssemblyAccessionConverter(SequenceAccessionConverter):
    """Converter that needs to receive the INSDC assembly id and can translate from any convention to any convention
    within that assembly"""
    def __init__(self, source_assembly, source_naming_convention, target_naming_convention, contig_alias_url=None):
        super().__init__(target_naming_convention, contig_alias_url)
        assert target_naming_convention in supported_conventions, \
            f'The source naming convention {source_naming_convention} is not on of the supported ones ' \
            f'{", ".join(sorted(supported_conventions))}'
        self.source_assembly = source_assembly
        self.source_naming_convention = source_naming_convention
        self._cache_assembly_dict()

    @retry(tries=3, delay=2, backoff=1.2, jitter=(1, 3))
    def _assembly_get(self, page=0, size=10):
        url = self.contig_alias_url + 'v1/assemblies/' + self.source_assembly + f'/chromosomes?page={page}&size={size}'
        response = requests.get(url, headers={'accept': 'application/json'})
        response.raise_for_status()
        response_json = response.json()
        return response_json

    def _add_chromosomes(self, assembly_data):
        for entity in assembly_data.get('chromosomeEntities', []):
            self._cache[entity[self.source_naming_convention]] = entity[self.target_naming_convention]

    def _cache_assembly_dict(self):
        page = 0
        size = 1000
        response_json = self._assembly_get(page=page, size=size)
        self._add_chromosomes(response_json['_embedded'])
        while 'next' in response_json['_links']:
            page += 1
            response_json = self._assembly_get(page=page, size=size)
            self._add_chromosomes(response_json['_embedded'])

    def convert(self, contig_name):
        return self._cache.get(contig_name)
