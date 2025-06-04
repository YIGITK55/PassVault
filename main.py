import tkinter as tk
from tkinter import messagebox, simpledialog
from crypto_utils import encrypt_password, decrypt_password
import json
import os

DB_FILE = "database.json"
MASTER_FILE = "master.key"

# Şifre işlemleri, DB yükleme kaydetme aynen önceki gibi (kopyala yapıştırabilirsin)

def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f)

def add_password(db, site, password):
    enc_pass = encrypt_password(password).decode('utf-8')
    db[site] = enc_pass
    save_db(db)

def get_password(db, site):
    enc_pass = db.get(site)
    if not enc_pass:
        return None
    return decrypt_password(enc_pass.encode('utf-8'))

def list_sites(db):
    return list(db.keys())

def set_master_password():
    while True:
        pw1 = simpledialog.askstring("Ana Şifre", "Ana şifreni belirle:", show='*')
        pw2 = simpledialog.askstring("Ana Şifre", "Ana şifreyi tekrar gir:", show='*')
        if pw1 == pw2:
            with open(MASTER_FILE, "w") as f:
                f.write(pw1)
            messagebox.showinfo("Başarılı", "Ana şifre başarıyla kaydedildi!")
            break
        else:
            messagebox.showerror("Hata", "Şifreler uyuşmuyor, tekrar dene.")

def check_master_password(root):
    if not os.path.exists(MASTER_FILE):
        set_master_password()
    with open(MASTER_FILE, "r") as f:
        stored_pw = f.read()

    for _ in range(3):
        attempt = simpledialog.askstring("Ana Şifre", "Ana şifreyi gir:", show='*', parent=root)
        if attempt == stored_pw:
            messagebox.showinfo("Başarılı", "Giriş başarılı!")
            return True
        else:
            messagebox.showerror("Hata", "Hatalı şifre.")
    messagebox.showerror("Hata", "3 kez hatalı giriş. Program kapanıyor.")
    return False

class PassVaultApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PassVault - Şifrelerin Patronu")
        self.geometry("600x400")
        self.db = load_db()
        
        # Sol liste
        self.site_listbox = tk.Listbox(self)
        self.site_listbox.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        self.site_listbox.bind("<<ListboxSelect>>", self.on_site_select)

        # Sağ panel
        right_frame = tk.Frame(self)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.site_label = tk.Label(right_frame, text="Site adı:")
        self.site_label.pack(anchor="w")
        self.site_entry = tk.Entry(right_frame)
        self.site_entry.pack(fill=tk.X)

        self.pass_label = tk.Label(right_frame, text="Parola:")
        self.pass_label.pack(anchor="w")
        self.pass_entry = tk.Entry(right_frame, show="*")
        self.pass_entry.pack(fill=tk.X)

        self.show_pass_var = tk.IntVar()
        self.show_pass_check = tk.Checkbutton(right_frame, text="Parolayı Göster", variable=self.show_pass_var, command=self.toggle_password)
        self.show_pass_check.pack(anchor="w")

        btn_frame = tk.Frame(right_frame)
        btn_frame.pack(pady=10)

        self.add_btn = tk.Button(btn_frame, text="Parola Ekle/Güncelle", command=self.add_or_update_password)
        self.add_btn.pack(side=tk.LEFT, padx=5)

        self.delete_btn = tk.Button(btn_frame, text="Sil", command=self.delete_password)
        self.delete_btn.pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(self, text="", fg="green")
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        self.refresh_site_list()

    def refresh_site_list(self):
        self.site_listbox.delete(0, tk.END)
        for site in list_sites(self.db):
            self.site_listbox.insert(tk.END, site)

    def on_site_select(self, event):
        if not self.site_listbox.curselection():
            return
        index = self.site_listbox.curselection()[0]
        site = self.site_listbox.get(index)
        self.site_entry.delete(0, tk.END)
        self.site_entry.insert(0, site)

        password = get_password(self.db, site)
        self.pass_entry.delete(0, tk.END)
        self.pass_entry.insert(0, password if password else "")
        self.pass_entry.config(show="*")
        self.show_pass_var.set(0)
        self.status_label.config(text="")

    def toggle_password(self):
        if self.show_pass_var.get():
            self.pass_entry.config(show="")
        else:
            self.pass_entry.config(show="*")

    def add_or_update_password(self):
        site = self.site_entry.get().strip()
        password = self.pass_entry.get().strip()
        if not site or not password:
            messagebox.showwarning("Uyarı", "Site adı ve parola boş olamaz!")
            return
        add_password(self.db, site, password)
        self.status_label.config(text=f"{site} için parola kaydedildi.")
        self.refresh_site_list()

    def delete_password(self):
        site = self.site_entry.get().strip()
        if site in self.db:
            if messagebox.askyesno("Onay", f"{site} kaydını silmek istediğine emin misin?"):
                del self.db[site]
                save_db(self.db)
                self.status_label.config(text=f"{site} kaydı silindi.")
                self.refresh_site_list()
                self.site_entry.delete(0, tk.END)
                self.pass_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Uyarı", "Silmek için geçerli bir site adı gir.")

def main():
    root = PassVaultApp()
    if check_master_password(root):
        root.mainloop()
    else:
        root.destroy()

if __name__ == "__main__":
    main()
