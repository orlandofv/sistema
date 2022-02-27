from decimal import Decimal
from facturacao_classe import Facturacao

f = Facturacao()

cod = ""
numero = 1
coddocumento = "DC20181111111"
codcliente = "CL20181111111"
# data = today
custo = Decimal(0)
subtotal = Decimal(0)
desconto = Decimal(0)
taxa = Decimal(0)
total = Decimal(0)
lucro = Decimal(0)
debito = Decimal(0)
credito = Decimal(0)
saldo = Decimal(0)
troco = Decimal(0)
banco = Decimal(0)
cash = Decimal(0)
transferencia = Decimal(0)
estado = 1
extenso = ""
# ano = ANO_ACTUAL
# mes = MES
obs = ""
# created = today
# modified = today
modified_by = "administrador"
created_by = "administrador"
finalizado = 0
caixa = "CX2019819UShi"
pago = Decimal(0)
comissao = Decimal(0)
pagamento = Decimal(0)

# facturacaodetalhe table fields
codfacturacao = "FT2019121212"
f.codproduto = "C-000007"
custo_produto = Decimal(0)
preco = Decimal(0)
quantidade = Decimal(0)
subtotal_produto = Decimal(0)
desconto_produto = Decimal(0)
taxa_produto = Decimal(0)
total_produto = Decimal(0)
lucro_produto = Decimal(0)
f.codarmazem = "AR201875cNP1"

#MySQL DB Connection
conn = ""
cur = ""
f.actualizar_detalhes = True

# f.delete_data("FT2019121212")
r = f.create_invoice(codfacturacao, caixa, coddocumento, codcliente, modified_by)

p = f.get_valor_taxa("TX20182222222")

p = f.get_produto_detalhe("C-000007", "AR201875cNP1")
print(p)

i = Decimal(0)