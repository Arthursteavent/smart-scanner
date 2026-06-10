import sys
import eel
import os
import threading
import tkinter as tk
from tkinter import filedialog
from database.database import init_db
from database.undo_repository import undo_batch, get_last_batch_id
from core.scanner import FolderScanner
from core.preview_builder import PreviewBuilder
from core.organizer import FileOrganizer
from core.config_manager import load_config, save_config
from pathlib import Path

# Need to hide the root tkinter window
root = tk.Tk()
root.withdraw()
root.attributes('-topmost', True)

last_tree = None

def send_log(message):
    eel.append_log(message)()

@eel.expose
def select_folder():
    folder_path = filedialog.askdirectory(parent=root, title="Select Folder to Organize")
    return folder_path

@eel.expose
def get_config():
    return load_config()

@eel.expose
def save_settings(settings):
    save_config(settings)
    return True

@eel.expose
def run_scan_and_ai(folder_paths):
    global last_tree
    
    def status_callback(msg, progress=None):
        eel.update_status(msg, progress)()
        
    def worker():
        global last_tree
        try:
            status_callback("Scanning folders...")
            scanner = FolderScanner()
            files_metadata = []
            total_folders = 0
            seen_hashes = {}
            for path in folder_paths:
                send_log(f"> Scanning \"{path}\"")
                files, folder_count = scanner.scan_directory(path, lambda count: status_callback(f"Scanned {len(files_metadata) + count} files..."), seen_hashes=seen_hashes)
                files_metadata.extend(files)
                total_folders += folder_count
                
            send_log(f"> Scan Complete: Found {len(files_metadata)} files across {total_folders} folders.")
            
            if not files_metadata:
                eel.scan_complete(False, "No files found to organize.")()
                return
                
            send_log(f"> Preparing {len(files_metadata)} files for Smart Local Analysis...")
            status_callback(f"Starting Smart Local Analysis for {len(files_metadata)} files...", 0.0)
            
            from providers.local_provider import LocalProvider
            provider = LocalProvider()
            
            BATCH_SIZE = 300
            total_batches = (len(files_metadata) + BATCH_SIZE - 1) // BATCH_SIZE
            builder = PreviewBuilder()
            combined_tree = {}
            
            for i in range(0, len(files_metadata), BATCH_SIZE):
                batch_num = (i // BATCH_SIZE) + 1
                batch_files = files_metadata[i:i + BATCH_SIZE]
                
                send_log(f"> Analyzing file batch {batch_num}/{total_batches} ({len(batch_files)} files)...")
                current_file_count = min(i + BATCH_SIZE, len(files_metadata))
                status_callback(f"Analyzing batch {batch_num}/{total_batches} ({current_file_count}/{len(files_metadata)} files)...", (batch_num - 1) / total_batches)
                
                response_json = provider.classify_files(batch_files)
                
                send_log(f"> Batch {batch_num} analysis complete. Building preview...")
                try:
                    batch_tree = builder.parse_ai_response(response_json)
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
                    send_log(f"! Warning: Failed to parse batch {batch_num}: {e}")
                    
            if not combined_tree:
                raise ValueError("Failed to classify any files. Please check the logs.")
                
            last_tree = combined_tree
            send_log("> Smart analysis complete. Ready for preview.")
            status_callback("Smart Organization complete. Please review the preview.", 1.0)
            eel.scan_complete(True, "Analysis complete.", combined_tree)()
            
        except Exception as e:
            send_log(f"! Error: {e}")
            eel.scan_complete(False, f"Error: {e}")()
            
    threading.Thread(target=worker, daemon=True).start()

@eel.expose
def delete_duplicates():
    global last_tree
    if not last_tree:
        return {"deleted": 0, "failed": 0, "tree": last_tree}
        
    duplicates = last_tree.get("Duplicates", {})
    if not duplicates:
        return {"deleted": 0, "failed": 0, "tree": last_tree}
        
    deleted_count = 0
    failed_count = 0
    
    for subcat, items in duplicates.items():
        for item in items:
            path = item["path"]
            try:
                if Path(path).exists():
                    os.remove(path)
                    deleted_count += 1
                    send_log(f"> Deleted duplicate: {path}")
            except Exception as e:
                failed_count += 1
                send_log(f"> Failed to delete {path}: {e}")
                
    if "Duplicates" in last_tree:
        del last_tree["Duplicates"]
        
    return {"deleted": deleted_count, "failed": failed_count, "tree": last_tree}

@eel.expose
def apply_organization():
    global last_tree
    if not last_tree:
        return False
        
    config = load_config()
    saved_target = config.get("target_folder")
    if not saved_target:
        send_log("! Error: Destination folder not set. Please set it in Settings first.")
        eel.org_complete(False, "Destination folder not set.")()
        return False
        
    target_folder = Path(saved_target)
    send_log(f"> Starting file organization in {target_folder}")
    
    def worker():
        try:
            organizer = FileOrganizer(str(target_folder), log_callback=send_log)
            send_log("> Executing moves...")
            def prog_callback(progress):
                eel.update_org_progress(progress)()
                
            organizer.apply_organization(last_tree, progress_callback=prog_callback)
            send_log("> Organization finished successfully.")
            eel.org_complete(True, "Success")()
        except Exception as e:
            send_log(f"Error applying organization: {e}")
            eel.org_complete(False, str(e))()
            
    threading.Thread(target=worker, daemon=True).start()
    return True

@eel.expose
def undo_last_operation():
    batch_id = get_last_batch_id()
    if not batch_id:
        return {"restored": 0, "failed": 0}
    restored, failed = undo_batch(batch_id, log_callback=send_log)
    return {"restored": restored, "failed": failed}

def get_web_dir():
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, 'web')
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web')

def main():
    init_db()
    eel.init(get_web_dir())
    
    # Start app
    try:
        eel.start('index.html', size=(1200, 850), port=0)
    except Exception as e:
        print(f"Error starting eel: {e}")

if __name__ == "__main__":
    main()
