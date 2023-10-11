import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import filedialog, IntVar, ttk
from tkinter import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import math

janela = Tk()  
janela.title("Data Reader")
janela.geometry("1920x1080")

math_window = None
resultado_canal_mat = None

x = []
resultado_ativado = IntVar()
resultado_ativado.set(0)

resultado_do_canal = None  
nome_do_canal = StringVar()  

vertical_line = None

def abrirarq():
    global colors, df, sig, sig_vars, ax, x
    arquivo = [("Arquivos CSV", "*.csv")]
    filepath = filedialog.askopenfilename(filetypes=arquivo)

    if filepath:

        df = pd.read_csv(filepath, delimiter=';')
        sig = df.columns

        for i, s in enumerate(sig):
            sig_name = s
            sig_vars[sig_name] = IntVar()
            color = colors[i]
            sig_colors[sig_name] = color
            checkbox = Checkbutton(frame_checkbuttons, text=sig_name, variable=sig_vars[sig_name])
            checkbox.pack(anchor='w')

mouse_pressed = False

def grafico():
    global df, sig, sig_vars, colors, cursor_vertical_line, cursor_horizontal_line_left, cursor_horizontal_line_right, fig, ax, canvas, x, y, mouse_pressed, s

    ax.clear()

    selected_sigs = [sig for sig, var in sig_vars.items() if var.get() == 1]
    
    min_y = np.inf
    max_y = -np.inf
    
    for idx, s in enumerate(selected_sigs):
        y = df[s]
        x = df.iloc[:, 0]

        color = sig_colors[s]
        
        if idx == 0:
            ax.plot(x, y, label=s, color=color)
            ax.set_ylabel(s, color=color)
        else:
            ax1 = ax.twinx()
            ax1.spines['right'].set_position(('outward', 60 * (idx - 1)))
            ax1.plot(x, y, label=s, color=color)
            ax1.set_ylabel(s, color=color)

        ax.set_xlabel("tempo(s)")
        ax.legend(loc='upper left')
        
        min_y = min(min_y, np.min(y))
        max_y = max(max_y, np.max(y))
        
        ax.grid(True)

        canvas.draw()

    vertical_line, = ax.plot([], [], color='black', linestyle='-', linewidth=1)
    horizontal_line_left, = ax.plot([], [], color='black', linestyle='-', linewidth=1)
    horizontal_line_right, = ax.plot([], [], color='black', linestyle='-', linewidth=1)

    x_cursor = None
    y_cursor = None

    def atualizar_legenda_y(y_cursor, s):
        texto_legenda.delete(1.0, END)
        texto_legenda.insert(INSERT, f'Valor de {s}: {y_cursor:.2f}')
        
    def update_cursor(event):
        global x_cursor, y_cursor, mouse_pressed, s
            
        if mouse_pressed and event.inaxes:
            x_cursor = event.xdata
            y_cursor = np.interp(x_cursor, x, y)

            vertical_line.set_data([x_cursor, x_cursor], [min_y, max_y])
            
            y_ax = np.interp(x_cursor, x, ax.get_lines()[0].get_ydata())
            horizontal_line_left.set_data([x_cursor - 4, x_cursor], [y_ax, y_ax])
            horizontal_line_right.set_data([x_cursor, x_cursor + 4], [y_ax, y_ax])

            atualizar_legenda_y(y_cursor, s)
            
            fig.canvas.draw()

    def mouse_press(event):
        global mouse_pressed, x_cursor, y_cursor
        if event.button == 1:
            mouse_pressed = True
            x_cursor = event.xdata
            y_cursor = np.interp(x_cursor, x, y)

            vertical_line.set_data([x_cursor, x_cursor], [min_y, max_y])

            y_ax = np.interp(x_cursor, x, ax.get_lines()[0].get_ydata())
            horizontal_line_left.set_data([x_cursor - 4, x_cursor], [y_ax, y_ax])
            horizontal_line_right.set_data([x_cursor, x_cursor + 4], [y_ax, y_ax])

            fig.canvas.draw()

    def mouse_release(event):
        global mouse_pressed
        if event.button == 1:
            mouse_pressed = False

    fig.canvas.mpl_connect('motion_notify_event', update_cursor)
    fig.canvas.mpl_connect('button_press_event', mouse_press)
    fig.canvas.mpl_connect('button_release_event', mouse_release)

    fig.canvas.mpl_connect('scroll_event', on_mouse_scroll)

def on_mouse_scroll(event):
    global ax

    if event.inaxes:
        x_min, x_max = ax.get_xlim()
        x_cursor = event.xdata

        zoom_factor = 1.2 if event.step < 0 else 0.8
        x_new_min = x_cursor - (x_cursor - x_min) * zoom_factor
        x_new_max = x_cursor + (x_max - x_cursor) * zoom_factor

        ax.set_xlim(x_new_min, x_new_max)
        ax.figure.canvas.draw()
        
def limparselecao():
    for var in sig_vars.values():
        var.set(0)
    for ax1 in ax.figure.get_axes():
        if ax1 != ax:
            ax.figure.delaxes(ax1)
    
    ax.set_ylabel('')  
    canvas.draw()

