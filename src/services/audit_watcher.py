import time
import requests
import re
import json

from web3 import Web3
from web3.middleware import geth_poa_middleware
from hashlib import sha256

# Woke fuzzer
#from woke.fuzz import Fuzzer   # TODO
from woke.testing import *
from woke.testing.fuzzing import *

import openai

from config import web3_provider
from config import etherscan_api_key
from config import openai_api_key

openai.api_key = openai_api_key

owner_address = "0xabcdef..."  # Address of the owner of the Python script
private_key = "your-private-key"  # Private key of the owner's address

def has_numbered_bullet_points(text):
    bullet_points = re.findall(r'\d+\.\s(.+)', text)
    
    if bullet_points:
        return True
    # else
    return False

def removeComments(solidity_string):
    # Regular expression pattern to match Solidity comments
    comment_pattern = r'\/\/.*|\/\*[\s\S]*?\*\/'
    
    # Use regex to remove comments from the string
    stripped_string = re.sub(comment_pattern, '', solidity_string)
    
    return stripped_string

def get_contract_abi(address):
    url = f"https://api.etherscan.io/api?module=contract&action=getabi&address={address}&apikey={etherscan_api_key}"

    try:
        response = requests.get(url)
        data = response.json()
        
        if data["status"] == "1" and data["message"] == "OK":
            contract_abi = data["result"]
            return contract_abi
        
    except requests.exceptions.RequestException as e:
        print("Error retrieving contract ABI:", str(e))
    
    return None

def get_contract_code(address):
    url = f"https://api.etherscan.io/api?module=contract&action=getsourcecode&address={address}&apikey={etherscan_api_key}"

    try:
        response = requests.get(url)
        data = response.json()
        if data["status"] == "1" and data["message"] == "OK" and len(data["result"]) > 0:
            # NOTE : this ridiculous structure ES uses means this will get 
            # confused for new style multi-contract submissions
            sources = data["result"][0]["SourceCode"]
            return sources
        else:
            print("Failed to get verified contract code:", data["message"])
    except requests.exceptions.RequestException as e:
        print("Error connecting to Etherscan API:", str(e))

    return None

def get_contract_bytecode(address):
    # Get the contract bytecode
    web3 = Web3(Web3.HTTPProvider(web3_provider))
    contract_bytecode = web3.eth.get_code(address).hex()
    print("Contract bytecode:", contract_bytecode)
    return contract_bytecode
    
def decompile_bytecode(bytecode):
    print("Error decompiling bytecode:", str(e))
    return None
    # BROKEN due to Mythril
    #try:
    #    decompiled_code = decompile(bytecode)
    #except Exception as e:
    #    print("Error decompiling bytecode:", str(e))
    #    return None

    #print("Contract decompiled:")
    #print(decompiled_code)
    #return decompiled_code

def push_audit_result(address, result):
    # Perform the audit (simplified for demonstration purposes)
    try:
        # Generate URL and checksum
        url = "https://example.com/audit-report/" + address
        checksum = sha256(address.encode()).hexdigest()

        # Post the audit result back to the contract
        contract.functions.setAuditResult(address, url, checksum).transact(
            {"from": owner_address}
        )

        print("Audit result posted to the contract")
    except SolcError as e:
        print("Error compiling contract:", str(e))

def generate_audit(address):
    print("Auding " + address + "...")

    cc = get_contract_code(address)

    if cc is None:
        print("Failed to get verified contract code, attempting to get bytecode..")
        cbc = get_contract_bytecode(address)

        if cbc is None:
            print("Failed: couldn't get bytecode for " + address)
            push_audit_result(address, False)
            return
        
        cc = decompile_bytecode(cbc)

    if cc is None:
        print("Failed: couldn't generate code for " + address)
        push_audit_result(address, False)
        return

    abi = get_contract_abi(address)

    if abi is None:
        print("Failed: couldn't generate code for " + address)
        push_audit_result(address, False)
        return

    initialCodeSize = len(cc)
    cc = removeComments(cc)
    optimisedCodeSize = len(cc)

    reducedSizeAmount = (float(optimisedCodeSize) / float(initialCodeSize)) * 100

    print("Optimised code is " + str(int(reducedSizeAmount)) + "% smaller")

    audit_passed, audit = audit_code(address, cc, abi)
    print("Audit result: " + str(audit_passed) + " for " + address)

    #push_audit_result(address, audit_passed)

