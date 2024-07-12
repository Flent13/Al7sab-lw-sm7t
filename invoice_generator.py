import tkinter as tk
from tkinter import ttk, messagebox
from docxtpl import DocxTemplate
import datetime
from database import Session, Item, Invoice, InvoiceItem

# Initialize the invoice list
invoice_list = []

# Utility Functions
def clear_item():
    """Clear the item entry fields."""
    qty_spinbox.delete(0, tk.END)
    qty_spinbox.insert(0, "1")
    item_combobox.set("")
    price_spinbox.delete(0, tk.END)
    price_spinbox.insert(0, "0.0")

def add_item():
    """Add an item to the invoice list."""
    try:
        qty = int(qty_spinbox.get())
        item = item_combobox.get()
        price = float(price_spinbox.get())
        if qty <= 0 or price < 0:
            raise ValueError("Quantity must be positive and price non-negative.")
        line_total = qty * price
        invoice_item = [qty, item, price, line_total]
        tree.insert('', 0, values=invoice_item)
        clear_item()
        invoice_list.append(invoice_item)
    except ValueError as e:
        messagebox.showerror("Input Error", str(e))

def new_invoice():
    """Reset the form for a new invoice."""
    first_name_entry.delete(0, tk.END)
    last_name_entry.delete(0, tk.END)
    phone_entry.delete(0, tk.END)
    clear_item()
    tree.delete(*tree.get_children())
    invoice_list.clear()

def generate_invoice():
    """Generate the invoice document."""
    if not first_name_entry.get() or not last_name_entry.get() or not phone_entry.get() or not invoice_list:
        messagebox.showwarning("Incomplete Data", "Please fill out all fields and add at least one item.")
        return
    
    session = Session()
    
    try:
        # Decrement item quantities in the database
        for item in invoice_list:
            item_name = item[1]
            qty = item[0]
            db_item = session.query(Item).filter_by(name=item_name).first()
            if db_item and db_item.quantity >= qty:
                db_item.quantity -= qty
            else:
                raise ValueError(f"Not enough quantity for item: {item_name}")
        
        # Save the invoice
        name = first_name_entry.get() + " " + last_name_entry.get()
        phone = phone_entry.get()
        subtotal = sum(item[3] for item in invoice_list)
        salestax = 0.1
        total = subtotal * (1 + salestax)
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        new_invoice = Invoice(
            customer_name=name,
            phone=phone,
            subtotal=subtotal,
            salestax=salestax,
            total=total,
            date=date
        )
        session.add(new_invoice)
        session.commit()
        
        # Save the invoice items
        for item in invoice_list:
            item_name = item[1]
            qty = item[0]
            unit_price = item[2]
            total_price = item[3]
            db_item = session.query(Item).filter_by(name=item_name).first()
            
            invoice_item = InvoiceItem(
                invoice_id=new_invoice.id,
                item_id=db_item.id,
                quantity=qty,
                unit_price=unit_price,
                total_price=total_price
            )
            session.add(invoice_item)
        
        session.commit()
        
        # Generate the invoice document
        doc = DocxTemplate("invoice_template.docx")
        doc.render({
            "name": name,
            "phone": phone,
            "invoice_list": invoice_list,
            "subtotal": subtotal,
            "salestax": f"{salestax * 100:.0f}%",
            "total": total
        })
        
        doc_name = f"new_invoice_{name.replace(' ', '_')}_{datetime.datetime.now():%Y-%m-%d-%H%M%S}.docx"
        doc.save(doc_name)
        messagebox.showinfo("Invoice Complete", "Invoice has been generated successfully.")
        
        new_invoice()
    
    except ValueError as e:
        session.rollback()
        messagebox.showerror("Inventory Error", str(e))
    
    finally:
        session.close()

def open_inventory():
    """Open the inventory management window."""
    import inventory_management
    inventory_management.InventoryManagementWindow()

def load_items():
    """Load items from the database into the item combobox."""
    session = Session()
    items = session.query(Item).all()
    item_list = [item.name for item in items]
    item_combobox['values'] = item_list
    session.close()

import tkinter as tk
from tkinter import ttk

# Initialize the main window
window = tk.Tk()
window.title("Invoice Generator Form")

# Set up a classic Windows 3.1 style
style = ttk.Style()
style.theme_use('classic')  # Using 'classic' theme for a more vintage look

style.configure('TFrame', background='#f0f0f0')  # Lighter background for frames
style.configure('TButton', background='#c0c0c0', foreground='black')  # Slightly darker buttons
style.configure('TLabel', background='#f0f0f0', foreground='black')  # Lighter labels
style.configure('TEntry', background='white', foreground='black')  # White entries for contrast
style.configure('TSpinbox', background='white', foreground='black')  # Consistent with TEntry
style.configure('Treeview', background='white', foreground='black', fieldbackground='white')  # Treeview for inventory

# Set up frames and layout
frame = ttk.Frame(window, padding="10 10 10 10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Input fields for customer information
first_name_label = ttk.Label(frame, text="First Name")
first_name_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
last_name_label = ttk.Label(frame, text="Last Name")
last_name_label.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

first_name_entry = ttk.Entry(frame, width=20)
last_name_entry = ttk.Entry(frame, width=20)
first_name_entry.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
last_name_entry.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))

phone_label = ttk.Label(frame, text="Phone")
phone_label.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
phone_entry = ttk.Entry(frame, width=20)
phone_entry.grid(row=1, column=2, padx=5, pady=5, sticky=(tk.W, tk.E))

# Input fields for invoice items
qty_label = ttk.Label(frame, text="Qty")
qty_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
qty_spinbox = ttk.Spinbox(frame, from_=1, to=100, width=5)
qty_spinbox.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)

item_label = ttk.Label(frame, text="Item")
item_label.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
item_combobox = ttk.Combobox(frame, width=20)
item_combobox.grid(row=3, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))

price_label = ttk.Label(frame, text="Unit Price")
price_label.grid(row=2, column=2, padx=5, pady=5, sticky=tk.W)
price_spinbox = ttk.Spinbox(frame, from_=0.0, to=500, increment=0.5, width=10)
price_spinbox.grid(row=3, column=2, padx=5, pady=5, sticky=(tk.W, tk.E))

# Buttons for adding items and generating invoices
add_item_button = ttk.Button(frame, text="Add item", command=add_item)
add_item_button.grid(row=4, column=2, padx=5, pady=5, sticky=(tk.W, tk.E))

columns = ('qty', 'item', 'price', 'total')
tree = ttk.Treeview(frame, columns=columns, show="headings")
tree.heading('qty', text='Qty')
tree.heading('item', text='Item')
tree.heading('price', text='Unit Price')
tree.heading('total', text="Total")
tree.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky=(tk.W, tk.E))

save_invoice_button = ttk.Button(frame, text="Generate Invoice", command=generate_invoice)
save_invoice_button.grid(row=6, column=0, columnspan=3, padx=5, pady=5, sticky=(tk.W, tk.E))
new_invoice_button = ttk.Button(frame, text="New Invoice", command=new_invoice)
new_invoice_button.grid(row=7, column=0, columnspan=3, padx=5, pady=5, sticky=(tk.W, tk.E))

inventory_button = ttk.Button(frame, text="Inventory", command=open_inventory)
inventory_button.grid(row=8, column=0, columnspan=3, padx=5, pady=5, sticky=(tk.W, tk.E))

# Configure grid weight
for i in range(3):
    frame.columnconfigure(i, weight=1)
window.columnconfigure(0, weight=1)
window.rowconfigure(0, weight=1)


# Load items into the item_combobox
load_items()

# Start the main event loop
window.mainloop()
