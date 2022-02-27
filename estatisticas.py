
import sys
from PyQt5.QtWidgets import (QApplication, QDialog, QCommandLinkButton, QGridLayout, QMessageBox)

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QMargins

from flowlayout import FlowLayout
from lista_de_recibos import MainWindow as nao_pagas

class Estatisticas(QDialog):


    def __init__(self, parent=None):
        super(Estatisticas, self).__init__(parent)

        if self.parent() is not None:
            self.empresa = self.parent().empresa
            self.cur = self.parent().cur
            self.conn = self.parent().conn
            self.user = self.parent().user
        else:
            self.empresa = "Empresa Teste"

        self.ui()
        self.setWindowTitle("Estatísticas/Relatórios")

    def ui(self):

        familias = QCommandLinkButton('Familias', 'Total de items {}'.format(self.totais('cod', 'familia')))
        familias.setIcon(QIcon("./icons/familias.ico"))
        subfamilias = QCommandLinkButton('Subfamilias', 'Total de items {}'.format(self.totais('cod', 'subfamilia')))
        subfamilias.setIcon(QIcon("./icons/subfamilias.ico"))
        produtos = QCommandLinkButton('Produtos/Serviços', 'Total de items {}'.format(self.totais('cod', 'produtos')))
        produtos.setIcon(QIcon("./icons/produtos.ico"))
        armazens = QCommandLinkButton('Armazéns', 'Total de items {}'.format(self.totais('cod', 'armazem')))
        armazens.setIcon(QIcon("./icons/armazens.ico"))
        stock = QCommandLinkButton('Stock', 'Total de items {}'.format(self.totais('cod', 'stock')))
        stock.setIcon(QIcon("./icons/stock.ico"))
        clientes = QCommandLinkButton('Clientes', 'Total de items {}'.format(self.totais('cod', 'clientes')))
        clientes.setIcon(QIcon("./icons/clientes.ico"))
        fornecedores = QCommandLinkButton('Fornecedores',
                                          'Total de items {}'.format(self.totais('cod', 'fornecedores')))
        fornecedores.setIcon(QIcon("./icons/fornecedores.ico"))

        taxas = QCommandLinkButton('Taxas',
                                          'Total de items {}'.format(self.totais('cod', 'taxas')))
        taxas.setIcon(QIcon("./icons/taxas.ico"))

        documentos = QCommandLinkButton('Tipos de Documentos',
                                          'Total de items {}'.format(self.totais('cod', 'documentos')))
        documentos.setIcon(QIcon("./icons/documentos.ico"))

        usuarios = QCommandLinkButton('Usuários', 'Total de items {}'.format(self.totais('cod', 'users')))
        usuarios.setIcon(QIcon("./icons/users.ico"))
        facturas = QCommandLinkButton('Todas Facturas',
                                      'Total de items {}'.format(self.totais('cod',
                                                                             "facturacao WHERE coddocumento='DC20182222222' ")))
        facturas.setIcon(QIcon("./icons/familias.ico"))

        facturas_nao_pagas = QCommandLinkButton('Facturas não Pagas',
                                                'Total de items {}'.format(self.totais('cod',
                                                                                       "facturacao WHERE coddocumento='DC20182222222' and saldo>0")))
        facturas_nao_pagas.setIcon(QIcon("./icons/coin_stacks_copper_remove.ico"))
        
        facturas_fornecedores = QCommandLinkButton('Facturas de Fornecedores',
                                                   'Total de items {}'.format(self.totais('cod', 'stock')))
        facturas_fornecedores.setIcon(QIcon("./icons/familias.ico"))
        vds = QCommandLinkButton('Vendas a Dinheiro',
                                 'Total de items {}'.format(self.totais('cod',
                                                                        "facturacao WHERE coddocumento='DC20181111111' ")))
        vds.setIcon(QIcon("./icons/Dollar.ico"))
        requisicoes = QCommandLinkButton('Requisicões de Stock', 'Total de items {}'.format(self.totais('cod', "requisicao")))
        requisicoes.setIcon(QIcon("./icons/familias.ico"))
        requisicoes_pendentes = QCommandLinkButton('Requisicoes pendentes',
                                                   'Total de items {}'.format(self.totais('cod', "requisicao WHERE estado=0")))
        requisicoes_pendentes.setIcon(QIcon("./icons/familias.ico"))
        requisicoes_aprovadas = QCommandLinkButton('Requisicoes aprovadas',
                                                   'Total de items {}'.format(self.totais('cod', "requisicao WHERE estado=1")))
        requisicoes_aprovadas.setIcon(QIcon("./icons/familias.ico"))
        requisicoes_reprovadas = QCommandLinkButton('Requisicoes reprovadas',
                                                    'Total de items {}'.format(self.totais('cod', "requisicao WHERE finalizado=0")))
        requisicoes_reprovadas.setIcon(QIcon("./icons/familias.ico"))

        gridlayout = QGridLayout()
        gridlayout.setSpacing(0)
        gridlayout.setContentsMargins(QMargins(0, 0, 0, 0))

        gridlayout.addWidget(familias, 0, 0)
        gridlayout.addWidget(subfamilias, 0, 1)
        gridlayout.addWidget(produtos, 0, 2)
        gridlayout.addWidget(armazens, 0, 3)
        gridlayout.addWidget(stock, 1, 0)
        gridlayout.addWidget(clientes, 1, 1)
        gridlayout.addWidget(fornecedores, 1, 2)
        gridlayout.addWidget(taxas, 1, 3)
        gridlayout.addWidget(documentos, 2, 0)
        gridlayout.addWidget(usuarios, 2, 1)
        gridlayout.addWidget(facturas, 2, 2)
        gridlayout.addWidget(facturas_nao_pagas, 2, 3)
        gridlayout.addWidget(facturas_fornecedores, 3, 0)
        gridlayout.addWidget(vds, 3, 1)

        self.setLayout(gridlayout)
        # Texte de FlowLayout()
        # layout = FlowLayout()
        # layout.addWidget(familias)
        # layout.addWidget(subfamilias)
        # layout.addWidget(produtos)
        # layout.addWidget(armazens)
        # layout.addWidget(stock)
        # layout.addWidget(clientes)
        # layout.addWidget(fornecedores)
        # layout.addWidget(taxas)
        # layout.addWidget(documentos)
        # layout.addWidget(usuarios)
        # layout.addWidget(facturas)
        # layout.addWidget(facturas_nao_pagas)
        # layout.addWidget(facturas_fornecedores)
        # layout.addWidget(vds)
        # layout.addWidget(requisicoes)
        # layout.addWidget(requisicoes_pendentes)
        # layout.addWidget(requisicoes_aprovadas)
        # layout.addWidget(requisicoes_reprovadas)
        #
        # self.setLayout(layout)

        clientes.clicked.connect(self.parent().listaclientes)
        fornecedores.clicked.connect(self.parent().listafornecedores)
        usuarios.clicked.connect(self.parent().listausers)
        familias.clicked.connect(self.parent().listafamilias)
        subfamilias.clicked.connect(self.parent().listasubfamilias)
        produtos.clicked.connect(self.parent().listaprodutos)
        armazens.clicked.connect(self.parent().listaarmazems)
        taxas.clicked.connect(self.parent().listataxas)
        stock.clicked.connect(self.parent().listastock)
        documentos.clicked.connect(self.parent().listadocumentos)
        facturas_nao_pagas.clicked.connect(self.parent().facturas_nao_pagas)

    def facturas_nao_pagas(self):
        np = nao_pagas(self)
        np.setWindowTitle('Lista de Facturas a Receber')
        np.showMaximized()

    def totais(self, coluna, tabela):
        sql = "SELECT COUNT({cod}) from {tabela} GROUP BY {cod}".format(cod=coluna, tabela=tabela)
        self.cur.execute(sql)
        data = self.cur.fetchall()

        return len(data)

    def lista_requesicao(self):
        from lista_de_requisicoes import MainWindow as lreq

        listareq = lreq(self)
        listareq.showMaximized()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    barcode =Estatisticas()
    barcode.show()
    sys.exit(app.exec_())