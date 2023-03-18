from setuptools import setup

setup(
    name='pyhyperhealth',
    version='1.0',
    packages=['pyhyperhealth'],
    package_data={'pyhyperhealth': ['network.sh', 'Network_Files/node1/config.docker', 'Network_Files/node2/config.docker', 'Network_Files/node3plus/config.docker', 
                                    'Network_Files/node1/genesis.block', 'Network_Files/node2/genesis.block'], 'Network_Files/node3plus/genesis.block',
                                    'Network_Files/node1/*.priv', 'Network_Files/node2/*.priv', 'Network_Files/node3plus/*.priv',
                                    'Network_Files/node1/*.pub', 'Network_Files/node2/*.pub', 'Network_Files/node3plus/*.pub'},
    url='https://github.com/Dcode99/Blockchain-Healthcare-Project/',
    license='Apache 2.0',
    author='Dillon Tate',
    author_email='dillon.tate@uky.edu',
    description='Python Hyperledger Iroha Healthcare Permissions Library',
    install_requires=['iroha',
                     'flask'],

)
