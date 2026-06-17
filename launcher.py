import os
import sys
import subprocess
import threading
import json
import customtkinter as ctk

# Настройки стиля
ctk.set_appearance_mode("Light") # Принудительно светлая для этого стиля
ctk.set_default_color_theme("blue")

class ZapretManagerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        os.chdir(self.base_dir)
        self.config_file = os.path.join(self.base_dir, "config.json")
        self.service_bat = os.path.join(self.base_dir, "service.bat")

        # Цвета в стиле UI Kit
        self.accent_color = "#FF6B00" # Тот самый оранжевый
        self.bg_color = "#FFFFFF"
        self.text_color = "#2D2D2D"

        self.title("Zapret Manager")
        self.geometry("400x580")
        self.configure(fg_color=self.bg_color)

        # Заголовок
        self.title_label = ctk.CTkLabel(self, text="Zapret Manager", font=("Segoe UI", 24, "bold"), text_color=self.text_color)
        self.title_label.pack(pady=(30, 20))

        # Основная карта (контейнер)
        self.card = ctk.CTkFrame(self, fg_color="#F8F8F8", corner_radius=20, border_width=1, border_color="#EBEBEB")
        self.card.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Комбобокс
        self.alt_files = [f for f in os.listdir(self.base_dir) if f.endswith(".bat") and "general" in f.lower()]
        self.alt_combobox = ctk.CTkComboBox(self.card, values=self.alt_files, height=40, corner_radius=12, 
                                            fg_color="white", text_color=self.text_color, dropdown_fg_color="white",
                                            border_color="#E0E0E0", border_width=1, font=("Segoe UI", 14))
        self.alt_combobox.pack(fill="x", padx=25, pady=25)
        
        # Кнопки (Главные)
        self.btn_run = ctk.CTkButton(self.card, text="ЗАПУСТИТЬ", height=45, corner_radius=12, 
                                     fg_color=self.accent_color, hover_color="#E66000",
                                     font=("Segoe UI", 14, "bold"), command=self.run_strategy)
        self.btn_run.pack(fill="x", padx=25, pady=(0, 10))
        
        self.btn_stop = ctk.CTkButton(self.card, text="СТОП", height=45, corner_radius=12, 
                                      fg_color="#FF3B30", hover_color="#D12E26",
                                      font=("Segoe UI", 14, "bold"), command=self.kill_winws)
        self.btn_stop.pack(fill="x", padx=25, pady=(0, 20))

        # Сетка вспомогательных кнопок
        util_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        util_frame.pack(fill="x", padx=20, pady=(0, 15))
        util_frame.columnconfigure((0, 1), weight=1)

        btn_style = {"height": 35, "corner_radius": 10, "fg_color": "#EBEBEB", "text_color": self.text_color, "hover_color": "#DCDCDC"}

        ctk.CTkButton(util_frame, text="Правка", **btn_style, command=self.edit_service).grid(row=0, column=0, padx=5, sticky="ew")
        ctk.CTkButton(util_frame, text="Папка", **btn_style, command=lambda: os.startfile(self.base_dir)).grid(row=0, column=1, padx=5, sticky="ew")

        # Логи
        self.log_box = ctk.CTkTextbox(self.card, font=("Consolas", 12), fg_color="white", 
                                      text_color="#555555", corner_radius=12, border_width=1, border_color="#EBEBEB")
        self.log_box.pack(fill="both", expand=True, padx=25, pady=(0, 25))

        self.load_config()

    # Функционал оставляем прежним, просто обновили визуал
    def load_config(self):
        self.config = {}
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f: self.config = json.load(f)
                if self.alt_files and self.config.get("last_selected") in self.alt_files:
                    self.alt_combobox.set(self.config["last_selected"])
            except: pass

    def save_config(self):
        with open(self.config_file, 'w') as f: json.dump({"last_selected": self.alt_combobox.get()}, f)

    def edit_service(self):
        if os.path.exists(self.service_bat): os.startfile(self.service_bat)

    def log(self, message):
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")

    def read_output(self, proc):
        try:
            for line in iter(proc.stdout.readline, ''):
                if line: self.after(0, self.log, line.strip())
        finally: proc.stdout.close()

    def run_strategy(self):
        file = self.alt_combobox.get()
        if file:
            self.save_config()
            self.kill_winws()
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            try:
                self.process = subprocess.Popen(
                    os.path.join(self.base_dir, file), cwd=self.base_dir,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                    bufsize=1, encoding='cp866', errors='replace',
                    startupinfo=startupinfo, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
                threading.Thread(target=self.read_output, args=(self.process,), daemon=True).start()
                self.log(f"Запущено: {file}")
            except Exception as e: self.log(f"Ошибка: {e}")

    def kill_winws(self):
        subprocess.run("taskkill /f /im winws.exe", shell=True, capture_output=True, creationflags=0x08000000)
        self.log("--- Процессы остановлены ---")

if __name__ == "__main__":
    app = ZapretManagerGUI()
    app.mainloop()