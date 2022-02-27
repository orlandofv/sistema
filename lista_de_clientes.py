# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QMessageBox, QProgressDialog

from clientes import Cliente
from powergrid import MainWindow as PowerGrid


class MainWindow(PowerGrid):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.child_form = Cliente
        self.defautl_table_id = 'CL20181111111'
        self.table_name = 'clientes'

        self.search_data.textChanged.connect(self.enche_items)
        self.export_csv.triggered.connect(self.export_para_csv)
        self.search_data.setText('a')
        self.search_data.setText('')

        if len(self.table_data) > 0:
            recibo = self.imprimir_lista('templates/admin/pessoal_template.html', self.table_data, self.table_header)
            self.print.triggered.connect(lambda: self.preview_dialog(recibo))

        self.sms_action.setVisible(False)

    def enche_items(self):
        header = [
            'ID',
            'Nome',
            'Endereço',
            'NUIT',
            'Email',
            'Contactos',
            'Estado',
            'Crédito Máximo',
            'Valor p/ Desconto',
            'Desconto (%)',
            'Actualização',
            'Actualizado por',
            'Notas'
        ]

        sql = """select cod, nome, endereco, NUIT, email, contactos, estado, credito, valor_minimo, desconto, modified, 
        modified_by, obs from clientes WHERE nome like "%{nome}%" """.format(nome=self.search_data.text())

        self.cur.execute(sql)
        lista = self.cur.fetchall()
        data = [list(str(item) for item in t) for t in lista]

        if len(data) > 0:
            for x in data:
                if int(x[6]) == 1:
                    x[6] = 'Activo'
                else:
                    x[6] = 'Inactivo'

        self.fill_table(header, data, (0, 3, 4, 8, 9))
        self.total_items.setText('ITEMS: {}'.format(self.totalItems))

        self.table_header = header
        self.table_data = data

        return header, data

