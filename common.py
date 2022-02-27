from os.path import join, dirname

class Invoice(dict):

    @property
    def total(self):
        return sum(l['amount'] for l in self['lines'])

    @property
    def vat(self):
        return self.total * 0.21

line=[{'item': {'name': 'Papas','reference': 'Azedas', 'price': 10.34}, 'quantity': 100, 'amount': 7*10.34},]
line+=[{'item': {'name': 'Siruma 500g','reference': 'VDKA-001', 'price': 10.34}, 'quantity': 7, 'amount': 7*10.34},]

inv = Invoice(customer={'name': 'Orlando Vilanculo', 'address': {'street': 'Smirnov street','zip': 1000, 'city': 'Montreux'}},
              clienteweb='www',
              clienteendereco='Baixa',
              clientenome='Dlakama Afonso',
              clientenuit=40045478,
              clientecontactos=21402518,
              empresanome='microgest',
              empresaendereco='Mahotas',
              empresanuit='123456789',
              empresacontactos=21402518,
              empresaweb='www.microgest.com',
              licenca='DGI-254879',
              lines=line,
              id='99999/122018',
              status='late',
              doc=123456,
              datadoc='2018-12-12',
              operador='Orlando Filipe Vilanculo',
              subtotal=100.00,
              desconto=0.00,
              iva=17.00,
              totalgeral=117.00,
              bottle=(open(join(dirname(__file__), 'bouteille.png'), 'rb'), 'image/png'))
print(inv)
from relatorio.templates.opendocument import Template
basic = Template(source='', filepath='basic.odt')
open('bonham_basic.odt', 'wb').write(basic.generate(o=inv).render().getvalue())
