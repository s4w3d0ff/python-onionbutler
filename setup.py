from setuptools import setup
setup(name='python-onionbutler',
	version='0.1',
	description='A Tor Onion Sevice Manager',
	url='https://github.com/s4w3d0ff/python-onionbutler',
	author='s4w3d0ff',
	license='GPL v2',
	packages=['onionbutler'],
	install_requires=['stem', 'requests'],
    zip_safe=False)
