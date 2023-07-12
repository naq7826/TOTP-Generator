import pyotp
import datetime
import time
import threading
import pyperclip
import ttkbootstrap as ttk
from ttkbootstrap import Style
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame
import ctypes
from appdata import AppDataPaths
import os

scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0)

app_paths = AppDataPaths('TOTP Generator',".dat","logs","locks",os.getenv("LOCALAPPDATA"))
if app_paths.require_setup:
    app_paths.setup(True)

def getScaledSize(dimension):
    newDimension = int(dimension)*(int(scale_factor)/100)
    return int(newDimension)

class Account:
    def __init__(self, secretkey, name, issuer):
        self.secretkey = secretkey
        self.name = name
        self.issuer = issuer
    
    def getSecretKey(self):
        return self.secretkey
    
    def getName(self):
        return self.name
    
    def getIssuer(self):
        return self.issuer
    
    def __str__(self) -> str:
        return f"{self.secretkey}:{self.name}:{self.issuer}"

class App(ttk.Window):
    def __init__(self):
        super().__init__(themename='darkly', title="OTP Generator", resizable=(False, False))
    
        #self.Window = self.Window()
        currentResolution = str(int(getScaledSize(600)))+("x")+str(int(getScaledSize(435)))
        self.geometry(currentResolution)
    
        self.position_center()
        self.sf = ScrolledFrame(self, height=getScaledSize(350), width=getScaledSize(200))
        self.sf.grid(column=1, row=1, rowspan=20, columnspan=4,pady=getScaledSize(5))
        self.count=1
        self.selection = ttk.StringVar()
        style = ttk.Style(theme="darkly")
        style.configure('Custom.TRadiobutton', padding=(10, 20, 10, 20), relief=FLAT)
        style.map('Custom.TRadiobutton', background=[('selected', '#424242'), ('active', '#424242')])
        for account in self.getAllAccounts():
            ttk.Radiobutton(self.sf, width=27, style="Custom.TRadiobutton", bootstyle="outline-toolbutton", variable=self.selection, text=account.getName(), value=account.getSecretKey()).grid(row=self.count, sticky='we')
            self.count += 1

        self.otp_code = ttk.StringVar(self)
        self.otp_code.set("------")
        self.remaining_time_var = ttk.StringVar(self)
        self.remaining_time_var.set("Time remaining: 0s")
    
        self.otp_code_label = ttk.Label(self, textvariable=self.otp_code, font=("Arial", 30))
        self.otp_code_label.grid(column=7, row=5)

        self.remaining_time_label = ttk.Label(self, textvariable=self.remaining_time_var, font=("Arial", 10))
        self.remaining_time_label.grid(column=7, row=10)

        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=getScaledSize(350), mode="determinate")
        self.progress_bar.grid(column=6, row=11, columnspan=3, padx= getScaledSize(25))

        self.copyBtn = ttk.Button(self, width= 54, text="Copy", command=self.code_copy)
        self.copyBtn.grid(column=6, row=20, columnspan=3, padx= getScaledSize(25))

        self.importBtn = ttk.Button(self, width= 12, bootstyle="outline", text="Import")
        self.importBtn.grid(column=1, row=21, pady=getScaledSize(10), columnspan=2)

        self.exportBtn = ttk.Button(self, width= 12, bootstyle="outline", text="Export")
        self.exportBtn.grid(column=3, row=21, columnspan=2)

        self.deleteBtn = ttk.Button(self, width= 12, bootstyle="outline-danger", text="Delete")
        self.deleteBtn.grid(column=1, row=22, columnspan=2)

        self.addBtn = ttk.Button(self, width= 12, bootstyle="outline-success", text="Add")
        self.addBtn.grid(column=3, row=22, columnspan=2)

        self.frame = ttk.Labelframe(self, bootstyle="info")
        self.frame.grid(column=3, row=1, columnspan=2)

        self.update_thread = threading.Thread(target=self.update_code_info, args=())
        self.update_thread.daemon = True
        self.update_thread.start()
    
    # TOTP secret key obtained from Discord
    totp_secret = "JBSWY3DPEHPK3PXP"

    # Create a TOTP object
    totp = pyotp.TOTP(totp_secret)

    def getAllAccounts(self):
        list = [] 
        with open(app_paths.config_path,"r") as f:
            for line in f:
                info = line.strip().split(":")
                try:
                    list.append(Account(info[0], info[1], info[2]))
                except:
                    return list
        f.close()
        return list

    def update_code_info(self):
        while True:
            # Calculate the remaining time
            current_time = datetime.datetime.now()
            remaining_time = self.totp.interval - (current_time.timestamp() % self.totp.interval)

            # Update the GUI
            self.remaining_time_var.set("Time remaining: {:.0f}s".format(remaining_time))
            if (int(remaining_time) == 30 or int(remaining_time) == 29):
                self.copyBtn.config(text= "Copy")
            try:
                self.otp_code.set(self.totp.now())
            except:
                self.otp_code.set("Invalid OTP")
                self.remaining_time_var.set("Please setup 2FA for this account again!")
                self.progress_bar["value"] = 80
                return False
            
            self.progress_bar["value"] = (remaining_time / self.totp.interval) * 100

            # Wait for 1 second
            time.sleep(1)

    def code_copy(self):
        pyperclip.copy(self.otp_code.get())
        self.copyBtn.config(text= "Copied!")

if __name__ == "__main__":
    app = App()
    app.mainloop()
