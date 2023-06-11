resultTemplate = """
<!DOCTYPE html>
<html>
<head>
    <title>Smart Contract Audit Result</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
        }

        h1 {
            color: #333;
        }

        h2 {
            color: #666;
        }

        p {
            margin-bottom: 10px;
        }

        a {
            color: #007bff;
            text-decoration: none;
        }

        .bar {
            height: 20px;
            margin-top: 20px;
            margin-bottom: 20px;
        }

        .bar.Passed {
            background-color: #6fcf97;
        }

        .bar.Failed {
            background-color: #ff4d4f;
        }

        .icon {
            vertical-align: middle;
            margin-right: 5px;
        }

        textarea {
            width: 100%;
            border: none;
            resize: vertical;
        }
    </style>
        
    <script src="https://cdn.jsdelivr.net/npm/web3@1.5.3/dist/web3.min.js"></script>
    <script>
        document.addEventListener("DOMContentLoaded", () => {
            const contractAddress = $verificationContract;
            const functionName = "checkAudit";

            // Function to handle connecting a wallet
            async function connectWallet() {
                if (window.ethereum) {
                    const resultElement = document.getElementById("verify_result");
                    try {
                        await window.ethereum.enable();
                        const web3 = new Web3(window.ethereum);
                        const accounts = await web3.eth.getAccounts();
                        const account = accounts[0];

                        // Call the smart contract function
                        const contract = new web3.eth.Contract([], contractAddress);
                        const result = await contract.methods[functionName]().call({ from: account });
                        resultElement.textContent = " Result:" + result;
                    } catch (error) {
                        resultElement.textContent = " Error connecting wallet " + error;
                    }
                } else {
                    resultElement.textContent = " No wallet found";
                }
            }

            const connectButton = document.getElementById("verify");
            connectButton.addEventListener("click", connectWallet);
        });
    </script>
</head>
<body>
    <h1>Smart Contract Audit Result</h1>
    
    <h2>Contract Details</h2>
    <p>Contract Address: <a href="https://blockexplorer.com/address/$contractAddress" target="_blank">$contractAddress</a></p>
    <p>Verification hash: $auditHash</p>
    <p>Verification: <button id="verify">Verify</button><span id="verify_result"></></p>

    <h2>Audit Result</h2>
    <div class="bar $auditResult">
    $icon
        
        $auditResult
    </div>
    
    <h2>Audit Notes</h2>
    <textarea rows="8" cols="50" readonly>$auditNotes</textarea>
</body>
</html>
"""

positiveIcon = """
    <span class="icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="#ffffff">
                <path d="M9 16.17l-3.59-3.59L4 14l5 5 10-10L19.59 7z"/>
            </svg>
    </span>
    """

negativeIcon = """
    <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="#ffffff">
                <path d="M10.34 6.34L12 4.66 13.66 6.34 15 5l-1.66-1.66L15 1 13.66 2.34 12 1.66 10.34 3 9 1.66 10.66 1 12 2.34 13.66 1 15 1.66 13.34 3 12 4.66 10.34 6.34zM12 19c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm0-2c3.31 0 6-2.69 6-6s-2.69-6-6-6-6 2.69-6 6 2.69 6 6 6z"/>
            </svg>
"""