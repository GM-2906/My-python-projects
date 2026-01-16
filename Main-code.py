import os
import sys
import subprocess
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

def resource_path(relative_path):
    """ Получает абсолютный путь к ресурсам (для работы внутри EXE и в редакторе) """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class UltimateConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Good Converter")
        self.root.geometry("500x500")
        self.root.config(bg="#1c1c1c")
        self.root.resizable(False, False)

        # Установка иконки окна
        icon_path = resource_path("icon.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)

        # --- БАЗА ДАННЫХ ФОРМАТОВ ---
        self.categories = {
            "Видео": {
                "input": [".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".webm"],
                "output": ["mp3", "wav", "ogg", "flac", "mp4", "mov", "avi", "mkv"]
            },
            "Изображения": {
                "input": [".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff"],
                "output": ["png", "jpg", "jpeg", "webp", "gif", "bmp"]
            },
            "Архивы": {
                "input": [".zip", ".7z", ".rar", ".iso", ".tar", ".gz"],
                "output": ["zip", "tar"] # 7z/ISO требуют внешних библиотек, оставим базу
            }
        }

        self.selected_file = ""
        self.setup_ui()

    def setup_ui(self):
        # Стилизация выпадающих списков
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TCombobox", fieldbackground="#333", background="#333", foreground="white", arrowcolor="white")

        # --- ЗАГОЛОВОК ---
        header_frame = tk.Frame(self.root, bg="#1c1c1c")
        header_frame.pack(pady=20)
        
        tk.Label(header_frame, text="Медиа конвертер", fg="#00FF00", bg="#1c1c1c", font=("Impact", 24)).pack()
        tk.Label(header_frame, text="Видео • Аудио • Изо. • Архивы", fg="#888", bg="#1c1c1c", font=("Arial", 9)).pack()

        # --- ШАГ 1: КАТЕГОРИЯ ---
        step1_frame = tk.Frame(self.root, bg="#1c1c1c")
        step1_frame.pack(pady=10, fill="x", padx=40)

        tk.Label(step1_frame, text="1. Выберите тип файла:", fg="white", bg="#1c1c1c", font=("Arial", 10, "bold")).pack(anchor="w")
        
        self.cat_combo = ttk.Combobox(step1_frame, values=list(self.categories.keys()), state="readonly", font=("Arial", 11))
        self.cat_combo.pack(fill="x", pady=5)
        self.cat_combo.current(0)
        self.cat_combo.bind("<<ComboboxSelected>>", self.reset_selection) # Сброс при смене категории

        # --- ШАГ 2: ФАЙЛ ---
        step2_frame = tk.Frame(self.root, bg="#1c1c1c")
        step2_frame.pack(pady=10, fill="x", padx=40)

        self.btn_file = tk.Button(step2_frame, text="ВЫБРАТЬ ФАЙЛ...", command=self.select_file, 
                                  bg="#333", fg="white", activebackground="#444", activeforeground="white",
                                  font=("Arial", 11, "bold"), relief="flat", padx=10, pady=5)
        self.btn_file.pack(fill="x")

        self.lbl_file_status = tk.Label(step2_frame, text="Файл не выбран", fg="#666", bg="#1c1c1c", font=("Arial", 9))
        self.lbl_file_status.pack(pady=5)

        # --- ШАГ 3: ФОРМАТ ---
        step3_frame = tk.Frame(self.root, bg="#1c1c1c")
        step3_frame.pack(pady=10, fill="x", padx=40)

        tk.Label(step3_frame, text="2. Конвертировать в:", fg="white", bg="#1c1c1c", font=("Arial", 10, "bold")).pack(anchor="w")
        
        self.format_combo = ttk.Combobox(step3_frame, state="disabled", font=("Arial", 11))
        self.format_combo.pack(fill="x", pady=5)

        # --- КНОПКА СТАРТ ---
        self.btn_start = tk.Button(self.root, text="НАЧАТЬ КОНВЕРТАЦИЮ", command=self.process, 
                                   bg="#005500", fg="#888", font=("Arial", 14, "bold"), 
                                   relief="flat", state="disabled", pady=10)
        self.btn_start.pack(side="bottom", fill="x", padx=40, pady=30)

    def reset_selection(self, event=None):
        """ Сбрасывает выбор файла при смене категории """
        self.selected_file = ""
        self.lbl_file_status.config(text="Файл не выбран", fg="#666")
        self.format_combo.set("")
        self.format_combo.config(state="disabled")
        self.btn_start.config(state="disabled", bg="#005500", fg="#888")

    def select_file(self):
        category = self.cat_combo.get()
        # Фильтр файлов зависит от категории
        file_path = filedialog.askopenfilename(title=f"Выберите файл ({category})")
        
        if not file_path:
            return

        # --- ВАЛИДАЦИЯ ---
        ext = os.path.splitext(file_path)[1].lower()
        allowed_exts = self.categories[category]["input"]

        if ext not in allowed_exts:
            messagebox.showerror("Ошибка категории", 
                f"Вы выбрали категорию '{category}', но файл '{ext}'.\n\n"
                f"Для категории '{category}' поддерживаются:\n{', '.join(allowed_exts)}")
            return

        # Если всё ок
        self.selected_file = file_path
        self.lbl_file_status.config(text=f"✔ {os.path.basename(file_path)}", fg="#00FF00")
        
        # Обновляем список выходных форматов
        output_formats = self.categories[category]["output"]
        self.format_combo.config(values=output_formats, state="readonly")
        self.format_combo.current(0)
        
        # Активируем кнопку старт
        self.btn_start.config(state="normal", bg="#00AA00", fg="white", cursor="hand2")

    def process(self):
        if not self.selected_file: return

        category = self.cat_combo.get()
        target_ext = self.format_combo.get()
        input_dir = os.path.dirname(self.selected_file)
        input_name = os.path.splitext(os.path.basename(self.selected_file))[0]
        output_file = os.path.join(input_dir, f"{input_name}_converted.{target_ext}")

        self.btn_start.config(text="ОБРАБОТКА...", state="disabled", bg="#AAaa00")
        self.root.update()

        try:
            # === ЛОГИКА ДЛЯ ВИДЕО И ФОТО (FFMPEG) ===
            if category in ["Видео", "Изображения"]:
                ffmpeg_path = resource_path("ffmpeg.exe")
                
                # Простая команда: ffmpeg -i input -y output
                cmd = f'"{ffmpeg_path}" -i "{self.selected_file}" -y "{output_file}"'
                
                # Скрываем консоль
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
                process = subprocess.Popen(cmd, startupinfo=startupinfo, shell=True)
                process.wait()

                if process.returncode != 0:
                    raise Exception("FFmpeg вернул ошибку.")

            # === ЛОГИКА ДЛЯ АРХИВОВ ===
            elif category == "Архивы":
                if target_ext in ["zip", "tar"]:
                    # Используем shutil
                    base_name = os.path.splitext(output_file)[0]
                    shutil.make_archive(base_name, target_ext, input_dir, input_name)
                else:
                    # Заглушка для сложных форматов
                    messagebox.showwarning("Внимание", "Форматы 7z/RAR требуют внешних библиотек.\nСоздан ZIP-архив как резерв.")
                    base_name = os.path.splitext(output_file)[0]
                    shutil.make_archive(base_name, "zip", input_dir, input_name)

            messagebox.showinfo("Успех!", f"Готово!\nФайл сохранен: {os.path.basename(output_file)}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось конвертировать.\n{e}")
        
        finally:
            self.btn_start.config(text="НАЧАТЬ КОНВЕРТАЦИЮ", state="normal", bg="#00AA00")

if __name__ == "__main__":
    root = tk.Tk()
    app = UltimateConverter(root)
    root.mainloop()
