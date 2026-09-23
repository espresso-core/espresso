import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import hashlib
import binascii
import requests

from ecdsa import SigningKey, SECP256k1

class ToolTip:
    """Small hover tooltip. tkinter has no built-in one."""

    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tip = None
        self._job = None
        # add="+" so this never replaces bindings the widget already has.
        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<ButtonPress>", self._hide, add="+")

    def _schedule(self, _event=None):
        self._cancel()
        self._job = self.widget.after(self.delay, self._show)

    def _cancel(self):
        if self._job is not None:
            self.widget.after_cancel(self._job)
            self._job = None

    def _show(self):
        if self.tip is not None:
            return
        x = self.widget.winfo_rootx() + 12
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        self.tip = tk.Toplevel(self.widget)
        # No title bar or border — it should look like a tooltip, not a window.
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        tk.Label(
            self.tip,
            text=self.text,
            justify="left",
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            padx=6,
            pady=3,
        ).pack()

    def _hide(self, _event=None):
        self._cancel()
        if self.tip is not None:
            self.tip.destroy()
            self.tip = None


class Application:
    def __init__(self, root):
        self.root = root
        root.title("Espresso Wallet")
        root.geometry("520x400")
        root.update_idletasks()
        root.geometry(
            f"+{(root.winfo_screenwidth() - 520) // 2}"
            f"+{(root.winfo_screenheight() - 400) // 2}"
        )

        self.w_btn_generate_wallet = tk.Button(root, text="New Wallet", command=self.generate_wallet)
        self.w_btn_generate_wallet.place(x=20, y=20, width=96, height=32)
        ToolTip(self.w_btn_generate_wallet, "Create a new wallet")

        self.w_btn_load_wallet = tk.Button(root, text="Load Wallet", command=self.load_wallet)
        self.w_btn_load_wallet.place(x=130, y=20, width=96, height=32)
        ToolTip(self.w_btn_load_wallet, "Load a wallet")

        self.w_btn_save_wallet = tk.Button(root, text="Save Wallet", command=self.save_wallet)
        self.w_btn_save_wallet.place(x=240, y=20, width=96, height=32)
        ToolTip(self.w_btn_save_wallet, "Save a wallet")

        self.val_public_key = tk.Text(root)
        self.val_public_key.place(x=100, y=110, width=400, height=40)

        self.val_wallet_address = tk.Text(root)
        self.val_wallet_address.place(x=100, y=220, width=400, height=30)

        self.val_private_key = tk.Text(root)
        self.val_private_key.place(x=100, y=160, width=400, height=40)

        self.lbl_public_key = tk.Label(root, text="Public Key:")
        self.lbl_public_key.place(x=0, y=115, width=100, height=30)

        self.lbl_private_key = tk.Label(root, text="Private Key:")
        self.lbl_private_key.place(x=0, y=165, width=100, height=30)

        self.lbl_wallet_address = tk.Label(root, text="Wallet Address:")
        self.lbl_wallet_address.place(x=0, y=220, width=100, height=30)

        self.lbl_balance = tk.Label(root, text="Balance:", font=("Helvetica", 10, "bold"))
        self.lbl_balance.place(x=0, y=70, width=100, height=30)

        self.lbl_balance_value = tk.Label(root, text="0", font=("Helvetica", 10, "bold"))
        self.lbl_balance_value.place(x=100, y=70, width=110, height=30)

        self.w_btn_refresh_balance = tk.Button(root, text="Refresh Balance", command=self.refresh_balance)
        self.w_btn_refresh_balance.place(x=350, y=20, width=96, height=32)
        ToolTip(self.w_btn_refresh_balance, "Save a wallet")

        self.lbl_send = tk.Label(root, text="Send:", font=("Helvetica", 10, "bold"))
        self.lbl_send.place(x=0, y=270, width=100, height=30)

        self.lbl_amount = tk.Label(root, text="Amount:")
        self.lbl_amount.place(x=0, y=300, width=100, height=30)

        self.lbl_to = tk.Label(root, text="To:")
        self.lbl_to.place(x=0, y=340, width=100, height=30)

        self.val_amount = tk.Text(root)
        self.val_amount.place(x=100, y=300, width=200, height=30)

        self.val_to = tk.Text(root)
        self.val_to.place(x=100, y=340, width=400, height=30)

        self.w_tbn_send = tk.Button(root, text="Send", command=self.sent_amount)
        self.w_tbn_send.place(x=310, y=300, width=80, height=30)
        ToolTip(self.w_tbn_send, "Save a wallet")

        self.public_key = ""
        self.private_key = ""
        self.wallet_address = ""


    def load_wallet(self):
        """Open a file dialog and read one line at a time into the text widget."""
        file_path = filedialog.askopenfilename(
            title="Select a file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if not file_path:  # User canceled
            return

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                for idx, line in enumerate(file):

                    print([idx, line])
                    if idx==0:
                        self.wallet_address = line
                        self.val_wallet_address.config(state=tk.NORMAL)
                        self.val_wallet_address.delete(1.0, tk.END) # Clear previous content
                        self.val_wallet_address.insert(tk.END, line) # Insert new content
                        self.val_wallet_address.config(state=tk.DISABLED)
                        self.val_wallet_address = line

                    if idx==1:
                        self.public_key = line
                        self.val_public_key.config(state=tk.NORMAL)
                        self.val_public_key.delete(1.0, tk.END) # Clear previous content
                        self.val_public_key.insert(tk.END, line) # Insert new content
                        self.val_public_key.config(state=tk.DISABLED)
                        self.val_public_key = line

                    if idx==2:
                        self.private_key = line
                        self.val_private_key.config(state=tk.NORMAL)
                        self.val_private_key.delete(1.0, tk.END) # Clear previous content
                        self.val_private_key.insert(tk.END, line) # Insert new content
                        self.val_private_key.config(state=tk.DISABLED)
                        self.val_private_key = line

        except FileNotFoundError:
            messagebox.showerror("Error", "File not found.")
        except PermissionError:
            messagebox.showerror("Error", "Permission denied.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred:\n{e}")


    def save_wallet(self):
        try:
            # Ask user where to save the file
            file = filedialog.asksaveasfile(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                mode="w"
            )
            if file is None:  # User cancelled
                return
            
            # Get text from the widget
            content = self.wallet_address
            file.write(content)
            file.write("\n")

            content = self.public_key
            file.write(content)
            file.write("\n")

            content = self.private_key
            file.write(content)
            file.write("\n")
                       
            file.close()
            
            messagebox.showinfo("Success", "File saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file:\n{e}")

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

            self.val_private_key.config(state=tk.NORMAL)
            self.val_private_key.delete("1.0", tk.END)
            self.val_private_key.insert(tk.END, private_key_hex)
            self.val_private_key.config(state=tk.DISABLED)

            self.val_public_key.config(state=tk.NORMAL)
            self.val_public_key.delete("1.0", tk.END)
            self.val_public_key.insert(tk.END, public_key_hex)
            self.val_public_key.config(state=tk.DISABLED)

            self.val_wallet_address.config(state=tk.NORMAL)
            self.val_wallet_address.delete("1.0", tk.END)
            self.val_wallet_address.insert(tk.END, wallet_address)
            self.val_wallet_address.config(state=tk.DISABLED)

            self.lbl_balance_value.config(text="Balance: Not Queried")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))


    def refresh_balance(self):
        if not self.val_wallet_address:
            messagebox.showwarning(
                "Warning",
                "Generate a wallet first."
            )
            return
    
        try:
        # Example endpoint:
        # Replace with your own cryptocurrency server
        
            url = f"http://127.0.0.1:5000/jsonrpc"
            data = {
                "jsonrpc": "2.0",
                "method": "sso_getbalance",
                "params": ["fb82a34bdd491703f4935cd963505af2dd9d0f8f"],
                "id": 1
            }
            response = requests.post(url, json=data, headers={"Content-Type": "application/json"})
            response.raise_for_status()
            data=response.json()

            print(data)
            balance = data.get("result").get("balance")
            
            self.lbl_balance_value.config(text=f"{balance}")
            
        except requests.exceptions.RequestException as e:
            messagebox.showerror(
                "Network Error",
                f"Could not retrieve balance:\n{e}"
            )
        
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def sent_amount(self):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    app = Application(root)
    root.mainloop()
