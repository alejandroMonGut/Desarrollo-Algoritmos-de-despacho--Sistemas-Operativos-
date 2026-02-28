import tkinter as tk
from tkinter import messagebox
import copy  # Necesario para no modificar la lista original en cada algoritmo

class DispatchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Desarrollo de Algoritmos de Despacho")
        self.root.minsize(500, 300)
        
        self.num_processes = 0
        self.entry_processes = []
        self.colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', '#c2c2f0', '#ffb3e6', '#c2f0c2']
        
        # Aquí guardaremos los resultados calculados de todos los algoritmos
        self.results = {} 
        self.algorithm_list = ["FIFO", "SJF"]
        self.current_alg_index = 0
        
        self.create_welcome_screen()
    
    def create_welcome_screen(self):
        self._clear_screen()
        
        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.pack(expand=True, fill="both")
        
        tk.Label(frame, text="Sistemas Operativos\nAlgoritmos de Despacho", font=("Arial", 16, "bold"), justify="center").pack(pady=20) 
        tk.Label(frame, text="Ingrese la cantidad de procesos: ", font=("Arial", 12)).pack(pady=5)
        
        self.entry_input_num = tk.Entry(frame, font=("Arial", 12), justify="center")
        self.entry_input_num.pack(pady=5)
        
        tk.Button(frame, text="Guardar y Continuar", fg="white", bg="#4CAF50", font=("Arial", 11, "bold"), command=self.validate_and_proceed).pack(pady=20)
    
    def validate_and_proceed(self):
        try:
            value = int(self.entry_input_num.get())
            if value <= 0:
                messagebox.showerror("Error", "La cantidad de procesos debe ser positiva.")
                return
            self.num_processes = value
            self.create_table_screen()
        except ValueError:
            messagebox.showerror("Error", "Ingrese un número entero válido.")

    def create_table_screen(self):
        self._clear_screen()
        
        frame_table = tk.Frame(self.root, padx=20, pady=20)
        frame_table.pack(fill="both", expand=True)
        
        tk.Label(frame_table, text=f"Datos para {self.num_processes} procesos", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=4, pady=(0,20))
        
        headers = ["Proceso", "T. Llegada", "Ráfaga", "Prioridad"]
        for col, text in enumerate(headers):
            tk.Label(frame_table, text=text, font=("Arial", 11, "bold"), bg="#ddd", width=14, relief="ridge").grid(row=1, column=col, sticky="nsew")
        
        self.entry_processes = []
        for i in range(self.num_processes):
            row_idx = i + 2
            tk.Label(frame_table, text=f"P{i+1}").grid(row=row_idx, column=0, padx=1, pady=1)
            
            e_arr = tk.Entry(frame_table, width=10, justify="center")
            e_arr.grid(row=row_idx, column=1)
            e_bur = tk.Entry(frame_table, width=10, justify="center")
            e_bur.grid(row=row_idx, column=2)
            e_prio = tk.Entry(frame_table, width=10, justify="center")
            e_prio.grid(row=row_idx, column=3)
            
            self.entry_processes.append({
                "id": f"P{i+1}", 
                "llegada": e_arr, 
                "rafaga": e_bur, 
                "prioridad": e_prio
            })
            
        tk.Button(frame_table, text="Calcular Algoritmos", bg="#2196F3", fg="white", font=("Arial", 11, "bold"), command=self.process_data).grid(row=self.num_processes+3, column=0, columnspan=4, pady=20)
        tk.Button(frame_table, text="Volver", command=self.create_welcome_screen).grid(row=self.num_processes+4, column=0, columnspan=4)

    def process_data(self):
        raw_data = []
        try:
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
                    "original_idx": i
                })
            
            # --- AQUÍ OCURRE LA MAGIA: CALCULAMOS TODO ANTES DE MOSTRAR ---
            self.calculate_all_algorithms(raw_data)
            
            # Iniciamos mostrando el primero (FIFO)
            self.current_alg_index = 0
            self.show_results_screen()
            
        except ValueError:
            messagebox.showerror("Error", "Asegúrese de que todos los campos sean números enteros.")

    # ==========================================
    # LÓGICA DE ALGORITMOS (BACKEND)
    # ==========================================
    def calculate_all_algorithms(self, data):
        self.results = {}
        
        # 1. FIFO
        self.results["FIFO"] = self.solve_fifo(copy.deepcopy(data))
        
        # 2. SJF (Shortest Job First - Non Preemptive)
        self.results["SJF"] = self.solve_sjf(copy.deepcopy(data))
        
        # Aquí añadirías RR o Prioridad en el futuro...

    def solve_fifo(self, data):
        # Ordenar por llegada
        data.sort(key=lambda x: x['llegada'])
        
        current_time = 0
        schedule = []
        
        for p in data:
            start = max(current_time, p['llegada'])
            end = start + p['rafaga']
            
            # Cálculos de métricas
            wait_time = start - p['llegada']
            sys_time = end - p['llegada']
            
            schedule.append({
                "id": p['id'],
                "start": start,
                "end": end,
                "llegada": p['llegada'], # Guardamos para mostrar en tabla
                "rafaga": p['rafaga'],
                "prioridad": p['prioridad'],
                "wait": wait_time,
                "system": sys_time,
                "color": self.colors[p['original_idx'] % len(self.colors)]
            })
            current_time = end
            
        return schedule

    def solve_sjf(self, data):
        # Algoritmo SJF (No expropiativo)
        # 1. Ordenar inicialmente por llegada para facilitar la búsqueda
        data.sort(key=lambda x: x['llegada'])
        
        current_time = 0
        completed = []
        schedule = []
        n = len(data)
        
        while len(completed) < n:
            # Buscar procesos que ya llegaron y no están completados
            available = [p for p in data if p['llegada'] <= current_time and p not in completed]
            
            if not available:
                # Si nadie ha llegado, saltar el tiempo al próximo que llega
                # (Buscamos el mínimo tiempo de llegada de los que faltan)
                remaining = [p for p in data if p not in completed]
                current_time = min(remaining, key=lambda x: x['llegada'])['llegada']
                continue
            
            # De los disponibles, elegir el de MENOR RÁFAGA (Shortest Job)
            shortest = min(available, key=lambda x: x['rafaga'])
            
            start = current_time
            end = start + shortest['rafaga']
            
            # Métricas
            wait_time = start - shortest['llegada']
            sys_time = end - shortest['llegada']
            
            schedule.append({
                "id": shortest['id'],
                "start": start,
                "end": end,
                "llegada": shortest['llegada'],
                "rafaga": shortest['rafaga'],
                "prioridad": shortest['prioridad'],
                "wait": wait_time,
                "system": sys_time,
                "color": self.colors[shortest['original_idx'] % len(self.colors)]
            })
            
            current_time = end
            completed.append(shortest)
            
        return schedule

    # ==========================================
    # VISTA DE RESULTADOS (FRONTEND)
    # ==========================================
    def show_results_screen(self):
        self._clear_screen()
        
        # Obtener datos del algoritmo actual
        alg_name = self.algorithm_list[self.current_alg_index]
        schedule_data = self.results[alg_name]
        
        # Contenedor Principal
        main_container = tk.Frame(self.root, padx=10, pady=10)
        main_container.pack(fill="both", expand=True)
        
        # Título
        header_frame = tk.Frame(main_container)
        header_frame.pack(fill="x", pady=5)
        tk.Label(header_frame, text=f"Algoritmo: {alg_name}", font=("Arial", 18, "bold")).pack()
        
        content_frame = tk.Frame(main_container)
        content_frame.pack(fill="both", expand=True)

        # === IZQUIERDA: DATOS + MÉTRICAS CALCULADAS ===
        left_frame = tk.Frame(content_frame, bd=2, relief="groove", padx=5, pady=5)
        left_frame.pack(side="left", fill="y", padx=10)
        
        tk.Label(left_frame, text="Métricas Calculadas", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Encabezados
        h_frame = tk.Frame(left_frame)
        h_frame.pack()
        # Añadimos W (Espera) y S (Sistema)
        cols = ["ID", "Lleg", "Ráf", "Esp(TE)", "Sis(TS)"]
        for c in cols:
            tk.Label(h_frame, text=c, width=6, font=("Arial", 9, "bold"), bg="#eee", relief="ridge").pack(side="left")
            
        rows_frame = tk.Frame(left_frame)
        rows_frame.pack()
        
        avg_wait = 0
        avg_sys = 0
        
        for item in schedule_data:
            r = tk.Frame(rows_frame)
            r.pack(pady=1)
            tk.Label(r, text=item['id'], width=6, bg=item['color']).pack(side="left")
            tk.Label(r, text=item['llegada'], width=6).pack(side="left")
            tk.Label(r, text=item['rafaga'], width=6).pack(side="left")
            # Mostramos los cálculos
            tk.Label(r, text=item['wait'], width=6, font=("Arial", 9, "bold"), fg="#D32F2F").pack(side="left")
            tk.Label(r, text=item['system'], width=6, font=("Arial", 9, "bold"), fg="#1976D2").pack(side="left")
            
            avg_wait += item['wait']
            avg_sys += item['system']
            
        # Promedios
        avg_wait /= len(schedule_data)
        avg_sys /= len(schedule_data)
        
        tk.Label(left_frame, text="-----------------").pack()
        tk.Label(left_frame, text=f"Promedio Espera: {avg_wait:.2f}").pack()
        tk.Label(left_frame, text=f"Promedio Sistema: {avg_sys:.2f}").pack()

        # === DERECHA: GANTT ESCALONADO ===
        right_frame = tk.Frame(content_frame, bd=2, relief="groove", padx=5, pady=5)
        right_frame.pack(side="left", fill="both", expand=True)
        
        tk.Label(right_frame, text="Diagrama de Gantt", font=("Arial", 12, "bold")).pack(pady=5)
        
        row_height = 40
        top_margin = 30
        bottom_margin = 40
        total_canvas_height = (len(schedule_data) * row_height) + top_margin + bottom_margin
        
        canvas = tk.Canvas(right_frame, bg="white", height=total_canvas_height)
        canvas.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.root.update_idletasks()
        c_width = canvas.winfo_width()
        if c_width <= 50: c_width = 400
        
        total_time = schedule_data[-1]['end'] if schedule_data else 1
        scale = (c_width - 60) / total_time
        
        for i, item in enumerate(schedule_data):
            x0 = 30 + (item['start'] * scale)
            x1 = 30 + (item['end'] * scale)
            y0 = top_margin + (i * row_height)
            y1 = y0 + 30
            
            # Líneas guía
            canvas.create_line(x0, top_margin, x0, total_canvas_height - 20, fill="#e0e0e0", dash=(2, 2))
            canvas.create_line(x1, top_margin, x1, total_canvas_height - 20, fill="#e0e0e0", dash=(2, 2))
            
            # Barra
            canvas.create_rectangle(x0, y0, x1, y1, fill=item['color'], outline="black")
            canvas.create_text((x0 + x1)/2, (y0 + y1)/2, text=item['id'], font=("Arial", 9, "bold"))
            
            # Eje X
            canvas.create_text(x0, total_canvas_height - 10, text=str(item['start']), font=("Arial", 8))
            canvas.create_text(x1, total_canvas_height - 10, text=str(item['end']), font=("Arial", 8))

        canvas.create_line(30, total_canvas_height - 25, c_width - 30, total_canvas_height - 25, width=2)

        # === NAVEGACIÓN ===
        nav_frame = tk.Frame(main_container)
        nav_frame.pack(side="bottom", pady=20)
        
        btn_prev = tk.Button(nav_frame, text="< Datos", width=15, command=self.create_table_screen)
        btn_prev.pack(side="left", padx=10)
        
        # Lógica del botón siguiente
        is_last = self.current_alg_index == len(self.algorithm_list) - 1
        btn_text = "Ver Comparativa >" if is_last else "Siguiente Algoritmo >"
        btn_cmd = self.show_comparison if is_last else self.next_algorithm
        
        btn_next = tk.Button(nav_frame, text=btn_text, width=20, bg="#2196F3", fg="white", command=btn_cmd)
        btn_next.pack(side="left", padx=10)

    def next_algorithm(self):
        self.current_alg_index += 1
        self.show_results_screen()

    def show_comparison(self):
        messagebox.showinfo("Info", "¡Aquí implementaremos la tabla comparativa final en el siguiente paso!")
        # Aquí crearías la pantalla final con self.results['FIFO'] y self.results['SJF']

    def _clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = DispatchApp(root)
    root.mainloop()