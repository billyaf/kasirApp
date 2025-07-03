# ui_pages.py
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.widgets import DateEntry
from tkinter import messagebox, simpledialog
import sqlite3
import database
from datetime import datetime
import os
import openpyxl
import sys

# Impor untuk membuat PDF
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def resource_path(relative_path):
    """ Mendapatkan path absolut ke aset, berfungsi untuk dev dan PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

#====================================================================
# KELAS DIALOG (JENDELA POPUP)
#====================================================================

class AddProductDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Tambah Produk Baru")
        form_frame = ttk.Frame(self, padding=20)
        form_frame.pack(expand=True, fill='both')
        fields = ["Nama Produk:", "Harga Jual:", "Stok Awal:"]
        self.entries = {}
        for i, field in enumerate(fields):
            ttk.Label(form_frame, text=field).grid(row=i, column=0, sticky='w', padx=5, pady=5)
            entry = ttk.Entry(form_frame, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entries[field] = entry
        button_frame = ttk.Frame(self, padding=(0, 10, 10, 10))
        button_frame.pack(fill='x')
        ttk.Button(button_frame, text="Simpan", command=self.save, bootstyle="success").pack(side='right', padx=5)
        ttk.Button(button_frame, text="Batal", command=self.destroy, bootstyle="secondary").pack(side='right')
        self.transient(parent)
        self.grab_set()
    def save(self):
        try:
            name = self.entries["Nama Produk:"].get()
            price = float(self.entries["Harga Jual:"].get())
            stock = int(self.entries["Stok Awal:"].get())
            if not name or price < 0 or stock < 0: raise ValueError
            if database.add_new_product(name, price, stock):
                Messagebox.show_info("Produk baru berhasil ditambahkan.", "Sukses")
                self.destroy()
            else:
                Messagebox.show_error("Nama produk sudah ada.", "Gagal")
        except ValueError:
            Messagebox.show_error("Pastikan semua data terisi dengan benar.", "Input Error", parent=self)

class EditProductDialog(tk.Toplevel):
    def __init__(self, parent, product_data):
        super().__init__(parent)
        self.title("Edit Produk")
        self.product_id = product_data[0]
        form_frame = ttk.Frame(self, padding=20)
        form_frame.pack(expand=True, fill='both')
        fields = ["Nama Produk:", "Harga Jual:", "Jumlah Stok:"]
        self.entries = {}
        for i, field in enumerate(fields):
            ttk.Label(form_frame, text=field).grid(row=i, column=0, sticky='w', padx=5, pady=5)
            entry = ttk.Entry(form_frame, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entry.insert(0, product_data[i+1])
            self.entries[field] = entry
        button_frame = ttk.Frame(self, padding=(0, 10, 10, 10))
        button_frame.pack(fill='x')
        ttk.Button(button_frame, text="Simpan Perubahan", command=self.save_changes, bootstyle="success").pack(side='right', padx=5)
        ttk.Button(button_frame, text="Batal", command=self.destroy, bootstyle="secondary").pack(side='right')
        self.transient(parent)
        self.grab_set()
    def save_changes(self):
        try:
            new_name = self.entries["Nama Produk:"].get()
            new_price = float(self.entries["Harga Jual:"].get())
            new_stock = int(self.entries["Jumlah Stok:"].get())
            if not new_name or new_price < 0 or new_stock < 0: raise ValueError
            if database.edit_product(self.product_id, new_name, new_price, new_stock):
                Messagebox.show_info("Perubahan berhasil disimpan.", "Sukses")
                self.destroy()
            else:
                Messagebox.show_error("Gagal menyimpan perubahan.", "Error")
        except ValueError:
            Messagebox.show_error("Pastikan harga dan stok valid.", "Input Error", parent=self)

#====================================================================
# KELAS HALAMAN (FRAME UTAMA)
#====================================================================

class LoginPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        main_frame = ttk.Frame(self, padding=40)
        main_frame.grid(row=0, column=0)
        ttk.Label(main_frame, text="Login Kasir", font=("Arial", 24, "bold")).pack(pady=20)
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(pady=10)
        ttk.Label(form_frame, text="Username:", font=("Arial", 12)).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.username_entry = ttk.Entry(form_frame, font=("Arial", 12), width=25)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(form_frame, text="Password:", font=("Arial", 12)).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.password_entry = ttk.Entry(form_frame, show="*", font=("Arial", 12), width=25)
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        login_button = ttk.Button(main_frame, text="Login", command=self.check_login, bootstyle="primary", width=20)
        login_button.pack(pady=20)
        self.username_entry.focus()
        self.controller.bind("<Return>", lambda event: self.check_login())
    def check_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        conn = sqlite3.connect(database.DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash, role FROM users WHERE username=?", (username,))
        user_data_db = cursor.fetchone()
        conn.close()
        if user_data_db and database.hash_password(password) == user_data_db[0]:
            # Mendapatkan ID pengguna dari database
            conn = sqlite3.connect(database.DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            user_id = cursor.fetchone()[0]
            conn.close()
            user_info = {'id': user_id, 'username': username, 'role': user_data_db[1]}
            self.controller.show_frame("MainPage", user_data=user_info)
        else:
            Messagebox.show_error("Username atau Password salah.", "Gagal Login")

class KasirPage(ttk.Frame):
    def __init__(self, parent, controller, user_data):
        super().__init__(parent, padding=15)
        self.controller = controller
        self.user_data = user_data
        
        self.all_products = [] 
        self.cart = {}
        self.total_belanja_var = tk.StringVar(value="Rp 0.00")
        
        self.columnconfigure(1, weight=3)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self._create_left_panel()
        self._create_right_panel() 
        self.reset_transaction()

    def _create_left_panel(self):
        left_frame = ttk.Frame(self)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        input_frame = ttk.Labelframe(left_frame, text="Cari & Input Barang", padding=15)
        input_frame.pack(fill="x", pady=(0, 10), expand=True)

        ttk.Label(input_frame, text="Cari Nama Produk:").pack(fill="x")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_change)
        search_entry = ttk.Entry(input_frame, textvariable=self.search_var)
        search_entry.pack(fill="x", pady=(0, 5))
        
        self.search_results_listbox = tk.Listbox(input_frame, height=5)
        self.search_results_listbox.pack(fill="x", expand=True, pady=(0, 10))
        self.search_results_listbox.bind("<Double-1>", self._add_selected_from_listbox)
        
        ttk.Label(input_frame, text="Jumlah:").pack(fill="x")
        self.quantity_spinbox = ttk.Spinbox(input_frame, from_=1, to=100)
        self.quantity_spinbox.pack(fill="x", pady=(0, 10))
        
        add_button = ttk.Button(input_frame, text="Tambah ke Keranjang", command=self._add_to_cart_from_search, bootstyle="success")
        add_button.pack(fill="x")
        
        payment_frame = ttk.Labelframe(left_frame, text="Pembayaran", padding=15)
        payment_frame.pack(fill="x")
        ttk.Label(payment_frame, text="Total Belanja:", font="-size 12").pack(fill="x")
        ttk.Label(payment_frame, textvariable=self.total_belanja_var, font="-size 20 -weight bold").pack(fill="x", pady=(0,10))
        ttk.Label(payment_frame, text="Uang Bayar (Rp):").pack(fill="x")
        self.paid_amount_entry = ttk.Entry(payment_frame)
        self.paid_amount_entry.pack(fill="x", pady=(0,10))
        pay_button = ttk.Button(payment_frame, text="Proses & Buat Struk", command=self._process_payment, bootstyle="primary")
        pay_button.pack(fill="x")

    def _create_right_panel(self):
        right_frame = ttk.Frame(self)
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.rowconfigure(0, weight=1)
        right_frame.columnconfigure(0, weight=1)
        
        cart_frame = ttk.Labelframe(right_frame, text="Keranjang Belanja", padding=15)
        cart_frame.grid(row=0, column=0, sticky="nsew")
        cart_frame.rowconfigure(0, weight=1)
        cart_frame.columnconfigure(0, weight=1)
        
        cols = ("ID", "Nama Barang", "Jml", "Harga Satuan", "Subtotal")
        self.cart_tree = ttk.Treeview(cart_frame, columns=cols, show="headings", bootstyle="primary")
        for col in cols: self.cart_tree.heading(col, text=col)
        
        self.cart_tree.column("ID", width=0, stretch=tk.NO) 
        self.cart_tree.column("Jml", width=50, anchor="center")
        self.cart_tree.column("Harga Satuan", anchor="e")
        self.cart_tree.column("Subtotal", anchor="e")
        self.cart_tree.grid(row=0, column=0, sticky="nsew")
        
        self.cart_tree.bind("<Double-1>", self.edit_cart_item_quantity)
        
        action_frame = ttk.Frame(right_frame, padding=(0, 15))
        action_frame.grid(row=1, column=0, sticky="ew")
        
        edit_button = ttk.Button(action_frame, text="Edit Jumlah", command=self.edit_cart_item_quantity, bootstyle="info")
        edit_button.pack(side="left")
        reset_button = ttk.Button(action_frame, text="Transaksi Baru", command=self.reset_transaction, bootstyle="danger")
        reset_button.pack(side="right")

    def _on_search_change(self, *args):
        search_term = self.search_var.get().lower()
        self.search_results_listbox.delete(0, 'end')
        if not search_term: return
        for product in self.all_products:
            if search_term in product['nama_produk'].lower():
                display_text = f"{product['nama_produk']} (Stok: {product['stok']})"
                self.search_results_listbox.insert('end', display_text)

    def _add_selected_from_listbox(self, event=None):
        selected_indices = self.search_results_listbox.curselection()
        if not selected_indices: return
        selected_text = self.search_results_listbox.get(selected_indices[0])
        self._add_to_cart(selected_text)

    def _add_to_cart_from_search(self):
        self._add_selected_from_listbox()
            
    def _load_products_from_db(self):
        self.all_products = database.get_all_products()
            
    def _add_to_cart(self, selected_product_string):
        if not selected_product_string: return
        product_name_from_string = selected_product_string.split(" (Stok:")[0]
        product_info = next((p for p in self.all_products if p['nama_produk'] == product_name_from_string), None)
        if not product_info: return

        product_id = product_info['id']
        try:
            quantity_to_add = int(self.quantity_spinbox.get())
            if quantity_to_add <= 0: raise ValueError
        except ValueError:
            Messagebox.show_error("Jumlah harus angka positif.", "Error")
            return
        
        current_quantity_in_cart = self.cart.get(product_id, {}).get('jumlah', 0)
        total_quantity_needed = current_quantity_in_cart + quantity_to_add
        
        if total_quantity_needed > product_info['stok']:
            Messagebox.show_warning(f"Stok '{product_info['nama_produk']}' tidak mencukupi. Sisa stok: {product_info['stok']}", "Stok Kurang")
            return
            
        if product_id in self.cart: 
            self.cart[product_id]['jumlah'] += quantity_to_add
        else: 
            self.cart[product_id] = {'nama': product_info['nama_produk'], 'harga': product_info['harga_jual'], 'jumlah': quantity_to_add, 'stok': product_info['stok']}
            
        self.quantity_spinbox.set(1)
        self.search_var.set("")
        self._update_cart_display()

    def _update_cart_display(self):
        for item in self.cart_tree.get_children(): self.cart_tree.delete(item)
        current_total = 0
        for product_id, details in self.cart.items():
            subtotal = details['jumlah'] * details['harga']
            current_total += subtotal
            self.cart_tree.insert("", "end", values=(product_id, details['nama'], details['jumlah'], f"{details['harga']:,.0f}", f"{subtotal:,.0f}"))
        self.total_belanja_var.set(f"Rp {current_total:,.2f}")
    
    def edit_cart_item_quantity(self, event=None):
        selected_item = self.cart_tree.focus()
        if not selected_item:
            Messagebox.show_warning("Pilih barang di keranjang yang ingin diubah.", "Pilih Barang")
            return
        item_values = self.cart_tree.item(selected_item)['values']
        product_id = item_values[0]
        product_name = item_values[1]
        current_quantity = item_values[2]
        new_quantity_str = simpledialog.askstring("Ubah Jumlah", f"Masukkan jumlah baru untuk '{product_name}':", initialvalue=current_quantity, parent=self)
        if new_quantity_str:
            try:
                new_quantity = int(new_quantity_str)
                if new_quantity < 0:
                    Messagebox.show_error("Jumlah tidak boleh negatif.", "Error")
                    return
                if new_quantity > self.cart[product_id]['stok']:
                    Messagebox.show_warning(f"Stok '{product_name}' tidak mencukupi. Sisa stok: {self.cart[product_id]['stok']}", "Stok Kurang")
                    return
                if new_quantity == 0:
                    del self.cart[product_id]
                else:
                    self.cart[product_id]['jumlah'] = new_quantity
                self._update_cart_display()
            except (ValueError, TypeError):
                Messagebox.show_error("Harap masukkan angka yang valid.", "Input Salah")

    def _process_payment(self):
        if not self.cart: 
            Messagebox.show_warning("Keranjang masih kosong.", "Peringatan")
            return
        try:
            paid_amount = float(self.paid_amount_entry.get())
            total_amount = sum(details['harga'] * details['jumlah'] for details in self.cart.values())
            if paid_amount < total_amount: 
                Messagebox.show_error("Uang bayar kurang.", "Error")
                return
        except (ValueError, TypeError):
            Messagebox.show_error("Jumlah bayar tidak valid.", "Error")
            return
        change = paid_amount - total_amount
        transaction_id = database.record_transaction(total_amount, self.user_data.get('id'), self.cart)
        if transaction_id is None:
            Messagebox.show_error("Gagal menyimpan transaksi ke database.", "Database Error")
            return
        try:
            filename = self.create_receipt_pdf(transaction_id, total_amount, paid_amount, change)
            Messagebox.show_info(f"Transaksi Berhasil. Struk PDF '{filename}' telah dibuat dan akan dibuka.", "Sukses")
            os.startfile(filename)
        except Exception as e:
            Messagebox.show_error(f"Gagal membuat atau membuka PDF: {e}", "Error PDF")
        self.reset_transaction()

    def create_receipt_pdf(self, trx_id, total, bayar, kembali):
        dokumen_path = os.path.join(os.path.expanduser('~'), 'Documents')
        struk_path = os.path.join(dokumen_path, 'Struk Warung')
        os.makedirs(struk_path, exist_ok=True)
        waktu_file = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(struk_path, f"struk_{waktu_file}.pdf")
        
        lebar_kertas, tinggi_kertas = 80 * mm, 120 * mm 
        c = canvas.Canvas(filename, pagesize=(lebar_kertas, tinggi_kertas))
        
        try:
            pdfmetrics.registerFont(TTFont('Courier', 'Courier.ttf'))
            c.setFont('Courier', 8)
        except:
            print("Peringatan: Font Courier tidak ditemukan, menggunakan font default.")
            c.setFont("Helvetica", 7)
            
        x = 4 * mm
        line_height = 4 * mm
        y = tinggi_kertas - (10 * mm)

        # Menggambar Teks Header
        nama_toko = "TOKO ELVAN"
        alamat_toko = "Jl. Raya Ciawi No.21"
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(lebar_kertas / 2, y, nama_toko)
        y -= line_height
        c.setFont("Helvetica", 7)
        c.drawCentredString(lebar_kertas / 2, y, alamat_toko)
        y -= line_height * 1.5
        c.line(x, y, lebar_kertas - x, y)
        y -= line_height

        c.setFont("Helvetica", 8)
        c.drawString(x, y, f"No Transaksi: {trx_id}")
        y -= line_height
        c.drawString(x, y, f"Kasir: {self.user_data.get('username')}")
        y -= line_height
        c.drawString(x, y, f"Waktu: {datetime.now().strftime('%d-%m-%Y %H:%M')}")
        y -= line_height * 1.5
        c.line(x, y, lebar_kertas - x, y)
        y -= line_height

        for item in self.cart.values():
            harga_total_item = item['harga'] * item['jumlah']
            c.drawString(x, y, f"{item['nama']}")
            y -= line_height
            c.drawString(x + (4*mm), y, f"{item['jumlah']} x {item['harga']:,.0f}")
            c.drawRightString(lebar_kertas - x, y, f"{harga_total_item:,.0f}")
            y -= line_height

        y -= line_height * 0.5
        c.line(x, y, lebar_kertas - x, y)
        y -= line_height
        
        c.drawString(x, y, "TOTAL")
        c.drawRightString(lebar_kertas - x, y, f"Rp {total:,.0f}")
        y -= line_height
        c.drawString(x, y, "BAYAR")
        c.drawRightString(lebar_kertas - x, y, f"Rp {bayar:,.0f}")
        y -= line_height
        c.drawString(x, y, "KEMBALI")
        c.drawRightString(lebar_kertas - x, y, f"Rp {kembali:,.0f}")
        y -= line_height * 1.5
        c.line(x, y, lebar_kertas - x, y)
        y -= line_height * 2

        c.drawCentredString(lebar_kertas / 2, y, "Terima Kasih!")
        
        c.save()
        return filename

    def reset_transaction(self):
        self.cart.clear()
        self.total_belanja_var.set("Rp 0.00")
        self.paid_amount_entry.delete(0, 'end')
        self.quantity_spinbox.set(1)
        self.search_var.set("")
        self._update_cart_display()
        self._load_products_from_db()

class StokPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding=15)
        ttk.Label(self, text="Manajemen Produk & Stok", font="-size 16 -weight bold").pack(pady=(0,10))
        tree_frame = ttk.Frame(self)
        tree_frame.pack(expand=True, fill='both')
        cols = ('ID', 'Nama Produk', 'Harga Jual', 'Stok Tersedia')
        self.tree = ttk.Treeview(tree_frame, columns=cols, show='headings', bootstyle='primary')
        for col in cols: self.tree.heading(col, text=col)
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Nama Produk", width=300)
        self.tree.column("Harga Jual", anchor="e")
        self.tree.column("Stok Tersedia", width=120, anchor="center")
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        action_frame = ttk.Frame(self)
        action_frame.pack(fill='x', pady=10)
        ttk.Button(action_frame, text="Refresh Data", command=self.load_stock, bootstyle="info").pack(side='left', padx=(0,10))
        ttk.Button(action_frame, text="Tambah Produk Baru", command=self.open_add_product_dialog, bootstyle="success").pack(side='left', padx=(0,10))
        ttk.Button(action_frame, text="Edit Produk/Stok", command=self.open_edit_dialog, bootstyle="warning").pack(side='left', padx=(0,10))
        ttk.Button(action_frame, text="Hapus Produk", command=self.open_delete_dialog, bootstyle="danger").pack(side='left')
        self.load_stock()
    def load_stock(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        for product in database.get_all_products():
            self.tree.insert('', 'end', values=(product['id'], product['nama_produk'], product['harga_jual'], product['stok']))
    def open_add_product_dialog(self):
        dialog = AddProductDialog(self)
        self.wait_window(dialog)
        self.load_stock()
    def open_edit_dialog(self):
        selected_item = self.tree.focus()
        if not selected_item: 
            Messagebox.show_warning("Pilih produk yang ingin diedit.", "Peringatan")
            return
        product_id = self.tree.item(selected_item)['values'][0]
        conn = sqlite3.connect(database.DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nama_produk, harga_jual, stok FROM products WHERE id = ?", (product_id,))
        product_data_to_edit = cursor.fetchone()
        conn.close()
        if product_data_to_edit:
            dialog = EditProductDialog(self, product_data_to_edit)
            self.wait_window(dialog)
            self.load_stock()
    def open_delete_dialog(self):
        selected_item = self.tree.focus()
        if not selected_item:
            Messagebox.show_warning("Pilih produk yang ingin dihapus.", "Peringatan")
        return
    
        item_details = self.tree.item(selected_item)
        product_id = item_details['values'][0]
        product_name = item_details['values'][1]

        answer = messagebox.askyesno(
            "Konfirmasi Hapus", 
            f"Anda yakin ingin menghapus produk '{product_name}' secara permanen?\n\nTindakan ini tidak dapat dibatalkan.",
            parent=self
        )

        if answer:
            # --- PERBAIKAN DI SINI ---
            if database.delete_product(product_id):
                Messagebox.show_info("Produk berhasil dihapus.", "Sukses")
                self.load_stock()
            else:
                Messagebox.show_error("Gagal menghapus produk dari database.", "Error")

class RiwayatStokPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding=15)
        ttk.Label(self, text="Riwayat Pergerakan Stok", font="-size 16 -weight bold").pack(pady=(0,10))
        tree_frame = ttk.Frame(self)
        tree_frame.pack(expand=True, fill='both')
        cols = ('Waktu', 'Nama Produk', 'Perubahan', 'Keterangan')
        self.tree = ttk.Treeview(tree_frame, columns=cols, show='headings', bootstyle='primary')
        for col in cols: self.tree.heading(col, text=col)
        self.tree.column("Waktu", width=160)
        self.tree.column("Nama Produk", width=250)
        self.tree.column("Perubahan", width=100, anchor='center')
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        ttk.Button(self, text="Refresh Data", command=self.load_history, bootstyle="info").pack(pady=10)
        self.load_history()
    def load_history(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        for row in database.get_stock_history():
            self.tree.insert('', 'end', values=row)

class LaporanPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding=15)
        self.controller = controller
        self.current_report_data = []
        self.current_report_title = ""
        control_frame = ttk.Frame(self)
        control_frame.pack(fill='x', pady=(0, 15))
        daily_frame = ttk.Labelframe(control_frame, text="Laporan Harian", padding=10)
        daily_frame.pack(side='left', padx=(0, 10))
        self.date_entry = DateEntry(daily_frame, bootstyle="primary", dateformat='%Y-%m-%d')
        self.date_entry.pack(side='left', padx=(0,10))
        ttk.Button(daily_frame, text="Tampilkan", command=self.show_daily_report, bootstyle="primary").pack(side='left')
        monthly_frame = ttk.Labelframe(control_frame, text="Laporan Bulanan", padding=10)
        monthly_frame.pack(side='left', padx=(0, 10))
        self.month_spin = ttk.Spinbox(monthly_frame, from_=1, to=12, width=5)
        self.month_spin.set(datetime.now().month)
        self.month_spin.pack(side='left', padx=(0,5))
        self.year_spin = ttk.Spinbox(monthly_frame, from_=2020, to=2030, width=7)
        self.year_spin.set(datetime.now().year)
        self.year_spin.pack(side='left', padx=(0,10))
        ttk.Button(monthly_frame, text="Tampilkan", command=self.show_monthly_report, bootstyle="primary").pack(side='left')
        download_button = ttk.Button(control_frame, text="Download Excel", command=self.export_to_excel, bootstyle="success")
        download_button.pack(side='right', padx=10, pady=10)
        report_frame = ttk.Frame(self)
        report_frame.pack(expand=True, fill='both')
        report_frame.rowconfigure(1, weight=1)
        report_frame.columnconfigure(0, weight=1)
        self.report_title_label = ttk.Label(report_frame, text="Laporan Penjualan", font="-size 14 -weight bold")
        self.report_title_label.grid(row=0, column=0, sticky='w', pady=(0, 5))
        cols = ('Waktu', 'ID Trx', 'Nama Produk', 'Jml', 'Harga Satuan', 'Subtotal')
        self.report_tree = ttk.Treeview(report_frame, columns=cols, show="headings", bootstyle='primary')
        for col in cols: self.report_tree.heading(col, text=col)
        self.report_tree.column("Waktu", width=140)
        self.report_tree.column("ID Trx", width=60, anchor='center')
        self.report_tree.column("Jml", width=50, anchor='center')
        self.report_tree.column("Harga Satuan", anchor='e')
        self.report_tree.column("Subtotal", anchor='e')
        self.report_tree.grid(row=1, column=0, sticky='nsew')
        self.summary_label = ttk.Label(report_frame, text="Total Omzet: Rp 0", font="-size 12")
        self.summary_label.grid(row=2, column=0, sticky='e', pady=(5,0))
    def show_daily_report(self):
        try:
            selected_date_str = self.date_entry.entry.get()
            selected_date_obj = datetime.strptime(selected_date_str, '%Y-%m-%d')
            self.current_report_data = database.get_detailed_report(selected_date_str, selected_date_str)
            self.current_report_title = f"Laporan Harian - {selected_date_obj.strftime('%d %B %Y')}"
            self.update_report_table()
        except Exception as e:
            Messagebox.show_error(f"Gagal menampilkan laporan harian: {e}", "Error")
    def show_monthly_report(self):
        year = int(self.year_spin.get())
        month = int(self.month_spin.get())
        import calendar
        start_date = f"{year}-{month:02d}-01"
        last_day = calendar.monthrange(year, month)[1]
        end_date = f"{year}-{month:02d}-{last_day}"
        self.current_report_data = database.get_detailed_report(start_date, end_date)
        month_name = datetime(year, month, 1).strftime('%B')
        self.current_report_title = f"Laporan Bulanan - {month_name} {year}"
        self.update_report_table()
    def update_report_table(self):
        for item in self.report_tree.get_children(): self.report_tree.delete(item)
        total_omzet = 0
        for row in self.current_report_data:
            waktu = datetime.fromisoformat(row['timestamp']).strftime('%d-%m %H:%M')
            trx_id = row['transaction_id']
            produk = row['nama_produk']
            jml = row['quantity']
            harga = f"{row['price_at_sale']:,.0f}"
            subtotal = f"{row['subtotal']:,.0f}"
            self.report_tree.insert('', 'end', values=(waktu, trx_id, produk, jml, harga, subtotal))
            total_omzet += row['subtotal']
        self.report_title_label.config(text=self.current_report_title)
        self.summary_label.config(text=f"Total Omzet: Rp {total_omzet:,.0f}")
    def export_to_excel(self):
        if not self.current_report_data:
            Messagebox.show_warning("Tidak ada data untuk di-download. Silakan tampilkan laporan terlebih dahulu.", "Peringatan")
            return
        try:
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.title = "Laporan Penjualan"
            headers = ['Waktu', 'ID Transaksi', 'Nama Produk', 'Jumlah', 'Harga Satuan', 'Subtotal']
            sheet.append(headers)
            for row_data in self.current_report_data:
                sheet.append([
                    row_data['timestamp'],
                    row_data['transaction_id'],
                    row_data['nama_produk'],
                    row_data['quantity'],
                    row_data['price_at_sale'],
                    row_data['subtotal']
                ])
            safe_title = self.current_report_title.replace(" ", "_").replace("-", "")
            filename = f"{safe_title}.xlsx"
            dokumen_path = os.path.join(os.path.expanduser('~'), 'Documents')
            laporan_path = os.path.join(dokumen_path, 'Laporan Toko Elvan')
            os.makedirs(laporan_path, exist_ok=True)
            full_path = os.path.join(laporan_path, filename)
            workbook.save(full_path)
            Messagebox.show_info(f"Laporan berhasil di-download!\n\nTersimpan di: {full_path}", "Download Sukses")
            os.startfile(laporan_path)
        except Exception as e:
            Messagebox.show_error(f"Gagal membuat file Excel: {e}", "Error")

class KaryawanPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding=15)
        self.controller = controller
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)
        add_frame = ttk.Labelframe(self, text="Tambah Karyawan Baru", padding=20)
        add_frame.grid(row=0, column=0, padx=(0,10), pady=10, sticky='nsew')
        ttk.Label(add_frame, text="Username:").grid(row=0, column=0, sticky='w', pady=5, padx=5)
        self.username_entry = ttk.Entry(add_frame)
        self.username_entry.grid(row=0, column=1, pady=5, padx=5, sticky='ew')
        ttk.Label(add_frame, text="Password:").grid(row=1, column=0, sticky='w', pady=5, padx=5)
        self.password_entry = ttk.Entry(add_frame, show="*")
        self.password_entry.grid(row=1, column=1, pady=5, padx=5, sticky='ew')
        ttk.Button(add_frame, text="Simpan Karyawan", command=self.save_employee, bootstyle="success").grid(row=2, columnspan=2, pady=15)
        list_frame = ttk.Labelframe(self, text="Daftar Pengguna Aktif", padding=15)
        list_frame.grid(row=0, column=1, padx=(10, 0), pady=10, sticky='nsew')
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)
        cols = ('ID', 'Username', 'Peran')
        self.user_tree = ttk.Treeview(list_frame, columns=cols, show='headings')
        for col in cols: self.user_tree.heading(col, text=col)
        self.user_tree.column("ID", width=50, anchor="center")
        self.user_tree.pack(expand=True, fill='both', pady=(0, 10))
        action_frame = ttk.Frame(list_frame)
        action_frame.pack(fill='x')
        delete_button = ttk.Button(action_frame, text="Hapus Pengguna", command=self.delete_selected_user, bootstyle="danger")
        delete_button.pack(side='right')
        self.load_users()
    def load_users(self):
        for i in self.user_tree.get_children(): self.user_tree.delete(i)
        for user in database.get_all_users_and_roles():
            self.user_tree.insert('', 'end', values=(user['id'], user['username'], user['role']))
    def save_employee(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if not username or not password:
            Messagebox.show_warning("Data tidak boleh kosong.", "Peringatan")
            return
        if database.add_employee(username, password):
            Messagebox.show_info("Karyawan berhasil ditambahkan.", "Sukses")
            self.username_entry.delete(0, 'end')
            self.password_entry.delete(0, 'end')
            self.load_users()
        else:
            Messagebox.show_error("Username sudah ada.", "Gagal")
    def delete_selected_user(self):
        selected_item = self.user_tree.focus()
        if not selected_item:
            Messagebox.show_warning("Pilih pengguna yang ingin dihapus.", "Peringatan")
            return
        item_details = self.user_tree.item(selected_item)['values']
        user_id = item_details[0]
        username = item_details[1]
        user_role = item_details[2]
        if user_role == 'admin':
            Messagebox.show_error("Akun dengan peran 'admin' tidak dapat dihapus.", "Aksi Ditolak")
            return
        answer = messagebox.askyesno("Konfirmasi Hapus", f"Anda yakin ingin menghapus pengguna '{username}' secara permanen?", parent=self)
        if answer:
            if database.delete_user(user_id):
                Messagebox.show_info(f"Pengguna '{username}' berhasil dihapus.", "Sukses")
                self.load_users()
            else:
                Messagebox.show_error("Gagal menghapus pengguna dari database.", "Error")

class RiwayatTransaksiPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding=15)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=1)
        ttk.Label(self, text="Riwayat Semua Transaksi", font="-size 16 -weight bold").grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="w")
        left_frame = ttk.Labelframe(self, text="Daftar Transaksi", padding=10)
        left_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        left_frame.rowconfigure(0, weight=1)
        left_frame.columnconfigure(0, weight=1)
        cols_header = ('ID Transaksi', 'Waktu', 'Kasir', 'Total Belanja')
        self.header_tree = ttk.Treeview(left_frame, columns=cols_header, show='headings', bootstyle='primary')
        for col in cols_header: self.header_tree.heading(col, text=col)
        self.header_tree.column("ID Transaksi", width=100, anchor='center')
        self.header_tree.column("Waktu", width=160)
        self.header_tree.grid(row=0, column=0, sticky="nsew")
        self.header_tree.bind("<<TreeviewSelect>>", self.show_transaction_details)
        right_frame = ttk.Labelframe(self, text="Detail Barang", padding=10)
        right_frame.grid(row=1, column=1, sticky="nsew")
        right_frame.rowconfigure(0, weight=1)
        right_frame.columnconfigure(0, weight=1)
        cols_detail = ('Nama Barang', 'Jumlah', 'Harga Saat Transaksi')
        self.detail_tree = ttk.Treeview(right_frame, columns=cols_detail, show='headings', bootstyle='info')
        for col in cols_detail: self.detail_tree.heading(col, text=col)
        self.detail_tree.column("Jumlah", width=60, anchor='center')
        self.detail_tree.grid(row=0, column=0, sticky="nsew")
        self.load_history()
    def load_history(self):
        for item in self.header_tree.get_children(): self.header_tree.delete(item)
        for trx in database.get_transaction_history():
            total_formatted = f"Rp {trx['total_amount']:,.0f}"
            self.header_tree.insert('', 'end', values=(trx['id'], trx['timestamp'], trx['kasir'], total_formatted))
    def show_transaction_details(self, event):
        selected_item = self.header_tree.focus()
        if not selected_item: return
        for item in self.detail_tree.get_children(): self.detail_tree.delete(item)
        transaction_id = self.header_tree.item(selected_item)['values'][0]
        details = database.get_transaction_details_by_id(transaction_id)
        for item in details:
            price_formatted = f"Rp {item['price_at_sale']:,.0f}"
            self.detail_tree.insert('', 'end', values=(item['nama_produk'], item['quantity'], price_formatted))