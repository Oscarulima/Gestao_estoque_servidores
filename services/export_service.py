import csv
from tkinter import filedialog, messagebox

def exportar_para_csv(db_manager):
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        
        # Puxa todos os servidores cadastrados
        cursor.execute("""
            SELECT id, serial_number, marca, modelo, fator_forma, qtd_baias, 
                   tipo_slot, tem_trilho, tem_bezel, modulo_gerenciamento, observacoes
            FROM servidores ORDER BY id DESC
        """)
        servidores = cursor.fetchall()

        if not servidores:
            messagebox.showwarning("Aviso", "Não há dados cadastrados para exportar!")
            return

        linhas_exportacao = []

        for serv in servidores:
            servidor_id = serv[0]
            sn = serv[1]
            marca = serv[2]
            modelo = serv[3]
            fator = serv[4] or ""
            baias = serv[5] or ""
            
            # Monta o nome completo do Server (Ex: ThinkSystem SR630 V2 8x 2.5")
            nome_server = f"{marca} {modelo} {baias} {fator}".strip()

            # 1. Cabeçalho do Bloco do Servidor (Igual ao seu modelo)
            linhas_exportacao.append(["SN", "Server", ""])
            linhas_exportacao.append([sn, nome_server, ""])
            
            # 2. Cabeçalho das Peças
            linhas_exportacao.append(["PN", "Descrição", "QTD"])

            # 3. Puxa todas as peças cadastradas para este servidor
            cursor.execute("""
                SELECT part_number, tipo_componente, detalhes_extras, quantidade
                FROM componentes WHERE servidor_id = ?
            """, (servidor_id,))
            componentes = cursor.fetchall()

            if componentes:
                for comp in componentes:
                    pn = comp[0] or ""
                    tipo = comp[1] or ""
                    detalhes = comp[2] or ""
                    qtd = comp[3] or "1"

                    # Monta a descrição unindo Tipo e Detalhes
                    if detalhes:
                        descricao = f"{tipo} - {detalhes}"
                    else:
                        descricao = tipo

                    linhas_exportacao.append([pn, descricao, qtd])
            else:
                linhas_exportacao.append(["N/A", "Nenhum componente cadastrado", "0"])

            # Adiciona uma linha em branco entre um servidor e outro para separar no Excel
            linhas_exportacao.append(["", "", ""])

    # Seleciona onde salvar o arquivo
    caminho_arquivo = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("Arquivos CSV", "*.csv")],
        title="Salvar Relatório de Estoque"
    )

    if caminho_arquivo:
        with open(caminho_arquivo, mode="w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerows(linhas_exportacao)

        messagebox.showinfo("Sucesso", "Relatório exportado no modelo exato da sua planilha!")