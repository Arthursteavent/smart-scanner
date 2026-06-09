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
        self.card_frame = ctk.CTkFrame(self, fg_color="#1E293B", corner_radius=16, border_width=1, border_color="#334155")
        self.card_frame.pack(fill="both", expand=True, padx=40, pady=20)

        # Title
        self.title_label = ctk.CTkLabel(self.card_frame, text="Pindai Folder", font=ctk.CTkFont(family="Inter", size=28, weight="bold"), text_color="#F8FAFC")
        self.title_label.pack(pady=(40, 5), padx=40, anchor="w")

        # Instruction
        self.info_label = ctk.CTkLabel(self.card_frame, text="Tambahkan satu atau lebih folder untuk dianalisis. Sistem kami akan secara cerdas\nmengumpulkan data dan mengatur struktur file Anda secara otomatis.", text_color="#94A3B8", font=ctk.CTkFont(family="Inter", size=13), justify="left")
        self.info_label.pack(pady=(0, 25), padx=40, anchor="w")

        # Action Top Row
        self.action_top_frame = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        self.action_top_frame.pack(fill="x", padx=40, pady=(0, 20), anchor="w")

        # Select Folder Button
        self.select_button = ctk.CTkButton(
            self.action_top_frame, 
            text="➕ Tambah Folder", 
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"), 
            fg_color="#06B6D4", 
            hover_color="#0891B2",
            text_color="#F8FAFC",
            height=38,
            corner_radius=8,
            command=self.select_folder
        )
        self.select_button.pack(side="left")

        # Quick Add Recommended Folders
        self.quick_add_frame = ctk.CTkFrame(self.action_top_frame, fg_color="transparent")
        self.quick_add_frame.pack(side="left", padx=(20, 0))
        
        quick_add_label = ctk.CTkLabel(self.quick_add_frame, text="Cepat Tambah:", text_color="#94A3B8", font=ctk.CTkFont(family="Inter", size=12, weight="bold"))
        quick_add_label.pack(side="left", padx=(0, 10))

        home_path = Path.home()
        for folder_name in ["Downloads", "Documents", "Desktop"]:
            folder_path = home_path / folder_name
            if folder_path.exists():
                btn = ctk.CTkButton(
                    self.quick_add_frame,
                    text=folder_name,
                    font=ctk.CTkFont(family="Inter", size=12),
                    fg_color="#334155",
                    hover_color="#475569",
                    text_color="#F8FAFC",
                    height=28,
                    corner_radius=14,
                    command=lambda p=str(folder_path): self.add_specific_folder(p)
                )
                btn.pack(side="left", padx=4)

        # Daftar Path Aktif Header
        self.list_header_frame = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        self.list_header_frame.pack(fill="x", padx=40, pady=(10, 0))
        ctk.CTkLabel(self.list_header_frame, text="Daftar Path Aktif", font=ctk.CTkFont(family="Inter", size=13, weight="bold"), text_color="#F8FAFC").pack(side="left")
        self.folder_count_label = ctk.CTkLabel(self.list_header_frame, text="0 Folder Terdeteksi", font=ctk.CTkFont(family="Inter", size=12), text_color="#94A3B8")
        self.folder_count_label.pack(side="right")

        # Progress Section (Packed bottom first so it stays at the bottom)
        self.progress_frame = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        self.progress_frame.pack(side="bottom", fill="x", padx=40, pady=(0, 20))
        
        self.status_header_frame = ctk.CTkFrame(self.progress_frame, fg_color="transparent")
        self.status_header_frame.pack(fill="x", pady=(0, 5))
        
        self.status_title = ctk.CTkLabel(self.status_header_frame, text="Mempersiapkan Scan...", text_color="#06B6D4", font=ctk.CTkFont(family="Inter", size=12, weight="bold"))
        self.status_title.pack(side="left")
        self.pct_label = ctk.CTkLabel(self.status_header_frame, text="0%", text_color="#06B6D4", font=ctk.CTkFont(family="Inter", size=18, weight="bold"))
        self.pct_label.pack(side="right")
        
        self.status_label = ctk.CTkLabel(self.progress_frame, text="Sistem siap untuk melakukan pengindeksan file.", text_color="#94A3B8", font=ctk.CTkFont(family="Inter", size=11))
        self.status_label.pack(anchor="w", pady=(0, 8))

        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, height=8, progress_color="#06B6D4", fg_color="#334155")
        self.progress_bar.pack(fill="x")
        self.progress_bar.set(0)

        # Start Button (Packed bottom, above progress frame)
        self.start_button = ctk.CTkButton(
            self.card_frame, 
            text="🚀 Mulai Pindai Cerdas", 
            font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
            fg_color="#D8B4FE",
            hover_color="#C084FC",
            text_color="#0F172A",
            height=45,
            corner_radius=8,
            state="disabled",
            command=self.start_process
        )
        self.start_button.pack(side="bottom", pady=(0, 20), padx=40, fill="x")

        # Scrollable Frame for Selected Folders (Takes up remaining middle space)
        self.folders_frame = ctk.CTkScrollableFrame(self.card_frame, height=140, fg_color="#0F172A", corner_radius=8, border_width=1, border_color="#334155")
        self.folders_frame.pack(fill="both", expand=True, padx=40, pady=(5, 15))

    def select_folder(self):
        folder_path = filedialog.askdirectory(title="Select Folder to Organize")
        if folder_path:
            self.add_specific_folder(folder_path)

    def add_specific_folder(self, folder_path):
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
            self.folder_count_label.configure(text="0 Folder Terdeteksi")
            
            # Placeholder dashed box
            placeholder_frame = ctk.CTkFrame(self.folders_frame, fg_color="transparent", border_width=1, border_color="#334155", corner_radius=8)
            placeholder_frame.pack(fill="both", expand=True, padx=20, pady=20)
            ctk.CTkLabel(placeholder_frame, text="📁\nTarik folder ke sini untuk menambah", text_color="#64748B", font=ctk.CTkFont(family="Inter", size=13)).pack(expand=True)
            return

        self.folder_count_label.configure(text=f"{len(self.selected_paths)} Folder Terdeteksi")

        # Add items
        for path in self.selected_paths:
            row_frame = ctk.CTkFrame(self.folders_frame, fg_color="#1E293B", corner_radius=8, border_width=1, border_color="#334155")
            row_frame.pack(fill="x", pady=5, padx=5)
            
            icon_lbl = ctk.CTkLabel(row_frame, text="📁", font=ctk.CTkFont(size=24))
            icon_lbl.pack(side="left", padx=(15, 10), pady=10)
            
            text_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            text_frame.pack(side="left", fill="x", expand=True, pady=10)
            
            path_lbl = ctk.CTkLabel(text_frame, text=path, text_color="#F8FAFC", font=ctk.CTkFont(family="Inter", size=13, weight="bold"))
            path_lbl.pack(anchor="w")
            sub_lbl = ctk.CTkLabel(text_frame, text="System Path • Menunggu Scan", text_color="#94A3B8", font=ctk.CTkFont(family="Inter", size=11))
            sub_lbl.pack(anchor="w")
            
            btn = ctk.CTkButton(
                row_frame, text="✕", width=32, height=32, fg_color="transparent", hover_color="#EF4444", text_color="#94A3B8", corner_radius=6,
                command=lambda p=path: self.remove_folder(p)
            )
            btn.pack(side="right", padx=15, pady=10)
            
        # Add drop placeholder at bottom
        drop_frame = ctk.CTkFrame(self.folders_frame, fg_color="transparent", border_width=1, border_color="#334155", corner_radius=8)
        drop_frame.pack(fill="x", padx=5, pady=(10, 5))
        ctk.CTkLabel(drop_frame, text="Tarik folder ke sini untuk menambah", text_color="#64748B", font=ctk.CTkFont(family="Inter", size=12)).pack(pady=15)

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
                    
        # Also disable quick add buttons
        for widget in self.quick_add_frame.winfo_children():
            if isinstance(widget, ctk.CTkButton):
                widget.configure(state="disabled")

        self.status_label.configure(text="Scanning files across all folders...")
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()
        
        # Pass the list of paths instead of a single path
        thread = threading.Thread(target=self.app_controller.run_scan_and_ai, args=(self.selected_paths, self.update_status, self.on_process_complete))
        thread.start()

    def update_status(self, text, progress=None):
        def _update():
            self.status_label.configure(text=text)
            if progress is not None:
                if self.progress_bar.cget("mode") != "determinate":
                    self.progress_bar.configure(mode="determinate")
                    self.progress_bar.stop()
                self.progress_bar.set(progress)
                self.pct_label.configure(text=f"{int(progress * 100)}%")
            else:
                if self.progress_bar.cget("mode") != "indeterminate":
                    self.progress_bar.configure(mode="indeterminate")
                    self.progress_bar.start()
                self.pct_label.configure(text="--%")
        self.after(0, _update)

    def on_process_complete(self, success, message):
        self.after(0, lambda: self._handle_completion(success, message))
        
    def _handle_completion(self, success, message):
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(1)
        self.status_label.configure(text=message)
        
        self.select_button.configure(state="normal")
        self.start_button.configure(state="normal")
        
        # Re-enable quick add buttons
        for widget in self.quick_add_frame.winfo_children():
            if isinstance(widget, ctk.CTkButton):
                widget.configure(state="normal")
                
        # Re-enable remove buttons
        self.refresh_folder_list()
        
        if success:
            self.app_controller.show_preview_page()
