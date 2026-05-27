import sys
import os
import ctypes
import tkinter as tk
from tkinter import messagebox, ttk

# --- C Structure Definitions ---
class Request(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_int),
        ("area", ctypes.c_char * 30),
        ("fill", ctypes.c_int),
        ("priority", ctypes.c_int)
    ]

class Node(ctypes.Structure):
    pass
Node._fields_ = [("data", Request), ("next", ctypes.POINTER(Node))]

class Queue(ctypes.Structure):
    _fields_ = [("front", ctypes.POINTER(Node)), ("rear", ctypes.POINTER(Node))]

class MinHeap(ctypes.Structure):
    _fields_ = [("arr", ctypes.POINTER(Request)), ("size", ctypes.c_int), ("capacity", ctypes.c_int)]

# --- DLL Loading ---
lib_path = os.path.abspath("libfunctions.dll")
lib = None

try:
    lib = ctypes.CDLL(lib_path)
except Exception as e:
    print(f"\n--- ERROR ---\nCould not load libfunctions.dll.\nReason: {e}\n-------------")
    sys.exit(1)

# --- Define Function Signatures ---
lib.initQueue.argtypes = [ctypes.POINTER(Queue)]
lib.initHeap.argtypes = [ctypes.POINTER(MinHeap), ctypes.c_int]
lib.enqueue.argtypes = [ctypes.POINTER(Queue), Request]
lib.dequeue.argtypes = [ctypes.POINTER(Queue), ctypes.POINTER(Request)]
lib.insertHeap.argtypes = [ctypes.POINTER(MinHeap), Request]
lib.extractMin.argtypes = [ctypes.POINTER(MinHeap), ctypes.POINTER(Request)]
lib.idExists.argtypes = [ctypes.POINTER(Queue), ctypes.POINTER(MinHeap), ctypes.c_int]
lib.idExists.restype = ctypes.c_int

try:
    lib.heapifyUp.argtypes = [ctypes.POINTER(MinHeap), ctypes.c_int]
    lib.heapifyDown.argtypes = [ctypes.POINTER(MinHeap), ctypes.c_int]
except AttributeError:
    pass

