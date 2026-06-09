import shutil
from pathlib import Path
from typing import Optional
from database.database import get_connection

def log_operation(source_path: str, destination_path: str, batch_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO operations (source_path, destination_path, batch_id) VALUES (?, ?, ?)",
        (source_path, destination_path, batch_id)
    )
    conn.commit()
    conn.close()

def get_last_batch_id() -> Optional[str]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT batch_id FROM operations ORDER BY timestamp DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def get_operations_by_batch(batch_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, source_path, destination_path FROM operations WHERE batch_id = ? ORDER BY id DESC",
        (batch_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows

def undo_batch(batch_id: str, log_callback=None, progress_callback=None):
    operations = get_operations_by_batch(batch_id)
    success_count = 0
    failed_count = 0
    total = len(operations)

    for i, (op_id, source_path, destination_path) in enumerate(operations):
        src = Path(source_path)
        dst = Path(destination_path)

        # In an undo operation, the file is currently at destination_path,
        # and we want to move it back to source_path.
        if dst.exists():
            try:
                # Ensure the original parent directory exists just in case
                src.parent.mkdir(parents=True, exist_ok=True)
                if log_callback:
                    if dst.is_dir():
                        log_callback(f"|WHITE|< undo project folder \"{dst.name}\" back to \"{src.parent}\"")
                    else:
                        log_callback(f"< undo \"{dst.name}\" back to \"{src.parent}\"")
                shutil.move(str(dst), str(src))
                success_count += 1
                
                # Optionally delete empty folders left behind
                if dst.parent.exists() and not any(dst.parent.iterdir()):
                    try:
                        dst.parent.rmdir()
                        if log_callback:
                            log_callback(f"< removed empty folder \"{dst.parent}\"")
                    except OSError:
                        pass
            except Exception as e:
                if log_callback:
                    log_callback(f"! Failed to move {dst} back to {src}: {e}")
                else:
                    print(f"Failed to move {dst} back to {src}: {e}")
                failed_count += 1
        else:
            if log_callback:
                log_callback(f"! File not found at {dst}, cannot undo.")
            else:
                print(f"File not found at {dst}, cannot undo.")
            failed_count += 1
            
        if progress_callback and total > 0:
            progress_callback((i + 1) / total)
            
    # Remove the batch from history after undoing
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM operations WHERE batch_id = ?", (batch_id,))
    conn.commit()
    conn.close()

    return success_count, failed_count
