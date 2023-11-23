import pyotp
import datetime
import time
import threading
import pyperclip
import ttkbootstrap as ttk
from ttkbootstrap import Style
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame

class MyOTP:
    def __init__(self, totp_secret, issuer, name):
        self.totp_secret =  totp_secret
        self.issuer = issuer
        self.name = name

# TOTP secret key obtained from Discord
totp_secret = ""

# Create a TOTP object
totp = pyotp.TOTP(totp_secret,issuer="in", name="a")

# Create a Tkinter GUI window

window = ttk.Window(themename='darkly', title="OTP Generator", resizable=(False, False))
window.geometry("600x435")
window.position_center()
sf = ScrolledFrame(window, height=350, width=200)
sf.grid(column=1, row=1, rowspan=20, columnspan=4)


# Create a Tkinter StringVar for UI
otp_code = ttk.StringVar()
otp_code.set("------")
remaining_time_var = ttk.StringVar()
remaining_time_var.set("Time remaining: 0s")

# Create the Tkinter Labels to display the UI
otp_code_label = ttk.Label(window, textvariable=otp_code, font=("Arial", 30))
otp_code_label.grid(column=7, row=5)

remaining_time_label = ttk.Label(window, textvariable=remaining_time_var, font=("Arial", 10))
remaining_time_label.grid(column=7, row=10)

progress_bar = ttk.Progressbar(window, orient="horizontal", length=350, mode="determinate")
progress_bar.grid(column=6, row=11, columnspan=3, padx= 25)

copyBtn = ttk.Button()
copyBtn.grid(column=6, row=20, columnspan=3, padx= 25)

importBtn = ttk.Button(width= 10, bootstyle="outline", text="Import")
importBtn.grid(column=1, row=21, pady=10, columnspan=2)

exportBtn = ttk.Button(width= 10, bootstyle="outline", text="Export")
exportBtn.grid(column=3, row=21, columnspan=2)

deleteBtn = ttk.Button(width= 10, bootstyle="outline-danger", text="Delete")
deleteBtn.grid(column=1, row=22, columnspan=2)

addBtn = ttk.Button(width= 10, bootstyle="outline-success", text="Add")
addBtn.grid(column=3, row=22, columnspan=2)

def update_code_info():
    while True:
        # Calculate the remaining time
        current_time = datetime.datetime.now()
        remaining_time = totp.interval - (current_time.timestamp() % totp.interval)

        # Update the GUI
        remaining_time_var.set("Time remaining: {:.0f}s".format(remaining_time))
        try:
            otp_code.set(totp.now())
        except:
            otp_code.set("Invalid OTP")
            remaining_time_var.set("Please setup 2FA for this account again!")
            progress_bar["value"] = 80
            return False
        progress_bar["value"] = (remaining_time / totp.interval) * 100

        # Wait for 1 second
        time.sleep(1)
    
def code_copy():
    pyperclip.copy(otp_code.get())
    copyBtn.config(text= "Copied!")

# Create a thread for the update_code_info function
update_thread = threading.Thread(target=update_code_info)
update_thread.daemon = True
update_thread.start()

copyBtn.config(width= 54, text="Copy", command=code_copy)

window.mainloop()