Blockchain-Healthcare-Project

This project is part of a Masters project through the University of Kentucky extending work on an independant study course.

Goal: 

Demonstrating a method of secure communication using trusted private blockchain ledgers for hospitals and healthcare providers to digitally keep track of who should be able to access personal health information. 

Existing projects: 

A combination of Golang (https://blog.logrocket.com/how-to-build-blockchain-from-scratch-go/) and Hyperledger fabric (https://hyperledger-fabric.readthedocs.io/en/release-2.2/blockchain.html) was used to create KitChain (https://www.kitchain.org/) which manages pharmaceutical supply chains using smart contracts.
	
MyClinic.com (https://myclinic.com/) was created using Hyperledger, and uses the blockchain system “to schedule appointments, review medical reports and request further investigations or assistance”.
	
Verified.Me is a Canadian blockchain-based digital identity network that uses Hyperledger fabric to allow consumers to choose who to share healthcare information with.

Project Structure

This project utilizes a private ledger that is split into different roles. These three roles have different accesses and are split into patients, healthcare workers, and administrators. Administrators have access to the whole system, and should include limited trusted individuals. Healthcare workers include physicians, nurses, and other healthcare staff who may need access to patient data. This role can only be added by administrators to ensure only verified healthcare workers are added to the blockchain. This role will most likely be used by the hospital staff who enter the data rather than each doctor individually. Patients are individuals who are entered into the system by healthcare workers or administrators and may have health information attached to their account. Patients can only access their own data or give access to their data to other accounts. All of these roles are under the hospital domain. When implemented across multiple healthcare offices, each healthcare facility may have a unique domain created by an administrator. Each role is only given access to the minimal commands and data they need. This reduces the chances of malicious actors gaining access to any patient data.

Since the goal of this project is to keep the storage and transferring of healthcare data secure, it is important to investigate the best way to identify patient records. Some patients may have the same name, which could cause confusion or errors if each account was based solely on patient names. To protect against this, patient accounts should be identified by a unique username rather than their actual name. This simplification means less information has to be stored on the blockchain and less information is visible for others to view. It also protects patient identities if a malicious user were to gain access to the blockchain.

While blockchain is great for separating user roles and keeping track of access, it does not have robust storage capabilities for documents. Because of this, the actual health records will not be stored on the ledger. Each health record will be stored in a separate database owned by each hospital, as is currently done for many healthcare institutions. These databases will be referenced in the blockchain using a unique ID for each patient record. This ID can be found on the blockchain by users with the correct permissions and can be used to query the actual health records which may be an EHR, an X-ray, an MRI, or any other type of health record. Without this ID, a user cannot access the desired health record from the database. For this project, the healthcare records will be abstracted to this ID for demonstration purposes.

Prerequisites

To run this demonstration, a system running Unbuntu and docker is needed, along with an installation of Python3, pip3, and the iroha python library.

Network Requirements

To set up the network, simply run the network shell script as root user using "bash network.sh down" to clear the setup, and "bash network.sh up_1" to setup the main network. To restart the network, use the command "bash network.sh restart_1" as root. The peer-addition branch of the project requires specific machines and IP addresses, and it will not succeed without them. These can be edited if the user desires to use different IP addresses, or the multiple nodes branch can be used for local testing. The shell script is slightly different in some branches, make sure to look at the network.sh to determine which argument is needed.

Python Exectuion

To execute the python program and work on the blockchain after the network is setup, use the following command from the base directory for this project: "python3 python_programs/main.py". Once executed, the script will run a series of test commands with test output before giving the user a menu of further commands they can run using custom functions to execute on the blockchain. The list of commands includes getting account details, creating a domain, creating an asset, creating an account, appending a role to an account, adding a record. The current iteration runs using the administrator keys.

Flask Execution

To start the flask server, the command is "flask --app python_programs/api.py run --host=0.0.0.0". This command runs the flask application using the python program api.py on all public IPs, which for the primary node in testing is 128.163.181.53. Running without "--host" will only run the flask application locally.

Sources: 

The initial commands and structure for this document used is from the Hyperledger Iroha Python repository (https://github.com/hyperledger/iroha-python).
The network structure for multiple Iroha nodes is based off of the work by Ta-SeenJunaid (https://github.com/Ta-SeenJunaid/Hyperledger_Iroha_Multi_Node_Tutorial).

Notes:

Commands for setting up the blockchain are located in the "Notes on creating iroha node" document. These notes detail how to delete and set up a new blockchain if you have the prerequisites installed. The official guide is located in the Iroha documentation (https://iroha.readthedocs.io/en/main/getting_started/index.html).
