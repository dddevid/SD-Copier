import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import win32api
import win32file
import wmi
import ctypes
import os

class SDCopyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SD Copy Utility")
        self.root.geometry("400x200")
        
        self.wmi_obj = wmi.WMI()

        style = ttk.Style()
        style.configure('TLabel', font=('Helvetica', 12))
        style.configure('TButton', font=('Helvetica', 12))
        style.configure('TCombobox', font=('Helvetica', 12))

        self.source_label = ttk.Label(root, text="Select Source SD:")
        self.source_label.pack(pady=10)

        self.source_drive = tk.StringVar()
        self.source_dropdown = ttk.Combobox(root, textvariable=self.source_drive, values=self.get_physical_drives(), state='readonly')
        self.source_dropdown.pack(pady=10)

        self.destination_label = ttk.Label(root, text="Select Destination SD:")
        self.destination_label.pack(pady=10)

        self.destination_drive = tk.StringVar()
        self.destination_dropdown = ttk.Combobox(root, textvariable=self.destination_drive, values=self.get_physical_drives(), state='readonly')
        self.destination_dropdown.pack(pady=10)

        self.copy_button = ttk.Button(root, text="Copy SD Card", command=self.confirm_and_copy_sd_card)
        self.copy_button.pack(pady=20)

    def get_physical_drives(self):
        drives = []
        for drive in self.wmi_obj.Win32_DiskDrive():
            drives.append(drive.DeviceID)
        return drives

    def confirm_and_copy_sd_card(self):
        source_drive = self.source_drive.get()
        destination_drive = self.destination_drive.get()

        if not source_drive or not destination_drive:
            messagebox.showerror("Error", "Please select both source and destination drives.")
            return

        if messagebox.askyesno("Confirm", f"Are you sure you want to format and copy {source_drive} to {destination_drive}? This will overwrite the destination drive's data."):
            # Second confirmation for the process
            if messagebox.askyesno("Warning", "This process might take some time. Do you want to proceed with formatting and copying the SD card?"):
                self.format_and_copy_sd_card(source_drive, destination_drive)

    def format_and_copy_sd_card(self, source_drive, destination_drive):
        try:
            # Format the destination drive
            drive_letter = destination_drive[0]
            if not self.format_drive(drive_letter):
                messagebox.showerror("Error", "Failed to format the destination drive.")
                return

            # Proceed with the copy operation
            self.copy_sd_card(source_drive, destination_drive)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def format_drive(self, drive_letter):
        try:
            # Using the DeviceIoControl API to format the drive
            # Obtain a handle to the drive
            drive_path = f"\\\\.\\{drive_letter}:"
            handle = win32file.CreateFile(
                drive_path,
                win32file.GENERIC_WRITE,
                0,
                None,
                win32file.OPEN_EXISTING,
                0,
                None
            )
            
            # The IOCTL_DISK_FORMAT_TRACKS control code formats the drive
            # NOTE: This is a simplified example. In practice, you'd need more parameters
            IOCTL_DISK_FORMAT_TRACKS = 0x00074000
            result = win32file.DeviceIoControl(
                handle,
                IOCTL_DISK_FORMAT_TRACKS,
                None,
                None
            )
            win32api.CloseHandle(handle)
            return result is not None
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while formatting the drive: {e}")
            return False

    def copy_sd_card(self, source_drive, destination_drive):
        try:
            # Open the source SD card in read mode
            source_handle = win32file.CreateFile(
                source_drive,
                win32file.GENERIC_READ,
                win32file.FILE_SHARE_READ,
                None,
                win32file.OPEN_EXISTING,
                0,
                None
            )

            # Open the destination SD card in write mode
            destination_handle = win32file.CreateFile(
                destination_drive,
                win32file.GENERIC_WRITE,
                0,
                None,
                win32file.CREATE_ALWAYS,
                0,
                None
            )

            # Copy data
            while True:
                data = win32file.ReadFile(source_handle, 4096)[1]
                if not data:
                    break
                win32file.WriteFile(destination_handle, data)

            # Close file handles
            win32api.CloseHandle(source_handle)
            win32api.CloseHandle(destination_handle)

            messagebox.showinfo("Success", "Copy completed successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during the copy: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SDCopyApp(root)
    root.mainloop()
