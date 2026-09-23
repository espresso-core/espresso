import requests

def rpc_post(url, method, arguments):

    data = {
        "jsonrpc": "2.0",
        "method": method,
        "params": arguments,
        "id": 1
    }
    response = requests.post(url, json=data, headers={"Content-Type": "application/json"})
    response.raise_for_status()

    return response.json().get("result")