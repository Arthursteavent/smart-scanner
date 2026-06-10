import customtkinter as ctk
from tkinter import ttk
import threading

class PreviewPage(ctk.CTkFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, **kwargs)
        self.app_controller = app_controller

        # Top Bar
        self.top_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.top_bar.pack(fill="x", padx=40, pady=(40, 0))
        
        self.mode_label = ctk.CTkLabel(self.top_bar, text="Preview Mode", font=ctk.CTkFont(family="Inter", size=20, weight="bold"), text_color="#F8FAFC")
        self.mode_label.pack(side="left")
        self.mode_sublabel = ctk.CTkLabel(self.top_bar, text="Analyzing Structure...", font=ctk.CTkFont(family="Inter", size=13), text_color="#94A3B8")
        self.mode_sublabel.pack(side="left", padx=15, pady=(5, 0))

        # Card Frame
        self.card_frame = ctk.CTkFrame(self, fg_color="#1E293B", corner_radius=16, border_width=1, border_color="#334155")
        self.card_frame.pack(fill="both", expand=True, padx=40, pady=(20, 40))

        # Header Frame
        self.header_frame = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=40, pady=(30, 20))

        # Left Header
        self.header_left = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.header_left.pack(side="left")
        
        self.title_label = ctk.CTkLabel(self.header_left, text="Preview\nOrganization", font=ctk.CTkFont(family="Inter", size=28, weight="bold"), text_color="#F8FAFC", justify="left")
        self.title_label.pack(anchor="w")

        self.info_label = ctk.CTkLabel(self.header_left, text="✓ Scan complete. Files analyzed.", text_color="#F59E0B", font=ctk.CTkFont(family="Inter", size=13))
        self.info_label.pack(pady=(5, 0), anchor="w")

        # Right Header (Buttons)
        self.header_right = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.header_right.pack(side="right", anchor="s")

        self.apply_button = ctk.CTkButton(
            self.header_right, 
            text="✓  Apply Changes", 
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"), 
            fg_color="#CFFAFE", # Very light cyan
            hover_color="#A5F3FC", 
            text_color="#0F172A", 
            height=45, 
            corner_radius=8, 
            command=self.apply_changes
        )
        self.apply_button.pack(side="left", padx=5)

        self.undo_button = ctk.CTkButton(
            self.header_right, 
            text="↩  Undo Last Operation", 
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"), 
            fg_color="transparent", 
            border_width=1,
            border_color="#F59E0B",
            hover_color="#1E293B", 
            text_color="#F59E0B", 
            height=45, 
            corner_radius=8, 
            command=self.undo_changes
        )
        self.undo_button.pack(side="left", padx=5)
        
        self.delete_dupes_button = ctk.CTkButton(
            self.header_right, 
            text="🗑️ Delete Duplicates", 
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"), 
            fg_color="transparent", 
            border_width=1,
            border_color="#EF4444",
            hover_color="#1E293B", 
            text_color="#EF4444", 
            height=45, 
            corner_radius=8, 
            command=self.delete_duplicates
        )
        # Packed later if dupes exist

        self.back_button = ctk.CTkButton(
            self.header_right, 
            text="←  Back to Scan", 
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"), 
            fg_color="transparent", 
            border_width=1,
            border_color="#334155",
            hover_color="#0F172A", 
            text_color="#F8FAFC", 
            height=45, 
            corner_radius=8, 
            command=self.app_controller.show_scan_page
        )
        self.back_button.pack(side="left", padx=5)

        # Progress Section
        self.progress_frame = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        
        self.progress_header = ctk.CTkFrame(self.progress_frame, fg_color="transparent")
        self.progress_header.pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(self.progress_header, text="Virtual Reorganization Status", text_color="#F8FAFC", font=ctk.CTkFont(family="Inter", size=12, weight="bold")).pack(side="left")
        self.pct_label = ctk.CTkLabel(self.progress_header, text="0% Complete", text_color="#F8FAFC", font=ctk.CTkFont(family="Inter", size=12, weight="bold"))
        self.pct_label.pack(side="right")
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, height=8, progress_color="#06B6D4", fg_color="#334155")
        self.progress_bar.pack(fill="x")
        self.progress_bar.set(0)

        # Tabview for separation (Expands to fill the remaining middle space)
        self.tabview = ctk.CTkTabview(self.card_frame, fg_color="#0F172A", segmented_button_fg_color="#1E293B", segmented_button_selected_color="#334155", segmented_button_selected_hover_color="#475569", corner_radius=8)
        self.tabview.pack(side="top", fill="both", expand=True, padx=40, pady=(10, 30))
        
        self.tab_main = self.tabview.add("📁 Organized Files")
        self.tab_dupes = self.tabview.add("🗑️ Duplicate Files")
        
        # Style the Treeview globally
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                        background="#0F172A", 
                        foreground="#F8FAFC", 
                        fieldbackground="#0F172A", 
                        borderwidth=0,
                        rowheight=32)
        style.map('Treeview', background=[('selected', '#334155')])
        style.configure("Treeview.Heading", background="#1E293B", foreground="#F8FAFC", relief="flat")

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
            self.delete_dupes_button.pack(side="left", padx=5)
            self.tabview.set("📁 Organized Files")
        else:
            self.delete_dupes_button.pack_forget()
            self.tabview.set("📁 Organized Files")

    def update_progress(self, progress):
        def _update():
            self.progress_bar.set(progress)
            self.pct_label.configure(text=f"{int(progress * 100)}% Complete")
        self.after(0, _update)

    def apply_changes(self):
        self.apply_button.configure(state="disabled")
        self.progress_frame.pack(fill="x", padx=40, pady=(0, 15), before=self.tabview)
        self.progress_bar.set(0)
        
        def process():
            success = self.app_controller.apply_organization(progress_callback=self.update_progress)
            self.after(0, self._apply_done, success)
            
        threading.Thread(target=process).start()
        
    def _apply_done(self, success):
        self.apply_button.configure(state="normal")
        self.progress_frame.pack_forget()
        if success:
            self.info_label.configure(text="✓ Files successfully organized!", text_color="#10B981")
        else:
            self.info_label.configure(text="! Error applying organization.", text_color="#EF4444")

    def undo_changes(self):
        self.undo_button.configure(state="disabled")
        self.progress_frame.pack(fill="x", padx=40, pady=(0, 15), before=self.tabview)
        self.progress_bar.set(0)
        
        def process():
            success_count, failed_count = self.app_controller.undo_last_operation(progress_callback=self.update_progress)
            self.after(0, self._undo_done, success_count, failed_count)
            
        threading.Thread(target=process).start()
        
    def _undo_done(self, success_count, failed_count):
        self.undo_button.configure(state="normal")
        self.progress_frame.pack_forget()
        self.info_label.configure(text=f"✓ Undo complete. Restored: {success_count}, Failed: {failed_count}", text_color="#10B981")

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
