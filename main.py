import sqlite3
import customtkinter as ctk
from tkinter import messagebox, ttk
from database.db_manager import DBManager
from services.export_service import exportar_para_csv

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Base Completa de Modelos e Famílias por Fabricante
BASE_MODELOS = {
    "IBM": [
        "x3550 (7978)", "x3650 (7979)", "x3755 (8877)", "x3850 M2", "x3950 E",
        "x3200 (4362)", "x3250 (4364)", "x3400 (7973)", "x3500 (7977)",
        "x3550 M2", "x3650 M2", "x3755 M2", "x3850 X5", "x3200 M2", "x3250 M2", "x3400 M2", "x3500 M2",
        "x3550 M3", "x3650 M3", "x3755 M3", "x3850 X5", "x3950 X5", "x3200 M3", "x3250 M3", "x3400 M3", "x3500 M3",
        "x3530 M4", "x3550 M4", "x3630 M4", "x3650 M4", "x3750 M4", "x3850 X6", "x3950 X6",
        "x3100 M4", "x3250 M4", "x3300 M4", "x3500 M4",
        "x3550 M5", "x3650 M5", "x3850 X6", "x3950 X6", "x3100 M5", "x3250 M5", "x3500 M5"
    ],
    "Lenovo": [
        "System x3550 M5", "System x3650 M5", "System x3850 X6", "System x3950 X6", "NeXtScale nx360 M5",
        "x3550 M5", "x3650 M5", "x3850 X6",
        "TS130", "TS140", "TS150", "TS430", "TS440", "TS460", "TD340", "TD350",
        "RS140", "RS160", "RD330", "RD340", "RD350", "RD430", "RD440", "RD450", "RD530", "RD540", "RD550", "RD630", "RD640", "RD650",
        "SR530", "SR550", "SR570", "SR590", "SR630", "SR650", "SR850", "SR860", "SR950",
        "SR635", "SR655", "SR645", "SR665", "ST50", "ST250", "ST550", "SN550", "SN850", "SD530",
        "SR630 V2", "SR650 V2", "SR670 V2", "SR850 V2", "SR860 V2", "SR645 V2", "SR665 V2",
        "ST50 V2", "ST250 V2", "ST650 V2",
        "SR630 V3", "SR650 V3", "SR670 V3", "SR850 V3", "SR860 V3",
        "SR635 V3", "SR655 V3", "SR645 V3", "SR665 V3", "SR675 V3", "ST50 V3", "ST250 V3", "ST650 V3"
    ],
    "Dell": [
        "PowerEdge R200", "PowerEdge R300", "PowerEdge R805", "PowerEdge R900", "PowerEdge T100", "PowerEdge T300", "PowerEdge T605",
        "PowerEdge R210", "PowerEdge R310", "PowerEdge R410", "PowerEdge R510", "PowerEdge R610", "PowerEdge R710", "PowerEdge R810", "PowerEdge R910",
        "PowerEdge R415", "PowerEdge R515", "PowerEdge R715", "PowerEdge R815",
        "PowerEdge R220", "PowerEdge R320", "PowerEdge R420", "PowerEdge R520", "PowerEdge R620", "PowerEdge R720", "PowerEdge R720xd", "PowerEdge R820", "PowerEdge R920",
        "PowerEdge R230", "PowerEdge R330", "PowerEdge R430", "PowerEdge R530", "PowerEdge R630", "PowerEdge R730", "PowerEdge R730xd", "PowerEdge R830", "PowerEdge R930",
        "PowerEdge R240", "PowerEdge R340", "PowerEdge R440", "PowerEdge R540", "PowerEdge R640", "PowerEdge R740", "PowerEdge R740xd", "PowerEdge R840", "PowerEdge R940",
        "PowerEdge R6415", "PowerEdge R7415", "PowerEdge R7425",
        "PowerEdge R250", "PowerEdge R350", "PowerEdge R450", "PowerEdge R550", "PowerEdge R650", "PowerEdge R650xs", "PowerEdge R750", "PowerEdge R750xs", "PowerEdge R750xa", "PowerEdge R850", "PowerEdge R950",
        "PowerEdge R6515", "PowerEdge R6525", "PowerEdge R7515", "PowerEdge R7525",
        "PowerEdge R260", "PowerEdge R360", "PowerEdge R660", "PowerEdge R660xs", "PowerEdge R760", "PowerEdge R760xs", "PowerEdge R760xa", "PowerEdge R760xd2", "PowerEdge R860", "PowerEdge R960",
        "PowerEdge R6615", "PowerEdge R6625", "PowerEdge R7615", "PowerEdge R7625", "PowerEdge R9675",
        "R210", "R310", "R410", "R510", "R610", "R710", "R320", "R420", "R520", "R620", "R720", "R720xd",
        "R330", "R430", "R530", "R630", "R730", "R730xd", "R440", "R540", "R640", "R740", "R740xd", "R650", "R750"
    ],
    "HPE": [
        "ProLiant DL160 Gen8", "ProLiant DL320e Gen8", "ProLiant DL360e Gen8", "ProLiant DL360p Gen8", "ProLiant DL380e Gen8", "ProLiant DL380p Gen8", "ProLiant DL560 Gen8", "ProLiant DL385p Gen8", "ProLiant DL585 Gen8",
        "ProLiant ML310e Gen8", "ProLiant ML350e Gen8", "ProLiant ML350p Gen8", "MicroServer Gen8",
        "ProLiant DL20 Gen9", "ProLiant DL60 Gen9", "ProLiant DL80 Gen9", "ProLiant DL120 Gen9", "ProLiant DL160 Gen9", "ProLiant DL180 Gen9", "ProLiant DL360 Gen9", "ProLiant DL380 Gen9", "ProLiant DL560 Gen9", "ProLiant DL580 Gen9", "ProLiant DL385 Gen9",
        "ProLiant ML10 Gen9", "ProLiant ML35 Gen9", "ProLiant ML110 Gen9", "ProLiant ML150 Gen9", "ProLiant ML350 Gen9",
        "ProLiant DL20 Gen10", "ProLiant DL160 Gen10", "ProLiant DL180 Gen10", "ProLiant DL360 Gen10", "ProLiant DL380 Gen10", "ProLiant DL560 Gen10", "ProLiant DL580 Gen10",
        "ProLiant DL325 Gen10", "ProLiant DL385 Gen10", "ProLiant DL345 Gen10", "ProLiant ML30 Gen10", "ProLiant ML110 Gen10", "ProLiant ML350 Gen10", "MicroServer Gen10",
        "DL360 Gen9", "DL380 Gen9", "DL360 Gen10", "DL380 Gen10", "DL360 Gen10 Plus", "DL380 Gen10 Plus", "DL360 Gen11", "DL380 Gen11"
    ],
    "Supermicro": [
        "SuperServer 1U Rack", "SuperServer 2U Rack", "SuperServer 3U Rack", "SuperServer 4U Rack",
        "BigTwin 2U 4-Node", "FatTwin 4U", "SuperBlade", "Ultra SuperServer"
    ]
}

