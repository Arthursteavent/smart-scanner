import customtkinter as ctk
from tkinter import filedialog
import threading
from pathlib import Path

class ScanPage(ctk.CTkFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, **kwargs)
        self.app_controller = app_controller
        self.selected_paths = [] # List to hold multiple folders

        # Card Frame for content
        self.card_frame = ctk.CTkFrame(self, fg_color="#18181B", corner_radius=16, border_width=1, border_color="#27272A")
        self.card_frame.pack(fill="both", expand=True, padx=40, pady=20)

        # Title
        self.title_label = ctk.CTkLabel(self.card_frame, text="Scan Folders", font=ctk.CTkFont(family="Inter", size=32, weight="bold"), text_color="#FAFAFA")
        self.title_label.pack(pady=(40, 5), padx=40, anchor="w")

        # Instruction
        self.info_label = ctk.CTkLabel(self.card_frame, text="Add one or more folders to analyze. We will aggregate and organize them.", text_color="#A1A1AA", font=ctk.CTkFont(family="Inter", size=14))
        self.info_label.pack(pady=(0, 30), padx=40, anchor="w")

        # Select Folder Button
        self.select_button = ctk.CTkButton(
            self.card_frame, 
            text="➕ Add Folder", 
            font=ctk.CTkFont(family="Inter", size=14, weight="bold"), 
            fg_color="#27272A", 
            hover_color="#3F3F46",
            text_color="#FAFAFA",
            height=40,
            corner_radius=8,
            command=self.select_folder
        )
        self.select_button.pack(pady=(0, 15), padx=40, anchor="w")

        # Scrollable Frame for Selected Folders
        self.folders_frame = ctk.CTkScrollableFrame(self.card_frame, height=120, fg_color="#09090B", corner_radius=8, border_width=1, border_color="#27272A")
        self.folders_frame.pack(fill="both", expand=True, padx=40, pady=0)

        # Empty state label
        self.empty_label = ctk.CTkLabel(self.folders_frame, text="No folders added yet.", text_color="#52525B", font=ctk.CTkFont(family="Inter", size=13))
        self.empty_label.pack(pady=20)

        # Progress Section
        self.progress_frame = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        self.progress_frame.pack(fill="x", padx=40, pady=25)
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, width=500, height=8, progress_color="#10B981", fg_color="#27272A")
        self.progress_bar.pack(anchor="w")
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(self.progress_frame, text="", text_color="#A1A1AA", font=ctk.CTkFont(family="Inter", size=12))
        self.status_label.pack(pady=(8, 0), anchor="w")

        # Start Button
        self.start_button = ctk.CTkButton(
            self.card_frame, 
            text="🚀 Start Intelligent Scan", 
            font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
            fg_color="#6366F1",
            hover_color="#4F46E5",
            text_color="#FFFFFF",
            height=50,
            corner_radius=8,
            state="disabled",
            command=self.start_process
        )
        self.start_button.pack(pady=(10, 25), padx=40, fill="x")

    def select_folder(self):
        folder_path = filedialog.askdirectory(title="Select Folder to Organize")
        if folder_path and folder_path not in self.selected_paths:
            self.selected_paths.append(folder_path)
            self.refresh_folder_list()
            self.start_button.configure(state="normal")

    def remove_folder(self, path):
        if path in self.selected_paths:
            self.selected_paths.remove(path)
            self.refresh_folder_list()
            if not self.selected_paths:
                self.start_button.configure(state="disabled")

    def refresh_folder_list(self):
        # Clear existing widgets
        for widget in self.folders_frame.winfo_children():
            widget.destroy()

        if not self.selected_paths:
            self.empty_label = ctk.CTkLabel(self.folders_frame, text="No folders added yet.", text_color="#52525B", font=ctk.CTkFont(family="Inter", size=13))
            self.empty_label.pack(pady=40)
            return

        # Add items
        for path in self.selected_paths:
            row_frame = ctk.CTkFrame(self.folders_frame, fg_color="#18181B", corner_radius=6)
            row_frame.pack(fill="x", pady=4, padx=5)
            
            lbl = ctk.CTkLabel(row_frame, text=path, text_color="#FAFAFA", font=ctk.CTkFont(family="Inter", size=13))
            lbl.pack(side="left", padx=15, pady=8)
            
            btn = ctk.CTkButton(
                row_frame, text="✕", width=28, height=28, fg_color="#EF4444", hover_color="#DC2626", text_color="#FFFFFF", corner_radius=6,
                command=lambda p=path: self.remove_folder(p)
            )
            btn.pack(side="right", padx=10, pady=8)

    def start_process(self):
        if not self.selected_paths:
            return
            
        self.start_button.configure(state="disabled")
        self.select_button.configure(state="disabled")
        
        # Also disable remove buttons
        for widget in self.folders_frame.winfo_children():
            for child in widget.winfo_children():
                if isinstance(child, ctk.CTkButton):
                    child.configure(state="disabled")
                    
        self.status_label.configure(text="Scanning files across all folders...")
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()
        
        # Pass the list of paths instead of a single path
        thread = threading.Thread(target=self.app_controller.run_scan_and_ai, args=(self.selected_paths, self.update_status, self.on_process_complete))
        thread.start()

    def update_status(self, text):
        self.after(0, lambda: self.status_label.configure(text=text))

    def on_process_complete(self, success, message):
        self.after(0, lambda: self._handle_completion(success, message))
        
    def _handle_completion(self, success, message):
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(1)
        self.status_label.configure(text=message)
        
        self.select_button.configure(state="normal")
        self.start_button.configure(state="normal")
        
        # Re-enable remove buttons
        self.refresh_folder_list()
        
        if success:
            self.app_controller.show_preview_page()
