import sqlite3
import customtkinter as ctk
from tkinter import messagebox, ttk
from database.db_manager import DBManager
from services.export_service import exportar_para_csv

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class AppEstoque(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestão e Cadastro de Servidores")
        self.geometry("1100x850")

        self.db = DBManager()
        self.servidor_em_edicao_id = None
        self.linhas_componentes = []

        # Sistema de Abas
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_cadastro = self.tabview.add("Cadastrar / Editar")
        self.tab_consulta = self.tabview.add("Consultar / Filtrar")

        self.setup_tab_cadastro()
        self.setup_tab_consulta()

        # Rola a tela automaticamente quando o cursor avança via teclado (Tab)
        self.bind_all("<FocusIn>", self.auto_scroll_ao_focar)

    # ==================== ABA 1: CADASTRO / EDIÇÃO ====================
    def setup_tab_cadastro(self):
        self.scroll_cad = ctk.CTkScrollableFrame(self.tab_cadastro)
        self.scroll_cad.pack(fill="both", expand=True, padx=5, pady=5)

        # Informações Principais
        ctk.CTkLabel(self.scroll_cad, text="Informações do Servidor", font=("Arial", 16, "bold")).pack(anchor="w", pady=(10, 5))

        self.txt_serial = self.add_field("Serial Number / Service Tag *")
        
        ctk.CTkLabel(self.scroll_cad, text="Marca *").pack(anchor="w", pady=(5, 0))
        self.combo_marca = ctk.CTkComboBox(
            self.scroll_cad, 
            values=["Lenovo", "Dell", "HPE", "IBM", "Supermicro", "Outro"], 
            command=self.aplicar_autofill_marca
        )
        self.combo_marca.pack(fill="x", pady=2)

        self.txt_modelo = self.add_field("Modelo (ex: x3650 M5, PowerEdge R740) *")

        # Fator de Forma e Quantidade de Baias
        frame_baias = ctk.CTkFrame(self.scroll_cad)
        frame_baias.pack(fill="x", pady=5)

        f1 = ctk.CTkFrame(frame_baias)
        f1.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkLabel(f1, text='Fator de Forma das Baias').pack(anchor="w")
        self.combo_fator = ctk.CTkComboBox(f1, values=['SFF 2.5"', 'LFF 3.5"', "Outro"])
        self.combo_fator.pack(fill="x", pady=2)

        f2 = ctk.CTkFrame(frame_baias)
        f2.pack(side="right", fill="x", expand=True, padx=5)
        ctk.CTkLabel(f2, text='Quantidade de Baias').pack(anchor="w")
        self.txt_qtd_baias = ctk.CTkEntry(f2, placeholder_text="ex: 8, 12, 24")
        self.txt_qtd_baias.pack(fill="x", pady=2)

        # Tipo de Slot / Backplane
        ctk.CTkLabel(self.scroll_cad, text="Tipo de Slot / Backplane").pack(anchor="w", pady=(5, 0))
        self.combo_slot = ctk.CTkComboBox(self.scroll_cad, values=["SAS/SATA", "SOMENTE SATA", "NVMe", "Baia Universal (SAS/SATA/NVMe)", "Outro"])
        self.combo_slot.pack(fill="x", pady=2)

        # Trilho e Bezel Lado a Lado
        frame_acessorios = ctk.CTkFrame(self.scroll_cad)
        frame_acessorios.pack(fill="x", pady=5)

        f_trilho = ctk.CTkFrame(frame_acessorios)
        f_trilho.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkLabel(f_trilho, text="Possui Trilho Deslizável?").pack(anchor="w")
        self.combo_trilho = ctk.CTkComboBox(f_trilho, values=["Sim", "Não"])
        self.combo_trilho.pack(fill="x", pady=2)

        f_bezel = ctk.CTkFrame(frame_acessorios)
        f_bezel.pack(side="right", fill="x", expand=True, padx=5)
        ctk.CTkLabel(f_bezel, text="Possui Bezel (Tampa Frontal)?").pack(anchor="w")
        self.combo_bezel = ctk.CTkComboBox(f_bezel, values=["Sim", "Não"])
        self.combo_bezel.pack(fill="x", pady=2)

        self.txt_mgmt = self.add_field("Módulo de Gerenciamento & Licença (ex: iDRAC Enterprise)")

        # Peças e Componentes Internos
        ctk.CTkLabel(self.scroll_cad, text="Peças e Componentes Internos", font=("Arial", 16, "bold")).pack(anchor="w", pady=(20, 5))

        self.frame_pecas = ctk.CTkFrame(self.scroll_cad)
        self.frame_pecas.pack(fill="x", pady=5)

        btn_add_peca = ctk.CTkButton(self.scroll_cad, text="+ Adicionar Peça Extra", command=self.adicionar_linha_componente, fg_color="gray")
        btn_add_peca.pack(anchor="w", pady=5)

        # Observações
        ctk.CTkLabel(self.scroll_cad, text="Observações (Avarias, detalhes físicos)").pack(anchor="w", pady=(10, 0))
        self.txt_obs = ctk.CTkTextbox(self.scroll_cad, height=70)
        self.txt_obs.pack(fill="x", pady=5)

        # Botões de Ação
        frame_acoes = ctk.CTkFrame(self.scroll_cad)
        frame_acoes.pack(fill="x", pady=20)

        self.btn_salvar = ctk.CTkButton(frame_acoes, text="Salvar Servidor", command=self.salvar_cadastro, fg_color="green")
        self.btn_salvar.pack(side="left", padx=5, expand=True)

        ctk.CTkButton(frame_acoes, text="Limpar Formulário", command=self.limpar_formularios, fg_color="orange").pack(side="left", padx=5, expand=True)
        ctk.CTkButton(frame_acoes, text="Exportar CSV", command=lambda: exportar_para_csv(self.db), fg_color="blue").pack(side="right", padx=5, expand=True)

        self.adicionar_componentes_padrao()

    def add_field(self, label_text):
        ctk.CTkLabel(self.scroll_cad, text=label_text).pack(anchor="w", pady=(5, 0))
        entry = ctk.CTkEntry(self.scroll_cad)
        entry.pack(fill="x", pady=2)
        return entry

    def aplicar_autofill_marca(self, marca_selecionada):
        sugestoes = {
            "Lenovo": "XClarity Controller (XCC) Enterprise",
            "Dell": "iDRAC9 Enterprise",
            "HPE": "iLO 5 Advanced",
            "IBM": "IMM2 Advanced"
        }
        if marca_selecionada in sugestoes and not self.txt_mgmt.get():
            self.txt_mgmt.insert(0, sugestoes[marca_selecionada])

    def adicionar_linha_componente(self, tipo="", qtd="1", pn="", desc=""):
        row = ctk.CTkFrame(self.frame_pecas)
        row.pack(fill="x", pady=2)

        txt_tipo = ctk.CTkEntry(row, placeholder_text="Nome da Peça", width=180)
        txt_tipo.insert(0, tipo)
        txt_tipo.pack(side="left", padx=2)

        txt_qtd = ctk.CTkEntry(row, placeholder_text="Qtd", width=50)
        txt_qtd.insert(0, str(qtd))
        txt_qtd.pack(side="left", padx=2)

        txt_pn = ctk.CTkEntry(row, placeholder_text="Part Number (PN)", width=160)
        txt_pn.insert(0, pn)
        txt_pn.pack(side="left", padx=2)

        txt_desc = ctk.CTkEntry(row, placeholder_text="Descrição / Detalhes", width=280)
        txt_desc.insert(0, desc)
        txt_desc.pack(side="left", padx=2, fill="x", expand=True)

        btn_remover = ctk.CTkButton(row, text="X", width=30, fg_color="red", command=lambda: self.remover_linha_componente(row))
        btn_remover.pack(side="right", padx=2)

        self.linhas_componentes.append({
            "frame": row, 
            "tipo": txt_tipo, 
            "qtd": txt_qtd, 
            "pn": txt_pn, 
            "desc": txt_desc
        })

    def remover_linha_componente(self, row_frame):
        self.linhas_componentes = [c for c in self.linhas_componentes if c["frame"] != row_frame]
        row_frame.destroy()

    def adicionar_componentes_padrao(self):
        pecas_padrao = [
            "Placa Mãe",
            "Heatsink / Dissipador",
            "Fans / Coolers",
            "Riser Cards",
            "Controladora RAID",
            "Bateria / Cache RAID",
            "Cabos RAID / Controladora",
            "Backplane",
            "Cabos do Backplane",
            "Placa de Rede",
            "Airflow / Duto"
        ]
        for peca in pecas_padrao:
            self.adicionar_linha_componente(tipo=peca, qtd="1")

    def auto_scroll_ao_focar(self, event):
        try:
            widget = event.widget
            canvas = self.scroll_cad._parent_canvas
            inner_frame = self.scroll_cad._parent_frame

            if str(inner_frame) in str(widget):
                widget_y = widget.winfo_rooty()
                canvas_y = canvas.winfo_rooty()
                canvas_height = canvas.winfo_height()

                if widget_y > (canvas_y + canvas_height - 80) or widget_y < canvas_y + 20:
                    frame_y = inner_frame.winfo_rooty()
                    frame_height = inner_frame.winfo_height()
                    if frame_height > 0:
                        posicao_relativa = widget_y - frame_y
                        porcentagem = max(0.0, (posicao_relativa - 60) / float(frame_height))
                        canvas.yview_moveto(porcentagem)
        except Exception:
            pass

    # ==================== ABA 2: CONSULTA / FILTRO / VISUALIZAÇÃO / EDIÇÃO ====================
    def setup_tab_consulta(self):
        frame_filtro = ctk.CTkFrame(self.tab_consulta)
        frame_filtro.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(frame_filtro, text="Filtrar por Marca:").pack(side="left", padx=5)
        self.combo_filtro_marca = ctk.CTkComboBox(
            frame_filtro, 
            values=["Todas", "Lenovo", "Dell", "HPE", "IBM", "Supermicro"], 
            command=self.carregar_tabela_consulta
        )
        self.combo_filtro_marca.pack(side="left", padx=5)

        ctk.CTkButton(frame_filtro, text="Atualizar Lista", command=self.carregar_tabela_consulta).pack(side="left", padx=10)
        
        ctk.CTkButton(
            frame_filtro, 
            text="👁️ Visualizar Detalhes", 
            command=self.visualizar_detalhes_servidor, 
            fg_color="teal"
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            frame_filtro, 
            text="✏️ Editar Servidor", 
            command=self.carregar_servidor_para_edicao, 
            fg_color="green"
        ).pack(side="right", padx=5)

        tree_scroll = ttk.Scrollbar(self.tab_consulta)
        tree_scroll.pack(side="right", fill="y")

        cols = ("ID", "Serial", "Marca", "Modelo", "Baias", "Trilho", "Bezel")
        self.tree = ttk.Treeview(self.tab_consulta, columns=cols, show="headings", yscrollcommand=tree_scroll.set)
        
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=110)

        self.tree.pack(fill="both", expand=True)
        tree_scroll.config(command=self.tree.yview)

        self.tree.bind("<Double-1>", lambda event: self.visualizar_detalhes_servidor())
        self.carregar_tabela_consulta()

    def carregar_tabela_consulta(self, *args):
        for item in self.tree.get_children():
            self.tree.delete(item)

        marca_filtro = self.combo_filtro_marca.get()
        servidores = self.db.listar_servidores()

        for s in servidores:
            s_id, serial, marca, modelo, fator, slot, trilho, bezel = s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7]
            if marca_filtro == "Todas" or marca_filtro.lower() == marca.lower():
                self.tree.insert("", "end", values=(s_id, serial, marca, modelo, fator, trilho, bezel))

    def visualizar_detalhes_servidor(self):
        """Abre a ficha técnica em um campo de texto selecionável com botão de cópia rápida"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Seleção", "Selecione um servidor na lista para visualizar os detalhes!")
            return

        item = self.tree.item(selected[0])
        servidor_id = item['values'][0]

        servidor, componentes = self.db.obter_servidor_completo_por_id(servidor_id)

        if not servidor:
            return

        win = ctk.CTkToplevel(self)
        win.title(f"Ficha Técnica - Serial: {servidor[1]}")
        win.geometry("750x650")
        win.grab_set()

        # Monta todo o texto da ficha para exibição e cópia
        texto_completo = []
        texto_completo.append(f"SERVIDOR: {servidor[2]} {servidor[3]}\n" + "="*45)
        texto_completo.append(f"• Serial Number / Tag: {servidor[1]}")
        texto_completo.append(f"• Marca: {servidor[2]}")
        texto_completo.append(f"• Modelo: {servidor[3]}")
        texto_completo.append(f"• Fator de Forma: {servidor[4] or 'N/I'}")
        texto_completo.append(f"• Quantidade de Baias: {servidor[5] or 'N/I'}")
        texto_completo.append(f"• Interface / Backplane: {servidor[6] or 'N/I'}")
        texto_completo.append(f"• Possui Trilho: {servidor[7] or 'N/I'}")
        texto_completo.append(f"• Possui Bezel: {servidor[8] or 'N/I'}")
        texto_completo.append(f"• Módulo de Gerenciamento: {servidor[9] or 'N/I'}")
        texto_completo.append(f"• Observações: {servidor[10] or 'Nenhum registro'}\n")
        
        texto_completo.append("COMPONENTES E PEÇAS CADASTRADAS\n" + "="*45)
        
        if componentes:
            for c in componentes:
                # c = (tipo_componente, part_number, quantidade, detalhes_extras)
                linha_peca = f"• [{c[0]}] Qtd: {c[2]} | PN: {c[1] or 'N/A'}"
                if c[3]:
                    linha_peca += f" | Obs: {c[3]}"
                texto_completo.append(linha_peca)
        else:
            texto_completo.append("Nenhum componente cadastrado.")

        conteudo_final = "\n".join(texto_completo)

        # Caixa de texto onde tudo pode ser selecionado e copiado manualmente (Ctrl+A -> Ctrl+C)
        box_texto = ctk.CTkTextbox(win, font=("Consolas", 12))
        box_texto.pack(fill="both", expand=True, padx=15, pady=(15, 5))
        box_texto.insert("1.0", conteudo_final)

        # Frame com os botões de ação
        frame_botoes = ctk.CTkFrame(win)
        frame_botoes.pack(fill="x", padx=15, pady=10)

        # Função interna do botão de copiar
        def copiar_texto():
            self.clipboard_clear()
            self.clipboard_append(conteudo_final)
            messagebox.showinfo("Copiado!", "Toda a ficha técnica foi copiada para a Área de Transferência!")

        ctk.CTkButton(
            frame_botoes, 
            text="📋 Copiar Tudo para Área de Transferência", 
            command=copiar_texto, 
            fg_color="green"
        ).pack(side="left", padx=5, expand=True)

        ctk.CTkButton(
            frame_botoes, 
            text="Fechar", 
            command=win.destroy, 
            fg_color="gray"
        ).pack(side="right", padx=5, expand=True)
    def carregar_servidor_para_edicao(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Seleção", "Selecione um servidor na lista para editar!")
            return

        item = self.tree.item(selected[0])
        servidor_id = item['values'][0]

        servidor, componentes = self.db.obter_servidor_completo_por_id(servidor_id)

        if not servidor:
            return

        self.limpar_formularios()
        self.servidor_em_edicao_id = servidor_id

        self.txt_serial.insert(0, servidor[1])
        self.combo_marca.set(servidor[2])
        self.txt_modelo.insert(0, servidor[3])
        self.combo_fator.set(servidor[4] if servidor[4] else "")
        self.txt_qtd_baias.insert(0, servidor[5] if servidor[5] else "")
        self.combo_slot.set(servidor[6] if servidor[6] else "")
        self.combo_trilho.set(servidor[7] if servidor[7] else "")
        self.combo_bezel.set(servidor[8] if servidor[8] else "")
        self.txt_mgmt.insert(0, servidor[9] if servidor[9] else "")
        
        if servidor[10]:
            self.txt_obs.insert("1.0", servidor[10])

        for c in list(self.linhas_componentes):
            c["frame"].destroy()
        self.linhas_componentes.clear()

        for comp in componentes:
            self.adicionar_linha_componente(tipo=comp[0], qtd=comp[2], pn=comp[1], desc=comp[3])

        self.btn_salvar.configure(text="Atualizar Servidor", fg_color="darkblue")
        self.tabview.set("Cadastrar / Editar")
        messagebox.showinfo("Modo Edição", f"Servidor {servidor[1]} carregado para alteração!")

    # ==================== SALVAR / LIMPAR ====================
    def salvar_cadastro(self):
        serial = self.txt_serial.get().strip()
        marca = self.combo_marca.get().strip()
        modelo = self.txt_modelo.get().strip()

        if not serial or not marca or not modelo:
            messagebox.showerror("Aviso", "Preencha os campos obrigatórios: Serial, Marca e Modelo!")
            return

        obs_texto = self.txt_obs.get("1.0", "end-1c").strip()

        dados_servidor = (
            serial, marca, modelo,
            self.combo_fator.get(),
            self.txt_qtd_baias.get(),
            self.combo_slot.get(),
            self.combo_trilho.get(),
            self.combo_bezel.get(),
            self.txt_mgmt.get(),
            obs_texto
        )

        componentes = []
        for line in self.linhas_componentes:
            tipo_val = line["tipo"].get().strip()
            if tipo_val:
                componentes.append({
                    "tipo": tipo_val,
                    "qtd": line["qtd"].get().strip() or "1",
                    "pn": line["pn"].get().strip(),
                    "detalhes": line["desc"].get().strip()
                })

        try:
            if self.servidor_em_edicao_id:
                self.db.atualizar_servidor(self.servidor_em_edicao_id, dados_servidor, componentes)
                messagebox.showinfo("Sucesso", "Cadastro do servidor atualizado com sucesso!")
            else:
                self.db.salvar_servidor(dados_servidor, componentes)
                messagebox.showinfo("Sucesso", f"Servidor {serial} cadastrado!")

            self.limpar_formularios()
            self.carregar_tabela_consulta()

        except sqlite3.IntegrityError:
            messagebox.showwarning(
                "Serial Duplicado", 
                f"O Serial Number / Tag '{serial}' já está cadastrado no sistema!\n\nVerifique os dados ou utilize a aba de consulta para editá-lo."
            )
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Ocorreu um erro inesperado:\n{e}")

    def limpar_formularios(self):
        self.servidor_em_edicao_id = None
        self.txt_serial.delete(0, 'end')
        self.txt_modelo.delete(0, 'end')
        self.txt_qtd_baias.delete(0, 'end')
        self.txt_mgmt.delete(0, 'end')
        self.txt_obs.delete("1.0", "end")

        for c in list(self.linhas_componentes):
            c["frame"].destroy()
        self.linhas_componentes.clear()

        self.btn_salvar.configure(text="Salvar Servidor", fg_color="green")
        self.adicionar_componentes_padrao()

if __name__ == "__main__":
    app = AppEstoque()
    app.mainloop()