# Classe auxiliar para criar o Autocompletar Inline inteligente
class AutoCompleteEntry(ctk.CTkEntry):
    def __init__(self, master, lista_sugestoes=None, callback_selecao=None, **kwargs):
        super().__init__(master, **kwargs)
        self.lista_sugestoes = lista_sugestoes or []
        self.callback_selecao = callback_selecao
        self.sugestoes_atuais = []
        self.index_sugestao = 0

        self.bind("<KeyRelease>", self.ao_digitar)
        self.bind("<Down>", self.proxima_sugestao)
        self.bind("<Up>", self.sugestao_anterior)

    def atualizar_lista_sugestoes(self, nova_lista):
        self.lista_sugestoes = nova_lista

    def ao_digitar(self, event):
        # Ignora teclas de navegação para não estragar a seleção do usuário
        if event.keysym in ["BackSpace", "Left", "Right", "Up", "Down", "Tab", "Return", "Shift_L", "Shift_R"]:
            return

        texto_digitado = self.get()
        if not texto_digitado:
            return

        # Filtra os itens da lista que começam com o que foi digitado (ignorando maiúsculas/minúsculas)
        self.sugestoes_atuais = [
            item for item in self.lista_sugestoes 
            if item.lower().startswith(texto_digitado.lower())
        ]

        if self.sugestoes_atuais:
            self.index_sugestao = 0
            self.aplicar_sugestao(texto_digitado, self.sugestoes_atuais[0])

    def aplicar_sugestao(self, texto_original, sugestao_completa):
        self.delete(0, "end")
        self.insert(0, sugestao_completa)
        
        # Mantém apenas a parte sugerida selecionada (efeito visual azul do Windows)
        inicio_selecao = len(texto_original)
        fim_selecao = len(sugestao_completa)
        self._entry.select_range(inicio_selecao, fim_selecao)
        self._entry.icursor(inicio_selecao)

        if self.callback_selecao:
            self.callback_selecao(sugestao_completa)

    def proxima_sugestao(self, event):
        if self.sugestoes_atuais:
            self.index_sugestao = (self.index_sugestao + 1) % len(self.sugestoes_atuais)
            # Pega o texto que o usuário realmente digitou antes da seleção
            pos_cursor = self._entry.index("insert")
            texto_base = self.get()[:pos_cursor]
            self.aplicar_sugestao(texto_base, self.sugestoes_atuais[self.index_sugestao])
        return "break"

    def sugestao_anterior(self, event):
        if self.sugestoes_atuais:
            self.index_sugestao = (self.index_sugestao - 1) % len(self.sugestoes_atuais)
            pos_cursor = self._entry.index("insert")
            texto_base = self.get()[:pos_cursor]
            self.aplicar_sugestao(texto_base, self.sugestoes_atuais[self.index_sugestao])
        return "break"


