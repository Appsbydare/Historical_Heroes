import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import threading
from extraction_manager import run_extraction

BG_COLOR = '#f5f6fa'  # Light, modern background
FRAME_COLOR = '#ffffff'  # White for frames

class ExtractionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Wikipedia Extraction Manager / 위키백과 추출 관리자')
        self.geometry('700x550')
        self.resizable(False, False)
        self.configure(bg=BG_COLOR)

        self.output_type = tk.StringVar(value='sql')
        self.stop_flag = threading.Event()
        self.seed_url = tk.StringVar(value='https://en.wikipedia.org/wiki/Korean_War')
        self.max_degree = tk.IntVar(value=3)

        # Tabs
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background=BG_COLOR, borderwidth=0)
        style.configure('TNotebook.Tab', background=BG_COLOR, font=('Calibri', 10))
        style.map('TNotebook.Tab', background=[('selected', FRAME_COLOR)])

        notebook = ttk.Notebook(self)
        self.extraction_frame = tk.Frame(notebook, bg=FRAME_COLOR)
        self.settings_frame = tk.Frame(notebook, bg=FRAME_COLOR)
        notebook.add(self.extraction_frame, text='Extraction / 추출')
        notebook.add(self.settings_frame, text='Settings / 설정')
        notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # Extraction Tab
        tk.Label(self.extraction_frame, text='Wikipedia Extraction Manager / 위키백과 추출 관리자', font=('Impact', 16), bg=FRAME_COLOR).pack(pady=10)
        radio_frame = tk.Frame(self.extraction_frame, bg=FRAME_COLOR)
        radio_frame.pack(pady=5)
        tk.Radiobutton(radio_frame, text='SQL Database / SQL 데이터베이스', variable=self.output_type, value='sql', bg=FRAME_COLOR, font=('Calibri', 10)).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(radio_frame, text='CSV File / CSV 파일', variable=self.output_type, value='csv', bg=FRAME_COLOR, font=('Calibri', 10)).pack(side=tk.LEFT, padx=10)
        button_frame = tk.Frame(self.extraction_frame, bg=FRAME_COLOR)
        button_frame.pack(pady=10)
        self.start_btn = tk.Button(button_frame, text='Start Extraction / 추출 시작', command=self.start_extraction_thread, bg='#27ae60', fg='white', activebackground='#229954', activeforeground='white', font=('Calibri', 10, 'bold'))
        self.start_btn.pack(side=tk.LEFT, padx=10)
        self.stop_btn = tk.Button(button_frame, text='Stop / 중지', command=self.stop_extraction, bg='#c0392b', fg='white', activebackground='#922b21', activeforeground='white', font=('Calibri', 10, 'bold'))
        self.stop_btn.pack(side=tk.LEFT, padx=10)
        tk.Label(self.extraction_frame, text='Log / Status / 로그 / 상태:', bg=FRAME_COLOR).pack(anchor='w', padx=10)
        self.log_text = scrolledtext.ScrolledText(self.extraction_frame, height=18, width=90, state='disabled', font=('Consolas', 10), bg='#f0f0f5')
        self.log_text.pack(padx=10, pady=5, fill='both', expand=True)

        # Settings Tab
        tk.Label(self.settings_frame, text='Extraction Settings / 추출 설정', font=('Impact', 16), bg=FRAME_COLOR).pack(pady=10)
        form_frame = tk.Frame(self.settings_frame, bg=FRAME_COLOR)
        form_frame.pack(pady=10)
        tk.Label(form_frame, text='Seed URL / 시작 URL:', bg=FRAME_COLOR).grid(row=0, column=0, sticky='e', padx=5, pady=5)
        tk.Entry(form_frame, textvariable=self.seed_url, width=60, bg='#f0f0f5', font=('Calibri', 10)).grid(row=0, column=1, padx=5, pady=5)
        tk.Label(form_frame, text='Max Degree / 최대 단계:', bg=FRAME_COLOR).grid(row=1, column=0, sticky='e', padx=5, pady=5)
        tk.Spinbox(form_frame, from_=1, to=10, textvariable=self.max_degree, width=5, bg='#f0f0f5', font=('Calibri', 10)).grid(row=1, column=1, sticky='w', padx=5, pady=5)

    def start_extraction_thread(self):
        self.stop_flag.clear()
        self.clear_log()
        threading.Thread(target=self.start_extraction, daemon=True).start()

    def start_extraction(self):
        selected = self.output_type.get()
        seed_url = self.seed_url.get()
        max_degree = self.max_degree.get()
        self.log(f'Starting extraction with output type: {selected.upper()}')
        self.log(f'Seed URL: {seed_url}')
        self.log(f'Max Degree: {max_degree}')
        try:
            result = run_extraction(output_type=selected, seed_url=seed_url, max_degree=max_degree, stop_flag=self.stop_flag, log_callback=self.log)
            self.log(result)
            self.show_info('Extraction / 추출', result)
        except Exception as e:
            self.log(f'Extraction failed: {e}')
            self.show_info('Error / 오류', f'Extraction failed: {e}')

    def stop_extraction(self):
        self.log('Stop requested by user. / 사용자가 중지를 요청했습니다.')
        self.stop_flag.set()

    def log(self, message):
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)
        self.log_text.configure(state='disabled')

    def clear_log(self):
        self.log_text.configure(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state='disabled')

    def show_info(self, title, message):
        self.after(0, lambda: messagebox.showinfo(title, message))

if __name__ == '__main__':
    app = ExtractionApp()
    app.mainloop() 