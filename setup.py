from setuptools import setup, find_packages

setup(
    name='socialml',
    version='0.1',
    packages=find_packages(exclude=['tests*']),
    license='MIT',
    description='Package to convert social media messages into format sutiable for seq2seq modelling',
    long_description=open('README.md').read(),
    install_requires=['numpy', 'pyspellchecker'],
    url='https://github.com/erees1/socialml',
    author='Edward Rees',
)