class AppEstoque(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestão e Cadastro de Servidores")
        self.geometry("1100x850")

        self.db = DBManager()
        self.servidor_em_edicao_id = None
        self.linhas_componentes = []

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_cadastro = self.tabview.add("Cadastrar / Editar")
        self.tab_consulta = self.tabview.add("Consultar / Filtrar")

        self.setup_tab_cadastro()
        self.setup_tab_consulta()

        self.bind_all("<FocusIn>", self.auto_scroll_ao_focar)

    def setup_tab_cadastro(self):
        self.scroll_cad = ctk.CTkScrollableFrame(self.tab_cadastro)
        self.scroll_cad.pack(fill="both", expand=True, padx=5, pady=5)

        ctk.CTkLabel(self.scroll_cad, text="Informações do Servidor", font=("Arial", 16, "bold")).pack(anchor="w", pady=(10, 5))

        self.txt_serial = self.add_field("Serial Number / Service Tag *")
        
        # Campo Marca com Autocompletar Inline
        ctk.CTkLabel(self.scroll_cad, text="Marca *").pack(anchor="w", pady=(5, 0))
        self.txt_marca = AutoCompleteEntry(
            self.scroll_cad, 
            lista_sugestoes=list(BASE_MODELOS.keys()) + ["Supermicro", "IBM"],
            callback_selecao=self.ao_alterar_marca
        )
        self.txt_marca.pack(fill="x", pady=2)

        # Campo Modelo com Autocompletar Inline (Filtra apenas modelos da marca escolhida)
        ctk.CTkLabel(self.scroll_cad, text="Modelo *").pack(anchor="w", pady=(5, 0))
        self.txt_modelo = AutoCompleteEntry(self.scroll_cad, lista_sugestoes=[])
        self.txt_modelo.pack(fill="x", pady=2)

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

        ctk.CTkLabel(self.scroll_cad, text="Tipo de Slot / Backplane").pack(anchor="w", pady=(5, 0))
        self.combo_slot = ctk.CTkComboBox(self.scroll_cad, values=["SAS/SATA", "SOMENTE SATA", "NVMe", "Baia Universal (SAS/SATA/NVMe)", "Outro"])
        self.combo_slot.pack(fill="x", pady=2)

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

        ctk.CTkLabel(self.scroll_cad, text="Peças e Componentes Internos", font=("Arial", 16, "bold")).pack(anchor="w", pady=(20, 5))

        self.frame_pecas = ctk.CTkFrame(self.scroll_cad)
        self.frame_pecas.pack(fill="x", pady=5)

        btn_add_peca = ctk.CTkButton(self.scroll_cad, text="+ Adicionar Peça Extra", command=self.adicionar_linha_componente, fg_color="gray")
        btn_add_peca.pack(anchor="w", pady=5)

        ctk.CTkLabel(self.scroll_cad, text="Observações (Avarias, detalhes físicos)").pack(anchor="w", pady=(10, 0))
        self.txt_obs = ctk.CTkTextbox(self.scroll_cad, height=70)
        self.txt_obs.pack(fill="x", pady=5)

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

    # Atualiza as sugestões de modelo e o gerenciamento ao selecionar/digitar a Marca
    def ao_alterar_marca(self, marca_selecionada):
        marca_limpa = marca_selecionada.strip()
        
        # Procura se a marca digitada existe no dicionário
        marca_encontrada = None
        for key in BASE_MODELOS.keys():
            if key.lower() == marca_limpa.lower():
                marca_encontrada = key
                break

        if marca_encontrada:
            # Carrega a lista exclusiva dessa marca para o campo de Modelo
            self.txt_modelo.atualizar_lista_sugestoes(BASE_MODELOS[marca_encontrada])
        else:
            self.txt_modelo.atualizar_lista_sugestoes([])

        sugestoes_mgmt = {
            "Lenovo": "XClarity Controller (XCC) Enterprise",
            "Dell": "iDRAC9 Enterprise",
            "HPE": "iLO 5 Advanced",
            "IBM": "IMM2 Advanced"
        }
        if marca_encontrada in sugestoes_mgmt and not self.txt_mgmt.get():
            self.txt_mgmt.insert(0, sugestoes_mgmt[marca_encontrada])

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

    def setup_tab_consulta(self):
        frame_filtro = ctk.CTkFrame(self.tab_consulta)
        frame_filtro.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(frame_filtro, text="Filtrar por Marca:").pack(side="left", padx=5)
        self.combo_filtro_marca = ctk.CTkComboBox(
            frame_filtro, 
            values=["Todas", "IBM", "Lenovo", "Dell", "HPE", "Supermicro"], 
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
                linha_peca = f"• [{c[0]}] Qtd: {c[2]} | PN: {c[1] or 'N/A'}"
                if c[3]:
                    linha_peca += f" | Obs: {c[3]}"
                texto_completo.append(linha_peca)
        else:
            texto_completo.append("Nenhum componente cadastrado.")

        conteudo_final = "\n".join(texto_completo)

        box_texto = ctk.CTkTextbox(win, font=("Consolas", 12))
        box_texto.pack(fill="both", expand=True, padx=15, pady=(15, 5))
        box_texto.insert("1.0", conteudo_final)

        frame_botoes = ctk.CTkFrame(win)
        frame_botoes.pack(fill="x", padx=15, pady=10)

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
        
        # Preenche marca e modelo
        self.txt_marca.delete(0, 'end')
        self.txt_marca.insert(0, servidor[2])
        self.ao_alterar_marca(servidor[2])

        self.txt_modelo.delete(0, 'end')
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

    def salvar_cadastro(self):
        serial = self.txt_serial.get().strip()
        marca = self.txt_marca.get().strip()
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
        self.txt_marca.delete(0, 'end')
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