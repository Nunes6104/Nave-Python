"""
Projeto Final - Nave Online
Autores: João Nunes nº: 2023164
Cadeira: Programação IV
"""

#Bibliotecas de GUI e de acessos a API
import tkinter as tk
import random
import requests
import threading
from tkinter import messagebox

# Variáveis globais
altura = 600
largura = 800
nivel = 1
pontos = 0
planetas = []
velocidadePlanetas = 7
planetaNome = "Loading..."
nave = "🚀"
canvas = None
root = None
start = True

# arrays para as cores do texto do nivel, os emojis que aparecem na tela e as cores do bg na tela
coresPlanetas = ["white", "yellow", "orange", "lightblue", "lightgreen", "violet"]
emojisPlanetas = ["🪐", "🌕", "🌑", "🛸", "☄️", "🌞", "🌟", "🌠", "🌍"]
coresFundo = ["darkblue", "darkgreen", "darkred", "purple4", "midnightblue"]

# elementos visuais onde fica o texto
textoPontos = None
textoNivel = None
textoPlaneta = None

#função que permite acabar o jogo e fechar o programa
def sairDoJogo():
    #menu para confirmar exit
    if messagebox.askokcancel("Sair", "Deseja realmente sair do jogo?"):
        root.destroy()
#menu de pause e start do jogo
def startPauseJogo():
    global start
    if start == True:
        start = False
        if messagebox.showinfo("Jogo Pausado", "Pressione novamente para retomar"):
            start = True
            movePlanetas()
            verificarColisoes()                 
    else:
        start = True
#função principal quando o jogo é iniciado
def iniciarJogo():
    global root, canvas, nave, textoPontos, textoNivel, textoPlaneta, start
    #adicionar recursos à tela
    root = tk.Tk()
    root.title(f"Nave Online - Nível {nivel}")
    
    # Configuração do canvas
    canvas = tk.Canvas(root, width=largura, height=altura, bg=coresFundo[0])
    canvas.pack()
    menubar = tk.Menu(root)
    # Menu Game
    game_menu = tk.Menu(menubar, tearoff=0)
    game_menu.add_command(label="Start/Pause", command=startPauseJogo)
    game_menu.add_separator()
    game_menu.add_command(label="Exit", command=sairDoJogo)
    menubar.add_cascade(label="Game", menu=game_menu)
    root.config(menu=menubar)
    #para quando o jogo está em pause os objetos não correrem
    if start is not True:
        return
    else:
        # posicionar a nave no meio da tela
        nave = canvas.create_text(
            altura // 2,
            largura - 500,
            font=("Arial", 30),
            text= "🚀"
        )
        
        # Elementos de texto
        textoPontos = canvas.create_text(
            100, 30, text=f"Pontos: {pontos}", 
            font=("Arial", 16), fill="white"
        )
        textoNivel = canvas.create_text(
            largura - 100, 30, text=f"Nível: {nivel}", 
            font=("Arial", 16), fill="white"
        )
        textoPlaneta = canvas.create_text(
            largura //2, 30, text=f"Planeta: {planetaNome}", 
            font=("Arial", 16), fill="white"
        )
        
        # key binds para movimentar a nave para cima ou baixo e colocar no menu pause ou start e sair do jogo
        root.bind("<Up>", moveNave)
        root.bind("<Down>", moveNave)
        root.bind("<Escape>", lambda e: startPauseJogo())
        # Iniciar threads para o jogo e API dependendo do start ou pause para controlar o mapa
        criarPlaneta()
        movePlanetas()
        verificarColisoes()
        nomePlaneta()
        root.mainloop()
#funçao para receber os parametros do root bind e mover a nave na tela
def moveNave(event):
    global nave, start
    #método para decobrir as coordenadas da nave
    _, y = canvas.coords(nave)
    #só em caso do jogo estar ativo é possível mover a nave
    if start == True:
        if event.keysym == "Up" and y > 50:
            canvas.move(nave, 0, -20)
        elif event.keysym == "Down" and y < altura - 50:
            canvas.move(nave, 0, 20)
