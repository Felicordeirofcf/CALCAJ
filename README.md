# ⚖️ AJCALC — Calculadora Judicial

Sistema de gestão de cálculos judiciais com cadastro de clientes, prazos processuais e notificações automáticas.

---

## 📦 Funcionalidades

- Cadastro de clientes com nome, celular, e-mail e OAB
- Registro de cálculos judiciais por cliente
- Controle de prazos com datas e valores
- Filtro por número de processo ou nome do cliente
- Notificações automáticas:
  - Na inicialização do sistema (prazos vencidos, de hoje e de amanhã)
  - Criadas no Agendador de Tarefas do Windows
  - Notificações na bandeja com `win10toast`
- Alternância entre tema claro e escuro
- Interface moderna com PySide6 (Qt para Python)

---

## 🧱 Estrutura do Projeto

📁 AJCALC/ 
├── main.py # Ponto de entrada do app
├── ui_mainwindow.py # Interface gráfica principal 
├── controllers/ │ └── database.py # Funções de banco de dados SQLite
├── utils/ │ └── helpers.py # Utilitários (callbacks, etc.) 
├── logo.png # Logotipo do sistema 
└── README.md # Este arquivo

arquivo

yaml
Copiar
Editar

---

## ▶️ Como Executar

1. Clone o projeto:
```bash
git clone https://github.com/seu-usuario/AJCALC.git
cd AJCALC
Instale as dependências:

bash
Copiar
Editar
pip install -r requirements.txt
Execute o sistema:

bash
Copiar
Editar
python main.py
✅ Requisitos
Python 3.8 ou superior

Windows (para integração com schtasks e msg)

Módulos Python:

nginx
Copiar
Editar
PySide6
win10toast
Você pode instalar tudo com:

bash
Copiar
Editar
pip install PySide6 win10toast
Ou criar um requirements.txt com:

nginx
Copiar
Editar
PySide6
win10toast
💡 Observações
As tarefas são criadas com o Agendador de Tarefas do Windows (schtasks) e não aparecem no aplicativo de "Alarmes".

As notificações na bandeja aparecem ao abrir o sistema, utilizando win10toast.

📸 Imagens (opcional)
Adicione aqui prints do sistema em execução, se desejar.

📜 Licença
Distribuído sob a licença MIT. Veja LICENSE para mais informações.

👨‍💻 Autor
Desenvolvido por [FELIPE FERREIRA]
