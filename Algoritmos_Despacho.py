import tkinter as tk
from tkinter import messagebox
import copy

# ==========================================
# CONFIGURACIÓN DE TEMA Y TAMAÑO
# ==========================================
BASE_SIZE = 14

THEME = {
    "bg_window": "#eceff1",       
    "bg_card": "#ffffff",         
    "fg_text": "#37474f",         
    "fg_header": "#263238",       
    "accent": "#455a64",          
    "btn_primary": "#37474f",     
    "btn_action": "#0277bd",      
    "btn_success": "#2e7d32",     
    "btn_text": "#ffffff",        
    "entry_bg": "#ffffff",        
    "entry_fg": "#000000",        
    "font_title": ("Segoe UI", BASE_SIZE + 10, "bold"),      
    "font_subtitle": ("Segoe UI", BASE_SIZE, "bold"),    
    "font_text": ("Segoe UI", BASE_SIZE),                    
    "font_bold": ("Segoe UI", BASE_SIZE, "bold"),            
    "font_input": ("Segoe UI", BASE_SIZE),               
}

class DispatchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Algoritmos de Despacho")
        self.root.minsize(1200, 600) 
        self.root.configure(bg=THEME["bg_window"])
        
        self.num_processes = 0
        self.quantum = 2
        self.entry_processes = []
        
        self.colors = ['#ef9a9a', '#90caf9', '#a5d6a7', '#ffcc80', '#ce93d8', '#80cbc4', '#e6ee9c', '#ffab91', '#81d4fa']
        
        self.results = {} 
        self.algorithm_list = ["FIFO", "SJF (No Exp)", "Prioridad (No Exp)", "Round Robin (FIFO)", "Round Robin (SJF)", "Round Robin (Prioridad)"]
        self.current_alg_index = 0
        
        self.create_welcome_screen()
    
    def _clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_card_frame(self, parent, padx=20, pady=20):
        frame = tk.Frame(parent, bg=THEME["bg_card"], bd=1, relief="groove")
        frame.pack(padx=padx, pady=pady, fill="both", expand=True)
        return frame

    def create_styled_button(self, parent, text, command, bg_color=None, width=15):
        if bg_color is None: bg_color = THEME["btn_primary"]
        btn = tk.Button(parent, text=text, command=command,
                        bg=bg_color, fg=THEME["btn_text"],
                        font=THEME["font_bold"],
                        relief="raised", bd=2, width=width,
                        cursor="hand2", activebackground=THEME["accent"], activeforeground="#fff")
        return btn

    # ==========================================
    # NUEVA FUNCIÓN AUXILIAR: SCROLLABLE FRAME
    # ==========================================
    def create_scrollable_container(self, parent, bg_color):
        """Crea un área con scroll vertical. Retorna (contenedor_externo, frame_interno)."""
        container = tk.Frame(parent, bg=bg_color)
        canvas = tk.Canvas(container, bg=bg_color, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        
        scrollable_frame = tk.Frame(canvas, bg=bg_color)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Habilitar scroll con rueda del ratón
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Bindear cuando el mouse entra al canvas
        canvas.bind('<Enter>', lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind('<Leave>', lambda e: canvas.unbind_all("<MouseWheel>"))

        return container, scrollable_frame

    # ==========================================
    # 1. PANTALLA DE INICIO
    # ==========================================
    def create_welcome_screen(self):
        self._clear_screen()
        outer_frame = tk.Frame(self.root, bg=THEME["bg_window"])
        outer_frame.pack(expand=True, fill="both")
        
        card = tk.Frame(outer_frame, bg=THEME["bg_card"], bd=2, relief="ridge", padx=50, pady=50)
        card.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(card, text="Sistemas Operativos \nDesarrollo de Algoritmos de Despacho", font=THEME["font_title"], bg=THEME["bg_card"], fg=THEME["fg_header"]).pack(pady=(0, 20))
        tk.Label(card, text="Ingrese la cantidad de procesos a simular:", font=THEME["font_text"], bg=THEME["bg_card"], fg=THEME["fg_text"]).pack(pady=5)
        
        self.entry_input_num = tk.Entry(card, font=THEME["font_input"], justify="center", 
                                        bg="white", fg="black", relief="solid", bd=1)
        self.entry_input_num.pack(pady=15, ipady=5)
        self.entry_input_num.insert(0, "4")
        
        self.create_styled_button(card, "Iniciar Configuración", self.validate_and_proceed, bg_color=THEME["btn_success"], width=22).pack(pady=25)
    
    def validate_and_proceed(self):
        try:
            val = int(self.entry_input_num.get())
            if val <= 0: raise ValueError
            self.num_processes = val
            self.create_table_screen()
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingrese un número entero positivo.")

    # ==========================================
    # 2. PANTALLA DE DATOS (CON SCROLL)
    # ==========================================
    def create_table_screen(self):
        self._clear_screen()
        
        top_bar = tk.Frame(self.root, bg=THEME["bg_window"], padx=20, pady=15)
        top_bar.pack(fill="x")
        tk.Label(top_bar, text="Configuración de Procesos", font=THEME["font_title"], bg=THEME["bg_window"], fg=THEME["fg_header"]).pack(side="left")
        
        # ---------------------------------------------------------
        # AJUSTE 1: Eliminamos padx extra aquí si es necesario
        # ---------------------------------------------------------
        card = self.create_card_frame(self.root, padx=20, pady=10)
        
        # Sección Quantum
        q_frame = tk.Frame(card, bg=THEME["bg_card"], pady=15)
        q_frame.pack(fill="x", padx=10)
        tk.Label(q_frame, text="Quantum (Round Robin):", font=THEME["font_bold"], bg=THEME["bg_card"], fg=THEME["fg_text"]).pack(side="left")
        
        self.entry_quantum = tk.Entry(q_frame, width=6, justify="center", font=THEME["font_input"], bg="white", relief="solid", bd=1)
        self.entry_quantum.insert(0, str(self.quantum))
        self.entry_quantum.pack(side="left", padx=10)

        # --- TABLA CON SCROLL ---
        
        # 1. Wrapper con borde: Reducimos el padding para ganar espacio
        # Antes padx=30, ahora padx=10 para que esté más cerca del borde
        wrapper_frame = tk.Frame(card, bg=THEME["bg_card"], 
                                 highlightbackground=THEME["accent"], highlightthickness=2, bd=0)
        wrapper_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 2. Creamos el contenedor scrollable
        scroll_container, frame_table = self.create_scrollable_container(wrapper_frame, THEME["bg_card"])
        
        # AJUSTE 2: Quitamos el padx interno (antes 20) para que la tabla toque los bordes
        scroll_container.pack(fill="both", expand=True, padx=0, pady=0)

        # ---------------------------------------------------------
        # AJUSTE CRÍTICO: FORZAR ANCHO COMPLETO
        # Esto hace que la tabla interna se estire al 100% del ancho disponible
        # ---------------------------------------------------------
        def update_inner_frame_width(event):
            # Obtenemos el canvas (es el primer hijo de scroll_container)
            canvas = scroll_container.winfo_children()[0]
            # Ajustamos el ancho de la ventana interna del canvas al ancho del canvas
            canvas.itemconfig(canvas.find_all()[0], width=event.width)

        # Vinculamos el evento de cambio de tamaño del wrapper
        canvas_obj = scroll_container.winfo_children()[0]
        canvas_obj.bind("<Configure>", update_inner_frame_width)
        # ---------------------------------------------------------

        # Configurar grid weights para que las columnas se repartan el espacio
        frame_table.grid_columnconfigure(0, weight=1)
        frame_table.grid_columnconfigure(1, weight=1)
        frame_table.grid_columnconfigure(2, weight=1)
        frame_table.grid_columnconfigure(3, weight=1)

        headers = ["Proceso", "T. Llegada", "Ráfaga", "Prioridad (0=Alta)"]
        
        for col, text in enumerate(headers):
            lbl = tk.Label(frame_table, text=text, font=THEME["font_bold"], bg=THEME["accent"], fg="white", pady=8)
            # sticky="nsew" es vital para que el fondo llene la celda
            lbl.grid(row=0, column=col, sticky="nsew", padx=1, pady=1)
        
        self.entry_processes = []
        for i in range(self.num_processes):
            row_idx = i + 1
            row_bg = "#f5f5f5" if i % 2 == 0 else "#ffffff"
            
            lbl_id = tk.Label(frame_table, text=f"P{i+1}", font=THEME["font_bold"], bg=row_bg, fg=THEME["fg_text"])
            lbl_id.grid(row=row_idx, column=0, sticky="nsew", padx=1, pady=1)
            
            e_arr = tk.Entry(frame_table, justify="center", bg="white", relief="solid", bd=1, font=THEME["font_text"])
            e_arr.grid(row=row_idx, column=1, sticky="ns", pady=4, padx=5)
            e_arr.insert(0, str(i * 2)) 
            
            e_bur = tk.Entry(frame_table, justify="center", bg="white", relief="solid", bd=1, font=THEME["font_text"])
            e_bur.grid(row=row_idx, column=2, sticky="ns", pady=4, padx=5)
            e_bur.insert(0, str((i % 3) + 3))
            
            e_prio = tk.Entry(frame_table, justify="center", bg="white", relief="solid", bd=1, font=THEME["font_text"])
            e_prio.grid(row=row_idx, column=3, sticky="ns", pady=4, padx=5)
            e_prio.insert(0, str((self.num_processes - i)))

            self.entry_processes.append({ "id": f"P{i+1}", "llegada": e_arr, "rafaga": e_bur, "prioridad": e_prio })
            
        btn_frame = tk.Frame(card, bg=THEME["bg_card"], pady=20)
        btn_frame.pack()
        
        self.create_styled_button(btn_frame, "Volver", self.create_welcome_screen, bg_color=THEME["btn_primary"], width=15).pack(side="left", padx=15)
        self.create_styled_button(btn_frame, "Calcular y Simular", self.process_data, bg_color=THEME["btn_action"], width=25).pack(side="left", padx=15)
    def process_data(self):
        raw_data = []
        try:
            self.quantum = int(self.entry_quantum.get())
            if self.quantum <= 0: raise ValueError
            
            for i, row in enumerate(self.entry_processes):
                pid = row["id"]
                arr = int(row["llegada"].get())
                bur = int(row["rafaga"].get())
                prio = int(row["prioridad"].get())
                
                if arr < 0 or bur <= 0 or prio < 0:
                    messagebox.showerror("Error", f"Datos inválidos en {pid}.")
                    return
                
                raw_data.append({
                    "id": pid, "llegada": arr, "rafaga": bur, "prioridad": prio,
                    "original_idx": i, "remaining": bur,
                })
            
            self.calculate_all_algorithms(raw_data)
            self.current_alg_index = 0
            self.show_results_screen()
            
        except ValueError:
            messagebox.showerror("Error", "Revise que todos los campos sean números enteros positivos.")

    # ==========================================
    # 3. LÓGICA (INTACTA)
    # ==========================================
    def calculate_all_algorithms(self, data):
        self.results = {}
        self.results["FIFO"] = self.solve_fifo(copy.deepcopy(data))
        self.results["SJF (No Exp)"] = self.solve_sjf(copy.deepcopy(data))
        self.results["Prioridad (No Exp)"] = self.solve_priority(copy.deepcopy(data))
        self.results["Round Robin (FIFO)"] = self.solve_round_robin(copy.deepcopy(data), self.quantum)
        self.results["Round Robin (SJF)"] = self.solve_round_robin_sjf(copy.deepcopy(data), self.quantum)
        self.results["Round Robin (Prioridad)"] = self.solve_round_robin_priority(copy.deepcopy(data), self.quantum)

    def calculate_metrics_from_timeline(self, timeline, original_data):
        metrics = []
        for p in original_data:
            finish_time = 0
            for block in timeline:
                if block['id'] == p['id']:
                    finish_time = max(finish_time, block['end'])
                    
            sys_time = finish_time - p['llegada']
            wait_time = sys_time - p['rafaga']
            
            metrics.append({
                "id": p['id'], "llegada": p['llegada'], "rafaga": p['rafaga'], "prioridad": p['prioridad'],
                "wait": wait_time, "system": sys_time,
                "original_idx": p['original_idx'],
                "color": self.colors[p['original_idx'] % len(self.colors)]
            })
        return metrics

    def _create_block(self, p, start, end):
        return { "id": p['id'], "start": start, "end": end, "original_idx": p['original_idx'], "color": self.colors[p['original_idx'] % len(self.colors)] }

    def solve_fifo(self, data):
        data.sort(key=lambda x: x['llegada'])
        timeline = []; time = 0
        for p in data:
            start = max(time, p['llegada'])
            end = start + p['rafaga']
            timeline.append(self._create_block(p, start, end))
            time = end
        return timeline, self.calculate_metrics_from_timeline(timeline, data)

    def solve_sjf(self, data):
        data.sort(key=lambda x: x['llegada'])
        time = 0; completed = []; timeline = []; n = len(data)
        while len(completed) < n:
            avail = [p for p in data if p['llegada'] <= time and p not in completed]
            if not avail:
                remaining = [p for p in data if p not in completed]
                time = min(remaining, key=lambda x: x['llegada'])['llegada']
                continue
            shortest = min(avail, key=lambda x: x['rafaga'])
            start = time; end = start + shortest['rafaga']
            timeline.append(self._create_block(shortest, start, end))
            time = end; completed.append(shortest)
        return timeline, self.calculate_metrics_from_timeline(timeline, data)

    def solve_priority(self, data):
        data.sort(key=lambda x: x['llegada'])
        time = 0; completed = []; timeline = []; n = len(data)
        while len(completed) < n:
            avail = [p for p in data if p['llegada'] <= time and p not in completed]
            if not avail:
                remaining = [p for p in data if p not in completed]
                time = min(remaining, key=lambda x: x['llegada'])['llegada']
                continue
            highest = min(avail, key=lambda x: x['prioridad'])
            start = time; end = start + highest['rafaga']
            timeline.append(self._create_block(highest, start, end))
            time = end; completed.append(highest)
        return timeline, self.calculate_metrics_from_timeline(timeline, data)

    def solve_round_robin(self, data, quantum):
        local_data = copy.deepcopy(data)
        local_data.sort(key=lambda x: x['llegada'])
        timeline = []; time = 0; completed_count = 0; n = len(local_data)
        current_round = []; next_round = []; ptr = 0
        while completed_count < n:
            while ptr < n and local_data[ptr]['llegada'] <= time:
                current_round.append(local_data[ptr]); ptr += 1
            if not current_round and not next_round and ptr < n:
                time = local_data[ptr]['llegada']
                while ptr < n and local_data[ptr]['llegada'] <= time:
                    current_round.append(local_data[ptr]); ptr += 1
            if not current_round and next_round:
                current_round = next_round; next_round = []
                current_round.sort(key=lambda x: x['llegada'])
            if not current_round: continue
            p = current_round.pop(0)
            burst = min(p['remaining'], quantum)
            start = time; end = start + burst
            timeline.append(self._create_block(p, start, end))
            p['remaining'] -= burst; time = end
            while ptr < n and local_data[ptr]['llegada'] <= time:
                current_round.append(local_data[ptr]); ptr += 1
            if p['remaining'] > 0: next_round.append(p)
            else: completed_count += 1
        return timeline, self.calculate_metrics_from_timeline(timeline, data)

    def solve_round_robin_sjf(self, data, quantum):
        local_data = copy.deepcopy(data)
        local_data.sort(key=lambda x: x['llegada'])
        timeline = []; time = 0; completed_count = 0; n = len(local_data)
        current_round = []; next_round = []; ptr = 0
        while completed_count < n:
            while ptr < n and local_data[ptr]['llegada'] <= time:
                current_round.append(local_data[ptr]); ptr += 1
            if not current_round and not next_round and ptr < n:
                time = local_data[ptr]['llegada']
                while ptr < n and local_data[ptr]['llegada'] <= time:
                    current_round.append(local_data[ptr]); ptr += 1
            if not current_round and next_round:
                current_round = next_round; next_round = []
            if not current_round: continue
            current_round.sort(key=lambda x: (x['remaining'], x['llegada']))
            p = current_round.pop(0)
            burst = min(p['remaining'], quantum)
            start = time; end = start + burst
            timeline.append(self._create_block(p, start, end))
            p['remaining'] -= burst; time = end
            while ptr < n and local_data[ptr]['llegada'] <= time:
                current_round.append(local_data[ptr]); ptr += 1
            if p['remaining'] > 0: next_round.append(p)
            else: completed_count += 1
        return timeline, self.calculate_metrics_from_timeline(timeline, data)

    def solve_round_robin_priority(self, data, quantum):
        local_data = copy.deepcopy(data)
        local_data.sort(key=lambda x: x['llegada'])
        timeline = []; time = 0; completed_count = 0; n = len(local_data)
        current_round = []; next_round = []; ptr = 0
        while completed_count < n:
            while ptr < n and local_data[ptr]['llegada'] <= time:
                current_round.append(local_data[ptr]); ptr += 1
            if not current_round and not next_round and ptr < n:
                time = local_data[ptr]['llegada']
                while ptr < n and local_data[ptr]['llegada'] <= time:
                    current_round.append(local_data[ptr]); ptr += 1
            if not current_round and next_round:
                current_round = next_round; next_round = []
            if not current_round: continue
            current_round.sort(key=lambda x: (x['prioridad'], x['llegada']))
            p = current_round.pop(0)
            burst = min(p['remaining'], quantum)
            start = time; end = start + burst
            timeline.append(self._create_block(p, start, end))
            p['remaining'] -= burst; time = end
            while ptr < n and local_data[ptr]['llegada'] <= time:
                current_round.append(local_data[ptr]); ptr += 1
            if p['remaining'] > 0: next_round.append(p)
            else: completed_count += 1
        return timeline, self.calculate_metrics_from_timeline(timeline, data)

    # ==========================================
    # 4. PANTALLA DE RESULTADOS (CON SCROLLS)
    # ==========================================
    def show_results_screen(self):
        self._clear_screen()
        alg_name = self.algorithm_list[self.current_alg_index]
        timeline, metrics_data = self.results[alg_name]
        
        header_frame = tk.Frame(self.root, bg=THEME["bg_window"], pady=10)
        header_frame.pack(fill="x", padx=20)
        title_text = f"{alg_name}"
        if "Round Robin" in alg_name: title_text += f" (Q={self.quantum})"
        tk.Label(header_frame, text=title_text, font=THEME["font_title"], bg=THEME["bg_window"], fg=THEME["fg_header"]).pack(side="left")

        card = self.create_card_frame(self.root, padx=20, pady=5)

        # --- IZQUIERDA: MÉTRICAS (Con Scroll Vertical) ---
        left_frame = tk.Frame(card, bg=THEME["bg_card"], bd=0, padx=10, pady=10)
        left_frame.pack(side="left", fill="y")
        
        tk.Label(left_frame, text="Métricas Detalladas", font=THEME["font_subtitle"], bg=THEME["bg_card"], fg=THEME["fg_text"]).pack(pady=(0,10), anchor="w")
        
        # Contenedor del borde de la tabla
        table_border_frame = tk.Frame(left_frame, bg=THEME["bg_card"], highlightbackground=THEME["accent"], highlightthickness=2, bd=0)
        table_border_frame.pack(fill="both", expand=True) 
        
        # Encabezados (Fijos)
        cols_frame = tk.Frame(table_border_frame, bg=THEME["bg_card"])
        cols_frame.pack(fill="x")
        columns = ["ID", "Lleg", "Ráf", "Prio", "Esp(TE)", "Sis(TS)"]
        widths =  [5,    6,     6,     6,      7,       7]
        for c, w in zip(columns, widths):
            tk.Label(cols_frame, text=c, font=("Segoe UI", BASE_SIZE, "bold"), width=w, bg=THEME["accent"], fg="white", relief="flat").pack(side="left", padx=1)
            
        # Área de Filas (Scrollable)
        scroll_cont, rows_frame = self.create_scrollable_container(table_border_frame, THEME["bg_card"])
        scroll_cont.pack(fill="both", expand=True, pady=5)
        
        metrics_data.sort(key=lambda x: x['original_idx'])
        avg_wait = 0; avg_sys = 0
        
        for i, m in enumerate(metrics_data):
            row_bg = "#f5f5f5" if i % 2 == 0 else "#ffffff"
            r = tk.Frame(rows_frame, bg=row_bg)
            r.pack(pady=1, fill="x")
            
            tk.Label(r, text=m['id'], width=5, bg=m['color'], fg="#333", font=("Segoe UI", BASE_SIZE, "bold")).pack(side="left", padx=1)
            tk.Label(r, text=m['llegada'], width=6, bg=row_bg, font=THEME["font_text"]).pack(side="left", padx=1)
            tk.Label(r, text=m['rafaga'], width=6, bg=row_bg, font=THEME["font_text"]).pack(side="left", padx=1)
            tk.Label(r, text=m['prioridad'], width=6, bg=row_bg, font=THEME["font_text"]).pack(side="left", padx=1)
            tk.Label(r, text=m['wait'], width=7, font=("Segoe UI", BASE_SIZE , "bold"), fg="#d32f2f", bg=row_bg).pack(side="left", padx=1)
            tk.Label(r, text=m['system'], width=7, font=("Segoe UI", BASE_SIZE , "bold"), fg="#1976d2", bg=row_bg).pack(side="left", padx=1)
            avg_wait += m['wait']; avg_sys += m['system']
            
        if metrics_data:
            avg_wait /= len(metrics_data); avg_sys /= len(metrics_data)
        
        res_summary = tk.Frame(left_frame, pady=15, bg=THEME["bg_card"], bd=1, relief="solid")
        res_summary.pack(fill="x", pady=10)
        tk.Label(res_summary, text=f"Promedio Espera: {avg_wait:.2f}", font=THEME["font_bold"], fg="#d32f2f", bg=THEME["bg_card"]).pack()
        tk.Label(res_summary, text=f"Promedio Sistema: {avg_sys:.2f}", font=THEME["font_bold"], fg="#1976d2", bg=THEME["bg_card"]).pack()

        tk.Frame(card, width=2, bg="#e0e0e0").pack(side="left", fill="y", padx=15, pady=10)

        # --- DERECHA: GANTT (Con Scroll Bidireccional) ---
        right_frame = tk.Frame(card, bg=THEME["bg_card"], padx=10, pady=10)
        right_frame.pack(side="left", fill="both", expand=True)
        tk.Label(right_frame, text="Diagrama de Gantt", font=THEME["font_subtitle"], bg=THEME["bg_card"], fg=THEME["fg_text"]).pack(anchor="w", pady=(0, 5))
        
        # Contenedor para Canvas + Scrollbars
        gantt_container = tk.Frame(right_frame, bg="white", bd=1, relief="solid")
        gantt_container.pack(fill="both", expand=True)
        
        # Barras de scroll
        v_scroll = tk.Scrollbar(gantt_container, orient="vertical")
        h_scroll = tk.Scrollbar(gantt_container, orient="horizontal")
        
        canvas = tk.Canvas(gantt_container, bg="white", bd=0, highlightthickness=0,
                           yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        v_scroll.config(command=canvas.yview)
        h_scroll.config(command=canvas.xview)
        
        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Dibujado del Gantt
        row_height = 50 
        top_margin = 40; bottom_axis_height = 50
        total_h = (self.num_processes * row_height) + top_margin + bottom_axis_height
        
        # Determinar ancho necesario
        max_time = max([b['end'] for b in timeline], default=1)
        max_time_display = max_time + 1
        
        # Calcular ancho dinámico basado en duración
        calculated_width = max(800, max_time_display * 30) # 30 px por unidad de tiempo
        
        left_m = 50; right_m = 30
        draw_width = calculated_width - left_m - right_m
        scale = draw_width / max_time_display
        
        # Nombres de procesos (Y axis)
        for i in range(self.num_processes):
            y = top_margin + i*row_height
            canvas.create_text(25, y + 25, text=f"P{i+1}", font=THEME["font_bold"], fill="#555")
            canvas.create_line(left_m, y+50, calculated_width-right_m, y+50, fill="#f0f0f0") 
            
        # Bloques de tiempo
        for block in timeline:
            idx = block['original_idx']
            x0 = left_m + block['start'] * scale
            x1 = left_m + block['end'] * scale
            y0 = top_margin + idx*row_height + 15
            y1 = y0 + 25 
            canvas.create_rectangle(x0, y0, x1, y1, fill=block['color'], outline="#666")
            
        # Eje X
        axis_y = total_h - 25
        canvas.create_line(left_m, axis_y, left_m + (max_time_display * scale), axis_y, width=2, fill="#333")
        
        step = 1
        if max_time > 20: step = 2
        if max_time > 50: step = 5
        
        for t in range(0, max_time + 2, step):
            if t > max_time_display: break
            x = left_m + (t * scale)
            canvas.create_line(x, axis_y, x, axis_y + 5, width=1, fill="#333")
            canvas.create_text(x, axis_y + 15, text=str(t), font=("Segoe UI", BASE_SIZE - 2), fill="#333")

        # Configurar región de scroll
        canvas.config(scrollregion=(0, 0, calculated_width, total_h))
        
        # Scroll con mouse para el Gantt (Vertical y Horizontal con Shift)
        def _gantt_scroll(event):
            if event.state & 1: # Shift presionado -> Horizontal
                 canvas.xview_scroll(int(-1*(event.delta/120)), "units")
            else: # Vertical
                 canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind('<Enter>', lambda e: canvas.bind_all("<MouseWheel>", _gantt_scroll))
        canvas.bind('<Leave>', lambda e: canvas.unbind_all("<MouseWheel>"))

        # --- BOTONES DE NAVEGACIÓN ---
        nav = tk.Frame(self.root, bg=THEME["bg_window"], pady=15)
        nav.pack(side="bottom", fill="x")
        nav_buttons = tk.Frame(nav, bg=THEME["bg_window"])
        nav_buttons.pack()
        self.create_styled_button(nav_buttons, "Configuración", self.create_table_screen, bg_color=THEME["btn_primary"]).pack(side="left", padx=5)
        
        if self.current_alg_index > 0:
            self.create_styled_button(nav_buttons, "< Anterior", self.previous_algorithm, bg_color="#f57c00").pack(side="left", padx=5) 
        
        is_last = self.current_alg_index == len(self.algorithm_list) - 1
        btn_text = "VER COMPARATIVA FINAL >" if is_last else "Siguiente Algoritmo >"
        btn_bg = THEME["btn_success"] if is_last else THEME["btn_action"]
        cmd = self.show_comparison_screen if is_last else self.next_algorithm
        self.create_styled_button(nav_buttons, btn_text, cmd, bg_color=btn_bg, width=30).pack(side="left", padx=5)

    def next_algorithm(self):
        self.current_alg_index += 1
        self.show_results_screen()

    def previous_algorithm(self):
        if self.current_alg_index > 0:
            self.current_alg_index -= 1
            self.show_results_screen()

    # ==========================================
    # 5. PANTALLA COMPARATIVA
    # ==========================================
    def show_comparison_screen(self):
        self._clear_screen()
        outer_frame = tk.Frame(self.root, bg=THEME["bg_window"])
        outer_frame.pack(fill="both", expand=True)
        
        card = self.create_card_frame(outer_frame, padx=40, pady=40)
        
        tk.Label(card, text="Tabla Comparativa Final", font=THEME["font_title"], bg=THEME["bg_card"], fg=THEME["fg_header"]).pack(pady=(0, 20))
        
        tbl_frame = tk.Frame(card, bg="#999999", bd=1) 
        tbl_frame.pack(fill="x", expand=True, padx=10)
        
        tbl_frame.grid_columnconfigure(0, weight=2) 
        tbl_frame.grid_columnconfigure(1, weight=1) 
        tbl_frame.grid_columnconfigure(2, weight=1) 

        headers = ["Algoritmo", "Prom. Espera", "Prom. Sistema"]
        
        for i, h in enumerate(headers):
            tk.Label(tbl_frame, text=h, font=THEME["font_bold"], bg=THEME["accent"], fg="white", pady=12).grid(row=0, column=i, sticky="nsew", padx=1, pady=1)
        
        best_alg = ""; min_wait = float('inf')
        
        for i, alg in enumerate(self.algorithm_list):
            _, metrics = self.results[alg]
            avg_w = sum(m['wait'] for m in metrics) / len(metrics)
            avg_s = sum(m['system'] for m in metrics) / len(metrics)
            
            if avg_w < min_wait: min_wait = avg_w; best_alg = alg
            
            row = i + 1
            bg_row = "#f9f9f9" if row % 2 == 0 else "#ffffff"
            
            tk.Label(tbl_frame, text=alg, anchor="w", padx=15, bg=bg_row, pady=8, font=THEME["font_text"]).grid(row=row, column=0, sticky="nsew", padx=1, pady=1)
            tk.Label(tbl_frame, text=f"{avg_w:.2f}", bg=bg_row, pady=8, font=THEME["font_text"]).grid(row=row, column=1, sticky="nsew", padx=1, pady=1)
            tk.Label(tbl_frame, text=f"{avg_s:.2f}", bg=bg_row, pady=8, font=THEME["font_text"]).grid(row=row, column=2, sticky="nsew", padx=1, pady=1)
            
        res_frame = tk.Frame(card, bg=THEME["bg_card"], pady=20, padx=20, bd=2, relief="groove")
        res_frame.pack(pady=30)
        tk.Label(res_frame, text=f"Mejor rendimiento (Menor Espera):", font=THEME["font_subtitle"], bg=THEME["bg_card"]).pack()
        tk.Label(res_frame, text=best_alg, font=("Segoe UI", BASE_SIZE + 8, "bold"), fg=THEME["btn_success"], bg=THEME["bg_card"]).pack(pady=10)
        
        self.create_styled_button(card, "Reiniciar Simulación", self.create_welcome_screen, bg_color=THEME["btn_action"], width=25).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    app = DispatchApp(root)
    root.mainloop()