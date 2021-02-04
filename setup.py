from setuptools import setup, find_packages, find_namespace_packages

setup(
    name='pyri-variable-storage',
    version='0.1.0',
    description='PyRI Teach Pendant Variables Database',
    author='John Wason',
    author_email='wason@wasontech.com',
    url='http://pyri.tech',
    package_dir={'': 'src'},
    packages=find_namespace_packages(where='src'),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'pyri-common',
        'sqlalchemy'
    ],
    tests_require=['pytest','pytest-asyncio'],
    extras_require={
        'test': ['pytest','pytest-asyncio']
    },
    entry_points = {
        'pyri.plugins.factory': ['pyri-variable-storage-plugin=pyri.variable_storage.factory:get_factory'],
        'pyri.plugins.robdef': ['pyri-variable-storage-robdef=pyri.variable_storage.robdef:get_variable_storage_robdef']
    }
)