import tkinter as tk
from tkinter import ttk, messagebox
from database import Session, Item

import tkinter as tk
from tkinter import ttk

class InventoryManagementWindow:
    def __init__(self):
        self.window = tk.Toplevel()
        self.window.title("Inventory Management")
        
        # Set up a classic Windows 3.1 style
        style = ttk.Style()
        style.theme_use('classic')  # Switching to 'classic' for a vintage look

        style.configure('TFrame', background='#f0f0f0')  # Lighter background for frames
        style.configure('TButton', background='#c0c0c0', foreground='black')  # Slightly darker buttons
        style.configure('TLabel', background='#f0f0f0', foreground='black')  # Lighter labels
        style.configure('TEntry', background='white', foreground='black')  # White entries for contrast
        style.configure('TSpinbox', background='white', foreground='black')  # Consistent with TEntry
        style.configure('Treeview', background='white', foreground='black', fieldbackground='white')  # Treeview for inventory
        
        # Set up frames and layout
        frame = ttk.Frame(self.window, padding="10 10 10 10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input fields for inventory items
        item_label = ttk.Label(frame, text="Item")
        item_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.item_entry = ttk.Entry(frame, width=20)
        self.item_entry.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))

        qty_label = ttk.Label(frame, text="Quantity")
        qty_label.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self.qty_spinbox = ttk.Spinbox(frame, from_=0, to=1000, width=10)
        self.qty_spinbox.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))

        add_item_button = ttk.Button(frame, text="Add Item", command=self.add_item)
        add_item_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))

        columns = ('item', 'qty')
        self.tree = ttk.Treeview(frame, columns=columns, show="headings")
        self.tree.heading('item', text='Item')
        self.tree.heading('qty', text='Quantity')
        self.tree.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))

        for i in range(2):
            frame.columnconfigure(i, weight=1)
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)

        # Load existing items from the database
        self.load_items()

    def load_items(self):
        """Load items from the database and display them."""
        session = Session()
        items = session.query(Item).all()
        for item in items:
            self.tree.insert('', 0, values=(item.name, item.quantity))
        session.close()

    def add_item(self):
        """Add an item to the inventory list."""
        item_name = self.item_entry.get()
        try:
            qty = int(self.qty_spinbox.get())
            if not item_name:
                raise ValueError("Item name cannot be empty.")
            if qty < 0:
                raise ValueError("Quantity cannot be negative.")
            
            session = Session()
            existing_item = session.query(Item).filter_by(name=item_name).first()
            if existing_item:
                existing_item.quantity += qty
            else:
                new_item = Item(name=item_name, quantity=qty)
                session.add(new_item)
            session.commit()
            session.close()
            
            self.refresh_items()
            self.item_entry.delete(0, tk.END)
            self.qty_spinbox.delete(0, tk.END)
            self.qty_spinbox.insert(0, "0")
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))

    def refresh_items(self):
        """Refresh the items in the treeview."""
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.load_items()

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    InventoryManagementWindow()
    root.mainloop()
