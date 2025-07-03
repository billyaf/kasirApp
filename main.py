# main.py
import tkinter as tk
import ttkbootstrap as ttk
import database
from ui_pages import LoginPage, KasirPage, StokPage, LaporanPage, KaryawanPage, RiwayatStokPage, RiwayatTransaksiPage

from PIL import Image, ImageTk
import os
import sys

def resource_path(relative_path):
    """ Mendapatkan path absolut ke aset, berfungsi untuk dev dan PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

#====================================================================
# KELAS-KELAS APLIKASI
#====================================================================

class SplashScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Memuat Aplikasi")
        self.overrideredirect(True)
        lebar_splash = 400
        tinggi_splash = 300
        pos_x = (self.winfo_screenwidth() - lebar_splash) // 2
        pos_y = (self.winfo_screenheight() - tinggi_splash) // 2
        self.geometry(f"{lebar_splash}x{tinggi_splash}+{pos_x}+{pos_y}")
        main_frame = tk.Frame(self, background="white")
        main_frame.pack(expand=True, fill='both')
        try:
            logo_path = resource_path("logo.png")
            logo_pil = Image.open(logo_path)
            logo_pil = logo_pil.resize((128, 128), Image.Resampling.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(logo_pil) 
            tk.Label(main_frame, image=self.logo_img, background="white").pack(pady=(40, 10))
        except Exception as e:
            print(f"Gagal memuat logo: {e}")
            tk.Label(main_frame, text="TOKO ELVAN", font=("Arial", 24, "bold"), background="white").pack(pady=(60, 10))
        tk.Label(main_frame, text="Memuat Aplikasi...", font=("Arial", 10), background="white").pack(pady=10)
        self.after(3000, self.finish_splash)

    def finish_splash(self):
        self.master.deiconify()
        self.destroy()

class App(ttk.Window):
    def __init__(self):
        super().__init__(themename="journal")
        self.withdraw()
        
        self.title("TOKO ELVAN - Aplikasi Kasir")
        self.geometry("1100x700")
        self.place_window_center()
        
        try:
            try:
                icon_path = resource_path("logo.ico")
                self.iconbitmap(icon_path)
            except tk.TclError:
                icon_path_png = resource_path("logo_only.png")
                logo_img = tk.PhotoImage(file=icon_path_png)
                self.iconphoto(True, logo_img)
        except Exception as e:
            print(f"Peringatan: Gagal memuat ikon aplikasi: {e}")
        
        self.splash = SplashScreen(self)
        
        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        login_frame = LoginPage(parent=container, controller=self)
        self.frames[LoginPage.__name__] = login_frame
        login_frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame("LoginPage")

    def show_frame(self, page_name, user_data=None):
        if page_name == "MainPage":
            if "MainPage" in self.frames: self.frames["MainPage"].destroy()
            main_frame = MainPage(parent=self.frames[LoginPage.__name__].master, controller=self, user_data=user_data)
            self.frames[MainPage.__name__] = main_frame
            main_frame.grid(row=0, column=0, sticky="nsew")
            main_frame.tkraise()
        else:
            frame = self.frames[page_name]
            frame.tkraise()

class MainPage(ttk.Frame):
    def __init__(self, parent, controller, user_data):
        super().__init__(parent)
        self.controller = controller
        self.user_data = user_data
        
        header_frame = ttk.Frame(self, padding=(15, 10))
        header_frame.pack(fill='x')
        
        welcome_text = f"Selamat Datang, {self.user_data.get('username')} ({self.user_data.get('role')})"
        ttk.Label(header_frame, text=welcome_text, font=("-size 12")).pack(side='left')
        
        logout_button = ttk.Button(header_frame, text="Logout", command=self.logout, bootstyle="danger")
        logout_button.pack(side='right')

        notebook = ttk.Notebook(self, bootstyle="primary")
        notebook.pack(expand=True, fill='both', padx=10, pady=(0, 10))

        self.kasir_frame = KasirPage(notebook, controller, self.user_data)
        notebook.add(self.kasir_frame, text='Kasir')

        stok_frame = StokPage(notebook, controller)
        notebook.add(stok_frame, text='Manajemen Produk')

        if self.user_data.get('role') == 'admin':
            riwayat_stok_frame = RiwayatStokPage(notebook, controller)
            notebook.add(riwayat_stok_frame, text='Riwayat Stok')
            riwayat_transaksi_frame = RiwayatTransaksiPage(notebook, controller)
            notebook.add(riwayat_transaksi_frame, text='Riwayat Transaksi')
            laporan_frame = LaporanPage(notebook, controller)
            notebook.add(laporan_frame, text='Laporan Penjualan')
            karyawan_frame = KaryawanPage(notebook, controller)
            notebook.add(karyawan_frame, text='Manajemen Karyawan')
        
        notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def logout(self):
        self.controller.show_frame("LoginPage")

    def on_tab_changed(self, event):
        selected_tab = event.widget.select()
        tab_text = event.widget.tab(selected_tab, "text")
        if hasattr(self, 'kasir_frame') and tab_text == "Kasir":
            self.kasir_frame._load_products_from_db()

if __name__ == '__main__':
    database.setup_database()
    app = App()
    app.mainloop()