def perform_static_ai_anaylsis(code):
    # Construct the initial message with your prompt
    prompt = f"Audit the following Solidity smart contract only reporting critical security issues listing each with a number bullet point. If you are unable to audit say 'unable to audit':\n```solidity\n{code}\n```"

    # Create the API request
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a security auditor making an audit report of critical issues without recommendations."},
            {"role": "user", "content": prompt}
        ]
    )

    # Extract the AI's response
    if 'choices' in response and len(response['choices']) > 0:
        # Process the response and extract the audit report
        report = response['choices'][0]['message']['content']
        print(report)
        
        hasIssues = False

        #
        # Check for direct failure responses like:
        # 
        # I'm sorry, but the provided Solidity code is incomplete and contains 
        # irrelevant information. Could you please provide a complete and 
        # functional Solidity contract?
        #
        # or
        #
        # Unfortunately, the contract code is missing and cannot be audited 
        # for critical security issues. Please provide the contract code.
        #
        # ..etc

        if 'is incomplete' in report:
            hasIssues = True

        if "I'm sorry" in report or 'Unfortunately' in report:
            hasIssues = True

        if 'contract code is missing' in report:
            hasIssues = True

        if 'smart contract code is not provided' in report:
            hasIssues = True

        if report[:1] == '?':
            hasIssues = True

        if has_numbered_bullet_points(report):
            hasIssues = True

        if 'unable to audit' in report or 'Unable to audit':
            hasIssues = True

        print("Contract is free from issues : " + str(hasIssues == False))
        
        return (hasIssues == False), report
    
    # else
    return False, "Failed to generate AI audit report"

def perform_fuzzing_analysis(address, code, abi):
    web3 = Web3(Web3.HTTPProvider(web3_provider))
    contract = web3.eth.contract(address=address, abi=abi)

    # Generate and execute test cases for each callable function
    fuzzer = Fuzzer.from_abi(abi)

    fuzzerResult = True

    if fuzzer is not None:
        # Fuzzer created successfully
        # Iterate over each function in the ABI and generate test cases
        for function in contract_abi:
            if function["type"] == "function":
                function_name = function["name"]
                input_types = [param["type"] for param in function["inputs"]]
                test_case = fuzzer.fuzz_types(input_types)

                if test_case is not None:
                    print("Executing test case for function", function_name)
                    print("Input values:", test_case)

                    # Perform the function call with the generated test case inputs
                    try:
                        # Call the function on the contract with the test case inputs
                        contract.functions[function_name](*test_case).transact()
                        
                        print("Function call successful!\n")
                    except Exception as e:
                        print("Function call failed:", str(e), "\n")
                        fuzzerResult = False
                else:
                    print("No test cases generated for function", function_name)
    else:
        print("Failed to create fuzzer.")
        fuzzerResult = False

    # TODO : Report
    return fuzzerResult, ""

def audit_code(address, code, abi):
    # Stage 1: Static analysis
    # Perform static analysis on the contract code
    static_result, static_report = perform_static_ai_anaylsis(code)

    print("AI audit result " + str(static_result))

    if static_result == False:
        print("Static analysis failed")

    # Stage 2: Fuzz the functions (needs ABI)
    fuzzer_report = ""
    fuzzer_result = True
    #fuzzer_result, fuzz_report = perform_fuzzing_analysis(address, code, abi)

    #if fuzzer_result == False:
    #    print("Static analysis failed")

    auditResult = True
    if static_result != True or fuzzer_result != True:
        auditResult = False

    combinedReport = "Findings from AI analysis:\n" + static_report + "\n\nFrom fuzzing:\n" + fuzzer_report

    return auditResult, combinedReport

def run_watcher():
    # Connect to the Ethereum network
    web3 = Web3(Web3.HTTPProvider(web3_provider))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)

    # Load the contract ABI and address
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)

    # Set the owner's account as the default account
    web3.eth.default_account = owner_address

    while True:
        # Start event listening
        event_filter = contract.events.EventName.createFilter(fromBlock="latest")
        for event in event_filter.get_all_entries():
            print("Event received!")
            address = event["args"]["contractAddress"]
            generate_audit(address)

        time.sleep(30)  # Wait for 30 seconds before checking for new events

def test_decompiler():
    print("Test mode")
    # Use tether contract as test
    generate_audit("0xdAC17F958D2ee523a2206206994597C13D831ec7")
    # AAVE Wrapped Token Gateway v3
    #generate_audit("0xD322A49006FC828F9B5B37Ab215F99B4E5caB19C")
    # Sea port
    #generate_audit("0x00000000000000ADc04C56Bf30aC9d3c0aAF14dC")
    # Circle
    #generate_audit("0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48")
    # Coinbase wallet proxy
    #generate_audit("0xe66b31678d6c16e9ebf358268a790b763c133750")

    # Summarize code?
    # Static analysis is limited but perform as initial step
    # AI to generate fuzzing tests

# Main entry point
# run_watcher()

# Entry point for testing
test_decompiler()