import tkinter as tk
from tkinter import messagebox, ttk
import ctypes
import os

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

import sys

lib_path = os.path.abspath("libfunctions.dll")
lib = None # Initialize to None

try:
    # Try loading the DLL
    lib = ctypes.CDLL(lib_path)
except Exception as e:
    print(f"\n--- ERROR ---")
    print(f"Could not load libfunctions.dll.")
    print(f"Reason: {e}")
    print(f"This is usually a 32-bit vs 64-bit mismatch.")
    print(f"-------------\n")
    sys.exit(1) # Exit so we don't get NameError: 'lib' is not defined

# Define function signatures for ctypes
lib.initQueue.argtypes = [ctypes.POINTER(Queue)]
lib.initHeap.argtypes = [ctypes.POINTER(MinHeap), ctypes.c_int]
lib.enqueue.argtypes = [ctypes.POINTER(Queue), Request]
lib.dequeue.argtypes = [ctypes.POINTER(Queue), ctypes.POINTER(Request)]
lib.insertHeap.argtypes = [ctypes.POINTER(MinHeap), Request]
lib.extractMin.argtypes = [ctypes.POINTER(MinHeap), ctypes.POINTER(Request)]
lib.idExists.argtypes = [ctypes.POINTER(Queue), ctypes.POINTER(MinHeap), ctypes.c_int]
lib.idExists.restype = ctypes.c_int

# --- GUI Application ---
class WasteManagementGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Waste Management System")
        self.root.geometry("600x500")

        # Initialize Backend Data
        self.q = Queue()
        self.h = MinHeap()
        lib.initQueue(ctypes.byref(self.q))
        lib.initHeap(ctypes.byref(self.h), 10)

        self.setup_ui()

    def setup_ui(self):
        # Notebook (Tabs)
        self.tabs = ttk.Notebook(self.root)
        self.user_tab = ttk.Frame(self.tabs)
        self.admin_tab = ttk.Frame(self.tabs)
        
        self.tabs.add(self.user_tab, text="User Mode")
        self.tabs.add(self.admin_tab, text="Admin Mode")
        self.tabs.pack(expand=1, fill="both")

        self.setup_user_tab()
        self.setup_admin_tab()

    def setup_user_tab(self):
        tk.Label(self.user_tab, text="Add Bin Request", font=('Arial', 14, 'bold')).pack(pady=10)
        
        form = tk.Frame(self.user_tab)
        form.pack(pady=10)

        tk.Label(form, text="Bin ID:").grid(row=0, column=0)
        self.ent_id = tk.Entry(form)
        self.ent_id.grid(row=0, column=1)

        tk.Label(form, text="Area:").grid(row=1, column=0)
        self.ent_area = tk.Entry(form)
        self.ent_area.grid(row=1, column=1)

        tk.Label(form, text="Fill Level (0-100):").grid(row=2, column=0)
        self.ent_fill = tk.Entry(form)
        self.ent_fill.grid(row=2, column=1)

        tk.Button(self.user_tab, text="Submit Request", command=self.submit_request, bg="green", fg="white").pack(pady=10)

    def setup_admin_tab(self):
        tk.Label(self.admin_tab, text="Admin Controls", font=('Arial', 14, 'bold')).pack(pady=10)
        
        btn_frame = tk.Frame(self.admin_tab)
        btn_frame.pack()

        tk.Button(btn_frame, text="Move Queue to Heap", command=self.move_to_heap).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Auto-Clean Next", command=self.auto_clean, bg="blue", fg="white").grid(row=0, column=1, padx=5)
        
        self.tree = ttk.Treeview(self.admin_tab, columns=("ID", "Area", "Fill", "Priority"), show='headings')
        for col in ("ID", "Area", "Fill", "Priority"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(pady=20, fill="x")
        
        tk.Button(self.admin_tab, text="Refresh Heap View", command=self.refresh_heap).pack()

    # --- Logic ---
    def submit_request(self):
        try:
            bid = int(self.ent_id.get())
            area = self.ent_area.get().encode('utf-8')
            fill = int(self.ent_fill.get())
            
            if lib.idExists(ctypes.byref(self.q), ctypes.byref(self.h), bid):
                messagebox.showerror("Error", "ID already exists!")
                return

            req = Request(bid, area, fill, 100 - fill)
            lib.enqueue(ctypes.byref(self.q), req)
            messagebox.showinfo("Success", f"Bin {bid} added to queue.")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers.")

    def move_to_heap(self):
        req = Request()
        count = 0
        while lib.dequeue(ctypes.byref(self.q), ctypes.byref(req)):
            lib.insertHeap(ctypes.byref(self.h), req)
            count += 1
        self.refresh_heap()
        messagebox.showinfo("Admin", f"Moved {count} requests to Heap.")

    def auto_clean(self):
        req = Request()
        if lib.extractMin(ctypes.byref(self.h), ctypes.byref(req)):
            messagebox.showinfo("Cleaning", f"Cleaning Bin ID: {req.id} in {req.area.decode()} (Fill: {req.fill}%)")
            self.refresh_heap()
        else:
            messagebox.showwarning("Empty", "No bins in heap to clean.")

    def refresh_heap(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        for i in range(self.h.size):
            r = self.h.arr[i]
            self.tree.insert("", "end", values=(r.id, r.area.decode(), r.fill, r.priority))

if __name__ == "__main__":
    root = tk.Tk()
    app = WasteManagementGUI(root)
    root.mainloop()