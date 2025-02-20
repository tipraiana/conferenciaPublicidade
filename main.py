from PIL import Image
import os
import math
import smtplib
import ssl
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def log(mensagem, logs):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f'[{timestamp}] {mensagem}'
    print(log_entry)
    logs.append(log_entry)

def enviar_email(logs, arquivos):
    remetente = "praiana.ti@gmail.com"  # Substituir pelo seu e-mail
    senha = "ettllvahhhsvspdu"  # Substituir pela senha ou app password
    destinatarios = ["praiana.ti@gmail.com", "claudia@praiana.com.br"]  # Defina os destinatários

    assunto = "Relatório de Colagem de Fotos"
    corpo_email = "Segue em anexo o relatório de colagem de fotos.\n\n" + "\n".join(logs)

    # Criando e-mail com anexo
    msg = MIMEMultipart()
    msg["From"] = remetente
    msg["To"] = ", ".join(destinatarios)
    msg["Subject"] = assunto

    # Adicionando o corpo do e-mail
    msg.attach(MIMEText(corpo_email, "plain", "utf-8"))

    # Adicionando os anexos
    for arquivo in arquivos:
        if os.path.exists(arquivo):  # Verifica se o arquivo realmente existe
            with open(arquivo, "rb") as anexo:
                parte = MIMEBase("application", "octet-stream")
                parte.set_payload(anexo.read())
                encoders.encode_base64(parte)
                parte.add_header("Content-Disposition", f"attachment; filename={os.path.basename(arquivo)}")
                msg.attach(parte)

    # Enviando o e-mail
    contexto = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=contexto) as server:
            server.login(remetente, senha)
            server.sendmail(remetente, destinatarios, msg.as_string())
        log("E-mail enviado com sucesso!", logs)
    except Exception as e:
        log(f"Erro ao enviar e-mail: {e}", logs)

def criar_colagem(pasta_imagens, pasta_saida, fotos_por_folha=16, cols=4, rows=4, largura_a4=3508, altura_a4=2480, margem=10):
    logs = []
    imagens = [os.path.join(pasta_imagens, img) for img in os.listdir(pasta_imagens) if img.lower().endswith(('png', 'jpg', 'jpeg'))]
    imagens.sort()
    
    if not os.path.exists(pasta_saida):
        os.makedirs(pasta_saida)
    
    num_folhas = math.ceil(len(imagens) / fotos_por_folha)
    largura_foto = (largura_a4 - (margem * (cols + 1))) // cols
    altura_foto = (altura_a4 - (margem * (rows + 1))) // rows
    
    log(f'Iniciando colagem para {len(imagens)} imagens.', logs)
    arquivos_gerados = []
    
    for i in range(num_folhas):
        imagens_folha = imagens[i * fotos_por_folha:(i + 1) * fotos_por_folha]
        
        colagem = Image.new('RGB', (largura_a4, altura_a4), 'white')
        
        for idx, img_path in enumerate(imagens_folha):
            img = Image.open(img_path)
            img = img.resize((largura_foto, altura_foto), Image.LANCZOS)
            
            x = margem + (idx % cols) * (largura_foto + margem)
            y = margem + (idx // cols) * (altura_foto + margem)
            
            colagem.paste(img, (x, y))
        
        caminho_saida = os.path.join(pasta_saida, f'colagem_{i+1}.jpg')
        colagem.save(caminho_saida, 'JPEG', quality=90)
        arquivos_gerados.append(caminho_saida)
        log(f'Colagem {i+1} salva em {caminho_saida}', logs)
    
    log('Processo concluído.', logs)
    enviar_email(logs, arquivos_gerados)
    messagebox.showinfo("Concluído", "A colagem foi gerada com sucesso e enviada por e-mail!")

def abrir_interface():
    def selecionar_origem():
        pasta = filedialog.askdirectory(title="Selecione a pasta de origem das imagens")
        if pasta:
            entrada_origem.set(pasta)
    
    def selecionar_destino():
        pasta = filedialog.askdirectory(title="Selecione a pasta de destino para as colagens")
        if pasta:
            entrada_destino.set(pasta)
    
    def iniciar_colagem():
        origem = entrada_origem.get()
        destino = entrada_destino.get()
        if origem and destino:
            criar_colagem(origem, destino)
        else:
            messagebox.showwarning("Aviso", "Preencha todos os campos antes de iniciar.")
    
    root = tk.Tk()
    root.title("Gerador de Colagem de Fotos")
    root.geometry("400x250")
    
    entrada_origem = tk.StringVar()
    entrada_destino = tk.StringVar()
    
    tk.Label(root, text="Pasta de Origem:").pack(pady=5)
    tk.Entry(root, textvariable=entrada_origem, width=50).pack()
    tk.Button(root, text="Selecionar", command=selecionar_origem).pack(pady=5)
    
    tk.Label(root, text="Pasta de Destino:").pack(pady=5)
    tk.Entry(root, textvariable=entrada_destino, width=50).pack()
    tk.Button(root, text="Selecionar", command=selecionar_destino).pack(pady=5)
    
    tk.Button(root, text="Gerar Colagem", command=iniciar_colagem).pack(pady=20)
    
    root.mainloop()

# Para executar com interface:
abrir_interface()

#teste commit
