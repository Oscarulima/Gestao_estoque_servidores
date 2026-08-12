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
        self.geometry("1050x800")

        self.db = DBManager()
        self.servidor_em_edicao_id = None
        self.linhas_componentes = []

        # Sistema de Abas (Cadastro vs Consulta)
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_cadastro = self.tabview.add("Cadastrar / Editar")
        self.tab_consulta = self.tabview.add("Consultar / Filtrar")

        self.setup_tab_cadastro()
        self.setup_tab_consulta()
        self.bind_all("<FocusIn>", self.auto_scroll_ao_focar)

    # ==================== ABA 1: CADASTRO / EDIÇÃO ====================
    def setup_tab_cadastro(self):
        self.scroll_cad = ctk.CTkScrollableFrame(self.tab_cadastro)
        self.scroll_cad.pack(fill="both", expand=True, padx=5, pady=5)

        # Dados Principais
        ctk.CTkLabel(self.scroll_cad, text="Informações do Servidor", font=("Arial", 16, "bold")).pack(anchor="w", pady=(10, 5))

        self.txt_serial = self.add_field("Serial Number / Service Tag *")
        
        # Marca com Autofill
        ctk.CTkLabel(self.scroll_cad, text="Marca *").pack(anchor="w", pady=(5, 0))
        self.combo_marca = ctk.CTkComboBox(self.scroll_cad, values=["Lenovo", "Dell", "HPE", "IBM", "Supermicro", "Outro"], command=self.aplicar_autofill_marca)
        self.combo_marca.pack(fill="x", pady=2)

        self.txt_modelo = self.add_field("Modelo (ex: x3650 M5, PowerEdge R740) *")

        # Fator e Quantidade de Baias
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

        # Slots e Trilho
        ctk.CTkLabel(self.scroll_cad, text="Tipo de Slot / Backplane").pack(anchor="w", pady=(5, 0))
        self.combo_slot = ctk.CTkComboBox(self.scroll_cad, values=["SAS/SATA", "SOMENTE SATA", "NVMe", "Baia Universal (SAS/SATA/NVMe)", "Outro"])
        self.combo_slot.pack(fill="x", pady=2)

        ctk.CTkLabel(self.scroll_cad, text="Possui Trilho Deslizável?").pack(anchor="w", pady=(5, 0))
        self.combo_trilho = ctk.CTkComboBox(self.scroll_cad, values=["Sim", "Não"])
        self.combo_trilho.pack(fill="x", pady=2)

        self.txt_mgmt = self.add_field("Módulo de Gerenciamento & Licença (ex: iDRAC Enterprise)")

        # Componentes Dinâmicos
        ctk.CTkLabel(self.scroll_cad, text="Peças e Componentes Internos", font=("Arial", 16, "bold")).pack(anchor="w", pady=(20, 5))

        self.frame_pecas = ctk.CTkFrame(self.scroll_cad)
        self.frame_pecas.pack(fill="x", pady=5)

        btn_add_peca = ctk.CTkButton(self.scroll_cad, text="+ Adicionar Peça/Componente", command=self.adicionar_linha_componente, fg_color="gray")
        btn_add_peca.pack(anchor="w", pady=5)

        # Observações (Correção do ERRO do get)
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

        # Inicializa com peças padrão
        self.adicionar_componentes_padrao()

    def add_field(self, label_text):
        ctk.CTkLabel(self.scroll_cad, text=label_text).pack(anchor="w", pady=(5, 0))
        entry = ctk.CTkEntry(self.scroll_cad)
        entry.pack(fill="x", pady=2)
        return entry

    # Autofill inteligente ao selecionar a marca
    def aplicar_autofill_marca(self, marca_selecionada):
        sugestoes = {
            "Lenovo": "XClarity Controller (XCC) Enterprise",
            "Dell": "iDRAC9 Enterprise",
            "HPE": "iLO 5 Advanced",
            "IBM": "IMM2 Advanced"
        }
        if marca_selecionada in sugestoes and not self.txt_mgmt.get():
            self.txt_mgmt.insert(0, sugestoes[marca_selecionada])

    # Adiciona linha para cadastro de peça
    def adicionar_linha_componente(self, tipo="", qtd="1", pn="", desc=""):
        row = ctk.CTkFrame(self.frame_pecas)
        row.pack(fill="x", pady=2)

        # Sugestões para AutoFill de Peças
        opcoes_pecas = [
            "Placa Mãe", "Placa de Rede", "Placa HBA", "Fonte de Energia", 
            "Fan / Cooler", "Dissipador", "Controladora RAID", "Riser Card", 
            "Memória RAM", "Processador (CPU)", "Disco / SSD / HD", 
            "Bateria RAID / Cache", "Airflow / Duto", "Cabo Mini-SAS / Slimline"
        ]

        # ComboBox editável que aceita digitação e sugere opções
        combo_tipo = ctk.CTkComboBox(row, values=opcoes_pecas, width=160)
        combo_tipo.set(tipo if tipo else "Selecione ou digite...")
        combo_tipo.pack(side="left", padx=2)

        txt_qtd = ctk.CTkEntry(row, placeholder_text="Qtd", width=60)
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

        # Mapeamento dos elementos da linha
        self.linhas_componentes.append({
            "frame": row, 
            "tipo": combo_tipo, 
            "qtd": txt_qtd, 
            "pn": txt_pn, 
            "desc": txt_desc
        })

    # Remova a chamada do método antigo e substitua por esta versão limpa:
    def adicionar_componentes_padrao(self):
        # Inicia a tela apenas com 1 linha em branco com foco para rápida digitação
        self.adicionar_linha_componente()

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
        
        # Botões de Ação
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

        # Tabela com Scroll usando Treeview do Tkinter
        tree_scroll = ttk.Scrollbar(self.tab_consulta)
        tree_scroll.pack(side="right", fill="y")

        cols = ("ID", "Serial", "Marca", "Modelo", "Baias", "Trilho")
        self.tree = ttk.Treeview(self.tab_consulta, columns=cols, show="headings", yscrollcommand=tree_scroll.set)
        
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=120)

        self.tree.pack(fill="both", expand=True)
        tree_scroll.config(command=self.tree.yview)

        # Atalho: Duplo clique na linha abre os detalhes
        self.tree.bind("<Double-1>", lambda event: self.visualizar_detalhes_servidor())

        self.carregar_tabela_consulta()

    def visualizar_detalhes_servidor(self):
        """Abre uma janela pop-up mostrando a ficha completa do servidor e suas peças"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Seleção", "Selecione um servidor na lista para visualizar os detalhes!")
            return

        item = self.tree.item(selected[0])
        servidor_id = item['values'][0]

        servidor, componentes = self.db.obter_servidor_completo_por_id(servidor_id)

        if not servidor:
            return

        # Janela Pop-up de Detalhes
        win = ctk.CTkToplevel(self)
        win.title(f"Ficha Técnica - Servidor Serial: {servidor[1]}")
        win.geometry("750x600")
        win.grab_set()  # Mantém o foco na janela pop-up

        scroll = ctk.CTkScrollableFrame(win)
        scroll.pack(fill="both", expand=True, padx=15, pady=15)

        # Informações Principais
        ctk.CTkLabel(scroll, text=f"Servidor: {servidor[2]} {servidor[3]}", font=("Arial", 18, "bold")).pack(anchor="w", pady=(5, 10))

        info_text = (
            f"• Serial Number / Tag: {servidor[1]}\n"
            f"• Marca: {servidor[2]}\n"
            f"• Modelo: {servidor[3]}\n"
            f"• Fator de Forma: {servidor[4] or 'N/I'}\n"
            f"• Quantidade de Baias: {servidor[5] or 'N/I'}\n"
            f"• Interface / Backplane: {servidor[6] or 'N/I'}\n"
            f"• Possui Trilho: {servidor[7] or 'N/I'}\n"
            f"• Módulo de Gerenciamento: {servidor[8] or 'N/I'}\n"
            f"• Observações: {servidor[9] or 'Nenhum registro'}"
        )

        box_info = ctk.CTkTextbox(scroll, height=150)
        box_info.pack(fill="x", pady=5)
        box_info.insert("1.0", info_text)
        box_info.configure(state="disabled")

        # Lista de Peças Cadastradas
        ctk.CTkLabel(scroll, text="Componentes e Peças Cadastradas", font=("Arial", 16, "bold")).pack(anchor="w", pady=(15, 5))

        if componentes:
            for c in componentes:
                # c = (tipo_componente, part_number, quantidade, detalhes_extras)
                frame_comp = ctk.CTkFrame(scroll)
                frame_comp.pack(fill="x", pady=2, padx=2)

                texto_peca = f"• [{c[0]}] Qtd: {c[2]} | PN: {c[1] or 'N/A'}"
                if c[3]:
                    texto_peca += f" | Obs: {c[3]}"

                ctk.CTkLabel(frame_comp, text=texto_peca, anchor="w").pack(fill="x", padx=10, pady=5)
        else:
            ctk.CTkLabel(scroll, text="Nenhum componente cadastrado para este servidor.").pack(anchor="w")

        ctk.CTkButton(scroll, text="Fechar", command=win.destroy, fg_color="gray").pack(pady=15)

    def carregar_tabela_consulta(self, *args):
        for item in self.tree.get_children():
            self.tree.delete(item)

        marca_filtro = self.combo_filtro_marca.get()
        servidores = self.db.listar_servidores()

        for s in servidores:
            # s = (id, serial, marca, modelo, fator, slot, trilho)
            s_id, serial, marca, modelo, fator, slot, trilho = s[0], s[1], s[2], s[3], s[4], s[5], s[6]
            if marca_filtro == "Todas" or marca_filtro.lower() == marca.lower():
                self.tree.insert("", "end", values=(s_id, serial, marca, modelo, fator, trilho))

    def carregar_servidor_para_edicao(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Seleção", "Selecione um servidor na lista para editar!")
            return

        item = self.tree.item(selected[0])
        servidor_id = item['values'][0]

        # Busca dados do servidor e componentes no banco
        servidor, componentes = self.db.obter_servidor_completo_por_id(servidor_id)

        if not servidor:
            return

        self.limpar_formularios()
        self.servidor_em_edicao_id = servidor_id

        # Preenche os campos principais
        self.txt_serial.insert(0, servidor[1])
        self.combo_marca.set(servidor[2])
        self.txt_modelo.insert(0, servidor[3])
        self.combo_fator.set(servidor[4] if servidor[4] else "")
        self.txt_qtd_baias.insert(0, servidor[5] if servidor[5] else "")
        self.combo_slot.set(servidor[6] if servidor[6] else "")
        self.combo_trilho.set(servidor[7] if servidor[7] else "")
        self.txt_mgmt.insert(0, servidor[8] if servidor[8] else "")
        
        if servidor[9]:
            self.txt_obs.insert("1.0", servidor[9])

        # Preenche as peças
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

        # Correção definitiva do erro de busca de texto do Textbox
        obs_texto = self.txt_obs.get("1.0", "end-1c").strip()

        dados_servidor = (
            serial, marca, modelo,
            self.combo_fator.get(),
            self.txt_qtd_baias.get(),
            self.combo_slot.get(),
            self.combo_trilho.get(),
            self.txt_mgmt.get(),
            obs_texto
        )

        componentes = []
        for line in self.linhas_componentes:
            tipo = line["tipo"].get().strip()
            if tipo:
                componentes.append({
                    "tipo": tipo,
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
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar.\nErro: {e}")

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

    def auto_scroll_ao_focar(self, event):
        """Rola a tela automaticamente quando um campo recebe foco via teclado (Tab)"""
        try:
            widget = event.widget
            canvas = self.scroll_cad._parent_canvas
            inner_frame = self.scroll_cad._parent_frame

            # Verifica se o campo focado pertence ao painel rolável
            if str(inner_frame) in str(widget):
                widget_y = widget.winfo_rooty()
                canvas_y = canvas.winfo_rooty()
                canvas_height = canvas.winfo_height()

                # Se o campo estiver fora da área visível (abaixo ou acima)
                if widget_y > (canvas_y + canvas_height - 80) or widget_y < canvas_y + 20:
                    frame_y = inner_frame.winfo_rooty()
                    frame_height = inner_frame.winfo_height()
                    
                    if frame_height > 0:
                        posicao_relativa = widget_y - frame_y
                        porcentagem = max(0.0, (posicao_relativa - 60) / float(frame_height))
                        canvas.yview_moveto(porcentagem)
        except Exception:
            pass

if __name__ == "__main__":
    app = AppEstoque()
    app.mainloop()