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
            status_callback("Starting Smart Local Analysis...")
            
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
                status_callback(f"Analyzing batch {batch_num}/{total_batches}...")
                
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
            status_callback("Smart Organization complete. Please review the preview.")
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

    def apply_organization(self):
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
            organizer.apply_organization(self.last_tree)
            self.log("> Organization finished successfully.")
            return True
        except Exception as e:
            self.log(f"Error applying organization: {e}")
            print(f"Failed to apply: {e}")
            return False

    def undo_last_operation(self):
        batch_id = get_last_batch_id()
        if not batch_id:
            return 0, 0
        return undo_batch(batch_id)


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Apply modern premium dark theme
        ctk.set_appearance_mode("dark")

        self.title("Smart Folder Manager Enterprise")
        self.geometry("1000x750")
        # Ultra Dark Background
        self.configure(fg_color="#09090B")
        
        # Configure grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.controller = AppController()
        self.controller.set_app(self)

        # Create Navigation Sidebar (Premium Zinc-900)
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#18181B")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        # Logo Area
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Smart\nOrganizer", font=ctk.CTkFont(family="Inter", size=26, weight="bold"), text_color="#6366F1")
        self.logo_label.grid(row=0, column=0, padx=20, pady=(35, 30), sticky="w")

        # Nav Buttons
        nav_font = ctk.CTkFont(family="Inter", size=14, weight="bold")
        self.nav_scan = ctk.CTkButton(self.sidebar_frame, text="  📁 Scan Folders", font=nav_font, fg_color="transparent", text_color="#E4E4E7", hover_color="#27272A", anchor="w", command=self.controller.show_scan_page)
        self.nav_scan.grid(row=1, column=0, padx=15, pady=10, sticky="ew")

        self.nav_preview = ctk.CTkButton(self.sidebar_frame, text="  👁️ Preview", font=nav_font, fg_color="transparent", text_color="#E4E4E7", hover_color="#27272A", anchor="w", command=self.controller.show_preview_page)
        self.nav_preview.grid(row=2, column=0, padx=15, pady=10, sticky="ew")

        self.nav_settings = ctk.CTkButton(self.sidebar_frame, text="  ⚙️ Settings", font=nav_font, fg_color="transparent", text_color="#E4E4E7", hover_color="#27272A", anchor="w", command=self.controller.show_settings_page)
        self.nav_settings.grid(row=3, column=0, padx=15, pady=10, sticky="ew")

        # Create main content area
        self.main_container = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_container.grid_rowconfigure(0, weight=3)
        self.main_container.grid_columnconfigure(0, weight=1)

        # Bottom Console Log Area
        self.log_container = ctk.CTkFrame(self.main_container, fg_color="#000000", corner_radius=8, border_width=1, border_color="#27272A")
        self.log_container.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 20))
        self.log_container.grid_rowconfigure(1, weight=1)
        self.log_container.grid_columnconfigure(0, weight=1)

        # Terminal Header
        self.log_header = ctk.CTkLabel(self.log_container, text=">_ DEVELOPER CONSOLE", font=ctk.CTkFont(family="Consolas", size=11, weight="bold"), text_color="#52525B")
        self.log_header.grid(row=0, column=0, sticky="w", padx=15, pady=(8, 0))

        self.log_textbox = ctk.CTkTextbox(
            self.log_container, 
            fg_color="transparent", 
            text_color="#10B981", # Hacker Green
            font=ctk.CTkFont(family="Consolas", size=12),
            wrap="word"
        )
        self.log_textbox.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.log_textbox.configure(state="disabled")

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

    def append_log(self, message):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", message + "\n")
        self.log_textbox.yview("end")
        self.log_textbox.configure(state="disabled")
        self.update()
