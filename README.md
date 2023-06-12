# ChainSpecter

![image](https://github.com/konradstrachan/ethpraguehackathon23/assets/21056525/57957e30-c6e4-4e4a-b9e7-e3277e7b426e)

Security vulnerabilities are spooky

## Description 

This project seeks to provide an insight into how AI guided auditing using existing tools currently looks like whilst also seeking to democratise access to cheap, fast audits with verifiable results recorded on chain.

It was an opportunity for me to explore some recent advances in AI models focusing on their application in software security audits. It leverages the incredible capabilities of AI models like GPT-3.5/4 that excel at contextualising problems and, with sufficiently designed prompts and combined with other tools, can excel at building graph models of software interactions and using this to test for vulnerabilities more efficiently than human auditors.

I believe that within the coming years a significant portion of security audits will be performed or strongly assisted by AI models. This project serves as an opportunity for me to analyze the current state of the art in AI-assisted code review and auditing tools, and to develop an open protocol that enables anyone access to quick and cost-effective tools.

Smart contracts are built using relatively simple building blocks but rapidly expand into complex possibility spaces, particularly when interactions with other contracts or layers are considered. This has led to a number of high profile security issues over the years damaging the perception of web3 and the defi space.

To build secure systems, we either need a manner of expressing logic which is safe from unintentional consequences and protects protocols from accidental omissions (MUCH easier said than done) or we need to provide robust tooling to help teams have the flexibility to build with the confidence that they are supported and protected from making catastrophic errors.

Today these tools are better than ever, but only a subset of smart contract developers use them. Whilst most contracts undergo a formal audit before being used in production, these audits have been costly and have required significant lead times. Both of these could be significant stiflers of innovation, particularly for small teams.

ChainSpecter is an open, permissionless protocol that provides a solution to these problems by giving teams a way to easily, quickly and cheaply obtain audits verifiable on-chain using the best tools available whilst only paying a fraction of the cost of a formal audit to cover computation costs.

![image](https://github.com/konradstrachan/ethpraguehackathon23/assets/21056525/be0c84eb-fb10-49aa-8bc3-0a2d508b8105)

This project was created as part of the ETH Prague 2023 hackathon.

## Features

* Static analysis and fuzzing using AI models based on GPT to guide and optimise auditing
* Permissionless auditing process with any team being able to request and pay for an audit directly on-chain
* Verifiable audit results that can be referenced from anywhere and provable on-chain

## Technologies Used

* Solidity for smart contract development
* Woke Fuzzer (https://ackeeblockchain.com/woke/docs/1.2.1/fuzzer/)
* React, Hardhat, NextJS for rapid prototying and testing (via Scaffold-ETH 2)
* Scroll, Taiko for deploying and demoing contracts

## Usage

![image](https://github.com/konradstrachan/ethpraguehackathon23/assets/21056525/4518ec97-0dd1-4482-b209-b2d134136c3f)

### requestAudit(address contractAddress)

This function allows users to request an audit for a specific contract by providing the contractAddress parameter. The function requires a payment of at least 0.1 ETH to proceed. 

It checks if the audit for the given contractAddress has already been completed and emits an AuditRequested event.

### checkAudit(address contractAddress)

This function allows users to check the result of an audit for a specific contract. It takes the contractAddress as a parameter and returns the url and checksum associated with the audit result if it has been completed. 

If no audit result is available for the given contractAddress, it throws an exception.

### setAuditResult(address contractAddress, string calldata url, bytes32 checksum)

This function is used by the contract owner to set the audit result for a specific contract. 

It requires the contractAddress, url, and checksum parameters. The function updates the auditURL, auditChecksum, and auditCompleted mappings with the provided values and emits an AuditResultSet event.

### Events

The contract defines two events:

#### AuditRequested

This event is emitted when an audit is requested for a contract. It includes the contractAddress parameter.

#### AuditResultSet

This event is emitted when the audit result is set for a contract. It includes the contractAddress, url, and checksum parameters.

## Deployment

The contract can be deployed on any EVM network using a compatible development framework.

It is deployed and verified on:
* Scroll Alpha https://blockscout.scroll.io/address/0x2B0d36FACD61B71CC05ab8F3D2355ec3631C0dd5
* Taiko Alpha3 https://explorer.test.taiko.xyz/address/0x5FbDB2315678afecb367f032d93F642f64180aa3

For this project I used https://github.com/scaffold-eth/scaffold-eth-2 which contains all the tools needed to build, compile and deploy.

## License

This project is licensed under the MIT License.

## Disclaimer

The code in this repo is the product of a few hours of rapid prototyping as part of a Hackathon. Care was taken to ensure it is free from defects and security vulnerabilities but it should not be considered production ready and is thus provided as-is without any warranty.

Anyone wishing to use this should exercise caution and perform due diligence before using this code in a production environment.