# --- GUI Application ---
class CompleteWasteManagementGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Smart Waste Management System")
        self.root.geometry("1000x700")
        
        # UI Styling (Making it look modern)
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("Treeview.Heading", font=('Arial', 10, 'bold'), background="#dcdde1")
        self.style.configure("Treeview", font=('Consolas', 10), rowheight=25)
        
        # Initialize Backend C Data Structures
        self.q = Queue()
        self.h = MinHeap()
        lib.initQueue(ctypes.byref(self.q))
        lib.initHeap(ctypes.byref(self.h), 20) 

        self.setup_ui()

    def generate_fill_bar(self, fill_percent):
        """Creates a visual text-based progress bar for the fill level"""
        blocks = int(fill_percent // 10)
        spaces = 10 - blocks
        return f"[{'█' * blocks}{'░' * spaces}] {fill_percent}%"

    def setup_ui(self):
        self.tabs = ttk.Notebook(self.root)
        self.user_tab = ttk.Frame(self.tabs)
        self.admin_tab = ttk.Frame(self.tabs)
        
        self.tabs.add(self.user_tab, text="👤 User Mode (Requests)")
        self.tabs.add(self.admin_tab, text="🛡️ Admin Mode (Dispatch)")
        self.tabs.pack(expand=1, fill="both", padx=10, pady=10)

        self.setup_user_tab()
        self.setup_admin_tab()

    # ================= USER TAB =================
    def setup_user_tab(self):
        lbl_title = tk.Label(self.user_tab, text="Submit Smart Bin Request", font=('Arial', 16, 'bold'), fg="#2c3e50")
        lbl_title.pack(pady=15)
        
        form_frame = ttk.LabelFrame(self.user_tab, text=" Bin Details ", padding=15)
        form_frame.pack(pady=5, fill="x", padx=30)
        form_frame.columnconfigure(1, weight=1)

        tk.Label(form_frame, text="Bin ID (Number):", font=('Arial', 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.ent_id = ttk.Entry(form_frame, font=('Arial', 11))
        self.ent_id.grid(row=0, column=1, sticky="ew", pady=5, padx=10)

        tk.Label(form_frame, text="Location / Area:", font=('Arial', 10)).grid(row=1, column=0, sticky="w", pady=5)
        self.ent_area = ttk.Entry(form_frame, font=('Arial', 11))
        self.ent_area.grid(row=1, column=1, sticky="ew", pady=5, padx=10)

        tk.Label(form_frame, text="Fill Level (0-100%):", font=('Arial', 10)).grid(row=2, column=0, sticky="w", pady=5)
        
        self.fill_var = tk.IntVar(value=50)
        fill_slider_frame = tk.Frame(form_frame)
        fill_slider_frame.grid(row=2, column=1, sticky="ew", padx=10)
        
        self.scale_fill = ttk.Scale(fill_slider_frame, from_=0, to=100, variable=self.fill_var, orient="horizontal")
        self.scale_fill.pack(side="left", fill="x", expand=True)
        
        self.lbl_fill_val = tk.Label(fill_slider_frame, text="50%", font=('Arial', 10, 'bold'), width=5)
        self.lbl_fill_val.pack(side="right", padx=5)
        
        self.scale_fill.configure(command=lambda val: self.lbl_fill_val.config(text=f"{int(float(val))}%"))

        btn_submit = tk.Button(self.user_tab, text="📥 Add Bin to Intake Queue", command=self.submit_request, 
                               bg="#27ae60", fg="white", font=('Arial', 12, 'bold'), cursor="hand2", pady=5)
        btn_submit.pack(pady=15)

        queue_frame = ttk.LabelFrame(self.user_tab, text=" Active Request Queue (Ingestion Area) ", padding=10)
        queue_frame.pack(pady=10, fill="both", expand=True, padx=30)

        self.user_queue_tree = ttk.Treeview(queue_frame, columns=("ID", "Area", "Fill", "Priority"), show='headings')
        self.user_queue_tree.heading("ID", text="Bin ID")
        self.user_queue_tree.heading("Area", text="Location")
        self.user_queue_tree.heading("Fill", text="Fill Status")
        self.user_queue_tree.heading("Priority", text="Priority")
        
        self.user_queue_tree.column("ID", width=80, anchor="center")
        self.user_queue_tree.column("Area", width=200, anchor="w")
        self.user_queue_tree.column("Fill", width=150, anchor="center")
        self.user_queue_tree.column("Priority", width=120, anchor="center")
        
        self.user_queue_tree.tag_configure('critical', foreground='#c0392b', font=('Consolas', 10, 'bold')) 
        self.user_queue_tree.pack(side="left", fill="both", expand=True)

    # ================= ADMIN TAB =================
    def setup_admin_tab(self):
        lbl_title = tk.Label(self.admin_tab, text="System Administrator Dashboard", font=('Arial', 16, 'bold'), fg="#2c3e50")
        lbl_title.pack(pady=10)

        ctrl_frame = ttk.LabelFrame(self.admin_tab, text=" Action Controls ", padding=15)
        ctrl_frame.pack(fill="x", padx=20, pady=5)

        tk.Button(ctrl_frame, text="⚙️ Process Queue ➔ Heap", command=self.move_to_heap, bg="#f39c12", fg="white", font=('Arial', 10, 'bold'), cursor="hand2").grid(row=0, column=0, padx=5)
        tk.Button(ctrl_frame, text="🚀 Dispatch Auto-Clean", command=self.auto_clean, bg="#2980b9", fg="white", font=('Arial', 10, 'bold'), cursor="hand2").grid(row=0, column=1, padx=5)
        
        # --- FIXED: ADDED SEARCH BY AREA BACK IN ---
        filter_frame = tk.Frame(ctrl_frame)
        filter_frame.grid(row=0, column=2, padx=15)
        tk.Label(filter_frame, text="🔍 Search Area:", font=('Arial', 10, 'bold')).pack(side="left")
        
        self.ent_filter_area = ttk.Entry(filter_frame, width=12, font=('Arial', 10))
        self.ent_filter_area.pack(side="left", padx=5)
        # Binds the typing event so it live-updates the table!
        self.ent_filter_area.bind("<KeyRelease>", lambda e: self.refresh_queues()) 
        
        tk.Button(filter_frame, text="Clear", command=self.clear_filter, bg="#bdc3c7", cursor="hand2").pack(side="left")
        # ---------------------------------------------

        manual_frame = tk.Frame(ctrl_frame)
        manual_frame.grid(row=0, column=3, padx=15)
        tk.Label(manual_frame, text="Target ID:").pack(side="left")
        self.ent_manual_id = ttk.Entry(manual_frame, width=8, font=('Arial', 11, 'bold'))
        self.ent_manual_id.pack(side="left", padx=5)
        tk.Button(manual_frame, text="🎯 Clean Target", command=self.manual_clean_bin, bg="#e74c3c", fg="white", font=('Arial', 10, 'bold'), cursor="hand2").pack(side="left")

        tk.Label(self.admin_tab, text="💡 Tip: Double-click a bin in the Heap table below to auto-target it for cleaning.", font=('Arial', 9, 'italic'), fg="gray").pack(anchor="w", padx=25, pady=(5,0))

        views_frame = tk.Frame(self.admin_tab)
        views_frame.pack(fill="both", expand=True, padx=20, pady=(5,10))

        q_monitor = ttk.LabelFrame(views_frame, text=" Raw Ingestion Queue ", padding=5)
        q_monitor.pack(side="left", fill="both", expand=True, padx=5)
        
        self.admin_queue_tree = ttk.Treeview(q_monitor, columns=("ID", "Area", "Fill"), show='headings')
        self.admin_queue_tree.heading("ID", text="ID")
        self.admin_queue_tree.heading("Area", text="Area")
        self.admin_queue_tree.heading("Fill", text="Fill")
        self.admin_queue_tree.column("ID", width=50, anchor="center")
        self.admin_queue_tree.column("Area", width=120, anchor="w")
        self.admin_queue_tree.column("Fill", width=120, anchor="center")
        self.admin_queue_tree.tag_configure('critical', foreground='#c0392b', font=('Consolas', 10, 'bold'))
        self.admin_queue_tree.pack(fill="both", expand=True)

        h_monitor = ttk.LabelFrame(views_frame, text=" Priority Min-Heap Routing ", padding=5)
        h_monitor.pack(side="right", fill="both", expand=True, padx=5)
        
        self.admin_heap_tree = ttk.Treeview(h_monitor, columns=("Idx", "ID", "Area", "Fill", "Priority"), show='headings')
        for col, width in zip(("Idx", "ID", "Area", "Fill", "Priority"), (40, 50, 120, 120, 70)):
            self.admin_heap_tree.heading(col, text=col)
            self.admin_heap_tree.column(col, width=width, anchor="center")
        
        self.admin_heap_tree.tag_configure('critical', foreground='#c0392b', font=('Consolas', 10, 'bold'))
        self.admin_heap_tree.pack(fill="both", expand=True)
        
        self.admin_heap_tree.bind("<Double-1>", self.on_heap_double_click)

        tk.Button(self.admin_tab, text="🔄 Refresh Monitors", command=self.refresh_queues, bg="#bdc3c7", cursor="hand2").pack(pady=5)

    # ================= CORE INTERACTION LOGIC =================
    def clear_filter(self):
        """Clears the area search box and resets the table"""
        self.ent_filter_area.delete(0, tk.END)
        self.refresh_queues()

    def on_heap_double_click(self, event):
        selected = self.admin_heap_tree.selection()
        if selected:
            item = self.admin_heap_tree.item(selected[0])
            bin_id = item['values'][1] 
            self.ent_manual_id.delete(0, tk.END)
            self.ent_manual_id.insert(0, str(bin_id))
            messagebox.showinfo("Target Acquired", f"Bin {bin_id} targeted for manual dispatch.")

    def submit_request(self):
        try:
            bid = int(self.ent_id.get())
            area_str = self.ent_area.get().strip()
            fill = self.fill_var.get()  

            if not area_str:
                messagebox.showerror("Validation Error", "Area cannot be empty.")
                return

            if lib.idExists(ctypes.byref(self.q), ctypes.byref(self.h), bid):
                messagebox.showerror("System Restriction", f"Bin ID {bid} already tracked globally.")
                return

            area_bytes = area_str.encode('utf-8')
            priority = 100 - fill

            req = Request(bid, area_bytes, fill, priority)
            lib.enqueue(ctypes.byref(self.q), req)
            
            self.ent_id.delete(0, tk.END)
            self.ent_area.delete(0, tk.END)
            self.fill_var.set(50) 
            self.lbl_fill_val.config(text="50%")

            self.refresh_queues()
            self.tabs.select(self.user_tab)
            
        except ValueError:
            messagebox.showerror("Type Error", "ID must be a whole number.")

    def move_to_heap(self):
        req = Request()
        count = 0
        while lib.dequeue(ctypes.byref(self.q), ctypes.byref(req)):
            lib.insertHeap(ctypes.byref(self.h), req)
            count += 1
            
        self.refresh_queues()
        if count > 0:
            messagebox.showinfo("Pipeline Action", f"Shifted {count} bin logs into the Priority Scheduling Heap.")
        else:
            messagebox.showwarning("Pipeline Empty", "No records in the entry queue to process.")

    def auto_clean(self):
        req = Request()
        if lib.extractMin(ctypes.byref(self.h), ctypes.byref(req)):
            messagebox.showinfo("Dispatched Service", f"🚀 Dispatching Vehicle to:\n\nBin ID: {req.id}\nLocation: {req.area.decode()}\nFill State: {req.fill}%\nPriority Rating: {req.priority}")
            self.refresh_queues()
        else:
            messagebox.showwarning("Collection Empty", "The priority tree contains 0 pending items.")

    def manual_clean_bin(self):
        try:
            target_id = int(self.ent_manual_id.get())
        except ValueError:
            messagebox.showerror("Invalid Value", "Please provide a numeric Bin ID.")
            return

        if self.h.size == 0:
            messagebox.showwarning("Empty Structure", "No data resides inside Heap.")
            return

        found_index = -1
        for i in range(self.h.size):
            if self.h.arr[i].id == target_id:
                found_index = i
                break

        if found_index == -1:
            messagebox.showerror("Not Found", f"Bin ID {target_id} could not be located inside Priority Heap context.")
            return

        target_bin = self.h.arr[found_index]
        messagebox.showinfo("Manual Dispatch", f"Cleaning Custom Pick Target:\nID {target_bin.id} situated at {target_bin.area.decode()}")

        self.h.arr[found_index] = self.h.arr[self.h.size - 1]
        self.h.size -= 1

        if self.h.size > 0 and found_index < self.h.size:
            try:
                if found_index > 0 and self.h.arr[found_index].priority < self.h.arr[(found_index - 1) // 2].priority:
                    lib.heapifyUp(ctypes.byref(self.h), found_index)
                else:
                    lib.heapifyDown(ctypes.byref(self.h), found_index)
            except AttributeError:
                pass

        self.ent_manual_id.delete(0, tk.END)
        self.refresh_queues()

    def refresh_queues(self):
        for t in (self.user_queue_tree, self.admin_queue_tree, self.admin_heap_tree):
            for item in t.get_children():
                t.delete(item)

        # GET THE SEARCH QUERY HERE
        filter_area_str = self.ent_filter_area.get().strip().lower()

        # 1. Read linked list records dynamically via pointers
        curr_node_ptr = self.q.front
        while curr_node_ptr:
            node = curr_node_ptr.contents
            r = node.data
            
            b_id = r.id
            b_area = r.area.decode('utf-8', errors='ignore')
            fill_bar = self.generate_fill_bar(r.fill)
            tag = 'critical' if r.fill > 80 else 'normal'

            # FILTER LOGIC APPLIED TO QUEUES
            if not filter_area_str or filter_area_str in b_area.lower():
                self.user_queue_tree.insert("", "end", values=(b_id, b_area, fill_bar, r.priority), tags=(tag,))
                self.admin_queue_tree.insert("", "end", values=(b_id, b_area, fill_bar), tags=(tag,))

            curr_node_ptr = node.next

        # 2. Extract linear heap elements
        for i in range(self.h.size):
            r = self.h.arr[i]
            h_area = r.area.decode('utf-8', errors='ignore')
            fill_bar = self.generate_fill_bar(r.fill)
            tag = 'critical' if r.fill > 80 else 'normal'
            
            # FILTER LOGIC APPLIED TO HEAP
            if not filter_area_str or filter_area_str in h_area.lower():
                self.admin_heap_tree.insert("", "end", values=(f"[{i}]", r.id, h_area, fill_bar, r.priority), tags=(tag,))


if __name__ == "__main__":
    root = tk.Tk()
    app = CompleteWasteManagementGUI(root)
    root.mainloop()
