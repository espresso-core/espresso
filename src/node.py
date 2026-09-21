from flask import Flask, jsonify
 
app = Flask(__name__)
 
balances = {
    "fb82a34bdd491703f4935cd963505af2dd9d0f8f": 12.5,
    "def456": 100.0
}
 
@app.route("/balance/<address>")
def get_balance(address):
    balance = balances.get(address, 0)
 
    return jsonify({
        "address": address,
        "balance": balance
    })

if __name__ == "__main__":
    try:
        # Run on localhost (127.0.0.1) and custom port 8080
        app.run(host='127.0.0.1', port=5000, debug=True)
    except OSError as e:
        print(f"Error starting server: {e}")