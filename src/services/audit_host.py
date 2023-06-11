from flask import Flask, render_template, request
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Try /audit?contractAddress=0x1234"

@app.route('/audit')
def contract_audit():
    contract_address = request.args.get('contractAddress', '')
    filename = f"{contract_address}.html"
    
    current_directory = os.path.abspath(os.path.dirname(__file__))
    file_path = os.path.join(current_directory, filename)
    
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            contract_text = file.read()
        
        return contract_text
    else:
        return f"File not found for contract address: {contract_address}", 404



if __name__ == '__main__':
    app.run()