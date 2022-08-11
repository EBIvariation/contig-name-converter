from distutils.core import setup
from os.path import join, abspath, dirname

base_dir = abspath(dirname(__file__))
requirements_txt = join(base_dir, 'requirements.txt')
requirements = [l.strip() for l in open(requirements_txt) if l and not l.startswith('#')]

version = open(join(base_dir, 'VERSION')).read().strip()

setup(
    name='contig_name_converter',
    packages=['contig_name_converter'],
    package_data={'contig_name_converter': ['VERSION']},
    scripts=['bin/convert_vcf_file.py'],
    version=version,
    license='Apache',
    description='EBI EVA - VCF merge library',
    url='https://github.com/EBIvariation/contig_name_converter',
    keywords=['ebi', 'eva', 'python', 'vcf'],
    install_requires=requirements,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3'
    ]
)