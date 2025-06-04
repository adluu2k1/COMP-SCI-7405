import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import database
import utils
from datetime import datetime

class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management")
        self.root.geometry("800x600")
        
        # Tabs
        tab_control = ttk.Notebook(root)
        self.stock_tab = ttk.Frame(tab_control)
        self.orders_tab = ttk.Frame(tab_control)
        tab_control.add(self.stock_tab, text='Stock')
        tab_control.add(self.orders_tab, text='Orders')
        tab_control.pack(expand=1, fill='both')

        self.create_stock_tab()
        self.create_orders_tab()
        self.refresh_stock()
        self.refresh_orders()

    def create_stock_tab(self):
        # Stock Tree
        self.stock_tree = ttk.Treeview(self.stock_tab, columns=("ID", "Name", "Qty", "Price"), show='headings')
        for col in self.stock_tree['columns']:
            self.stock_tree.heading(col, text=col)
        self.stock_tree.pack(fill='both', expand=1)

        # Stock Buttons
        frame = tk.Frame(self.stock_tab)
        frame.pack(pady=10)
        tk.Button(frame, text="Add Stock", command=self.add_stock).pack(side='left', padx=5)
        tk.Button(frame, text="Edit Stock", command=self.edit_stock).pack(side='left', padx=5)
        tk.Button(frame, text="Delete Stock", command=self.delete_stock).pack(side='left', padx=5)

    def create_orders_tab(self):
        self.orders_tree = ttk.Treeview(self.orders_tab, columns=("ID", "Stock", "Qty", "Total", "Date"), show='headings')
        for col in self.orders_tree['columns']:
            self.orders_tree.heading(col, text=col)
        self.orders_tree.pack(fill='both', expand=1)

        frame = tk.Frame(self.orders_tab)
        frame.pack(pady=10)
        tk.Button(frame, text="Add Order", command=self.add_order).pack(side='left', padx=5)
        tk.Button(frame, text="Export PDF Report", command=self.export_pdf).pack(side='left', padx=5)

    def refresh_stock(self):
        for row in self.stock_tree.get_children():
            self.stock_tree.delete(row)
        for item in database.get_all_stock():
            self.stock_tree.insert('', 'end', values=item)

    def refresh_orders(self):
        for row in self.orders_tree.get_children():
            self.orders_tree.delete(row)
        for item in database.get_all_orders():
            self.orders_tree.insert('', 'end', values=item)

    def add_stock(self):
        self.stock_form()

    def edit_stock(self):
        selected = self.stock_tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Select an item to edit.")
            return
        item = self.stock_tree.item(selected)['values']
        self.stock_form(item)

    def stock_form(self, data=None):
        form = tk.Toplevel(self.root)
        form.title("Stock Form")
        tk.Label(form, text="Name").grid(row=0, column=0)
        tk.Label(form, text="Quantity").grid(row=1, column=0)
        tk.Label(form, text="Price").grid(row=2, column=0)

        name = tk.Entry(form)
        qty = tk.Entry(form)
        price = tk.Entry(form)

        if data:
            name.insert(0, data[1])
            qty.insert(0, data[2])
            price.insert(0, data[3])

        name.grid(row=0, column=1)
        qty.grid(row=1, column=1)
        price.grid(row=2, column=1)

        def save():
            if data:
                database.update_stock(data[0], name.get(), int(qty.get()), float(price.get()))
            else:
                database.add_stock(name.get(), int(qty.get()), float(price.get()))
            self.refresh_stock()
            form.destroy()

        tk.Button(form, text="Save", command=save).grid(row=3, column=0, columnspan=2)

    def delete_stock(self):
        selected = self.stock_tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Select an item to delete.")
            return
        item = self.stock_tree.item(selected)['values']
        database.delete_stock(item[0])
        self.refresh_stock()

    def add_order(self):
        form = tk.Toplevel(self.root)
        form.title("Add Order")

        tk.Label(form, text="Select Stock").grid(row=0, column=0)
        stock_list = database.get_all_stock()
        stock_names = [f"{item[0]} - {item[1]} (Qty: {item[2]})" for item in stock_list]
        
        selected_stock = tk.StringVar()
        stock_dropdown = ttk.Combobox(form, textvariable=selected_stock, values=stock_names, state='readonly')
        stock_dropdown.grid(row=0, column=1)

        tk.Label(form, text="Quantity").grid(row=1, column=0)
        qty = tk.Entry(form)
        qty.grid(row=1, column=1)

        def place_order():
            try:
                if not stock_dropdown.get():
                    messagebox.showerror("Error", "Please select a stock item.")
                    return
                stock_id = int(stock_dropdown.get().split(" - ")[0])
                quantity = int(qty.get())
                database.add_order(stock_id, quantity, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                self.refresh_orders()
                self.refresh_stock()
                form.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(form, text="Place Order", command=place_order).grid(row=2, column=0, columnspan=2)


    def export_pdf(self):
        file = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if file:
            utils.export_sales_report(file)
            messagebox.showinfo("Success", f"Report exported to {file}")

def main():
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
