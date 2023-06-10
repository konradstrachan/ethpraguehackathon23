import time
from web3 import Web3
from web3.middleware import geth_poa_middleware
from solc import compile_source
from solc.exceptions import SolcError
from hashlib import sha256

# Woke fuzzer
#from woke.fuzz import Fuzzer
from woke.testing import *
from woke.testing.fuzzing import *

# Mythril Classic. It is a security analysis tool for Ethereum smart contracts 
# and provides a decompiler to generate Solidity-like pseudocode from bytecode.
#from mythril import mythril

# Configurable values
#contract_address = "0x123456789..."  # Address of the configured blockchain contract
#contract_abi = [...]  # ABI (Application Binary Interface) of the contract

web3_provider = "https://ropsten.infura.io/v3/your-infura-project-id"  # Infura endpoint or your own Ethereum node URL

owner_address = "0xabcdef..."  # Address of the owner of the Python script
private_key = "your-private-key"  # Private key of the owner's address

def get_contract_bytecode(address):
    # Get the contract bytecode
    # TODO error handling
    contract_bytecode = Web3.eth.getCode(address).hex()
    print("Contract bytecode:", contract_bytecode)
    return contract_bytecode
    
def decompile_bytecode(byteCode):
    try:
        decompiled_code = mythril.disassemble(bytecode)
    except Exception as e:
        print("Error decompiling bytecode:", str(e))
        return None

    print("Contract decompiled:")
    print(decompiled_code)
    return decompiled_code

def generate_audit(contractCode):
    # Stage 1 : static analysis

    # Stage 2 : fuzz the functions (needs ABI) 
    # Compile the Solidity code
    compiled_contract = compile_source(contractCode)
    contract_interface = compiled_contract["<stdin>:<ContractName>"]
    
    # Initialize the web3 instance
    web3 = Web3(Web3.HTTPProvider(web3_provider))
    Web3.middleware_onion.inject(geth_poa_middleware, layer=0)

    # Load the contract ABI
    contract = Web3.eth.contract(abi=contract_abi)
    
    # Initialize the fuzzer
    fuzzer = Fuzzer()

    # Generate and execute test cases for each callable function
    for function in contract_interface["abi"]:
        if function["type"] == "function" and function["stateMutability"] != "view" and function["stateMutability"] != "pure":
            inputs = function["inputs"]
            input_types = [param["type"] for param in inputs]
            test_case = fuzzer.fuzz_types(input_types)
            print("Executing test case for function", function["name"])
            print("Input values:", test_case)
            
            # Perform the function call with the generated test case inputs
            try:
                contract.functions[function["name"]](*test_case).transact()
                print("Function call successful!\n")
            except Exception as e:
                print("Function call failed:", str(e), "\n")
    
    return True, ""

def push_audit_result(address, result):
    # Perform the audit (simplified for demonstration purposes)
    try:
        # Generate URL and checksum
        url = "https://example.com/audit-report/" + address
        checksum = sha256(address).hexdigest()

        # Post the audit result back to the contract
        contract.functions.setAuditResult(address, url, checksum).transact(
            {"from": owner_address}
        )

        print("Audit result posted to the contract")
    except SolcError as e:
        print("Error compiling contract:", str(e))

def generate_audit(address):
    print("Auding " + address + "...")
    cbc = get_contract_bytecode(address)

    if cbc is None:
        print("Failed : couldn't get bytecode for " + address)
        push_audit_result(address, False)
    
    cc = decompile_bytecode(cbc)
    if contractCode is None:
        print("Failed : couldn't generate code for " + address)
        push_audit_result(address, False)

    audit_passed, audit = generate_audit(cc)
    print("Audit result : " + str(audit_passed) + " for " + address)
    push_audit_result(address, audit_passed)

def run_watcher():
    # Connect to the Ethereum network
    web3 = Web3(Web3.HTTPProvider(web3_provider))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)

    # Load the contract ABI and address
    contract = Web3.eth.contract(address=contract_address, abi=contract_abi)

    # Set the owner's account as the default account
    Web3.eth.default_account = owner_address

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
    # Summarise code ?
    # Static analysis is limited but perform as initial step
    # AI to generate fuzzing tests


# Main entry point
#run_watcher()

# Entry point for testing
test_decompiler()