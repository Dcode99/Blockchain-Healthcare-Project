from setuptools import setup

setup(
    name='pyhyperhealth',
    version='0.8',
    packages=['pyhyperhealth'],
    url='https://github.com/Dcode99/Blockchain-Healthcare-Project/',
    license='Apache 2.0',
    author='Dillon Tate',
    author_email='dillon.tate@uky.edu',
    description='Python Hyperledger Iroha Healthcare Permissions Library',
    install_requires=['iroha',
                     'flask'],

)
