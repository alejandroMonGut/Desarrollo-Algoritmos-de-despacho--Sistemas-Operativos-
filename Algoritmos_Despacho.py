import tkinter as tk
from tkinter import messagebox
import copy

class DispatchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Algoritmos de Despacho (Sistemas Operativos)")
        self.root.minsize(1000, 450) # Un poco más ancho para las nuevas columnas
        
        self.num_processes = 0
        self.quantum = 2
        self.entry_processes = []
        # Paleta de colores suave
        self.colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', '#c2c2f0', '#ffb3e6', '#c2f0c2', '#ffcc00', '#00cccc']
        
        self.results = {} 
        
        # Lista ajustada a lo solicitado
        self.algorithm_list = [
            "FIFO", 
            "SJF (No Exp)", 
            "Prioridad (No Exp)", 
            "Round Robin (FIFO)", 
            "Round Robin (SJF)",      # Respeta Quantum, ordena cola por ráfaga
            "Round Robin (Prioridad)" # Respeta Quantum, ordena cola por prioridad
        ]
        self.current_alg_index = 0
        
        self.create_welcome_screen()
    
    def _clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # ==========================================
    # 1. PANTALLA DE INICIO
    # ==========================================
    def create_welcome_screen(self):
        self._clear_screen()
        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.pack(expand=True, fill="both")
        
        tk.Label(frame, text="Algoritmos de Despacho", font=("Segoe UI", 20, "bold")).pack(pady=20) 
        
        tk.Label(frame, text="Ingrese cantidad de procesos:", font=("Arial", 12)).pack(pady=5)
        self.entry_input_num = tk.Entry(frame, font=("Arial", 12), justify="center")
        self.entry_input_num.pack(pady=5)
        self.entry_input_num.insert(0, "4")
        
        tk.Button(frame, text="Continuar", bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), 
                  command=self.validate_and_proceed).pack(pady=20)
    
    def validate_and_proceed(self):
        try:
            val = int(self.entry_input_num.get())
            if val <= 0: raise ValueError
            self.num_processes = val
            self.create_table_screen()
        except ValueError:
            messagebox.showerror("Error", "Ingrese un entero positivo.")

    # ==========================================
    # 2. PANTALLA DE DATOS
    # ==========================================
    def create_table_screen(self):
        self._clear_screen()
        
        top_frame = tk.Frame(self.root, padx=20, pady=10)
        top_frame.pack(fill="x")
        
        tk.Label(top_frame, text=f"Configuración ({self.num_processes} procesos)", font=("Arial", 14, "bold")).pack(side="left")
        
        # Entrada de Quantum
        tk.Label(top_frame, text="Quantum (Round Robins):", font=("Arial", 11, "bold"), fg="#D32F2F").pack(side="left", padx=(30, 5))
        self.entry_quantum = tk.Entry(top_frame, width=5, justify="center", font=("Arial", 11))
        self.entry_quantum.insert(0, "2")
        self.entry_quantum.pack(side="left")

        frame_table = tk.Frame(self.root, padx=20, pady=10)
        frame_table.pack(fill="both", expand=True)
        
        headers = ["Proceso", "T. Llegada", "Ráfaga (CPU)", "Prioridad (1=Alta)"]
        for col, text in enumerate(headers):
            tk.Label(frame_table, text=text, font=("Arial", 10, "bold"), bg="#ddd", width=18, relief="ridge").grid(row=0, column=col, sticky="nsew")
        
        self.entry_processes = []
        for i in range(self.num_processes):
            row_idx = i + 1
            tk.Label(frame_table, text=f"P{i+1}", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, padx=1, pady=1)
            
            e_arr = tk.Entry(frame_table, width=10, justify="center")
            e_arr.grid(row=row_idx, column=1)
            e_arr.insert(0, str(i * 2)) 
            
            e_bur = tk.Entry(frame_table, width=10, justify="center")
            e_bur.grid(row=row_idx, column=2)
            e_bur.insert(0, str((i % 3) + 3))
            
            e_prio = tk.Entry(frame_table, width=10, justify="center")
            e_prio.grid(row=row_idx, column=3)
            e_prio.insert(0, str((self.num_processes - i)))

            self.entry_processes.append({ "id": f"P{i+1}", "llegada": e_arr, "rafaga": e_bur, "prioridad": e_prio })
            
        btn_frame = tk.Frame(self.root, pady=20)
        btn_frame.pack()
        tk.Button(btn_frame, text="Calcular Todo", bg="#2196F3", fg="white", font=("Arial", 12, "bold"), width=20, command=self.process_data).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Volver", command=self.create_welcome_screen, width=10).pack(side="left", padx=10)

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
                    "id": pid,
                    "llegada": arr,
                    "rafaga": bur,
                    "prioridad": prio,
                    "original_idx": i,
                    "remaining": bur, # Vital para los algoritmos RR
                })
            
            self.calculate_all_algorithms(raw_data)
            self.current_alg_index = 0
            self.show_results_screen()
            
        except ValueError:
            messagebox.showerror("Error", "Revise que todos los campos sean números enteros positivos.")

    # ==========================================
    # 3. LÓGICA DE ALGORITMOS
    # ==========================================
    def calculate_all_algorithms(self, data):
        self.results = {}
        # Algoritmos No Expropiativos
        self.results["FIFO"] = self.solve_fifo(copy.deepcopy(data))
        self.results["SJF (No Exp)"] = self.solve_sjf(copy.deepcopy(data))
        self.results["Prioridad (No Exp)"] = self.solve_priority(copy.deepcopy(data))
        
        # Algoritmos Round Robin Especializados
        self.results["Round Robin (FIFO)"] = self.solve_round_robin(copy.deepcopy(data), self.quantum)
        self.results["Round Robin (SJF)"] = self.solve_round_robin_sjf(copy.deepcopy(data), self.quantum)
        self.results["Round Robin (Prioridad)"] = self.solve_round_robin_priority(copy.deepcopy(data), self.quantum)

    # --- Función auxiliar para métricas completas ---
    def calculate_metrics_from_timeline(self, timeline, original_data):
        metrics = []
        for p in original_data:
            # Buscar el último instante en que se ejecutó
            finish_time = 0
            for block in timeline:
                if block['id'] == p['id']:
                    finish_time = max(finish_time, block['end'])
            
            sys_time = finish_time - p['llegada']
            wait_time = sys_time - p['rafaga']
            
            metrics.append({
                "id": p['id'],
                "llegada": p['llegada'],
                "rafaga": p['rafaga'],
                "prioridad": p['prioridad'],
                "wait": wait_time,
                "system": sys_time,
                "original_idx": p['original_idx'],
                "color": self.colors[p['original_idx'] % len(self.colors)]
            })
        return metrics

    def _create_block(self, p, start, end):
        return {
            "id": p['id'],
            "start": start,
            "end": end,
            "original_idx": p['original_idx'],
            "color": self.colors[p['original_idx'] % len(self.colors)]
        }

    # --- FIFO ---
    def solve_fifo(self, data):
        data.sort(key=lambda x: x['llegada'])
        timeline = []
        time = 0
        for p in data:
            start = max(time, p['llegada'])
            end = start + p['rafaga']
            timeline.append(self._create_block(p, start, end))
            time = end
        return timeline, self.calculate_metrics_from_timeline(timeline, data)

    # --- SJF No Expropiativo ---
    def solve_sjf(self, data):
        data.sort(key=lambda x: x['llegada'])
        time = 0
        completed = []
        timeline = []
        n = len(data)
        while len(completed) < n:
            avail = [p for p in data if p['llegada'] <= time and p not in completed]
            if not avail:
                remaining = [p for p in data if p not in completed]
                time = min(remaining, key=lambda x: x['llegada'])['llegada']
                continue
            
            shortest = min(avail, key=lambda x: x['rafaga'])
            start = time
            end = start + shortest['rafaga']
            timeline.append(self._create_block(shortest, start, end))
            time = end
            completed.append(shortest)
        return timeline, self.calculate_metrics_from_timeline(timeline, data)

    # --- Prioridad No Expropiativo ---
    def solve_priority(self, data):
        data.sort(key=lambda x: x['llegada'])
        time = 0
        completed = []
        timeline = []
        n = len(data)
        while len(completed) < n:
            avail = [p for p in data if p['llegada'] <= time and p not in completed]
            if not avail:
                remaining = [p for p in data if p not in completed]
                time = min(remaining, key=lambda x: x['llegada'])['llegada']
                continue
            
            # Menor número = Mayor prioridad
            highest = min(avail, key=lambda x: x['prioridad'])
            start = time
            end = start + highest['rafaga']
            timeline.append(self._create_block(highest, start, end))
            time = end
            completed.append(highest)
        return timeline, self.calculate_metrics_from_timeline(timeline, data)

    def solve_round_robin(self, data, quantum):
        local_data = copy.deepcopy(data)
        local_data.sort(key=lambda x: x['llegada'])
        
        timeline = []
        time = 0
        completed_count = 0
        n = len(local_data)
        
        current_round = [] # Los que están tomando su turno en este ciclo
        next_round = []    # Los que ya tomaron su turno y esperan el siguiente ciclo
        ptr = 0
        
        while completed_count < n:
            # 1. Atrapar llegadas en el tiempo actual (entran a la ronda ACTUAL)
            while ptr < n and local_data[ptr]['llegada'] <= time:
                current_round.append(local_data[ptr])
                ptr += 1
                
            # 2. Si no hay nadie, adelantamos el tiempo al próximo proceso
            if not current_round and not next_round and ptr < n:
                time = local_data[ptr]['llegada']
                while ptr < n and local_data[ptr]['llegada'] <= time:
                    current_round.append(local_data[ptr])
                    ptr += 1
                    
            # 3. ¡FIN DE LA RONDA! Si la ronda actual se vació, cargamos la siguiente
            if not current_round and next_round:
                current_round = next_round
                next_round = []
                # En FIFO, simplemente mantenemos el orden de llegada natural
                current_round.sort(key=lambda x: x['llegada'])
                
            if not current_round: 
                continue
                
            # 4. Ejecutar proceso
            p = current_round.pop(0)
            burst = min(p['remaining'], quantum)
            start = time
            end = start + burst
            
            timeline.append(self._create_block(p, start, end))
            
            p['remaining'] -= burst
            time = end
            
            # 5. Atrapar procesos que llegaron MIENTRAS este se ejecutaba
            # ¡Se unen a la ronda ACTUAL para garantizar su primer turno!
            while ptr < n and local_data[ptr]['llegada'] <= time:
                current_round.append(local_data[ptr])
                ptr += 1
                
            # 6. El proceso actual ya consumió su turno. Si le falta tiempo, va a la SIGUIENTE ronda.
            if p['remaining'] > 0:
                next_round.append(p)
            else:
                completed_count += 1
                
        return timeline, self.calculate_metrics_from_timeline(timeline, data)

    def solve_round_robin_sjf(self, data, quantum):
        local_data = copy.deepcopy(data)
        local_data.sort(key=lambda x: x['llegada'])
        
        timeline = []
        time = 0
        completed_count = 0
        n = len(local_data)
        
        current_round = []
        next_round = []
        ptr = 0
        
        while completed_count < n:
            while ptr < n and local_data[ptr]['llegada'] <= time:
                current_round.append(local_data[ptr])
                ptr += 1
                
            if not current_round and not next_round and ptr < n:
                time = local_data[ptr]['llegada']
                while ptr < n and local_data[ptr]['llegada'] <= time:
                    current_round.append(local_data[ptr])
                    ptr += 1
                    
            if not current_round and next_round:
                current_round = next_round
                next_round = []
                
            if not current_round: 
                continue
                
            # ¡LA MAGIA AQUÍ! Ordenamos siempre antes de ejecutar para acomodar a los recién llegados
            current_round.sort(key=lambda x: (x['remaining'], x['llegada']))
            
            p = current_round.pop(0)
            burst = min(p['remaining'], quantum)
            start = time
            end = start + burst
            
            timeline.append(self._create_block(p, start, end))
            
            p['remaining'] -= burst
            time = end
            
            while ptr < n and local_data[ptr]['llegada'] <= time:
                current_round.append(local_data[ptr])
                ptr += 1
                
            if p['remaining'] > 0:
                next_round.append(p)
            else:
                completed_count += 1
                
        return timeline, self.calculate_metrics_from_timeline(timeline, data)

    def solve_round_robin_priority(self, data, quantum):
        local_data = copy.deepcopy(data)
        local_data.sort(key=lambda x: x['llegada'])
        
        timeline = []
        time = 0
        completed_count = 0
        n = len(local_data)
        
        current_round = []
        next_round = []
        ptr = 0
        
        while completed_count < n:
            while ptr < n and local_data[ptr]['llegada'] <= time:
                current_round.append(local_data[ptr])
                ptr += 1
                
            if not current_round and not next_round and ptr < n:
                time = local_data[ptr]['llegada']
                while ptr < n and local_data[ptr]['llegada'] <= time:
                    current_round.append(local_data[ptr])
                    ptr += 1
                    
            if not current_round and next_round:
                current_round = next_round
                next_round = []
                
            if not current_round: 
                continue
                
            # ¡LA MAGIA AQUÍ! Ordenamos por prioridad (menor número = mayor prioridad) y luego llegada
            current_round.sort(key=lambda x: (x['prioridad'], x['llegada']))
            
            p = current_round.pop(0)
            burst = min(p['remaining'], quantum)
            start = time
            end = start + burst
            
            timeline.append(self._create_block(p, start, end))
            
            p['remaining'] -= burst
            time = end
            
            while ptr < n and local_data[ptr]['llegada'] <= time:
                current_round.append(local_data[ptr])
                ptr += 1
                
            if p['remaining'] > 0:
                next_round.append(p)
            else:
                completed_count += 1
                
        return timeline, self.calculate_metrics_from_timeline(timeline, data)

    # ==========================================
    # 4. PANTALLA DE RESULTADOS
    # ==========================================
    def show_results_screen(self):
        self._clear_screen()
        
        alg_name = self.algorithm_list[self.current_alg_index]
        timeline, metrics_data = self.results[alg_name]
        
        main_container = tk.Frame(self.root, padx=10, pady=10)
        main_container.pack(fill="both", expand=True)
        
        # Encabezado
        header = tk.Frame(main_container)
        header.pack(fill="x", pady=5)
        tk.Label(header, text=f"{alg_name}", font=("Arial", 16, "bold"), fg="#333").pack(side="left")
        if "Round Robin" in alg_name:
            tk.Label(header, text=f"(Quantum = {self.quantum})", font=("Arial", 12), fg="#666").pack(side="left", padx=10)

        content = tk.Frame(main_container)
        content.pack(fill="both", expand=True)

        # --- IZQUIERDA: MÉTRICAS (Con nuevas columnas) ---
        left_frame = tk.Frame(content, bd=2, relief="groove", padx=5, pady=5)
        left_frame.pack(side="left", fill="y", padx=5)
        
        tk.Label(left_frame, text="Métricas Detalladas", font=("Arial", 11, "bold")).pack(pady=(0,5))
        
        # Encabezados tabla métricas
        cols_frame = tk.Frame(left_frame)
        cols_frame.pack(fill="x")
        columns = ["ID", "Lleg", "Ráf", "Prio", "Esp(W)", "Sis(T)"]
        widths =  [4,    5,      5,     5,      6,        6]
        
        for c, w in zip(columns, widths):
            tk.Label(cols_frame, text=c, font=("Arial", 9, "bold"), width=w, bg="#e0e0e0", relief="ridge").pack(side="left")
            
        rows_frame = tk.Frame(left_frame)
        rows_frame.pack(fill="both", expand=True)
        
        metrics_data.sort(key=lambda x: x['original_idx'])
        
        avg_wait = 0
        avg_sys = 0
        
        for m in metrics_data:
            r = tk.Frame(rows_frame)
            r.pack(pady=1, fill="x")
            
            # Datos básicos
            tk.Label(r, text=m['id'], width=4, bg=m['color']).pack(side="left")
            tk.Label(r, text=m['llegada'], width=5).pack(side="left")
            tk.Label(r, text=m['rafaga'], width=5).pack(side="left")
            tk.Label(r, text=m['prioridad'], width=5).pack(side="left")
            
            # Resultados calculados
            tk.Label(r, text=m['wait'], width=6, font=("Arial", 9, "bold"), fg="#D32F2F").pack(side="left")
            tk.Label(r, text=m['system'], width=6, font=("Arial", 9, "bold"), fg="#1976D2").pack(side="left")
            
            avg_wait += m['wait']
            avg_sys += m['system']
            
        if metrics_data:
            avg_wait /= len(metrics_data)
            avg_sys /= len(metrics_data)
            
        res_summary = tk.Frame(left_frame, pady=10)
        res_summary.pack()
        tk.Label(res_summary, text=f"Prom. Espera: {avg_wait:.2f}", font=("Arial", 10, "bold"), fg="#D32F2F").pack()
        tk.Label(res_summary, text=f"Prom. Sistema: {avg_sys:.2f}", font=("Arial", 10, "bold"), fg="#1976D2").pack()

        # --- DERECHA: GANTT (Eje inferior) ---
        right_frame = tk.Frame(content, bd=2, relief="groove", padx=5, pady=5)
        right_frame.pack(side="left", fill="both", expand=True)
        
        row_height = 40
        top_margin = 30
        bottom_axis_height = 40
        total_h = (self.num_processes * row_height) + top_margin + bottom_axis_height
        
        canvas = tk.Canvas(right_frame, bg="white", height=total_h)
        canvas.pack(fill="both", expand=True)
        self.root.update_idletasks()
        
        # Calcular escala
        max_time = max([b['end'] for b in timeline], default=1)
        # Añadir un margen al tiempo final para que no quede pegado al borde
        max_time_display = max_time + 1 
        
        w = canvas.winfo_width()
        if w < 100: w = 400
        
        left_m = 40
        right_m = 20
        # Ancho útil para dibujar
        draw_width = w - left_m - right_m
        scale = draw_width / max_time_display
        
        # 1. Dibujar Filas de Procesos
        for i in range(self.num_processes):
            y = top_margin + i*row_height
            # Etiqueta P1, P2...
            canvas.create_text(20, y + 20, text=f"P{i+1}", font=("Arial", 10, "bold"))
            # Carril gris tenue
            canvas.create_line(left_m, y+40, w-right_m, y+40, fill="#f2f2f2") 

        # 2. Dibujar Bloques (SIN texto adentro)
        for block in timeline:
            idx = block['original_idx']
            x0 = left_m + block['start'] * scale
            x1 = left_m + block['end'] * scale
            y0 = top_margin + idx*row_height + 10
            y1 = y0 + 20 # Barra más delgada para ser elegante
            
            canvas.create_rectangle(x0, y0, x1, y1, fill=block['color'], outline="black")

        # 3. DIBUJAR EJE X (Números abajo)
        axis_y = total_h - 25
        canvas.create_line(left_m, axis_y, left_m + (max_time_display * scale), axis_y, width=2)
        
        # Decidir intervalo de números para no amontonar
        # Si hay mucho tiempo (ej. 50), mostrar de 5 en 5. Si es poco, de 1 en 1.
        step = 1
        if max_time > 20: step = 2
        if max_time > 50: step = 5
        
        for t in range(0, max_time + 2, step):
            if t > max_time_display: break
            x = left_m + (t * scale)
            # Pequeña marca (tick)
            canvas.create_line(x, axis_y, x, axis_y + 5, width=1)
            # Número
            canvas.create_text(x, axis_y + 15, text=str(t), font=("Arial", 8))

        # ==========================================
        # BOTONERA MODIFICADA
        # ==========================================
        nav = tk.Frame(main_container, pady=10)
        nav.pack(side="bottom")
        
        tk.Button(nav, text="< Configuración", command=self.create_table_screen).pack(side="left", padx=(0, 20))
        
        # Botón anterior (solo si no es el primer algoritmo)
        if self.current_alg_index > 0:
            tk.Button(nav, text="< Anterior", bg="#FF9800", fg="white", font=("Arial", 10, "bold"), command=self.previous_algorithm).pack(side="left", padx=5)
        
        is_last = self.current_alg_index == len(self.algorithm_list) - 1
        btn_text = "VER COMPARATIVA FINAL >" if is_last else "Siguiente Algoritmo >"
        btn_bg = "#673AB7" if is_last else "#2196F3"
        cmd = self.show_comparison_screen if is_last else self.next_algorithm
        
        tk.Button(nav, text=btn_text, bg=btn_bg, fg="white", font=("Arial", 10, "bold"), command=cmd).pack(side="left", padx=5)

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
        
        main = tk.Frame(self.root, padx=30, pady=30)
        main.pack(expand=True, fill="both")
        
        tk.Label(main, text="Tabla Comparativa Final", font=("Arial", 20, "bold")).pack(pady=(0, 20))
        
        tbl_frame = tk.Frame(main)
        tbl_frame.pack()
        
        # Headers
        headers = ["Algoritmo", "Prom. Espera", "Prom. Sistema"]
        for i, h in enumerate(headers):
            tk.Label(tbl_frame, text=h, font=("Arial", 11, "bold"), bg="#ddd", width=20, relief="ridge").grid(row=0, column=i, pady=5)
        
        best_alg = ""
        min_wait = float('inf')
        
        for i, alg in enumerate(self.algorithm_list):
            _, metrics = self.results[alg]
            
            avg_w = sum(m['wait'] for m in metrics) / len(metrics)
            avg_s = sum(m['system'] for m in metrics) / len(metrics)
            
            if avg_w < min_wait:
                min_wait = avg_w
                best_alg = alg
            
            row = i + 1
            tk.Label(tbl_frame, text=alg, width=20, anchor="w", padx=5, relief="groove").grid(row=row, column=0, sticky="nsew")
            tk.Label(tbl_frame, text=f"{avg_w:.2f}", width=20, relief="groove").grid(row=row, column=1, sticky="nsew")
            tk.Label(tbl_frame, text=f"{avg_s:.2f}", width=20, relief="groove").grid(row=row, column=2, sticky="nsew")

        res_frame = tk.Frame(main, pady=20)
        res_frame.pack()
        tk.Label(res_frame, text=f"Mejor rendimiento (Menor Espera):", font=("Arial", 12)).pack()
        tk.Label(res_frame, text=best_alg, font=("Arial", 16, "bold"), fg="#4CAF50").pack()
        
        tk.Button(main, text="Reiniciar Simulación", command=self.create_welcome_screen, bg="#FF5722", fg="white").pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    app = DispatchApp(root)
    root.mainloop()