# COPY A-Z - Công Cụ Triển Khai Dự Án Web Tĩnh

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-blue.svg)

## 🚩 Giới thiệu

**COPY A-Z** là công cụ quản lý và triển khai các dự án web tĩnh (HTML/CSS/JS) với nhiều lớp bảo mật, giao diện trực quan, hỗ trợ tự động hóa quá trình copy, ẩn mã nguồn, tạo shortcut truy cập nhanh và dọn dẹp dữ liệu.

## 🎯 Tính năng chính

- Triển khai nhanh nhiều dự án web tĩnh.
- Tự động tạo web server cục bộ (Flask).
- Bảo vệ mã nguồn qua cấu trúc thư mục phức tạp, đổi tên file, ẩn file/thư mục.
- Quản lý tập trung, thao tác nhiều dự án cùng lúc.
- Tạo shortcut trên Desktop, truy cập nhanh dự án.
- Dọn dẹp shortcut và dữ liệu chỉ với 1 click.
- Ghi log toàn bộ hoạt động để dễ quản lý.

## 📦 Yêu cầu & Thư viện

- **Python 3.7+**
- **Windows** (tối ưu, Linux hỗ trợ hạn chế)
- **Thư viện ngoài:**
  - Flask==2.3.3
  - pyinstaller==5.13.2
  - pywin32==306
- **Thư viện chuẩn:** tkinter, hashlib, secrets, shutil, configparser, threading, json

Cài đặt nhanh:
```bash
pip install Flask pyinstaller pywin32
```

## ⚙️ Cài đặt & Build

1. **Clone source về máy.**
2. **Cài dependencies** (xem trên).
3. **Build ứng dụng:**
   - Chạy `build.cmd` hoặc:
   ```bash
   pyinstaller --onefile --noconsole --icon="cp.ico" --hidden-import="jinja2" --hidden-import="werkzeug" --name=cp cp.py
   pyinstaller --onefile --windowed --icon="copyaz.ico" --name "CopyAZ" --hidden-import "win32timezone" CopyAZ.py
   ```
4. **Cấu trúc sau khi build:**
   ```
   project/
   ├── CopyAZ.exe          # GUI chính
   ├── cp.exe              # Web server
   ├── config.ini          # File cấu hình (tự tạo)
   ├── source/             # Chứa các dự án web
   └── ...
   ```

## 🚀 Hướng dẫn sử dụng

1. **Chuẩn bị dự án:** Đặt các folder dự án web vào `source/`, mỗi dự án 1 thư mục, phải có file `.html`.
2. **Chạy CopyAZ.exe:** Chọn dự án, nhấn **COPY** để triển khai.
3. **Truy cập:** Shortcut sẽ tự động tạo trên Desktop, click để mở dự án (web server tự tìm port trống).
4. **Quản lý:** 
   - **Refresh:** Cập nhật danh sách dự án.
   - **Clear Shortcut:** Xóa shortcut đã tạo.
   - **Clear Source:** Xóa toàn bộ dữ liệu đã triển khai (không thể hoàn tác).

## 🔒 Bảo mật & Cấu hình

- **Obfuscation:** Tạo đường dẫn ngẫu nhiên, nhiều cấp, đổi tên file HTML thành MD5, tạo hàng trăm thư mục rỗng gây nhiễu.
- **Ẩn file/thư mục:** Tự động đặt thuộc tính ẩn (Windows), đổi tên khó đoán.
- **Log:** Ghi lại mọi thao tác vào file log trong AppData.
- **Cấu hình:** File `config.ini` tự tạo, cho phép tùy chỉnh pattern, số lượng thư mục rỗng, trạng thái checkbox mặc định, v.v.

Ví dụ `config.ini`:
```ini
[Settings]
Checked = true
Pattern = l&WlsZDv#a)#
StringLength = 99
NumEmptyFolders = 789
```

## 🐞 Troubleshooting

| Lỗi                        | Nguyên nhân                | Giải pháp                        |
|----------------------------|----------------------------|----------------------------------|
| Không tìm thấy cp.exe      | Chưa build web server      | Build lại bằng build.cmd         |
| Permission denied          | Thiếu quyền admin          | Chạy với quyền admin             |
| Port already in use        | Port bị chiếm              | Web server tự tìm port khác      |
| Shortcut không hoạt động   | File bị xóa/di chuyển      | Chạy lại COPY hoặc Clear Shortcut|
| Không hiện dự án           | Lỗi thư mục source         | Kiểm tra lại cấu trúc source/    |

**Debug:** Chạy file `.py` trực tiếp để xem log chi tiết:
```bash
python CopyAZ.py
```

## 💻 Hỗ trợ hệ điều hành

| Tính năng         | Windows | Linux |
|-------------------|---------|-------|
| GUI               | ✅      | ✅    |
| Web Server        | ✅      | ✅    |
| Shortcut          | ✅      | ❌    |
| Ẩn file/thư mục   | ✅      | ✅    |
| Tích hợp hệ thống | ✅      | ⚠️    |

## ⚠️ Lưu ý

- **Clear Source** sẽ xóa vĩnh viễn dữ liệu đã triển khai.
- Shortcut chỉ dùng trên máy đã triển khai, không chia sẻ cho người khác.
- Nên backup dự án gốc trước khi thao tác.
- Có thể cần quyền admin lần đầu chạy.

## 📄 License

Phát hành theo giấy phép MIT. Xem file [LICENSE](LICENSE) để biết chi tiết.

## 👨‍💻 Tác giả

**Cao Phước Danh (@danh)**  
Email: danhcptube@gmail.com  
GitHub: [https://github.com/caophuocdanh](https://github.com/caophuocdanh)