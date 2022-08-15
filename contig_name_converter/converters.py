import requests
from retry import retry


class SequenceAccessionConverter:
    """Converter that needs to receive the INSDC contig accession that can uniquely identify the sequence to
    translate the contig name"""
    _contig_alias_url = 'https://www.ebi.ac.uk/eva/webservices/contig-alias/'

    def __init__(self, target_naming_convention, contig_alias_url=None):
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
        self.source_assembly = source_assembly
        self.source_naming_convention = source_naming_convention
        self._cache_assembly_dict()

    @retry(tries=3, delay=2, backoff=1.2, jitter=(1, 3))
    def _assembly_get(self, page=0, size=10):
        url = self.contig_alias_url + 'v1/assemblies/' + self.source_assembly + f'/chromosomes?page={page}&size={size}'
        response = requests.get(url, headers={'accept': 'application/json'})
        response.raise_for_status()
        response_data = response.json()
        return response_data['_embedded']

    def _cache_assembly_dict(self):
        page = 0
        size = 1000
        assembly_data = self._assembly_get(page=page, size=size)
        previous_size = -1
        while assembly_data and ('chromosomeEntities' in assembly_data or 'scaffoldEntities' in assembly_data):
            if len(self._cache) == previous_size:
                break
            previous_size = len(self._cache)
            if 'chromosomeEntities' in assembly_data:
                for entity in assembly_data['chromosomeEntities']:
                    self._cache[entity[self.source_naming_convention]] = entity[self.target_naming_convention]
            if 'scaffoldEntities' in assembly_data:
                for entity in assembly_data['scaffoldEntities']:
                    self._cache[entity[self.source_naming_convention]] = entity[self.target_naming_convention]
            page += 1
            assembly_data = self._assembly_get(page=page, size=size)

    def convert(self, contig_name):
        return self._cache.get(contig_name)
