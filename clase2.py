import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random

class SistemaPrescripcion:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion de medicamentos")
        self.root.geometry("900x700")

        self.create_widgets()
        self.medications = []
        self.medication_info = {
            "Acetaminofén": "Analgésico y antipirético usado para aliviar el dolor leve a moderado y reducir la fiebre. Actúa inhibiendo la producción de prostaglandinas en el sistema nervioso central.",
            "Ibuprofeno": "Antiinflamatorio no esteroideo (AINE) que reduce el dolor, la fiebre y la inflamación. Funciona inhibiendo la producción de prostaglandinas en todo el cuerpo.",
            "Amoxicilina": "Antibiótico de amplio espectro de la familia de las penicilinas. Se usa para tratar una variedad de infecciones bacterianas interfiriendo con la síntesis de la pared celular bacteriana.",
            "Omeprazol": "Inhibidor de la bomba de protones que reduce la producción de ácido en el estómago. Se usa para tratar úlceras, reflujo gastroesofágico y otras condiciones relacionadas con el exceso de ácido estomacal.",
            "Loratadina": "Antihistamínico de segunda generación usado para aliviar los síntomas de alergias como estornudos, picazón y secreción nasal. Actúa bloqueando la acción de la histamina en el cuerpo."
        }
        self.notification_thread = None
        self.stop_thread = threading.Event()

    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Formulario
        form_frame = ttk.LabelFrame(main_frame, text="Datos del Paciente y Medicamento", padding="10")
        form_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        labels = ["Nombre del usuario:", "Edad del usuario:", "Peso:", "Medicamento:", "Dosis:", "Frecuencia (horas):", "Días:", "Hora de inicio (HH:MM):", "Información del medicamento:"]
        self.entries = {}

        for i, label in enumerate(labels):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            if label == "Información del medicamento:":
                self.entries[label] = tk.Text(form_frame, height=3, width=30, wrap=tk.WORD)
                self.entries[label].grid(row=i, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
            else:
                self.entries[label] = ttk.Entry(form_frame)
                self.entries[label].grid(row=i, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)

        # Vincular el evento de cambio en el campo de medicamento
        self.entries["Medicamento:"].bind('<KeyRelease>', self.update_medication_info)

        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

        ttk.Button(button_frame, text="Añadir Medicamento", command=self.add_medication).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Modificar", command=self.modify_medication).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Eliminar", command=self.delete_medication).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Iniciar Notificaciones", command=self.start_notifications).grid(row=0, column=3, padx=5)
        ttk.Button(button_frame, text="Generar Gráfica Semanal", command=self.generate_weekly_graph).grid(row=0, column=4, padx=5)

        # Tabla de medicamentos
        self.tree = ttk.Treeview(main_frame, columns=tuple(labels[:-1]), show='headings')
        self.tree.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        for label in labels[:-1]:
            self.tree.heading(label, text=label)
            self.tree.column(label, width=100)

        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=2, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Área de información del medicamento
        info_frame = ttk.LabelFrame(main_frame, text="Información del Medicamento", padding="10")
        info_frame.grid(row=0, column=2, rowspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        self.info_text = tk.Text(info_frame, wrap=tk.WORD, width=30, height=15)
        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.info_text.config(state=tk.DISABLED)

        # Configurar el peso de las filas y columnas
        main_frame.columnconfigure(0, weight=3)
        main_frame.columnconfigure(2, weight=1)
        main_frame.rowconfigure(2, weight=1)
        info_frame.columnconfigure(0, weight=1)
        info_frame.rowconfigure(0, weight=1)

    def update_medication_info(self, event=None):
        medication = self.entries["Medicamento:"].get().capitalize()
        if medication in self.medication_info:
            self.entries["Información del medicamento:"].delete("1.0", tk.END)
            self.entries["Información del medicamento:"].insert(tk.END, self.medication_info[medication])

    def add_medication(self):
        values = [self.entries[label].get() for label in self.entries if label != "Información del medicamento:"]
        info = self.entries["Información del medicamento:"].get("1.0", tk.END).strip()
        if all(values) and info:
            self.tree.insert('', tk.END, values=values)
            self.medications.append(values + [info])
            self.clear_entries()
        else:
            messagebox.showwarning("Datos incompletos", "Por favor, rellene todos los campos.")

    def modify_medication(self):
        selected_item = self.tree.selection()
        if selected_item:
            values = [self.entries[label].get() for label in self.entries if label != "Información del medicamento:"]
            info = self.entries["Información del medicamento:"].get("1.0", tk.END).strip()
            if all(values) and info:
                self.tree.item(selected_item, values=values)
                index = self.tree.index(selected_item)
                self.medications[index] = values + [info]
                self.clear_entries()
            else:
                messagebox.showwarning("Datos incompletos", "Por favor, rellene todos los campos.")
        else:
            messagebox.showwarning("Selección requerida", "Por favor, seleccione un medicamento para modificar.")

    def delete_medication(self):
        selected_item = self.tree.selection()
        if selected_item:
            index = self.tree.index(selected_item)
            self.tree.delete(selected_item)
            del self.medications[index]
            self.clear_entries()
            self.clear_info()
        else:
            messagebox.showwarning("Selección requerida", "Por favor, seleccione un medicamento para eliminar.")

    def on_tree_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            index = self.tree.index(selected_item)
            values = self.medications[index]
            for label, value in zip(self.entries, values[:-1]):
                if label != "Información del medicamento:":
                    self.entries[label].delete(0, tk.END)
                    self.entries[label].insert(0, value)
            self.entries["Información del medicamento:"].delete("1.0", tk.END)
            self.entries["Información del medicamento:"].insert(tk.END, values[-1])
            self.update_info(values)

    def clear_entries(self):
        for label, entry in self.entries.items():
            if label != "Información del medicamento:":
                entry.delete(0, tk.END)
            else:
                entry.delete("1.0", tk.END)

    def clear_info(self):
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.config(state=tk.DISABLED)

    def update_info(self, values):
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        info = f"Nombre: {values[0]}\n"
        info += f"Medicamento: {values[3]}\n"
        info += f"Dosis: {values[4]}\n"
        info += f"Frecuencia: {values[5]} horas\n"
        info += f"Hora de inicio: {values[7]}\n\n"
        info += f"Información adicional:\n{values[-1]}"
        self.info_text.insert(tk.END, info)
        self.info_text.config(state=tk.DISABLED)

    def start_notifications(self):
        if self.notification_thread is None or not self.notification_thread.is_alive():
            self.stop_thread.clear()
            self.notification_thread = threading.Thread(target=self.notification_loop)
            self.notification_thread.start()
            messagebox.showinfo("Notificaciones", "Las notificaciones han sido iniciadas.")
        else:
            messagebox.showinfo("Notificaciones", "Las notificaciones ya están en ejecución.")

    def notification_loop(self):
        while not self.stop_thread.is_set():
            current_time = datetime.now()
            for medication in self.medications:
                name, _, _, med_name, dose, frequency, _, start_time, _ = medication
                start_datetime = datetime.combine(current_time.date(), datetime.strptime(start_time, "%H:%M").time())
                
                if start_datetime <= current_time:
                    time_diff = (current_time - start_datetime).total_seconds() / 3600
                    if time_diff % float(frequency) < 1:  # Si ha pasado un múltiplo de la frecuencia (con 1 hora de margen)
                        self.show_notification(name, med_name, dose)
            
            time.sleep(60)  # Esperar 1 minuto antes de la próxima verificación

    def show_notification(self, name, medication, dose):
        message = f"¡Es hora de que {name} tome su medicamento!\nMedicamento: {medication}\nDosis: {dose}"
        self.root.after(0, lambda: messagebox.showinfo("Recordatorio de medicamento", message))

    def generate_weekly_graph(self):
        # Crear una nueva ventana para la gráfica
        graph_window = tk.Toplevel(self.root)
        graph_window.title("Gráfica Semanal de Medicamentos")
        graph_window.geometry("800x600")

        # Simular datos de medicamentos tomados para una semana
        days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        medications = [med[3] for med in self.medications]  # Obtener nombres de medicamentos
        data = {med: [random.randint(0, 3) for _ in range(7)] for med in medications}

        # Crear la gráfica
        fig, ax = plt.subplots(figsize=(10, 6))
        bottom = [0] * 7
        for medication, counts in data.items():
            ax.bar(days, counts, label=medication, bottom=bottom)
            bottom = [b + c for b, c in zip(bottom, counts)]

        ax.set_title('Medicamentos Tomados por Día')
        ax.set_xlabel('Día de la Semana')
        ax.set_ylabel('Número de Dosis')
        ax.legend()

        # Mostrar la gráfica en la ventana de Tkinter
        canvas = FigureCanvasTkAgg(fig, master=graph_window)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def on_closing(self):
        self.stop_thread.set()
        if self.notification_thread:
            self.notification_thread.join()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SistemaPrescripcion(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()