import os
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox

import main  # our hashing logic

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class HashWatchApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("HashWatch - File Integrity Monitor")
        self.geometry("850x600")

        self.notebook = ctk.CTkTabview(self)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=20)

        self.monitor_tab = self.notebook.add("Monitor")
        self.reports_tab = self.notebook.add("Reports")
        self.settings_tab = self.notebook.add("Settings")

        self.create_monitor_tab()
        self.create_reports_tab()
        self.create_settings_tab()

    def create_monitor_tab(self):
        self.folder_path_var = tk.StringVar()

        ctk.CTkLabel(self.monitor_tab, text="Select Folder to Monitor:").pack(pady=10)
        self.folder_entry = ctk.CTkEntry(self.monitor_tab, textvariable=self.folder_path_var, width=500)
        self.folder_entry.pack(pady=5)

        browse_btn = ctk.CTkButton(self.monitor_tab, text="Browse", command=self.browse_folder)
        browse_btn.pack(pady=5)

        baseline_btn = ctk.CTkButton(self.monitor_tab, text="Generate Baseline", command=self.generate_baseline)
        baseline_btn.pack(pady=5)

        check_btn = ctk.CTkButton(self.monitor_tab, text="Check Integrity", command=self.check_integrity)
        check_btn.pack(pady=5)

    def create_reports_tab(self):
        ctk.CTkLabel(self.reports_tab, text="Available Reports:").pack(pady=10)

        self.report_listbox = tk.Listbox(self.reports_tab, height=10, width=50)
        self.report_listbox.pack(pady=5)

        refresh_btn = ctk.CTkButton(self.reports_tab, text="Refresh List", command=self.refresh_reports)
        refresh_btn.pack(pady=5)

        view_btn = ctk.CTkButton(self.reports_tab, text="View Report", command=self.view_report)
        view_btn.pack(pady=5)

        self.report_text = tk.Text(self.reports_tab, wrap="word", height=20, width=80, state="disabled")
        self.report_text.pack(pady=10)

        self.refresh_reports()

    def create_settings_tab(self):
        ctk.CTkLabel(self.settings_tab, text="Appearance:").pack(pady=10)

        switch = ctk.CTkSwitch(self.settings_tab, text="Dark Mode", command=self.toggle_theme)
        switch.pack(pady=10)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path_var.set(folder)

    def generate_baseline(self):
        folder = self.folder_path_var.get()
        if not folder:
            messagebox.showerror("Error", "Please select a folder first.")
            return
        main.generate_baseline(folder)
        messagebox.showinfo("Success", f"Baseline generated for {folder}.")

    def check_integrity(self):
        folder = self.folder_path_var.get()
        if not folder:
            messagebox.showerror("Error", "Please select a folder first.")
            return
        main.check_integrity(folder)
        messagebox.showinfo("Completed", f"Integrity check finished for {folder}.")

    def refresh_reports(self):
        self.report_listbox.delete(0, tk.END)
        if not os.path.exists("reports"):
            os.makedirs("reports")
        for file in os.listdir("reports"):
            if file.endswith(".txt"):
                self.report_listbox.insert(tk.END, file)

    def view_report(self):
        selected = self.report_listbox.curselection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a report first.")
            return
        filename = self.report_listbox.get(selected[0])
        filepath = os.path.join("reports", filename)

        with open(filepath, "r") as f:
            content = f.read()

        self.report_text.configure(state="normal")
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(tk.END, content)
        self.report_text.configure(state="disabled")

    def toggle_theme(self):
        if ctk.get_appearance_mode() == "Dark":
            ctk.set_appearance_mode("Light")
        else:
            ctk.set_appearance_mode("Dark")

if __name__ == "__main__":
    app = HashWatchApp()
    app.mainloop()
