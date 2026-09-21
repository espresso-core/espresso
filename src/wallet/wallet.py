import tkinter as tk
from tkinter import ttk, messagebox
import hashlib
import binascii
import requests

from ecdsa import SigningKey, SECP256k1


class CryptoWalletGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cryptocurrency Wallet")
        self.root.geometry("700x550")
    
        self.private_key = None
        self.public_key = None
        self.wallet_address = None

        self.create_widgets()

    def create_widgets(self):

        title = ttk.Label(
            self.root,
            text="Cryptocurrency Wallet",
            font=("Arial", 18, "bold")
        )
            
        title.pack(pady=10)

        generate_btn = ttk.Button(
            self.root,
            text="Generate New Wallet",
            command=self.generate_wallet
        )
        generate_btn.pack(pady=10)

        ttk.Label(self.root, text="Private Key").pack()
        self.private_text = tk.Text(self.root, height=5)
        self.private_text.pack(fill="x", padx=10)
        
        ttk.Label(self.root, text="Public Key").pack()
        self.public_text = tk.Text(self.root, height=5)
        self.public_text.pack(fill="x", padx=10)
        
        ttk.Label(self.root, text="Wallet Address").pack()
        self.address_text = tk.Text(self.root, height=2)
        self.address_text.pack(fill="x", padx=10)
        
        balance_btn = ttk.Button(
            self.root,
            text="Check Balance",
            command=self.check_balance
        )
        balance_btn.pack(pady=15)

        self.balance_label = ttk.Label(
            self.root,
            text="Balance: Not Queried",
            font=("Arial", 12)
        )
        self.balance_label.pack()

    def generate_wallet(self):
        try:
            # Generate private key
            signing_key = SigningKey.generate(curve=SECP256k1)
            verifying_key = signing_key.get_verifying_key()
            
            private_key_hex = signing_key.to_string().hex()
            public_key_hex = verifying_key.to_string().hex()
            
            # Simple wallet address
            sha256_hash = hashlib.sha256(
                bytes.fromhex(public_key_hex)
            ).digest()
            
            ripemd160 = hashlib.new(
                "ripemd160",
                sha256_hash
            ).digest()
            
            wallet_address = binascii.hexlify(
                ripemd160
            ).decode()
            
            self.private_key = private_key_hex
            self.public_key = public_key_hex
            self.wallet_address = wallet_address
            
            self.private_text.delete("1.0", tk.END)
            self.private_text.insert(tk.END, private_key_hex)
            
            self.public_text.delete("1.0", tk.END)
            self.public_text.insert(tk.END, public_key_hex)
            
            self.address_text.delete("1.0", tk.END)
            self.address_text.insert(tk.END, wallet_address)
            
            self.balance_label.config(text="Balance: Not Queried")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
        
    def check_balance(self):
        if not self.wallet_address:
            messagebox.showwarning(
                "Warning",
                "Generate a wallet first."
            )
            return
    
        try:
        # Example endpoint:
        # Replace with your own cryptocurrency server
        
            url = f"http://localhost:5000/balance/{self.wallet_address}"
            
            response = requests.get(
                url,
                timeout=10
            )
            
            response.raise_for_status()
            
            data = response.json()
            
            balance = data.get("balance", 0)
            
            self.balance_label.config(
                text=f"Balance: {balance}"
            )
            
        except requests.exceptions.RequestException as e:
            messagebox.showerror(
                "Network Error",
                f"Could not retrieve balance:\n{e}"
            )
        
        except Exception as e:
            messagebox.showerror("Error", str(e))
        
        
def main():
    root = tk.Tk()
    app = CryptoWalletGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()