#função para criar elementos aleatórios dos planetas
def criarPlaneta():
    global planetas, nivel, start
    
    tamanho = random.randint(30, 60)
    y = random.randint(tamanho, altura - tamanho)
    
    # Seleciona emoji e cor baseado no nível
    emoji = emojisPlanetas[nivel % len(emojisPlanetas)]
    cor = coresPlanetas[(nivel - 1) % len(coresPlanetas)]
    
    planeta = canvas.create_text(
        largura + tamanho, y, 
        text=emoji, 
        font=("Arial", tamanho), 
        fill=cor,
        tags="planeta"
    )
    #carrega o planeta na tela
    planetas.append(planeta)

    # Agenda a criação do próximo planeta
    intervalo = max(1000, 3000 - nivel * 100)
    root.after(intervalo, criarPlaneta)
#movimentação dos planetas da direita para a esquerda
def movePlanetas():
    global planetas, velocidadePlanetas, start
    #só move os planetas caso o jogo esteja a correr
    if start == True:
        for planeta in planetas[:]:
            canvas.move(planeta, - velocidadePlanetas, 0)
            x, y = canvas.coords(planeta)
            # Remove planetas que saíram da tela
            if x < -50:
                canvas.delete(planeta)
                planetas.remove(planeta)
        # Continua movendo os planetas
        root.after(50, movePlanetas)
#para adicionar os pontos e mudar o nivel
def verificarColisoes():
    global pontos, nivel, planetas, textoPontos, nave
    #método para encontrar coordenadas da nave
    naveX, naveY = canvas.coords(nave)
    if start == True:
        for planeta in planetas[:]:
            planetaX, planetaY = canvas.coords(planeta)
            planeta_raio = int(canvas.itemcget(planeta, "font").split()[-1])
            
            # Verifica colisão simples (distância entre centros)
            distancia = ((naveX - planetaX)**2 + (naveY - planetaY)**2)**0.5
            if distancia < planeta_raio + 20:  # 20 é o raio aproximado da nave
                pontos += 1
                canvas.delete(planeta)
                planetas.remove(planeta)
                # Atualiza pontuação
                canvas.itemconfig(textoPontos, text=f"Pontos: {pontos}")
                # Verifica se mudou de nível
                if pontos % 10 == 0:
                    mudarNivel()
        # Continua verificando colisões
        root.after(100, verificarColisoes)
#mudar de nível
def mudarNivel():
    global nivel, velocidadePlanetas, planetas, textoNivel, planetaNome, textoPlaneta
    
    nivel += 1
    velocidadePlanetas += 0.1
    
    # Atualiza informações do nível
    canvas.itemconfig(textoNivel, text=f"Nível: {nivel}")
    root.title(f"Nave Online - Nível {nivel}")
    
    # Muda o fundo
    nova_cor = coresFundo[(nivel - 1) % len(coresFundo)]
    canvas.config(bg=nova_cor)
    
    # Limpa planetas do nível anterior
    for planeta in planetas[:]:
        canvas.delete(planeta)
        planetas.remove(planeta)
    
    # Procura o novo nome de planeta
    criarPlaneta()
    movePlanetas()
    nomePlaneta()
    verificarColisoes()

def nomePlaneta():
    # API NASA para encontrar o nome do planeta
    global planetaNome, textoPlaneta, nivel

    def tarefa():
        try: 
            url = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select+pl_name+from+ps+where+pl_name+is+not+null&format=json"
            
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list) and len(data) > nivel:
                planetaNome = data[nivel]['pl_name']
            else:     
                planetaNome= "Desconhecido"
                
        except Exception as e:
            print(f"Erro ao acessar API: {e}")
            planetaNome = "API Indisponível - Modo Offline"
        
        def atualizarCanvas():
            canvas.itemconfig(textoPlaneta, text=f"Planeta: {planetaNome}")

        # Usar o método `after()` para garantir que o Tkinter atualiza corretamente
        canvas.after(0, atualizarCanvas)

    # Iniciar a thread para executar a tarefa
    thread = threading.Thread(target=tarefa)
    thread.start()

iniciarJogo()