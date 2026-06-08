import customtkinter as ctk
from tkinter import ttk
import threading

class PreviewPage(ctk.CTkFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, **kwargs)
        self.app_controller = app_controller

        # Card Frame
        self.card_frame = ctk.CTkFrame(self, fg_color="#18181B", corner_radius=16, border_width=1, border_color="#27272A")
        self.card_frame.pack(fill="both", expand=True, padx=40, pady=40)

        # Title
        self.title_label = ctk.CTkLabel(self.card_frame, text="Preview Organization", font=ctk.CTkFont(family="Inter", size=32, weight="bold"), text_color="#FAFAFA")
        self.title_label.pack(pady=(40, 5), padx=40, anchor="w")

        # Instruction
        self.info_label = ctk.CTkLabel(self.card_frame, text="Review the proposed folder structure. Click 'Apply Changes' when ready.", text_color="#A1A1AA", font=ctk.CTkFont(family="Inter", size=14))
        self.info_label.pack(pady=(0, 20), padx=40, anchor="w")

        # Tabview for separation
        self.tabview = ctk.CTkTabview(self.card_frame, fg_color="#09090B", segmented_button_fg_color="#27272A", segmented_button_selected_color="#6366F1", segmented_button_selected_hover_color="#4F46E5", corner_radius=8)
        self.tabview.pack(fill="both", expand=True, padx=40, pady=10)
        
        self.tab_main = self.tabview.add("📁 Organized Files")
        self.tab_dupes = self.tabview.add("🗑️ Duplicate Files")
        
        # Style the Treeview globally
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                        background="#09090B", 
                        foreground="#E4E4E7", 
                        fieldbackground="#09090B", 
                        borderwidth=0,
                        rowheight=28)
        style.map('Treeview', background=[('selected', '#6366F1')])
        style.configure("Treeview.Heading", background="#18181B", foreground="#FAFAFA", relief="flat")

        # Main Tree
        self.main_tree = ttk.Treeview(self.tab_main)
        self.main_tree.pack(side="left", fill="both", expand=True)
        self.main_scrollbar = ttk.Scrollbar(self.tab_main, orient="vertical", command=self.main_tree.yview)
        self.main_scrollbar.pack(side="right", fill="y")
        self.main_tree.configure(yscrollcommand=self.main_scrollbar.set)
        
        # Dupes Tree
        self.dupes_tree = ttk.Treeview(self.tab_dupes)
        self.dupes_tree.pack(side="left", fill="both", expand=True)
        self.dupes_scrollbar = ttk.Scrollbar(self.tab_dupes, orient="vertical", command=self.dupes_tree.yview)
        self.dupes_scrollbar.pack(side="right", fill="y")
        self.dupes_tree.configure(yscrollcommand=self.dupes_scrollbar.set)

        # Buttons Frame
        self.button_frame = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        self.button_frame.pack(fill="x", padx=40, pady=(15, 40))
        
        self.apply_button = ctk.CTkButton(self.button_frame, text="✅ Apply Changes", font=ctk.CTkFont(family="Inter", weight="bold"), fg_color="#10B981", hover_color="#059669", text_color="#FAFAFA", height=45, corner_radius=8, command=self.apply_changes)
        self.apply_button.pack(side="left")
        
        self.delete_dupes_button = ctk.CTkButton(self.button_frame, text="🗑️ Delete Duplicates", font=ctk.CTkFont(family="Inter", weight="bold"), fg_color="#EF4444", hover_color="#DC2626", text_color="#FAFAFA", height=45, corner_radius=8, command=self.delete_duplicates)
        self.delete_dupes_button.pack(side="left", padx=15)
        
        self.undo_button = ctk.CTkButton(self.button_frame, text="↩️ Undo Last", font=ctk.CTkFont(family="Inter", weight="bold"), fg_color="#F59E0B", hover_color="#D97706", text_color="#FAFAFA", height=45, corner_radius=8, command=self.undo_changes)
        self.undo_button.pack(side="left")
        
        self.back_button = ctk.CTkButton(self.button_frame, text="Back to Scan", font=ctk.CTkFont(family="Inter", weight="bold"), fg_color="#27272A", hover_color="#3F3F46", text_color="#FAFAFA", height=45, corner_radius=8, command=self.app_controller.show_scan_page)
        self.back_button.pack(side="right")

    def _populate_specific_tree(self, tree, data_subset):
        for item in tree.get_children():
            tree.delete(item)
            
        for cat, content in data_subset.items():
            cat_id = tree.insert("", "end", text=f"📁 {cat}", open=True)
            
            for subcat, items in content.items():
                if subcat == "_files":
                    for item in items:
                        filename = item["path"].split("\\")[-1].split("/")[-1]
                        tree.insert(cat_id, "end", text=f"📄 {filename} ({item['confidence']}%)")
                else:
                    if subcat == "":
                        # Handle empty subcategories smoothly (like duplicates)
                        for item in items:
                            filename = item["path"].split("\\")[-1].split("/")[-1]
                            tree.insert(cat_id, "end", text=f"📄 {filename} ({item['confidence']}%)")
                    else:
                        subcat_id = tree.insert(cat_id, "end", text=f"📂 {subcat}", open=True)
                        for item in items:
                            filename = item["path"].split("\\")[-1].split("/")[-1]
                            tree.insert(subcat_id, "end", text=f"📄 {filename} ({item['confidence']}%)")

    def populate_tree(self, tree_data):
        # Split data
        main_data = {k: v for k, v in tree_data.items() if k != "Duplicates"}
        dupes_data = {"Duplicates": tree_data.get("Duplicates", {})} if "Duplicates" in tree_data else {}
        
        # Populate Main Tree
        self._populate_specific_tree(self.main_tree, main_data)
        
        # Populate Dupes Tree
        self._populate_specific_tree(self.dupes_tree, dupes_data)
        
        # UI State Management
        if dupes_data and dupes_data["Duplicates"]:
            self.delete_dupes_button.pack(side="left", padx=15)
            # Select the main tab by default
            self.tabview.set("📁 Organized Files")
        else:
            self.delete_dupes_button.pack_forget()
            self.tabview.set("📁 Organized Files")

    def apply_changes(self):
        self.apply_button.configure(state="disabled", text="Applying...")
        
        def process():
            success = self.app_controller.apply_organization()
            self.after(0, self._apply_done, success)
            
        threading.Thread(target=process).start()
        
    def _apply_done(self, success):
        self.apply_button.configure(state="normal", text="Apply Changes")
        if success:
            self.info_label.configure(text="Files successfully organized!", text_color="green")
        else:
            self.info_label.configure(text="Error applying organization.", text_color="red")

    def undo_changes(self):
        self.undo_button.configure(state="disabled", text="Undoing...")
        
        def process():
            success_count, failed_count = self.app_controller.undo_last_operation()
            self.after(0, self._undo_done, success_count, failed_count)
            
        threading.Thread(target=process).start()
        
    def _undo_done(self, success_count, failed_count):
        self.undo_button.configure(state="normal", text="Undo Last Operation")
        self.info_label.configure(text=f"Undo complete. Restored: {success_count}, Failed: {failed_count}", text_color="yellow")

    def delete_duplicates(self):
        import tkinter.messagebox as messagebox
        
        duplicates_exist = "Duplicates" in self.app_controller.last_tree
        if not duplicates_exist:
            messagebox.showinfo("No Duplicates", "There are no duplicates detected in the current scan.")
            return
            
        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to PERMANENTLY delete all files listed under the 'Duplicates' category? This cannot be undone!"):
            self.delete_dupes_button.configure(state="disabled", text="Deleting...")
            
            def process():
                deleted, failed = self.app_controller.delete_duplicates()
                self.after(0, self._delete_dupes_done, deleted, failed)
                
            threading.Thread(target=process).start()
            
    def _delete_dupes_done(self, deleted, failed):
        self.delete_dupes_button.configure(state="normal", text="🗑️ Delete Duplicates")
        self.info_label.configure(text=f"Deleted {deleted} duplicates (Failed: {failed}).", text_color="yellow")
        # Refresh tree
        self.populate_tree(self.app_controller.last_tree)