#####################################INICIO CODIGO CANAL MATEMATICO##################################################

def canal_mat():
    global x, resultado_canal_mat, df, sig, sig_vars

    janela_canal_mat = tk.Toplevel()
    janela_canal_mat.title("Maths")
    janela_canal_mat.geometry("400x300")
    t_label = Label(janela_canal_mat, text="Selecione os sensores:")
    t_label.pack(pady=2)

    sinais_combobox = ttk.Combobox(janela_canal_mat, values=list(sig), state="readonly")
    sinais_combobox.set("Selecione um sinal")
    sinais_combobox.pack(pady=10)

    sinais_combobox2 = ttk.Combobox(janela_canal_mat, values=list(sig), state="readonly")
    sinais_combobox2.set("Selecione um sinal")
    sinais_combobox2.pack(pady=10)
    
    def atualizar_combobox2(event):
        selecionado = sinais_combobox.get()
        if selecionado:
            outras_opcoes = [s for s in sig if s != selecionado]
            sinais_combobox2["values"] = outras_opcoes
            sinais_combobox2.set("Selecione um sensor")

    def calcular_operacao():
        global resultado_ativado, df, ax, nome_do_canal
        
        sinal1 = sinais_combobox.get()
        sinal2 = sinais_combobox2.get()
        operacao = operacao_combobox.get()

        if not sinal1 or not sinal2 or not operacao:
            resultado_label.config(text="Por favor, selecione um sinal e uma operação.")
            return

        try:
            if not df.empty:
                resultado = None
                if operacao == "Adição":
                    resultado = df[sinal1] + df[sinal2]
                elif operacao == "Subtração":
                    resultado = df[sinal1] - df[sinal2]
                elif operacao == "Multiplicação":
                    resultado = df[sinal1] * df[sinal2]
                elif operacao == "Divisão":
                    resultado = df[sinal1] / df[sinal2]
        
            resultado_label.config(text=f"Resultado da {operacao}: \n{resultado}")
        except Exception as e:
            resultado_label.config(text=f"Erro ao calcular a operação: {str(e)}")

        x = df.iloc[:, 0]

        if resultado_ativado.get() == 1:
            ax2 = ax.twinx()
            ax2.plot(x, resultado, label=f"{nome_do_canal.get()}", color='black')
            ax2.set_ylabel(f"{nome_do_canal.get()}", color='black')
            ax2.legend(loc='upper right')
            ax2.grid(True)
            canvas.draw()
    
    sinais_combobox.bind("<<ComboboxSelected>>", atualizar_combobox2)

    operacao_combobox = ttk.Combobox(janela_canal_mat, values=["Adição", "Subtração", "Multiplicação", "Divisão"], state="readonly")
    operacao_combobox.set("Selecione uma operação")
    operacao_combobox.pack(pady=10)

    nome_label = Label(janela_canal_mat, text="Nome do Canal Matemático:")
    nome_label.pack(pady=10)

    nome_entry = Entry(janela_canal_mat, textvariable=nome_do_canal)
    nome_entry.pack(pady=10)
    
    calcular_button = ttk.Button(janela_canal_mat, text="Calcular", command=calcular_operacao)
    calcular_button.pack(pady=10)

    resultado_label = ttk.Label(janela_canal_mat, text="")
    resultado_label.pack(pady=10)

resultado_checkbox = Checkbutton(janela, textvariable=nome_do_canal, variable=resultado_ativado)
resultado_checkbox.place(x=10, y=70) 

############################FINAL CODIGO CANAL MATEMATICO##############################################################

frame_checkbuttons = Frame(janela)
frame_checkbuttons.pack(side=LEFT, padx=30, pady=10)

texto_select = Label(frame_checkbuttons, text="SELECIONE OS SENSORES:")
texto_select.pack()

sig_vars = {}
sig_colors = {}  
colors = ['blue', 'red', 'green', 'purple', 'orange', 'brown', 'magenta', 'yellow', 'lime', 'pink', 'black', 'Aqua', 'Light Green', 'Light Aqua', 'Light Purple', 'Grey']

botao = tk.Button(janela, text="Abrir Arquivo CSV", command=abrirarq)
botao.place(x=10, y=10)

botao_limpar = tk.Button(janela, text="Limpar Seleção", command=limparselecao)
botao_limpar.place(x=120, y=10)

fig = Figure(figsize=(22, 7), dpi=100, facecolor='#f0f0f0')
ax = fig.add_subplot(111)

canvas = FigureCanvasTkAgg(fig, master=janela)
canvas.get_tk_widget().pack(padx=100, side=LEFT)

toolbar = NavigationToolbar2Tk(canvas, janela)
toolbar.update()
toolbar.place(x=230, y=1)

botao_math = tk.Button(janela, text="Canais Matemáticos", command=canal_mat)
botao_math.place (x=10,y=40) 

botao_graph = tk.Button(janela, text="plotar gráfico", command = grafico)
botao_graph.place (x=132, y=40)

texto_legenda = Text(canvas.get_tk_widget(), height=2, width=35)
texto_legenda.place(relx=0.65, rely=0.065)

janela.mainloop()
