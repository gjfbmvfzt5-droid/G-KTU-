import csv
from datetime import datetime
import imghdr
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

BASE_DIR = Path.home() / "Desktop" / "RamakKala"
PHOTOS_DIR = BASE_DIR / "fotograflar"
DATA_FILE = BASE_DIR / "ramak_kala_kayitlari.csv"


class RamakKalaApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Ramak Kala ve Makine Risk Değerlendirme")
        self.root.geometry("1100x620")

        self.tarih_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.birim_var = tk.StringVar()
        self.makine_var = tk.StringVar()
        self.konu_var = tk.StringVar()
        self.fotograf_yolu_var = tk.StringVar()
        self.analiz_ozet_var = tk.StringVar(value="Fotoğraf analizi bekleniyor")

        self.siddet_var = tk.IntVar(value=1)
        self.olasilik_var = tk.IntVar(value=1)
        self.maruziyet_var = tk.IntVar(value=1)
        self.risk_puani_var = tk.StringVar(value="1")
        self.risk_seviye_var = tk.StringVar(value="Düşük")

        self._prepare_storage()
        self._build_ui()
        self._load_table()

    def _prepare_storage(self) -> None:
        BASE_DIR.mkdir(parents=True, exist_ok=True)
        PHOTOS_DIR.mkdir(parents=True, exist_ok=True)

    def _build_ui(self) -> None:
        form = ttk.LabelFrame(self.root, text="Yeni Ramak Kala + Makine Risk Kaydı")
        form.pack(fill="x", padx=12, pady=10)

        ttk.Label(form, text="Tarih (YYYY-AA-GG):").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        ttk.Entry(form, textvariable=self.tarih_var, width=20).grid(row=0, column=1, sticky="w", padx=8, pady=6)

        ttk.Label(form, text="Birim/Bölüm:").grid(row=1, column=0, sticky="w", padx=8, pady=6)
        ttk.Entry(form, textvariable=self.birim_var, width=30).grid(row=1, column=1, sticky="w", padx=8, pady=6)

        ttk.Label(form, text="Makine Adı:").grid(row=1, column=2, sticky="w", padx=8, pady=6)
        ttk.Entry(form, textvariable=self.makine_var, width=30).grid(row=1, column=3, sticky="w", padx=8, pady=6)

        ttk.Label(form, text="Olay Başlığı:").grid(row=2, column=0, sticky="w", padx=8, pady=6)
        ttk.Entry(form, textvariable=self.konu_var, width=65).grid(row=2, column=1, columnspan=3, sticky="we", padx=8, pady=6)

        ttk.Label(form, text="Açıklama:").grid(row=3, column=0, sticky="nw", padx=8, pady=6)
        self.aciklama_text = tk.Text(form, height=4, width=70)
        self.aciklama_text.grid(row=3, column=1, columnspan=3, sticky="we", padx=8, pady=6)

        ttk.Label(form, text="Fotoğraf:").grid(row=4, column=0, sticky="w", padx=8, pady=6)
        photo_frame = ttk.Frame(form)
        photo_frame.grid(row=4, column=1, columnspan=3, sticky="we", padx=8, pady=6)
        ttk.Entry(photo_frame, textvariable=self.fotograf_yolu_var, state="readonly", width=70).pack(side="left", fill="x", expand=True)
        ttk.Button(photo_frame, text="Seç", command=self._select_photo).pack(side="left", padx=6)
        ttk.Button(photo_frame, text="Analiz Et", command=self._analyze_photo).pack(side="left")

        ttk.Label(form, text="Analiz Özeti:").grid(row=5, column=0, sticky="nw", padx=8, pady=6)
        ttk.Label(form, textvariable=self.analiz_ozet_var, wraplength=700, foreground="#0b5394").grid(row=5, column=1, columnspan=3, sticky="w", padx=8, pady=6)

        risk_frame = ttk.LabelFrame(form, text="Makine Bazlı Risk Değerlendirmesi (1-5)")
        risk_frame.grid(row=6, column=0, columnspan=4, sticky="we", padx=8, pady=8)

        ttk.Label(risk_frame, text="Şiddet:").grid(row=0, column=0, padx=8, pady=6, sticky="w")
        ttk.Spinbox(risk_frame, from_=1, to=5, textvariable=self.siddet_var, width=5, command=self._update_risk).grid(row=0, column=1, padx=8, pady=6)

        ttk.Label(risk_frame, text="Olasılık:").grid(row=0, column=2, padx=8, pady=6, sticky="w")
        ttk.Spinbox(risk_frame, from_=1, to=5, textvariable=self.olasilik_var, width=5, command=self._update_risk).grid(row=0, column=3, padx=8, pady=6)

        ttk.Label(risk_frame, text="Maruziyet:").grid(row=0, column=4, padx=8, pady=6, sticky="w")
        ttk.Spinbox(risk_frame, from_=1, to=5, textvariable=self.maruziyet_var, width=5, command=self._update_risk).grid(row=0, column=5, padx=8, pady=6)

        ttk.Label(risk_frame, text="Risk Puanı:").grid(row=0, column=6, padx=(20, 8), pady=6, sticky="w")
        ttk.Label(risk_frame, textvariable=self.risk_puani_var, foreground="blue").grid(row=0, column=7, padx=8, pady=6)

        ttk.Label(risk_frame, text="Seviye:").grid(row=0, column=8, padx=(20, 8), pady=6, sticky="w")
        ttk.Label(risk_frame, textvariable=self.risk_seviye_var, foreground="red").grid(row=0, column=9, padx=8, pady=6)

        self.siddet_var.trace_add("write", lambda *_: self._update_risk())
        self.olasilik_var.trace_add("write", lambda *_: self._update_risk())
        self.maruziyet_var.trace_add("write", lambda *_: self._update_risk())

        ttk.Button(form, text="Kaydet", command=self._save_record).grid(row=7, column=3, sticky="e", padx=8, pady=10)

        table_frame = ttk.LabelFrame(self.root, text="Son Kayıtlar")
        table_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        columns = ("tarih", "birim", "makine", "konu", "risk", "seviye", "foto", "analiz")
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        for col, title in {
            "tarih": "Tarih",
            "birim": "Birim",
            "makine": "Makine",
            "konu": "Başlık",
            "risk": "Risk Puanı",
            "seviye": "Seviye",
            "foto": "Fotoğraf",
            "analiz": "Analiz Özeti",
        }.items():
            self.table.heading(col, text=title)

        self.table.column("tarih", width=100)
        self.table.column("birim", width=130)
        self.table.column("makine", width=140)
        self.table.column("konu", width=180)
        self.table.column("risk", width=90, anchor="center")
        self.table.column("seviye", width=90, anchor="center")
        self.table.column("foto", width=180)
        self.table.column("analiz", width=320)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscroll=scrollbar.set)
        self.table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _select_photo(self) -> None:
        dosya = filedialog.askopenfilename(title="Fotoğraf Seç", filetypes=[("Görsel", "*.png *.jpg *.jpeg *.bmp")])
        if dosya:
            self.fotograf_yolu_var.set(dosya)
            self.analiz_ozet_var.set("Fotoğraf seçildi. Analiz etmek için 'Analiz Et' butonuna basın.")

    def _analyze_photo(self) -> None:
        yol = self.fotograf_yolu_var.get().strip()
        if not yol:
            messagebox.showwarning("Fotoğraf Yok", "Lütfen önce bir fotoğraf seçin.")
            return
        p = Path(yol)
        if not p.exists():
            messagebox.showerror("Dosya Hatası", "Seçilen fotoğraf bulunamadı.")
            return

        tur = imghdr.what(p) or "bilinmeyen"
        boyut_kb = round(p.stat().st_size / 1024, 1)
        aciklama = self.aciklama_text.get("1.0", "end").lower()
        flags = []
        if any(k in aciklama for k in ["yağ", "sızıntı", "kaçak"]):
            flags.append("Sızıntı ihtimali")
        if any(k in aciklama for k in ["kablo", "elektrik", "kıvılcım"]):
            flags.append("Elektriksel tehlike")
        if any(k in aciklama for k in ["koruyucu", "muhafaza", "kapak"]):
            flags.append("Koruyucu ekipman kontrolü")
        if not flags:
            flags.append("Genel görsel inceleme önerilir")
        self.analiz_ozet_var.set(f"Tür: {tur}, Boyut: {boyut_kb} KB, Bulgular: {', '.join(flags)}")

    def _update_risk(self) -> None:
        puan = self._normalize_score(self.siddet_var.get()) * self._normalize_score(self.olasilik_var.get()) * self._normalize_score(self.maruziyet_var.get())
        self.risk_puani_var.set(str(puan))
        self.risk_seviye_var.set(self._risk_level(puan))

    @staticmethod
    def _normalize_score(value: int) -> int:
        return max(1, min(5, int(value)))

    @staticmethod
    def _risk_level(score: int) -> str:
        if score <= 20:
            return "Düşük"
        if score <= 50:
            return "Orta"
        if score <= 80:
            return "Yüksek"
        return "Çok Yüksek"

    def _save_record(self) -> None:
        self._update_risk()
        tarih, birim, makine, konu = self.tarih_var.get().strip(), self.birim_var.get().strip(), self.makine_var.get().strip(), self.konu_var.get().strip()
        aciklama = self.aciklama_text.get("1.0", "end").strip()
        if not all([tarih, birim, makine, konu, aciklama]):
            messagebox.showwarning("Eksik Bilgi", "Lütfen tüm alanları doldurun.")
            return
        try:
            datetime.strptime(tarih, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Hatalı Tarih", "Tarih formatı YYYY-AA-GG olmalıdır.")
            return

        fotograf_orijinal = self.fotograf_yolu_var.get().strip()
        foto_kayit_yolu = ""
        if fotograf_orijinal:
            src = Path(fotograf_orijinal)
            if src.exists():
                hedef_ad = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{src.name}"
                hedef = PHOTOS_DIR / hedef_ad
                shutil.copy2(src, hedef)
                foto_kayit_yolu = str(hedef)

        row = [
            tarih, birim, makine, konu,
            self.risk_puani_var.get().strip(), self.risk_seviye_var.get().strip(),
            foto_kayit_yolu, self.analiz_ozet_var.get().strip(), aciklama,
        ]
        new_file = not DATA_FILE.exists()
        with DATA_FILE.open("a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if new_file:
                w.writerow(["tarih", "birim", "makine", "konu", "risk_puani", "risk_seviye", "foto", "analiz_ozeti", "aciklama"])
            w.writerow(row)

        self.table.insert("", 0, values=(row[0], row[1], row[2], row[3], row[4], row[5], Path(row[6]).name if row[6] else "-", row[7]))
        self.birim_var.set("")
        self.makine_var.set("")
        self.konu_var.set("")
        self.aciklama_text.delete("1.0", "end")
        self.fotograf_yolu_var.set("")
        self.analiz_ozet_var.set("Fotoğraf analizi bekleniyor")
        self.siddet_var.set(1)
        self.olasilik_var.set(1)
        self.maruziyet_var.set(1)
        self._update_risk()
        messagebox.showinfo("Başarılı", f"Kayıt eklendi. Dosyalar: {BASE_DIR}")

    def _load_table(self) -> None:
        if not DATA_FILE.exists():
            return
        with DATA_FILE.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            required = {"tarih", "birim", "makine", "konu", "risk_puani", "risk_seviye", "foto", "analiz_ozeti", "aciklama"}
            if not required.issubset(set(reader.fieldnames or [])):
                return
            for row in reader:
                self.table.insert("", 0, values=(row["tarih"], row["birim"], row["makine"], row["konu"], row["risk_puani"], row["risk_seviye"], Path(row["foto"]).name if row["foto"] else "-", row["analiz_ozeti"]))


def main() -> None:
    root = tk.Tk()
    RamakKalaApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
