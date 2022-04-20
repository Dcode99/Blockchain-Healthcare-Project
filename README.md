# Blockchain-Healthcare-Project

Goal: Demonstrating a method of secure communication using trusted private blockchain ledgers for hospitals and healthcare providers to digitally keep track of who should be able to access personal health information. 

Existing projects: 
A combination of Golang (https://blog.logrocket.com/how-to-build-blockchain-from-scratch-go/) and Hyperledger fabric (https://hyperledger-fabric.readthedocs.io/en/release-2.2/blockchain.html) was used to create KitChain (https://www.kitchain.org/) which manages pharmaceutical supply chains using smart contracts.
	MyClinic.com (https://myclinic.com/) was created using Hyperledger, and uses the blockchain system “to schedule appointments, review medical reports and request further investigations or assistance”.
	Verified.Me is a Canadian blockchain-based digital identity network that uses Hyperledger fabric to allow consumers to choose who to share healthcare information with.

Design choices: 
Hyperledger Fabric can be used to setup the blockchain, with chaincode for smart contracts supported in Go, Node.js, and Java. It has a shared ledger using a world state and transaction logs.
	Etherium private network (https://merehead.com/blog/how-to-create-private-ethereum-blockchain/#:~:text=Ethereum%20private%20network%20is%20a,to%20people%20outside%20the%20organization.) is another option. Like Hyperledger fabric, it allows for smart contracts on a private network. The languages required for Etherium are Go, Python, and C++.

Hyperledger Iroha is considered a more flexible technology, and was the choice for this project.
