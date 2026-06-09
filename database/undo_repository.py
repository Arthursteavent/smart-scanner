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

def undo_batch(batch_id: str):
    operations = get_operations_by_batch(batch_id)
    success_count = 0
    failed_count = 0

    for op_id, source_path, destination_path in operations:
        src = Path(source_path)
        dst = Path(destination_path)

        # In an undo operation, the file is currently at destination_path,
        # and we want to move it back to source_path.
        if dst.exists():
            try:
                # Ensure the original parent directory exists just in case
                src.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(dst), str(src))
                success_count += 1
                
                # Optionally delete empty folders left behind
                if dst.parent.exists() and not any(dst.parent.iterdir()):
                    try:
                        dst.parent.rmdir()
                    except OSError:
                        pass
            except Exception as e:
                print(f"Failed to move {dst} back to {src}: {e}")
                failed_count += 1
        else:
            print(f"File not found at {dst}, cannot undo.")
            failed_count += 1
            
    # Remove the batch from history after undoing
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM operations WHERE batch_id = ?", (batch_id,))
    conn.commit()
    conn.close()

    return success_count, failed_count
