import csv
from tkinter import filedialog, messagebox

def exportar_para_csv(db_manager):
    dados = db_manager.obter_todos_dados_para_exportar()
    if not dados:
        messagebox.showwarning("Aviso", "Não há dados cadastrados para exportar!")
        return

    caminho_arquivo = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("Arquivos CSV", "*.csv")],
        title="Salvar Relatório de Estoque"
    )

    if caminho_arquivo:
        headers = [
            "Serial Number", "Marca", "Modelo", "Fator de Forma", "Tipo de Slot", 
            "Tem Trilho", "Observações", "Tipo Componente", "Part Number (PN)", 
            "Quantidade", "Detalhes Extras"
        ]
        
        with open(caminho_arquivo, mode="w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(headers)
            writer.writerows(dados)

        messagebox.showinfo("Sucesso", "Exportação para CSV concluída com sucesso!")