import customtkinter as ctk
from tkinter import filedialog
from core.config_manager import load_config, save_config

class SettingsPage(ctk.CTkFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, **kwargs)
        self.app_controller = app_controller

        # Load settings from config
        self.current_config = load_config()
        
        # Card Frame for content
        self.card_frame = ctk.CTkFrame(self, fg_color="#18181B", corner_radius=16, border_width=1, border_color="#27272A")
        self.card_frame.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Title
        self.title_label = ctk.CTkLabel(self.card_frame, text="Settings", font=ctk.CTkFont(family="Inter", size=32, weight="bold"), text_color="#FAFAFA")
        self.title_label.pack(pady=(40, 20), padx=40, anchor="w")
        
        # Target Organization Folder
        self.target_label = ctk.CTkLabel(self.card_frame, text="Managed Folder Destination:", text_color="#10B981", font=ctk.CTkFont(family="Inter", weight="bold"))
        self.target_label.pack(pady=(10, 5), padx=40, anchor="w")
        
        self.target_frame = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        self.target_frame.pack(fill="x", padx=40)
        
        self.target_entry = ctk.CTkEntry(self.target_frame, width=400, height=40, fg_color="#09090B", border_color="#27272A", text_color="#FAFAFA")
        self.target_entry.pack(side="left", pady=(5, 15))
        
        self.browse_button = ctk.CTkButton(self.target_frame, text="Browse", width=90, height=40, fg_color="#27272A", hover_color="#3F3F46", text_color="#FAFAFA", command=self.browse_target)
        self.browse_button.pack(side="left", padx=15, pady=(5, 15))
        
        # Load saved target
        saved_target = self.current_config.get("target_folder", "")
        if saved_target:
            self.target_entry.insert(0, saved_target)

        # Save Button
        self.save_button = ctk.CTkButton(self.card_frame, text="💾 Save Settings", font=ctk.CTkFont(family="Inter", size=14, weight="bold"), fg_color="#10B981", hover_color="#059669", text_color="#FAFAFA", height=45, corner_radius=8, command=self.save_settings)
        self.save_button.pack(pady=(20, 40), padx=40, anchor="w")

    def browse_target(self):
        folder = filedialog.askdirectory(title="Select Destination Folder")
        if folder:
            self.target_entry.delete(0, "end")
            self.target_entry.insert(0, folder)

    def on_provider_change(self, choice):
        pass

    def save_settings(self):
        # Update settings in app controller
        settings = {
            "target_folder": self.target_entry.get(),
            "provider": "Local",
            "openai_key": "",
            "gemini_key": "",
            "gemini_model": "gemini-2.5-flash"
        }
        
        # Save permanently
        save_config(settings)
        self.current_config = settings
        
        self.app_controller.update_settings(settings)
        
        # Show success message (simple label)
        success = ctk.CTkLabel(self.card_frame, text="Settings saved successfully!", text_color="#10B981", font=ctk.CTkFont(family="Inter", weight="bold"))
        success.pack(pady=10, padx=40, anchor="w")
        self.after(3000, success.destroy)
