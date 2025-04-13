from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QListWidget, QStackedLayout, QLineEdit, QComboBox,
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QFormLayout, QDateEdit
)
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtCore import Qt, QSettings, QDate
from datetime import datetime, timedelta
import subprocess
import threading

from plyer import notification  # ✅ substitui win10toast
from controllers.database import criar_banco, salvar_cliente, buscar_clientes, excluir_cliente, salvar_calculo, buscar_processos, buscar_prazos_por_data
from utils.helpers import gerar_callback_exclusao


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cálculos Judiciais")
        self.setGeometry(200, 100, 1000, 600)
        criar_banco()
        self.settings = QSettings("MinhaEmpresa", "CalculadoraJudicial")
        self.tema_escuro = self.settings.value("tema_escuro", False, type=bool)
        self.setStyleSheet(self.obter_estilo())

        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        logo = QLabel()
        pixmap = QPixmap("logo.png")
        if not pixmap.isNull():
            pixmap = pixmap.scaledToWidth(200)
            logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(logo)

        self.botao_tema = QPushButton("☀️ Modo Claro" if self.tema_escuro else "🌙 Modo Escuro")
        self.botao_tema.clicked.connect(self.alternar_tema)
        main_layout.addWidget(self.botao_tema)

        self.menu = QListWidget()
        for item in ["🏠 Dashboard", "👤 Clientes", "➕ Novo Cálculo", "📝 Cadastrar Cliente", "📑 Lista de Processos"]:
            self.menu.addItem(item)
        self.menu.setFixedWidth(200)
        self.menu.currentRowChanged.connect(self.display_page)

        self.pages = QStackedLayout()
        dashboard = QLabel("Bem-vindo!")
        dashboard.setAlignment(Qt.AlignCenter)
        dashboard.setFont(QFont("Arial", 16))
        self.pages.addWidget(self.wrap_widget(dashboard))

        self.clientes_page = self.criar_pagina_clientes()
        self.pages.addWidget(self.clientes_page)

        self.novo_calc_page = self.criar_pagina_novo_calculo()
        self.pages.addWidget(self.novo_calc_page)

        self.cadastrar_cliente_page = self.criar_pagina_cadastrar_cliente()
        self.pages.addWidget(self.cadastrar_cliente_page)

        self.lista_processos_page = self.criar_pagina_lista_processos()
        self.pages.addWidget(self.lista_processos_page)

        content = QHBoxLayout()
        content.addWidget(self.menu)
        content_widget = QWidget()
        content_widget.setLayout(self.pages)
        content.addWidget(content_widget)
        main_layout.addLayout(content)

        self.setCentralWidget(central_widget)
        self.carregar_clientes()
        self.carregar_clientes_combo()
        self.carregar_processos()
        self.verificar_prazos()

    def wrap_widget(self, widget):
        w = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(widget)
        w.setLayout(layout)
        return w

    def criar_pagina_clientes(self):
        page = QWidget()
        layout = QVBoxLayout()
        filtro_layout = QHBoxLayout()
        self.filtro_nome = QLineEdit()
        self.filtro_nome.setPlaceholderText("Buscar por nome")
        buscar_btn = QPushButton("Buscar")
        buscar_btn.clicked.connect(self.carregar_clientes)
        filtro_layout.addWidget(self.filtro_nome)
        filtro_layout.addWidget(buscar_btn)

        self.tabela_clientes = QTableWidget()
        self.tabela_clientes.setColumnCount(5)
        self.tabela_clientes.setHorizontalHeaderLabels(["Nome", "Celular", "Email", "OAB", ""])
        self.tabela_clientes.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela_clientes.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addLayout(filtro_layout)
        layout.addWidget(self.tabela_clientes)
        page.setLayout(layout)
        return page

    def criar_pagina_novo_calculo(self):
        page = QWidget()
        layout = QFormLayout()
        self.combo_clientes = QComboBox()
        self.processo_input = QLineEdit()
        self.prazo_input = QDateEdit()
        self.prazo_input.setCalendarPopup(True)
        self.prazo_input.setDate(QDate.currentDate())
        self.area_input = QComboBox()
        self.area_input.addItems(["Trabalhista", "Cível", "Federal"])
        self.valor_input = QLineEdit()
        self.pago_input = QComboBox()
        self.pago_input.addItems(["Não", "Sim"])
        self.enviado_input = QComboBox()
        self.enviado_input.addItems(["Não", "Sim"])

        layout.addRow("Cliente:", self.combo_clientes)
        layout.addRow("Nº Processo:", self.processo_input)
        layout.addRow("Prazo:", self.prazo_input)
        layout.addRow("Área:", self.area_input)
        layout.addRow("Valor (R$):", self.valor_input)
        layout.addRow("Pago?", self.pago_input)
        layout.addRow("Enviado?", self.enviado_input)

        salvar_btn = QPushButton("💾 Salvar Cálculo")
        salvar_btn.clicked.connect(self.salvar_calculo)
        layout.addRow(salvar_btn)

        page.setLayout(layout)
        return page

    def criar_pagina_cadastrar_cliente(self):
        page = QWidget()
        layout = QFormLayout()
        self.nome_cliente_input = QLineEdit()
        self.celular_input = QLineEdit()
        self.email_input = QLineEdit()
        self.oab_input = QLineEdit()
        layout.addRow("Nome:", self.nome_cliente_input)
        layout.addRow("Celular:", self.celular_input)
        layout.addRow("Email:", self.email_input)
        layout.addRow("OAB:", self.oab_input)
        salvar_btn = QPushButton("Salvar Cliente")
        salvar_btn.clicked.connect(self.salvar_cliente)
        layout.addRow(salvar_btn)
        page.setLayout(layout)
        return page

    def criar_pagina_lista_processos(self):
        page = QWidget()
        layout = QVBoxLayout()
        busca = QLineEdit()
        busca.setPlaceholderText("Buscar por número do processo ou cliente")
        busca.textChanged.connect(self.carregar_processos)
        self.busca_input = busca
        self.tabela_processos = QTableWidget()
        self.tabela_processos.setColumnCount(7)
        self.tabela_processos.setHorizontalHeaderLabels(["Cliente", "Nº Processo", "Prazo", "Área", "Valor", "Pago", "Enviado"])
        self.tabela_processos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(busca)
        layout.addWidget(self.tabela_processos)
        page.setLayout(layout)
        return page

    def carregar_processos(self):
        filtro = self.busca_input.text().strip().lower() if hasattr(self, 'busca_input') else ''
        self.tabela_processos.setRowCount(0)

        if filtro == '':
            processos = buscar_processos('')
        elif len(filtro) >= 4:
            processos = buscar_processos(filtro)
        else:
            return

        for processo in processos:
            row = self.tabela_processos.rowCount()
            self.tabela_processos.insertRow(row)
            for i, val in enumerate(processo):
                self.tabela_processos.setItem(row, i, QTableWidgetItem(str(val)))

    def salvar_cliente(self):
        nome = self.nome_cliente_input.text()
        celular = self.celular_input.text()
        email = self.email_input.text()
        oab = self.oab_input.text()

        if not nome or not celular:
            QMessageBox.warning(self, "Atenção", "Preencha ao menos nome e celular.")
            return

        salvar_cliente(nome, celular, email, oab)
        QMessageBox.information(self, "Sucesso", "Cliente salvo com sucesso!")
        self.nome_cliente_input.clear()
        self.celular_input.clear()
        self.email_input.clear()
        self.oab_input.clear()
        self.carregar_clientes()
        self.carregar_clientes_combo()

    def salvar_calculo(self):
        cliente_nome = self.combo_clientes.currentText()
        cliente_id = self.combo_clientes.currentData()
        if cliente_id is None:
            QMessageBox.warning(self, "Erro", "Selecione um cliente válido.")
            return

        numero = self.processo_input.text()
        prazo = self.prazo_input.date().toString("yyyy-MM-dd")
        area = self.area_input.currentText()
        valor = self.valor_input.text().replace(',', '.')

        try:
            float(valor)
        except ValueError:
            QMessageBox.warning(self, "Erro", "Informe um valor numérico válido.")
            return

        pago = self.pago_input.currentText()
        enviado = self.enviado_input.currentText()

        salvar_calculo(numero, cliente_id, area, valor, prazo, pago, enviado)

        try:
            data_prazo = datetime.strptime(prazo, "%Y-%m-%d")
            lembrete_data = (data_prazo - timedelta(days=1)).strftime("%d/%m/%Y")
            comando = f'schtasks /Create /SC ONCE /TN "Lembrete_{numero}" /TR "msg * Lembrete: cálculo para {cliente_nome} vence amanhã!" /ST 09:00 /SD {lembrete_data} /F'
            subprocess.run(comando, shell=True)
        except Exception as e:
            print("Erro ao criar lembrete:", e)

        QMessageBox.information(self, "Sucesso", "Cálculo salvo e lembrete criado.")
        self.carregar_processos()

    def carregar_clientes(self):
        nome_filtro = self.filtro_nome.text().lower()
        clientes = buscar_clientes()
        self.tabela_clientes.setRowCount(0)
        for id_, nome, celular, email, oab in clientes:
            if nome_filtro in nome.lower():
                row = self.tabela_clientes.rowCount()
                self.tabela_clientes.insertRow(row)
                self.tabela_clientes.setItem(row, 0, QTableWidgetItem(nome))
                self.tabela_clientes.setItem(row, 1, QTableWidgetItem(celular))
                self.tabela_clientes.setItem(row, 2, QTableWidgetItem(email))
                self.tabela_clientes.setItem(row, 3, QTableWidgetItem(oab))
                btn_excluir = QPushButton("Excluir")
                btn_excluir.clicked.connect(gerar_callback_exclusao(id_, self))
                container = QWidget()
                l = QHBoxLayout()
                l.addWidget(btn_excluir)
                l.setContentsMargins(0, 0, 0, 0)
                container.setLayout(l)
                self.tabela_clientes.setCellWidget(row, 4, container)

    def carregar_clientes_combo(self):
        self.combo_clientes.clear()
        for id_, nome, *_ in buscar_clientes():
            self.combo_clientes.addItem(nome, id_)

    def excluir_cliente(self, id_):
        excluir_cliente(id_)
        self.carregar_clientes()
        self.carregar_clientes_combo()
        QMessageBox.information(self, "Cliente Excluído", "O cliente foi removido com sucesso.")

    def alternar_tema(self):
        self.tema_escuro = not self.tema_escuro
        self.settings.setValue("tema_escuro", self.tema_escuro)
        self.setStyleSheet(self.obter_estilo())
        self.botao_tema.setText("☀️ Modo Claro" if self.tema_escuro else "🌙 Modo Escuro")

    def obter_estilo(self):
        if self.tema_escuro:
            return "QWidget { background-color: #2c3e50; color: white; }"
        return "QWidget { background-color: white; color: black; }"

    def obter_estilo(self):
        if self.tema_escuro:
            return """
            QWidget {
                background-color: #2b2b2b;
                color: #f0f0f0;
            }
            QTableWidget, QTableView {
                background-color: #3c3f41;
                alternate-background-color: #313335;
                color: #f0f0f0;
                gridline-color: #4f5254;
                selection-background-color: #555a5e;
                selection-color: white;
            }
            QHeaderView::section {
                background-color: #444;
                color: #f0f0f0;
                padding: 4px;
                border: 1px solid #666;
            }
            QLineEdit, QComboBox, QDateEdit {
                background-color: #3c3f41;
                color: #f0f0f0;
                border: 1px solid #555;
            }
            QPushButton {
                background-color: #4b6eaf;
                color: white;
                padding: 5px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #6d8fd6;
            }
            QListWidget {
                background-color: #2b2b2b;
                color: #f0f0f0;
            }
            """
        else:
            return """
            QWidget {
                background-color: white;
                color: black;
            }
            QTableWidget, QTableView {
                background-color: white;
                color: black;
            }
            QHeaderView::section {
                background-color: #e0e0e0;
                color: black;
                padding: 4px;
                border: 1px solid #ccc;
            }
            QLineEdit, QComboBox, QDateEdit {
                background-color: white;
                color: black;
            }
            QPushButton {
                background-color: #1976d2;
                color: white;
                padding: 5px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #4791db;
            }
            QListWidget {
                background-color: white;
                color: black;
            }
            """
    def display_page(self, index):
        self.pages.setCurrentIndex(index)
        if index == 1:
            self.carregar_clientes()
        elif index == 4:
            self.carregar_processos()

    def verificar_prazos(self):
        mensagens = []

        def mostrar_toast(titulo, mensagem):
            try:
                notification.notify(
                    title=titulo,
                    message=mensagem,
                    timeout=10
                )
            except Exception as e:
                print("Erro ao exibir notificação:", e)

        vencidos = buscar_prazos_por_data("vencido")
        if vencidos:
            texto = "\n".join([f"- {nome} (Proc. {numero})" for nome, numero, _ in vencidos])
            mensagens.append(f"⚠️ Prazos vencidos:\n{texto}")
            threading.Thread(target=mostrar_toast, args=("⚠️ Prazos Vencidos", f"{len(vencidos)} cálculo(s) vencido(s).")).start()

        hoje = buscar_prazos_por_data("hoje")
        if hoje:
            texto = "\n".join([f"- {nome} (Proc. {numero})" for nome, numero, _ in hoje])
            mensagens.append(f"📅 Prazos para hoje:\n{texto}")
            threading.Thread(target=mostrar_toast, args=("📅 Prazos para Hoje", f"{len(hoje)} vencendo hoje.")).start()

        amanha = buscar_prazos_por_data("amanha")
        if amanha:
            texto = "\n".join([f"- {nome} (Proc. {numero})" for nome, numero, _ in amanha])
            mensagens.append(f"📆 Prazos para amanhã:\n{texto}")
            threading.Thread(target=mostrar_toast, args=("📆 Prazos para Amanhã", f"{len(amanha)} vencendo amanhã.")).start()

        if mensagens:
            QMessageBox.information(self, "⏰ Alertas de Prazos", "\n\n".join(mensagens))
