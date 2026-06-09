import customtkinter as ctk
from ui.scan_page import ScanPage
from ui.preview_page import PreviewPage
from ui.settings_page import SettingsPage
from core.scanner import FolderScanner
from core.preview_builder import PreviewBuilder
from core.organizer import FileOrganizer
from database.undo_repository import undo_batch, get_last_batch_id

class AppController:
    def __init__(self):
        self.settings = {
            "provider": "Local",
            "openai_key": "",
            "gemini_key": "AIzaSyC4Rs1ekPEsGmYbwiZmIE7hHlISIkDuLq4", 
            "gemini_model": "gemini-2.5-flash"
        }
        self.last_tree = None
        self.root_folder = None
        
        # We need a reference to the main app to change pages and write logs
        self.app = None

    def set_app(self, app):
        self.app = app

    def log(self, message):
        if self.app and hasattr(self.app, "append_log"):
            self.app.append_log(message)
        print(message)

    def update_settings(self, new_settings):
        self.settings.update(new_settings)

    def run_scan_and_ai(self, folder_paths, status_callback, completion_callback):
        # We don't use self.root_folder anymore, since we have multiple
        # and the destination is from config.
        try:
            status_callback("Scanning folders...")
            scanner = FolderScanner()
            files_metadata = []
            total_folders = 0
            seen_hashes = {}
            for path in folder_paths:
                self.log(f"> Scanning \"{path}\"")
                # Append results
                files, folder_count = scanner.scan_directory(path, lambda count: status_callback(f"Scanned {len(files_metadata) + count} files..."), seen_hashes=seen_hashes)
                files_metadata.extend(files)
                total_folders += folder_count
            
            self.log(f"> Scan Complete: Found {len(files_metadata)} files across {total_folders} folders.")
            
            if not files_metadata:
                completion_callback(False, "No files found to organize.")
                return

            self.log(f"> Preparing {len(files_metadata)} files for Smart Local Analysis...")
            status_callback(f"Starting Smart Local Analysis for {len(files_metadata)} files...", progress=0.0)
            
            # Always use local offline provider, bypassing all cloud AI settings
            from providers.local_provider import LocalProvider
            provider = LocalProvider()

            # Batching to prevent huge JSON syntax errors
            BATCH_SIZE = 300
            total_batches = (len(files_metadata) + BATCH_SIZE - 1) // BATCH_SIZE
            builder = PreviewBuilder()
            combined_tree = {}
            
            for i in range(0, len(files_metadata), BATCH_SIZE):
                batch_num = (i // BATCH_SIZE) + 1
                batch_files = files_metadata[i:i + BATCH_SIZE]
                
                self.log(f"> Analyzing file batch {batch_num}/{total_batches} ({len(batch_files)} files)...")
                
                # Show informative text with progress percentage
                current_file_count = min(i + BATCH_SIZE, len(files_metadata))
                status_callback(f"Analyzing batch {batch_num}/{total_batches} ({current_file_count}/{len(files_metadata)} files)...", progress=(batch_num - 1) / total_batches)
                
                response_json = provider.classify_files(batch_files)
                
                self.log(f"> Batch {batch_num} analysis complete. Building preview...")
                try:
                    batch_tree = builder.parse_ai_response(response_json)
                    # Merge batch_tree into combined_tree
                    for cat, content in batch_tree.items():
                        if cat not in combined_tree:
                            combined_tree[cat] = {"_files": []}
                        
                        for subcat_or_files, items in content.items():
                            if subcat_or_files == "_files":
                                combined_tree[cat]["_files"].extend(items)
                            else:
                                if subcat_or_files not in combined_tree[cat]:
                                    combined_tree[cat][subcat_or_files] = []
                                combined_tree[cat][subcat_or_files].extend(items)
                except Exception as e:
                    self.log(f"! Warning: Failed to parse batch {batch_num}: {e}")
                    # We continue to the next batch even if one fails
                    
            if not combined_tree:
                raise ValueError("Failed to classify any files. Please check the logs.")
                
            self.last_tree = combined_tree
            self.log("> Smart analysis complete. Ready for preview.")
            status_callback("Smart Organization complete. Please review the preview.", progress=1.0)
            completion_callback(True, "Analysis complete.")
        except Exception as e:
            completion_callback(False, f"Error: {e}")

    def delete_duplicates(self):
        """Physically deletes all files categorized as Duplicates and removes them from the tree."""
        if not self.last_tree:
            return 0, 0
            
        duplicates = self.last_tree.get("Duplicates", {})
        if not duplicates:
            return 0, 0
            
        import os
        from pathlib import Path
        
        deleted_count = 0
        failed_count = 0
        
        # Iterate over subcategories inside Duplicates (usually just empty string "")
        for subcat, items in duplicates.items():
            for item in items:
                path = item["path"]
                try:
                    if Path(path).exists():
                        os.remove(path)
                        deleted_count += 1
                        self.log(f"> Deleted duplicate: {path}")
                except Exception as e:
                    failed_count += 1
                    self.log(f"> Failed to delete {path}: {e}")
                    
        # Remove Duplicates from the tree so they aren't moved later
        if "Duplicates" in self.last_tree:
            del self.last_tree["Duplicates"]
            
        return deleted_count, failed_count

    def show_scan_page(self):
        self.app.show_frame(ScanPage)
        
    def show_preview_page(self):
        # Update the tree view before showing
        if self.last_tree:
            self.app.preview_page.populate_tree(self.last_tree)
        self.app.show_frame(PreviewPage)
        
    def show_settings_page(self):
        self.app.show_frame(SettingsPage)

    def apply_organization(self, progress_callback=None):
        if not self.last_tree:
            return False
            
        try:
            from core.organizer import FileOrganizer
            from pathlib import Path
            from core.config_manager import get_target_folder
            
            # Use configured target folder
            saved_target = get_target_folder()
            if not saved_target:
                self.log("! Error: Destination folder not set. Please set it in Settings first.")
                # Show error popup
                import tkinter.messagebox as messagebox
                messagebox.showerror("Error", "Please set the Managed Folder Destination in Settings first!")
                return False
                
            target_folder = Path(saved_target)
            
            self.log(f"> Starting file organization in {target_folder}")
            
            organizer = FileOrganizer(str(target_folder), log_callback=self.log)
            
            self.log("> Executing moves...")
            organizer.apply_organization(self.last_tree, progress_callback=progress_callback)
            self.log("> Organization finished successfully.")
            return True
        except Exception as e:
            self.log(f"Error applying organization: {e}")
            print(f"Failed to apply: {e}")
            return False

    def undo_last_operation(self, progress_callback=None):
        batch_id = get_last_batch_id()
        if not batch_id:
            return 0, 0
        return undo_batch(batch_id, log_callback=self.log, progress_callback=progress_callback)


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Apply modern premium dark theme
        ctk.set_appearance_mode("dark")

        self.title("Smart Organizer Enterprise")
        self.geometry("1100x800")
        # Deep Dark Blue Background
        self.configure(fg_color="#0F172A")
        
        # Configure grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.controller = AppController()
        self.controller.set_app(self)

        # Create Navigation Sidebar (Slate-900 / Very Dark Blue)
        self.sidebar_frame = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color="#0B0F19")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1) # push storage down

        # Logo Area
        self.logo_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.logo_frame.grid(row=0, column=0, padx=20, pady=(35, 30), sticky="w")
        
        self.logo_title = ctk.CTkLabel(self.logo_frame, text="Smart Organizer", font=ctk.CTkFont(family="Inter", size=22, weight="bold"), text_color="#F8FAFC")
        self.logo_title.pack(anchor="w")
        self.logo_subtitle = ctk.CTkLabel(self.logo_frame, text="ENTERPRISE EDITION", font=ctk.CTkFont(family="Inter", size=10, weight="bold"), text_color="#94A3B8")
        self.logo_subtitle.pack(anchor="w")

        # Nav Buttons
        nav_font = ctk.CTkFont(family="Inter", size=14, weight="bold")
        self.nav_scan = ctk.CTkButton(self.sidebar_frame, text="  📁 Scan Folders", font=nav_font, fg_color="transparent", text_color="#F8FAFC", hover_color="#1E293B", anchor="w", command=self.controller.show_scan_page)
        self.nav_scan.grid(row=1, column=0, padx=15, pady=5, sticky="ew")

        self.nav_preview = ctk.CTkButton(self.sidebar_frame, text="  👁️ Preview", font=nav_font, fg_color="transparent", text_color="#F8FAFC", hover_color="#1E293B", anchor="w", command=self.controller.show_preview_page)
        self.nav_preview.grid(row=2, column=0, padx=15, pady=5, sticky="ew")

        self.nav_settings = ctk.CTkButton(self.sidebar_frame, text="  ⚙️ Settings", font=nav_font, fg_color="transparent", text_color="#F8FAFC", hover_color="#1E293B", anchor="w", command=self.controller.show_settings_page)
        self.nav_settings.grid(row=3, column=0, padx=15, pady=5, sticky="ew")

        # Storage Status
        self.storage_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.storage_frame.grid(row=6, column=0, sticky="s", padx=20, pady=(0, 30))
        
        self.storage_label = ctk.CTkLabel(self.storage_frame, text="STORAGE STATUS", font=ctk.CTkFont(family="Inter", size=11, weight="bold"), text_color="#94A3B8")
        self.storage_label.pack(anchor="w")
        self.storage_bar = ctk.CTkProgressBar(self.storage_frame, width=180, height=6, progress_color="#06B6D4", fg_color="#1E293B")
        self.storage_bar.pack(pady=(8, 5), anchor="w")
        self.storage_bar.set(0.7) # Mockup
        self.storage_text = ctk.CTkLabel(self.storage_frame, text="42.8 GB of 60 GB used", font=ctk.CTkFont(family="Inter", size=10), text_color="#94A3B8")
        self.storage_text.pack(anchor="w")

        # Create main content area
        self.main_container = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_container.grid_rowconfigure(0, weight=3)
        self.main_container.grid_columnconfigure(0, weight=1)

        # Bottom Console Log Area
        self.log_container = ctk.CTkFrame(self.main_container, fg_color="#0B0F19", corner_radius=8, border_width=1, border_color="#1E293B")
        self.log_container.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 20))
        self.log_container.grid_rowconfigure(1, weight=1)
        self.log_container.grid_columnconfigure(0, weight=1)

        # Terminal Header
        self.log_header_frame = ctk.CTkFrame(self.log_container, fg_color="transparent", height=30)
        self.log_header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(8, 0))
        
        # Left: Title
        self.log_header_left = ctk.CTkFrame(self.log_header_frame, fg_color="transparent")
        self.log_header_left.pack(side="left")
        self.log_icon = ctk.CTkLabel(self.log_header_left, text=">_ ", font=ctk.CTkFont(family="Consolas", size=12, weight="bold"), text_color="#06B6D4")
        self.log_icon.pack(side="left")
        self.log_header = ctk.CTkLabel(self.log_header_left, text="DEVELOPER CONSOLE", font=ctk.CTkFont(family="Inter", size=11, weight="bold"), text_color="#F8FAFC")
        self.log_header.pack(side="left")
        
        # Right: Mac Dots
        self.dots_frame = ctk.CTkFrame(self.log_header_frame, fg_color="transparent")
        self.dots_frame.pack(side="right")
        ctk.CTkLabel(self.dots_frame, text="●", text_color="#EF4444", font=ctk.CTkFont(size=14)).pack(side="left", padx=2)
        ctk.CTkLabel(self.dots_frame, text="●", text_color="#F59E0B", font=ctk.CTkFont(size=14)).pack(side="left", padx=2)
        ctk.CTkLabel(self.dots_frame, text="●", text_color="#10B981", font=ctk.CTkFont(size=14)).pack(side="left", padx=2)

        self.log_textbox = ctk.CTkTextbox(
            self.log_container, 
            fg_color="transparent", 
            text_color="#10B981", # Hacker Green
            font=ctk.CTkFont(family="Consolas", size=12),
            wrap="word"
        )
        self.log_textbox.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.log_textbox.configure(state="disabled")
        
        # Configure tags for colors
        self.log_textbox.tag_config("white", foreground="#F8FAFC")

        # Initialize pages
        self.scan_page = ScanPage(self.main_container, self.controller, fg_color="transparent")
        self.preview_page = PreviewPage(self.main_container, self.controller, fg_color="transparent")
        self.settings_page = SettingsPage(self.main_container, self.controller, fg_color="transparent")

        self.pages = {
            ScanPage: self.scan_page,
            PreviewPage: self.preview_page,
            SettingsPage: self.settings_page
        }

        # Show initial frame
        self.show_frame(ScanPage)

    def show_frame(self, page_class):
        for frame in self.pages.values():
            frame.grid_remove()
            
        frame = self.pages[page_class]
        frame.grid(row=0, column=0, sticky="nsew")
        
        # Update Nav Active State
        self.nav_scan.configure(fg_color="#1E293B" if page_class == ScanPage else "transparent")
        self.nav_preview.configure(fg_color="#1E293B" if page_class == PreviewPage else "transparent")
        self.nav_settings.configure(fg_color="#1E293B" if page_class == SettingsPage else "transparent")

    def append_log(self, message):
        self.log_textbox.configure(state="normal")
        if message.startswith("|WHITE|"):
            self.log_textbox.insert("end", message.replace("|WHITE|", "") + "\n", "white")
        else:
            self.log_textbox.insert("end", message + "\n")
        self.log_textbox.yview("end")
        self.log_textbox.configure(state="disabled")
        self.update()
