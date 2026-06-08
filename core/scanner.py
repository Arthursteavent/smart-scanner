import os
import hashlib
from pathlib import Path
from datetime import datetime

class FolderScanner:
    def __init__(self):
        # We can add ignored extensions or folders here
        self.ignore_folders = {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}
        
    def _get_file_hash(self, file_path, chunk_size=8192):
        hasher = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                # To be fast but accurate, we hash the first 1MB. 
                # For 100% accuracy, we hash the whole file. Let's do whole file for safety, but with large chunks.
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return None

    def scan_directory(self, root_path: str, progress_callback=None, seen_hashes=None):
        """
        Recursively scans the given directory and collects metadata for each file.
        Yields progress via progress_callback(current_count).
        Returns a tuple: (list of dictionaries containing file metadata, folder_count)
        """
        scanned_files = []
        folder_count = 0
        root = Path(root_path)
        
        # Keep track of hashes to detect duplicates across multiple scanned folders
        if seen_hashes is None:
            seen_hashes = {}

        if not root.exists() or not root.is_dir():
            raise ValueError(f"Invalid directory: {root_path}")

        count = 0
        for dirpath, dirnames, filenames in os.walk(root):
            # Modify dirnames in-place to ignore certain directories
            dirnames[:] = [d for d in dirnames if d not in self.ignore_folders]

            folder_count += 1
            for filename in filenames:
                file_path = Path(dirpath) / filename
                
                try:
                    stat = file_path.stat()
                    file_size = stat.st_size
                    
                    file_hash = self._get_file_hash(file_path)
                    
                    metadata = {
                        "filename": filename,
                        "extension": file_path.suffix.lower(),
                        "full_path": str(file_path),
                        "parent_folder": file_path.parent.name,
                        "file_size": file_size,
                        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "is_duplicate": False # Default, will be updated by logic below
                    }
                    
                    if file_hash:
                        if file_hash in seen_hashes:
                            existing_metadata = seen_hashes[file_hash]
                            
                            import re
                            def has_duplicate_suffix(name):
                                return bool(re.search(r'(\(\d+\)| - Copy| copy)', name, re.IGNORECASE))
                            
                            current_has_suffix = has_duplicate_suffix(filename)
                            existing_has_suffix = has_duplicate_suffix(existing_metadata["filename"])
                            
                            if existing_has_suffix and not current_has_suffix:
                                # Existing one is the ugly copy, current is the pristine original.
                                existing_metadata["is_duplicate"] = True
                                metadata["is_duplicate"] = False
                                seen_hashes[file_hash] = metadata # Update reference to the new original
                            elif current_has_suffix and not existing_has_suffix:
                                # Current has suffix, so it's clearly a duplicate.
                                metadata["is_duplicate"] = True
                            elif current_has_suffix and existing_has_suffix:
                                # Both have suffixes, mark current as duplicate.
                                metadata["is_duplicate"] = True
                            else:
                                # BOTH files have clean names (no (1), (2), etc).
                                # The user explicitly requested NOT to detect them as doubles if they don't have suffixes!
                                # So we keep BOTH as originals.
                                metadata["is_duplicate"] = False
                        else:
                            seen_hashes[file_hash] = metadata

                    scanned_files.append(metadata)
                    count += 1
                    
                    if progress_callback and count % 50 == 0:
                        progress_callback(count)
                        
                except Exception as e:
                    # Skip files we cannot access (e.g. permission denied)
                    print(f"Skipping {file_path}: {e}")

        if progress_callback:
            progress_callback(count) # Final call
            
        return scanned_files, folder_count
