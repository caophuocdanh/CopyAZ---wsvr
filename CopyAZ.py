# --- YÊU CẦU QUAN TRỌNG ---
# 1. Cần cài đặt thư viện pywin32 trước khi chạy: pip install pywin32
# 2. Yêu cầu file cp.exe (đã biên dịch từ webserver.py) phải nằm cùng thư mục với file này.

import tkinter as tk
import time
from platform import system
import os
import configparser
import secrets
import random
import string
import json
from datetime import datetime
import shutil
import hashlib
import threading
import subprocess

# --- PHẦN IMPORT THEO HỆ ĐIỀU HÀNH ---
if system() == "Windows":
    import pythoncom
    from win32com.shell import shell, shellcon
    import ctypes

# --- LỚP ỨNG DỤNG CHÍNH ---
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("COPY A-Z @danh")
        self.geometry("800x500")
        self.resizable(True, False)
        self.config(bg="white")
        
        # --- KHAI BÁO BIẾN CỦA LỚP ---
        self.select_all_var = tk.BooleanVar()
        self.sub_folders = []
        self.checkbox_vars = []
        self.setting_checked = True
        self.setting_pattern = 'l&WlsZDv#a)#'
        self.setting_length = 99
        self.setting_num_empty_folders = 789
        self.app_config = configparser.ConfigParser()
        
        # --- Đặt tên file thực thi của web server ---
        self.webserver_exe_path = "cp.exe"
        
        # --- KHỞI TẠO ---
        self.load_config()
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.create_top_bar()
        self.create_main_layout() 
        self._validate_and_log_settings() 
        self.populate_checkboxes()

    def create_main_layout(self):
        checkbox_container = tk.Frame(self, bg="white", relief="solid", borderwidth=1, height=250)
        checkbox_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(10, 5))
        checkbox_container.grid_propagate(False)
        bottom_section_frame = tk.Frame(self, bg="white")
        bottom_section_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(5, 10))
        self.create_checkbox_group(checkbox_container)
        self.create_bottom_section(bottom_section_frame)

    def _get_special_folder_path(self, folder_csidl):
        if system() == "Windows":
            try: return shell.SHGetFolderPath(0, folder_csidl, None, 0)
            except Exception: return None
        else:
            if folder_csidl == shellcon.CSIDL_DESKTOP: return os.path.join(os.path.expanduser('~'), 'Desktop')
            elif folder_csidl == shellcon.CSIDL_LOCAL_APPDATA: return os.path.expanduser('~')
        return None

    def _set_ui_state(self, state):
        self.copy_button.config(state=state)
        self.clear_shortcut_btn.config(state=state)
        self.clear_source_btn.config(state=state)
        self.refresh_button.config(state=state)
        self.select_all_cb.config(state=state)
        for widget in self.scrollable_frame.winfo_children(): widget.config(state=state)
        new_cursor = 'watch' if state == 'disabled' else ''
        self.config(cursor=new_cursor)
        self.update_idletasks()

    def _check_thread(self, thread):
        if thread.is_alive(): self.after(100, lambda: self._check_thread(thread))
        else: self._set_ui_state('normal')

    def _run_task_in_thread(self, task_function):
        self._set_ui_state('disabled')
        task_thread = threading.Thread(target=task_function, daemon=True)
        task_thread.start()
        self.after(100, lambda: self._check_thread(task_thread))

    def _log(self, message, clear_first=False):
        if clear_first: self.output_textbox.delete("1.0", tk.END)
        self.output_textbox.insert(tk.END, message)
        self.output_textbox.see(tk.END)
        self.update_idletasks()
    
    def toggle_select_all(self):
        is_checked = self.select_all_var.get()
        for var in self.checkbox_vars: var.set(is_checked)

    def create_default_config(self, filename):
        default_config = configparser.ConfigParser()
        default_config['Settings'] = {'Checked': 'true', 'Pattern': 'l&WlsZDv#a)#', 'StringLengh': '99', 'NumEmptyFolders': '789'}
        try:
            with open(filename, 'w', encoding='utf-8') as configfile: default_config.write(configfile)
            print(f"Đã tạo file config mặc định: {filename}")
        except IOError as e: print(f"Lỗi khi tạo file config: {e}")

    def load_config(self):
        config_file = 'config.ini'
        if not os.path.exists(config_file): self.create_default_config(config_file)
        try: self.app_config.read(config_file, encoding='utf-8')
        except configparser.Error as e: print(f"Lỗi khi đọc file config.ini: {e}")

    def _validate_and_log_settings(self):
        error_messages = []
        config_was_modified = False
        settings_section = 'Settings'
        if not self.app_config.has_section(settings_section):
            self.app_config.add_section(settings_section); config_was_modified = True
        try: self.setting_checked = self.app_config.getboolean(settings_section, 'Checked')
        except (ValueError, configparser.NoOptionError):
            self.setting_checked = True; self.app_config.set(settings_section, 'Checked', 'true'); error_messages.append("Cảnh báo: Giá trị 'Checked' không hợp lệ. Đã sửa thành: true"); config_was_modified = True
        try: self.setting_pattern = self.app_config.get(settings_section, 'Pattern')
        except configparser.NoOptionError:
            self.setting_pattern = 'l&WlsZDv#a)#'; self.app_config.set(settings_section, 'Pattern', self.setting_pattern); error_messages.append("Cảnh báo: Không tìm thấy 'Pattern'. Đã thêm giá trị mặc định."); config_was_modified = True
        try:
            self.setting_length = self.app_config.getint(settings_section, 'StringLengh')
            if self.setting_length < len(self.setting_pattern):
                self.setting_length = 99; self.app_config.set(settings_section, 'StringLengh', str(self.setting_length)); error_messages.append("Cảnh báo: 'StringLengh' phải lớn hơn độ dài Pattern. Đã sửa thành: 99"); config_was_modified = True
        except (ValueError, configparser.NoOptionError):
            self.setting_length = 99; self.app_config.set(settings_section, 'StringLengh', str(self.setting_length)); error_messages.append("Cảnh báo: Giá trị 'StringLengh' không hợp lệ. Đã sửa thành: 99"); config_was_modified = True
        try:
            self.setting_num_empty_folders = self.app_config.getint(settings_section, 'NumEmptyFolders')
            if self.setting_num_empty_folders < 0:
                self.setting_num_empty_folders = 789; self.app_config.set(settings_section, 'NumEmptyFolders', str(self.setting_num_empty_folders)); error_messages.append("Cảnh báo: 'NumEmptyFolders' không được âm. Đã sửa thành: 789"); config_was_modified = True
        except (ValueError, configparser.NoOptionError):
            self.setting_num_empty_folders = 789; self.app_config.set(settings_section, 'NumEmptyFolders', str(self.setting_num_empty_folders)); error_messages.append("Cảnh báo: Giá trị 'NumEmptyFolders' không hợp lệ. Đã sửa thành: 789"); config_was_modified = True
        if config_was_modified:
            try:
                with open('config.ini', 'w', encoding='utf-8') as configfile: self.app_config.write(configfile)
                error_messages.insert(0, "INFO: File config.ini đã được tự động sửa lỗi.")
            except IOError as e: error_messages.append(f"\nLỖI: Không thể ghi lại file config.ini đã sửa: {e}")
        self.select_all_var.set(self.setting_checked)
        if error_messages:
            self._log("--- THÔNG BÁO CẤU HÌNH ---\n" + "\n".join(error_messages) + "\n-----------------------------\n\n")

    def create_top_bar(self):
        top_frame = tk.Frame(self, bg="white"); top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(5,10))
        title_label = tk.Label(top_frame, text="COPY A-Z", font=("courier new", 24, "bold"), bg="white", fg="black"); title_label.pack(side="left")
        self.select_all_cb = tk.Checkbutton(top_frame, text="Select All", variable=self.select_all_var, command=self.toggle_select_all, bg="white", font=("courier new", 10)); self.select_all_cb.pack(side="left", padx=20)
        self.clock_label = tk.Label(top_frame, text="", font=("courier new", 24), bg="white", fg="black"); self.clock_label.pack(side="right")
        self.refresh_button = tk.Button(top_frame, text="♻", relief="flat", bg="white", command=self.populate_checkboxes, font=("courier new", 15), cursor="hand2"); self.refresh_button.pack(side="right", padx=(0, 20))
        self.update_clock()

    def create_checkbox_group(self, parent_frame):
        self.checkbox_canvas = tk.Canvas(parent_frame, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(parent_frame, orient="vertical", command=self.checkbox_canvas.yview); self.checkbox_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y"); self.checkbox_canvas.pack(side="left", fill="both", expand=True)
        self.scrollable_frame = tk.Frame(self.checkbox_canvas, bg="white"); [self.scrollable_frame.grid_columnconfigure(i, weight=1) for i in range(3)]
        self.canvas_window_id = self.checkbox_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        for widget in [self.checkbox_canvas, self.scrollable_frame]:
            widget.bind("<MouseWheel>", self._on_mousewheel_checkbox); widget.bind("<Button-4>", self._on_mousewheel_checkbox); widget.bind("<Button-5>", self._on_mousewheel_checkbox)
        self.scrollable_frame.bind("<Configure>", self.on_frame_configure); self.checkbox_canvas.bind("<Configure>", self.on_canvas_configure)

    def create_bottom_section(self, parent_frame):
        parent_frame.grid_columnconfigure(0, weight=0); parent_frame.grid_columnconfigure(1, weight=1); parent_frame.grid_rowconfigure(0, weight=1)
        left_column = tk.Frame(parent_frame, bg="white", width=150); left_column.grid(row=0, column=0, sticky="ns", padx=(0, 10)); left_column.grid_propagate(False)
        button_container = tk.Frame(left_column, bg="white"); button_container.pack(side="top", expand=True, fill='both')
        self.copy_button = tk.Button(button_container, text="COPY", font=("courier new", 24, "bold"), bg="white", fg="black", relief="solid", borderwidth=1, command=self.copy_action); self.copy_button.pack(expand=True, fill='both')
        self.clear_buttons_frame = tk.Frame(left_column, bg="white"); self.clear_buttons_frame.pack(side="bottom", pady=(5, 0))
        self.clear_shortcut_btn = tk.Button(self.clear_buttons_frame, text="Clear Shortcut", font=("courier new", 8), relief="solid", borderwidth=1, command=self.clear_shortcut); self.clear_shortcut_btn.pack(side="left", padx=(0, 5))
        self.clear_source_btn = tk.Button(self.clear_buttons_frame, text="Clear source", font=("courier new", 8), relief="solid", borderwidth=1, command=self.clear_source); self.clear_source_btn.pack(side="left")
        log_container = tk.Frame(parent_frame, relief="solid", borderwidth=1); log_container.grid(row=0, column=1, sticky="nsew")
        log_scrollbar = tk.Scrollbar(log_container)
        self.output_textbox = tk.Text(log_container, font=("courier new", 10), yscrollcommand=log_scrollbar.set, borderwidth=0, highlightthickness=0); log_scrollbar.config(command=self.output_textbox.yview)
        log_scrollbar.pack(side="right", fill="y"); self.output_textbox.pack(side="left", fill="both", expand=True)

    def update_clock(self):
        self.clock_label.config(text=time.strftime('%H:%M:%S')); self.after(1000, self.update_clock)

    def on_frame_configure(self, event): self.checkbox_canvas.configure(scrollregion=self.checkbox_canvas.bbox("all"))
    def on_canvas_configure(self, event): self.checkbox_canvas.itemconfig(self.canvas_window_id, width=event.width)
    def _on_mousewheel_checkbox(self, event):
        delta = -1 if event.num == 4 else 1 if event.num == 5 else int(-1*(event.delta/120)) if system() != "Linux" else 0
        self.checkbox_canvas.yview_scroll(delta, "units")

    def populate_checkboxes(self):
        source_dir = "source"
        if not os.path.exists(source_dir): self.initialize_source_directory(source_dir)
        for widget in self.scrollable_frame.winfo_children(): widget.destroy()
        self.checkbox_vars.clear(); self.sub_folders.clear()
        initial_check_state = self.setting_checked
        try: self.sub_folders = sorted([d for d in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, d))])
        except OSError as e: self._log(f"Lỗi khi quét thư mục {source_dir}: {e}\n")
        for i, folder_name in enumerate(self.sub_folders):
            var = tk.BooleanVar(value=initial_check_state)
            self.checkbox_vars.append(var)
            row, column = divmod(i, 3)
            cb = tk.Checkbutton(self.scrollable_frame, text=folder_name, variable=var, font=("courier new", 10), bg="white", fg="black", activebackground="white", selectcolor="white", anchor="w")
            cb.grid(row=row, column=column, sticky="ew", padx=10, pady=2)
            cb.bind("<MouseWheel>", self._on_mousewheel_checkbox); cb.bind("<Button-4>", self._on_mousewheel_checkbox); cb.bind("<Button-5>", self._on_mousewheel_checkbox)
        self.select_all_var.set(initial_check_state)

    def initialize_source_directory(self, source_dir):
        sample_folder_name = "Cao Phước Danh"; sample_file_name = "index.html"
        full_path = os.path.join(source_dir, sample_folder_name); file_path = os.path.join(full_path, sample_file_name)
        html_content = """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Cao Phước Danh</title><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol";background:linear-gradient(135deg,#f5f7fa 0,#c3cfe2 100%);display:flex;justify-content:center;align-items:center;min-height:100vh;color:#333}.card{width:90%;max-width:400px;background-color:#fff;border-radius:20px;box-shadow:0 10px 30px rgba(0,0,0,.1);text-align:center;overflow:hidden;transition:transform .3s ease,box-shadow .3s ease}.card:hover{box-shadow:0 20px 40px rgba(0,0,0,.55)}.card-header{background-color:#0077b5;height:120px;position:relative}.profile-icon{width:150px;height:150px;border-radius:50%;background:linear-gradient(135deg,#e0eafc,#cfdef3);border:5px solid #fff;box-shadow:0 5px 15px rgba(0,0,0,.1);display:flex;justify-content:center;align-items:center;font-size:5rem;position:absolute;bottom:-75px;left:50%;transform:translateX(-50%)}.card-body{padding:25px;padding-top:90px}.name{font-size:2em;font-weight:700;color:#1a1a1a}.title{font-size:1.1em;color:#666;margin-bottom:20px;font-weight:300}.social-links{margin-bottom:25px;display:flex;justify-content:center;gap:15px}.social-links a{text-decoration:none;width:50px;height:50px;border-radius:50%;display:flex;justify-content:center;align-items:center;font-weight:700;transition:all .3s ease}.social-links a:hover{transform:scale(1.1);box-shadow:0 4px 10px rgba(0,0,0,.2)}.icon-youtube{background-color:red;color:#fff;border:2px solid red;font-size:1.2em}.icon-youtube:hover{background-color:red;color:#fff}.icon-facebook{background-color:#1877f2;color:#fff;font-family:sans-serif;font-size:2em}.icon-facebook:hover{background-color:#166fe5}.icon-tiktok{background-color:#000;color:#fff;font-family:'Trebuchet MS',sans-serif;font-size:1.6em}.icon-tiktok:hover{background-color:#333}.contact-button{background:linear-gradient(135deg,#0077b5,#005a8d);color:#fff;border:none;padding:15px 30px;font-size:1em;font-weight:600;border-radius:50px;cursor:pointer;text-transform:uppercase;letter-spacing:1px;transition:background .3s ease,transform .2s ease;outline:0}.contact-button:hover{background:linear-gradient(135deg,#005a8d,#0077b5);transform:scale(1.05)}</style></head><body><div class="card"><div class="card-header"><div class="profile-icon">👨‍💻</div></div><div class="card-body"><h1 class="name">Cao Phước Danh</h1><p class="title">IT "Culi"</p><div class="social-links"><a href="https://youtube.com" target="_blank" aria-label="YouTube" class="icon-youtube">▷</a><a href="https://facebook.com" target="_blank" aria-label="Facebook" class="icon-facebook">f</a><a href="https://tiktok.com" target="_blank" aria-label="TikTok" class="icon-tiktok">t</a></div></div></div></body></html>"""
        try:
            os.makedirs(full_path, exist_ok=True)
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f: f.write(html_content)
        except OSError as e: self._log(f"Không thể khởi tạo thư mục: {e}\n")
    
    def _create_shortcut_properly(self, target_path, shortcut_path, work_dir):
        if system() != "Windows": return
        pythoncom.CoInitialize()
        try:
            shortcut = pythoncom.CoCreateInstance(shell.CLSID_ShellLink, None, pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink)
            shortcut.SetPath(target_path)
            shortcut.SetWorkingDirectory(work_dir)
            persist_file = shortcut.QueryInterface(pythoncom.IID_IPersistFile)
            persist_file.Save(shortcut_path, 0)
        finally: pythoncom.CoUninitialize()

    def _append_to_json_log(self, source_folder, encrypted_folder_name):
        app_data_path = self._get_special_folder_path(shellcon.CSIDL_LOCAL_APPDATA)
        if not app_data_path: self._log("\nLỖI: Không tìm thấy đường dẫn AppData, không thể ghi log."); return
        log_file_path = os.path.join(app_data_path, 'pattern.log')
        log_data = []
        try:
            if os.path.exists(log_file_path):
                with open(log_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content: log_data = json.loads(content)
                    if not isinstance(log_data, list): log_data = []
        except (json.JSONDecodeError, IOError): log_data = []
        new_entry = {"timestamp": datetime.now().isoformat(), "source": source_folder, "created_folder": encrypted_folder_name}
        log_data.append(new_entry)
        try:
            with open(log_file_path, 'w', encoding='utf-8') as f: json.dump(log_data, f, indent=4, ensure_ascii=False)
        except IOError as e: self._log(f"\n\nLỖI: Không thể ghi vào file pattern.log: {e}")
            
    def generate_random_string(self, pattern, length):
        required_random_len = length - len(pattern)
        if required_random_len < 0: return pattern[:length]
        alphabet = string.ascii_letters + string.digits + '!@#$%^&()-_=+[].,'
        random_part = ''.join(secrets.choice(alphabet) for _ in range(required_random_len))
        return pattern + random_part
        
    def copy_action(self): self._run_task_in_thread(self._copy_task)
    def clear_shortcut(self): self._run_task_in_thread(self._clear_shortcut_task)
    def clear_source(self): self._run_task_in_thread(self._clear_source_task)

    def _copy_task(self):
        self._log("", clear_first=True)
        if not os.path.exists(self.webserver_exe_path):
            self._log(f"✘ LỖI: Không tìm thấy file '{self.webserver_exe_path}'.\n")
            self._log("⚠   Vui lòng biên dịch và đặt nó vào cùng thư mục với ứng dụng.\n")
            return

        # 1. KIỂM TRA CÁC MỤC ĐƯỢC CHỌN TRƯỚC TIÊN
        selected_folders = [self.sub_folders[i] for i, var in enumerate(self.checkbox_vars) if var.get()]

        # 2. NẾU KHÔNG CÓ GÌ ĐƯỢC CHỌN, THÔNG BÁO VÀ DỪNG HOÀN TOÀN
        if not selected_folders:
            self._log("⚠  Không có mục nào được chọn để sao chép.\n")
            self._log("⚠  Tạm dừng thực thi copy.\n")
            return  # <-- Dừng hàm tại đây, không thực hiện các bước bên dưới

        # --- CHỈ KHI CÓ MỤC ĐƯỢC CHỌN, CÁC TÁC VỤ SAU MỚI ĐƯỢC THỰC THI ---
        
        app_data_path = self._get_special_folder_path(shellcon.CSIDL_LOCAL_APPDATA)
        desktop_path = self._get_special_folder_path(shellcon.CSIDL_DESKTOP)
        if not app_data_path:
            self._log("Lỗi nghiêm trọng: Không thể xác định đường dẫn AppData.")
            return
        if not desktop_path or not os.path.isdir(desktop_path):
            self._log("Cảnh báo: Không tìm thấy thư mục Desktop.")
            desktop_path = None
        
        random_string = self.generate_random_string(self.setting_pattern, self.setting_length)
        random_base_folder_name = f"{{{random_string}}}"
        random_base_folder_path = os.path.join(app_data_path, random_base_folder_name)
        os.makedirs(random_base_folder_path, exist_ok=True)
        self._log(f"{random_base_folder_name}\n")
        self._append_to_json_log("Main Root", random_base_folder_name)
        
        # 3. TIẾN HÀNH SAO CHÉP (KHÔNG CẦN KIỂM TRA LẠI VÌ ĐÃ LÀM Ở TRÊN)
        self._log(f"\n⚙️  BẮT ĐẦU SAO CHÉP DỮ LIỆU ⚙️\n")
        success_count, failure_count = 0, 0
        for folder_name in selected_folders:
            self._log(f"☛ Đang xử lý: ♬ {folder_name}\n")
            try:
                source_path = os.path.join('source', folder_name)
                md5_hash = hashlib.md5(folder_name.encode('utf-8')).hexdigest()
                final_destination_path = os.path.join(random_base_folder_path, *list(md5_hash[:16]))
                
                shutil.copytree(source_path, final_destination_path, dirs_exist_ok=True)
                shutil.copy2(self.webserver_exe_path, final_destination_path)
                
                original_html_name = next((f for f in os.listdir(final_destination_path) if f.lower().endswith('.html') and f != self.webserver_exe_path), None)
                if original_html_name:
                    new_html_name = f"{md5_hash}.html"
                    os.rename(os.path.join(final_destination_path, original_html_name), os.path.join(final_destination_path, new_html_name))
                    
                    if desktop_path and system() == "Windows":
                        webserver_target_path = os.path.join(final_destination_path, self.webserver_exe_path)
                        shortcut_desktop_path = os.path.join(desktop_path, f"{folder_name}.lnk")
                        self._create_shortcut_properly(webserver_target_path, shortcut_desktop_path, final_destination_path)
                        self._log(f"   ⫸ Đã tạo shortcut: {folder_name}.lnk 🔗\n")
                else:
                    self._log(" ✗  Cảnh báo: Không tìm thấy file .html trong thư mục nguồn.\n")
                success_count += 1
            except Exception as e:
                self._log(f"  - LỖI: {e}\n")
                failure_count += 1
        self._log(f"\n⚙️  HOÀN TẤT SAO CHÉP ⚙️\n✔   Thành công: {success_count}\n✘    Thất bại: {failure_count}\n")
            
        self._log("\n🛡️  BẢO MẬT DỮ LIỆU 🛡️\n")
        self._log("☛  Đang xây dựng hệ thống ma trận\n")
        try:
            build_emojis = ['⛏️', '🔨', '🔩', '⚙️', '🔧', '⚔️', '🏹']
            alphabet = string.ascii_lowercase + string.digits
            for i in range(self.setting_num_empty_folders):
                current_path = os.path.join(random_base_folder_path, *[secrets.choice(alphabet) for _ in range(16)])
                os.makedirs(current_path, exist_ok=True)
                if (i + 1) % 5 == 0:
                    self._log(random.choice(build_emojis), clear_first=False)
            self._log("\n✔ Hoàn thành hệ thống ma trận\n\n")
        except Exception as e:
            self._log(f"\n✘  Lỗi khi xây dựng hệ thống ma trận: {e}\n")
        
        self._log("☛  Thiết lập chế độ tàng hình\n")
        try:
            hide_count = 0
            for root, dirs, files in os.walk(random_base_folder_path, topdown=False):
                for name in files + dirs:
                    self._hide_path(os.path.join(root, name))
                    hide_count += 1;
                    if hide_count % 70 == 0:
                        self._log("🚧", clear_first=False)
            self._hide_path(random_base_folder_path)
            self._log("\n✔  Hoàn tất.\n")
        except Exception as e:
            self._log(f"\n✘  Lỗi trong quá trình tàng hình: {e}\n")
        self._log(f"\n🔥🔥🔥  TOÀN BỘ TÁC VỤ ĐÃ HOÀN TẤT 🔥🔥🔥")

    def _clear_shortcut_task(self, log_to_gui=True):
        if log_to_gui: self._log("☛  Bắt đầu dọn dẹp shortcut 🌟\n", clear_first=True)
        if system() != "Windows":
            if log_to_gui: self._log("⚠  Chức năng này chỉ hoạt động trên Windows.\n"); return
        
        deleted_count = 0
        try:
            desktop_path = self._get_special_folder_path(shellcon.CSIDL_DESKTOP)
            app_data_path = self._get_special_folder_path(shellcon.CSIDL_LOCAL_APPDATA)
            if not app_data_path or not desktop_path:
                if log_to_gui: self._log(" ✘  Lỗi: Không tìm thấy đường dẫn hệ thống.\n"); return

            log_file_path = os.path.join(app_data_path, 'pattern.log')
            if not os.path.exists(log_file_path): 
                if log_to_gui: self._log("⚠  Thông báo: Không tìm thấy file log.\n"); return
            
            with open(log_file_path, 'r', encoding='utf-8') as f:
                full_logged_paths = {os.path.normpath(os.path.join(app_data_path, entry['created_folder'])) for entry in json.load(f) if 'created_folder' in entry}
            
            if not full_logged_paths:
                if log_to_gui: self._log("⚠  File log rỗng.\n"); return

            if log_to_gui: self._log("\n ☛  Quét Desktop\n")
            for filename in os.listdir(desktop_path):
                if not filename.lower().endswith('.lnk'): continue
                shortcut_path = os.path.join(desktop_path, filename)
                try:
                    pythoncom.CoInitialize()
                    shortcut = pythoncom.CoCreateInstance(shell.CLSID_ShellLink, None, pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink)
                    persist_file = shortcut.QueryInterface(pythoncom.IID_IPersistFile)
                    persist_file.Load(shortcut_path, 0)
                    target_path, _ = shortcut.GetPath(shell.SLGP_UNCPRIORITY)
                    pythoncom.CoUninitialize()
                    
                    if target_path and any(os.path.normpath(os.path.dirname(target_path)).startswith(p) for p in full_logged_paths):
                        os.remove(shortcut_path)
                        if log_to_gui: self._log(f"✔  Đã xóa: {filename} 🔗\n")
                        deleted_count += 1
                except Exception: pythoncom.CoUninitialize() 
            if log_to_gui: self._log(f"\n☛  Đã xóa tổng cộng [{deleted_count}] shortcut.\n")
        except Exception as e:
            if log_to_gui: self._log(f"\n\n✘  LỖI KHÔNG XÁC ĐỊNH: {e}")

    def _hide_path(self, path_to_hide):
        if not os.path.exists(path_to_hide): return
        try:
            if system() == "Windows":
                attrs = ctypes.windll.kernel32.GetFileAttributesW(path_to_hide)
                if attrs != -1: ctypes.windll.kernel32.SetFileAttributesW(path_to_hide, attrs | 0x02)
            else:
                dirname, basename = os.path.split(path_to_hide)
                if not basename.startswith('.'):
                    new_path = os.path.join(dirname, '.' + basename)
                    if not os.path.exists(new_path): os.rename(path_to_hide, new_path)
        except Exception: pass

    def _rmtree_with_logging(self, path_to_delete):
        delete_count = 0
        delete_emojis = ['⚔️', '💣', '🔥','💥', '💀']
        try:
            for root, dirs, files in os.walk(path_to_delete, topdown=False):
                for name in files:
                    try: 
                        os.remove(os.path.join(root, name))
                        delete_count += 1
                    except OSError: pass
                for name in dirs:
                    try: 
                        os.rmdir(os.path.join(root, name))
                        delete_count += 1
                    except OSError: pass
                if delete_count % 50 == 0 and delete_count > 0:
                    self._log(random.choice(delete_emojis), clear_first=False)
            os.rmdir(path_to_delete)
        except OSError as e: self._log(f"\n✘  Lỗi trong khi xóa: {e.strerror}\n")

    def _kill_webserver_process(self):
        """Dừng tiến trình cp.exe nếu nó đang chạy."""
        if system() != "Windows":
            self._log(f"⚠  Tự động dừng tiến trình không được hỗ trợ trên {system()}. Bỏ qua.\n")
            return
            
        self._log(f"💥  Đang tìm và dừng tiến trình 👁️\n")
        try:
            subprocess.run(
                ["taskkill", "/F", "/IM", self.webserver_exe_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False
            )
            self._log(f"✔  Đã hoàn tất việc dừng tiến trình 🌀\n")
        except FileNotFoundError:
            self._log(f"✘  Lỗi: Không tìm thấy lệnh 'taskkill'. Không thể dừng tiến trình.\n")
        except Exception as e:
            self._log(f"✘  Lỗi không xác định khi dừng tiến trình: {e}\n")

    def _clear_source_task(self):
        self._log("☠☠☠      Bắt đầu dọn dẹp TOÀN BỘ     ☠☠☠\n☠☠☠ Hành động này không thể hoàn tác ☠☠☠\n\n", clear_first=True)
        
        self._kill_webserver_process()

        self._clear_shortcut_task(log_to_gui=False)
        self._log("\n✔  Đã hoàn tất dọn dẹp các shortcut trên Desktop.")
        app_data_path = self._get_special_folder_path(shellcon.CSIDL_LOCAL_APPDATA)
        if not app_data_path: self._log("\n✘  Lỗi: Không tìm thấy đường dẫn AppData\\Local."); return

        log_file_path = os.path.join(app_data_path, 'pattern.log')
        if not os.path.exists(log_file_path): self._log("\n✘  Không tìm thấy file log, bỏ qua việc xóa source."); return

        folders_to_delete, num_sources_found = set(), 0
        try:
            with open(log_file_path, 'r', encoding='utf-8') as f:
                valid_entries = [entry for entry in json.load(f) if 'created_folder' in entry]
                num_sources_found = len(valid_entries)
                for entry in valid_entries:
                    folder_name = entry['created_folder']
                    folders_to_delete.add(os.path.join(app_data_path, folder_name))
                    folders_to_delete.add(os.path.join(app_data_path, '.' + os.path.basename(folder_name)))
        except (IOError, json.JSONDecodeError) as e: self._log(f"\n✘  Lỗi khi đọc file pattern.log: {e}")
        
        if num_sources_found == 0: self._log("\n⚠  File log rỗng hoặc không có mục hợp lệ.")
        else:
            self._log(f"\n✔  Tìm thấy [{num_sources_found}] source gốc cần dọn dẹp.\n")
            deleted_count = 0
            for path in folders_to_delete:
                if os.path.isdir(path):
                    self._log(f"☛  Đang xóa source 💣\n")
                    self._rmtree_with_logging(path)
                    self._log("✔\n")
                    deleted_count += 1
            if deleted_count > 0: self._log(f"✔  Đã xóa thành công [{num_sources_found}] source.\n")

        try:
            os.remove(log_file_path)
            self._log("\n✔  Đã xóa file log.")
        except OSError as e: self._log(f"\n✘  Lỗi khi xóa file pattern.log: {e}")
            
        self._log(f"\n\n🔥🔥🔥  QUÁ TRÌNH DỌN DẸP HOÀN TẤT 🔥🔥🔥")

if __name__ == "__main__":
    app = App()
    app.mainloop()