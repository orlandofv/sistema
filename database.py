# Main database file
# Last update 07-05-2020
# Author: Orlando Filipe Vilanculos vilankazi@gmail.com

from sqlalchemy import Column, Integer, String, Date, DateTime, DECIMAL
from sqlalchemy import Sequence

class User (
	__tablename__ = 'users'
	
	cod = Column(String(50), primary_key=True)
	senha = Column(String(255))
	nome = Column(String(255))
	endereco = Column(String(255))
	sexo = Column(String(10)
	email = Column(String(255)
	nascimento = Column(Date) DEFAULT '1980-01-01'
	contacto = Column(String(255))
	tipo = Column(String(255))
	numero = Column(String(20))
	nacionalidade = Column(String(255)) default 'Moçambique'
	obs = Column(String(255))
	created = Column(Date)
	modified = Column(Date)
	modified_by = Column(String(255))
	created_by = Column(String(255))
	estado	= Column(Integer) DEFAULT 1
	admin	= Column(Integer) DEFAULT 1
	gestor = Column(Integer) DEFAULT 0

class Armazem (
	__tablename__ = 'armazem'
	
	cod = Column(String(255)) NOT NULL UNIQUE
	nome = Column(String(255)) NOT NULL UNIQUE
	endereco = Column(String(255))
	obs = Column(String(255))
	estado	= Column(Integer) DEFAULT 1
	created = Column(Date)
	modified = Column(Date)
	modified_by = Column(String(255))
	created_by = Column(String(255))
	PRIMARY KEY(cod)
	FOREIGN KEY(modified_by) REFERENCES users(cod)
	FOREIGN KEY(created_by) REFERENCES users(cod)


ALTER TABLE armazem ADD COLUMN mostrar = Column(Integer) DEFAULT 1

class caixa (
	cod = Column(String(255)) NOT NULL UNIQUE
	valor_inicial	DECIMAL(192) DEFAULT 0
	receitas	DECIMAL(192) DEFAULT 0
	despesas	DECIMAL(192) DEFAULT 0
	estado	= Column(Integer) DEFAULT 0
	created = Column(Date)
	modified = Column(Date)
	modified_by = Column(String(255))
	created_by = Column(String(255))
	obs = Column(String(255))
	PRIMARY KEY(cod)
	FOREIGN KEY(modified_by) REFERENCES users(cod)
	FOREIGN KEY(created_by) REFERENCES users(cod)

alter table caixa add column codarmazem = Column(String(50) DEFAULT 'AR201875cNP1'
ALTER TABLE caixa ADD CONSTRA= Column(Integer) codarmazem FOREIGN KEY(codarmazem) REFERENCES armazem(cod)

class caixadetalhe(
	cod = Column(Integer) Sequence NOT NULL PRIMARY KEY
	caixacod = Column(String(255))
	despesas = Column(Integer)
	receitas = Column(Integer)
	created = Column(Date)
	modified = Column(Date)
	modified_by = Column(String(255))
	created_by = Column(String(255))
	obs = Column(String(255))
	FOREIGN KEY(caixacod) REFERENCES caixa(cod)
	FOREIGN KEY(modified_by) REFERENCES users(cod)
	FOREIGN KEY(created_by) REFERENCES users(cod)


class receitas(
	cod = Column(Integer) Sequence NOT NULL PRIMARY KEY
	descricao = Column(String(255))
	valor DECIMAL(19 2)
	codcaixa = Column(String(50)
	codarmazem = Column(String(50)
	created = Column(Date)TIME
	modified = Column(Date)TIME
	modified_by = Column(String(50)
	created_by = Column(String(50)
	obs TEXT
	tipo = Column(Integer) DEFAULT 0
	estado = Column(Integer) DEFAULT 1
	FOREIGN KEY(codcaixa) REFERENCES caixa(cod) 
	FOREIGN KEY(created_by) REFERENCES users(cod)
	FOREIGN KEY(modified_by) REFERENCES users(cod) 
	FOREIGN KEY(codarmazem) REFERENCES armazem(cod)


class taxas (
	cod = Column(String(255)) NOT NULL UNIQUE
	nome = Column(String(40)NOT NULL UNIQUE
	valor	= Column(Integer) UNIQUE
	obs = Column(String(255))
	created = Column(Date)
	modified = Column(Date)
	modified_by = Column(String(255))
	created_by = Column(String(255))
	PRIMARY KEY(cod)
	FOREIGN KEY(modified_by) REFERENCES users(cod)
	FOREIGN KEY(created_by) REFERENCES users(cod)


class familia (
	cod = Column(String(255)) NOT NULL UNIQUE
	nome = Column(String(255)) NOT NULL UNIQUE
	obs = Column(String(255))
	estado	= Column(Integer) DEFAULT 1
	created = Column(Date)
	modified = Column(Date)
	created_by = Column(String(255))
	modified_by = Column(String(255))
	stock	= Column(Integer) DEFAULT 1
	PRIMARY KEY(cod)
	FOREIGN KEY(modified_by) REFERENCES users(cod)
	FOREIGN KEY(created_by) REFERENCES users(cod)


class subfamilia (
	cod = Column(String(255)) NOT NULL UNIQUE
	nome = Column(String(255)) NOT NULL UNIQUE
	codfamilia = Column(String(255)) NOT NULL
	obs = Column(String(255))
	estado	= Column(Integer) DEFAULT 1
	created = Column(Date)
	modified = Column(Date)
	created_by = Column(String(255))
	modified_by = Column(String(255))
	PRIMARY KEY(cod)
	FOREIGN KEY(codfamilia) REFERENCES familia(cod)
	FOREIGN KEY(modified_by) REFERENCES users(cod)
	FOREIGN KEY(created_by) REFERENCES users(cod)


class produtos (
	cod = Column(String(255)) NOT NULL UNIQUE
	nome = Column(String(255)) NOT NULL UNIQUE
	cod_barras = Column(String(255))
	codfamilia = Column(String(255))
	codsubfamilia = Column(String(255))
	custo	DECIMAL(192)
	preco	DECIMAL(192)
	quantidade	DECIMAL(192)
	quantidade_m	DECIMAL(192)
	unidade = Column(String(255))
	obs = Column(String(255))
	estado	= Column(Integer)
	foto = Column(String(255))
	created = Column(Date)
	modified = Column(Date)
	modified_by = Column(String(255))
	created_by = Column(String(255))
	PRIMARY KEY(cod)
	FOREIGN KEY(codfamilia) REFERENCES familia(cod)
	FOREIGN KEY(codsubfamilia) REFERENCES subfamilia(cod)
	FOREIGN KEY(modified_by) REFERENCES users(cod)
	FOREIGN KEY(created_by) REFERENCES users(cod)


ALTER TABLE produtos ADD COLUMN preco1 DECIMAL(192) DEFAULT 0
ALTER TABLE produtos ADD COLUMN preco2 DECIMAL(192) DEFAULT 0
ALTER TABLE produtos ADD COLUMN preco3 DECIMAL(192) DEFAULT 0
ALTER TABLE produtos ADD COLUMN preco4 DECIMAL(192) DEFAULT 0
ALTER TABLE produtos ADD COLUMN tipo = Column(Integer) DEFAULT 0
ALTER TABLE produtos ADD COLUMN codtaxa = Column(String(255)) DEFAULT 'TX20182222222'
ALTER TABLE produtos ADD CONSTRA= Column(Integer) taxa FOREIGN KEY(codtaxa) REFERENCES taxas(cod) 
ALTER TABLE produtos ADD COLUMN quantidade_max	DECIMAL(192) DEFAULT 0
ALTER TABLE produtos ADD COLUMN favorito int default 0
ALTER TABLE produtos ADD COLUMN promocao int default 0
ALTER TABLE produtos ADD COLUMN preco_de_venda int default 0

class produtosdetalhe (
	cod	= Column(Integer) Sequence NOT NULL PRIMARY KEY
	codproduto = Column(String(255)) NOT NULL
	codarmazem = Column(String(255)) NOT NULL
	quantidade	DECIMAL(192)
	created = Column(Date)
	modified = Column(Date)
	modified_by = Column(String(255))
	created_by = Column(String(255))
	FOREIGN KEY(codproduto) REFERENCES produtos(cod)
	FOREIGN KEY (codarmazem) REFERENCES armazem(cod)
	FOREIGN KEY(modified_by) REFERENCES users(cod)
	FOREIGN KEY(created_by) REFERENCES users(cod)

ALTER TABLE produtosdetalhe ADD COLUMN validade date DEFAULT '1980-01-01'
ALTER TABLE produtosdetalhe ADD COLUMN contagem int default 0

class relacoes(
	cod = Column(Integer) Sequence NOT NULL PRIMARY KEY
	codproduto1 = Column(String(100) NOT NULL
	quantidade1 DECIMAL(192) DEFAULT 0
	codproduto2 = Column(String(100) NOT NULL
	quantidade2 DECIMAL(192) DEFAULT 0
	codarmazem = Column(String(50)
	created = Column(Date)
	modified = Column(Date)
	modified_by = Column(String(100)
	created_by = Column(String(100)
	obs = Column(String(255))
	FOREIGN KEY (codproduto1) REFERENCES produtos(cod)
	FOREIGN KEY (codproduto2) REFERENCES produtos(cod)
	FOREIGN KEY (codarmazem) REFERENCES armazem(cod)
	FOREIGN KEY (created_by) REFERENCES users(cod)
	FOREIGN KEY (modified_by) REFERENCES users(cod)


class clientes (
	cod = Column(String(255)) NOT NULL UNIQUE
	nome = Column(String(255)) NOT NULL UNIQUE
	endereco = Column(String(255))
	NUIT = Column(String(255))
	email = Column(String(255))
	contactos = Column(String(255))
	desconto	DECIMAL(192)
	valor_minimo	DECIMAL(192)
	obs = Column(String(255))
	estado = Column(Integer) default 1
	created = Column(Date)
	modified = Column(Date)
	modified_by = Column(String(255))
	created_by = Column(String(255))
	PRIMARY KEY(cod)
	FOREIGN KEY (created_by) REFERENCES users(cod)
	FOREIGN KEY (modified_by) REFERENCES users(cod)


ALTER TABLE clientes ADD COLUMN credito DECIMAL(192) DEFAULT 0

class fornecedores (
	cod = Column(String(255)) NOT NULL UNIQUE
	nome = Column(String(255)) NOT NULL UNIQUE
	endereco = Column(String(255))
	NUIT = Column(String(255))
	email = Column(String(255))
	contactos = Column(String(255))
	obs = Column(String(255))
	estado = Column(Integer) default 1
	created = Column(Date)
	modified = Column(Date)
	modified_by = Column(String(255))
	created_by = Column(String(255))
	PRIMARY KEY(cod)
	FOREIGN KEY (created_by) REFERENCES users(cod)
	FOREIGN KEY (modified_by) REFERENCES users(cod)


class stock (
	cod = Column(String(255)) NOT NULL UNIQUE
	fornecedor = Column(String(255))
	numero	DECIMAL(192)
	data = Column(Date)
	valor	DECIMAL(192) DEFAULT 0
	pago	DECIMAL(192) DEFAULT 0
	taxa	DECIMAL(192) DEFAULT 0
	subtotal	DECIMAL(192) DEFAULT 0
	total	DECIMAL(192) DEFAULT 0
	created = Column(Date) 
	modified = Column(Date)
	modified_by = Column(String(255))
	created_by = Column(String(255))
	estado	= Column(Integer) DEFAULT 0
	PRIMARY KEY(cod)
	FOREIGN KEY (created_by) REFERENCES users(cod)
	FOREIGN KEY (modified_by) REFERENCES users(cod)


ALTER TABLE `stock` ADD COLUMN saldo DECIMAL(192) DEFAULT 0
ALTER TABLE `stock` CHANGE COLUMN `numero` `numero` = Column(String(255)) DEFAULT "" AFTER `fornecedor`

class stockdetalhe (
	cod	= Column(Integer) NOT NULL Sequence
	codstock = Column(String(255))
	codproduto = Column(String(255))
	codarmazem = Column(String(255))
	quantidade	DECIMAL(192) DEFAULT 0
	valor	DECIMAL(192) DEFAULT 0
	taxa	DECIMAL(192) DEFAULT 0
	subtotal	DECIMAL(192) DEFAULT 0
	total	DECIMAL(192) DEFAULT 0
	PRIMARY KEY(cod)
	FOREIGN KEY(codstock) REFERENCES stock(cod)
	FOREIGN KEY(codproduto) REFERENCES produtos(cod)
	FOREIGN KEY(codarmazem) REFERENCES armazem(cod)


ALTER TABLE stockdetalhe ADD COLUMN custo decimal(19 2) default 0
ALTER TABLE stockdetalhe ADD COLUMN validade datetime default "2021-01-01"

class documentos (
	cod = Column(String(255)) NOT NULL UNIQUE
	nome = Column(String(255)) NOT NULL UNIQUE
	subtotal	= Column(Integer) DEFAULT 1
	desconto	= Column(Integer) DEFAULT 1
	taxa	= Column(Integer) DEFAULT 1
	total	= Column(Integer) DEFAULT 1
	obs = Column(String(255))
	created = Column(Date)
	modified = Column(Date)
	modified_by = Column(String(255))
	created_by = Column(String(255))
	stock = Column(Integer) DEFAULT 0
	PRIMARY KEY (cod)
	FOREIGN KEY (created_by) REFERENCES users(cod)
	FOREIGN KEY (modified_by) REFERENCES users(cod)


ALTER TABLE documentos ADD COLUMN estado = Column(Integer)(11) default 1
alter table documentos add Column visivel int default 1

class facturacao (
	cod = Column(String(255)) NOT NULL UNIQUE
	numero	= Column(Integer)
	coddocumento = Column(String(255))
	codcliente = Column(String(255))
	data = Column(Date)
	custo	DECIMAL(192) DEFAULT 0
	subtotal	DECIMAL(192) DEFAULT 0
	desconto	DECIMAL(192) DEFAULT 0
	taxa	DECIMAL(192) DEFAULT 0
	total	DECIMAL(192) DEFAULT 0
	lucro	DECIMAL(192) DEFAULT 0
	debito	DECIMAL(192) DEFAULT 0
	credito	DECIMAL(192) DEFAULT 0
	saldo	DECIMAL(192) DEFAULT 0
	troco	DECIMAL(192) DEFAULT 0
	banco	DECIMAL(192) DEFAULT 0
	cash	DECIMAL(192) DEFAULT 0
	tranferencia	DECIMAL(192) DEFAULT 0
	estado	= Column(Integer) DEFAULT 1
	extenso = Column(String(255))
	ano	= Column(Integer)
	mes	= Column(Integer)
	obs	varchar (255)
	created = Column(Date)
	modified = Column(Date)
	modified_by = Column(String(255))
	created_by = Column(String(255))
	finalizado	= Column(Integer) DEFAULT 0
	caixa = Column(String(255)) NOT NULL
	pago	DECIMAL(192) DEFAULT 0
	validade = Column(Date)
	FOREIGN KEY(caixa) REFERENCES caixa(cod)
	FOREIGN KEY(codcliente) REFERENCES clientes(cod)
	PRIMARY KEY(cod)
	FOREIGN KEY (created_by) REFERENCES users(cod)
	FOREIGN KEY (modified_by) REFERENCES users(cod)


# Update 10-04-2019 as duas colunas sao usadas para agencia de Viagem apenas
ALTER TABLE facturacao ADD COLUMN comissao DECIMAL(192) DEFAULT 0
ALTER TABLE facturacao ADD COLUMN pagamento DECIMAL(192) DEFAULT 0
# para por o nome ao gravar o documento 
ALTER TABLE facturacao ADD COLUMN nome varchar(255))

class facturacaodetalhe (
	cod	= Column(Integer) NOT NULL Sequence
	codfacturacao = Column(String(255)) NOT NULL
	codproduto = Column(String(255))
	custo	DECIMAL(192) DEFAULT 0
	preco	DECIMAL(192) DEFAULT 0
	quantidade	DECIMAL(192) DEFAULT 0
	subtotal	DECIMAL(192) DEFAULT 0
	desconto	DECIMAL(192) DEFAULT 0
	taxa	DECIMAL(192) DEFAULT 0
	total	DECIMAL(192) DEFAULT 0
	lucro	DECIMAL(192) DEFAULT 0
	PRIMARY KEY(cod)
	FOREIGN KEY(codfacturacao) REFERENCES facturacao(cod)

ALTER TABLE facturacaodetalhe ADD COLUMN codarmazem = Column(String(50) DEFAULT 'AR201875cNP1'
ALTER TABLE facturacaodetalhe ADD CONSTRA= Column(Integer) armazem FOREIGN KEY(codarmazem) REFERENCES armazem(cod)
# UP= Column(Date) 13-12-2018 precisamos saber em que stock o produto saiu
ALTER TABLE facturacaodetalhe ADD COLUMN codstock = Column(String(50)
ALTER TABLE facturacaodetalhe ADD CONSTRA= Column(Integer) codstock FOREIGN KEY(codstock) REFERENCES stock(cod)

class requisicao (
	cod = Column(String(255)) NOT NULL UNIQUE
	numero	= Column(Integer)
	coddocumento = Column(String(255))
	codcliente = Column(String(255))
	codarmazem = Column(String(255))
	data = Column(Date)
	custo	DECIMAL(192) DEFAULT 0
	subtotal	DECIMAL(192) DEFAULT 0
	desconto	DECIMAL(192) DEFAULT 0
	taxa	DECIMAL(192) DEFAULT 0
	total	DECIMAL(192) DEFAULT 0
	lucro	DECIMAL(192) DEFAULT 0
	debito	DECIMAL(192) DEFAULT 0
	credito	DECIMAL(192) DEFAULT 0
	saldo	DECIMAL(192) DEFAULT 0
	troco	DECIMAL(192) DEFAULT 0
	banco	DECIMAL(192) DEFAULT 0
	cash	DECIMAL(192) DEFAULT 0
	tranferencia	DECIMAL(192) DEFAULT 0
	estado	= Column(Integer) DEFAULT 1
	extenso = Column(String(255))
	ano	= Column(Integer)
	mes	= Column(Integer)
	obs	varchar (255)
	created = Column(Date)
	modified = Column(Date)
	created_by = Column(String(255))
	finalizado	= Column(Integer) DEFAULT 0
	modified_by = Column(String(255))
	caixa = Column(String(255)) NOT NULL
	pago	DECIMAL(192) DEFAULT 0
	validade = Column(Date)
	FOREIGN KEY(caixa) REFERENCES caixa(cod)
	FOREIGN KEY(codcliente) REFERENCES clientes(cod)
	FOREIGN KEY(codarmazem) REFERENCES armazem(cod)
	PRIMARY KEY(cod)
	FOREIGN KEY (created_by) REFERENCES users(cod)
	FOREIGN KEY (modified_by) REFERENCES users(cod)


class requisicaodetalhe (
	cod	= Column(Integer) NOT NULL Sequence
	codrequisicao = Column(String(255)) NOT NULL
	codarmazem1 = Column(String(50) DEFAULT 'AR201875cNP1'
	codarmazem2 = Column(String(50) DEFAULT 'AR201875cNP1'
	codproduto = Column(String(255))
	custo	DECIMAL(192) DEFAULT 0
	preco	DECIMAL(192) DEFAULT 0
	quantidade	DECIMAL(192) DEFAULT 0
	subtotal	DECIMAL(192) DEFAULT 0
	desconto	DECIMAL(192) DEFAULT 0
	taxa	DECIMAL(192) DEFAULT 0
	total	DECIMAL(192) DEFAULT 0
	lucro	DECIMAL(192) DEFAULT 0
	PRIMARY KEY(cod)
	FOREIGN KEY(codrequisicao) REFERENCES requisicao(cod)


class recibos (
	cod = Column(String(255)) NOT NULL UNIQUE
	numero	= Column(Integer)
	codfactura = Column(String(255))
	codcliente = Column(String(255))
	data = Column(Date)
	total	DECIMAL(192) DEFAULT 0
	troco	DECIMAL(192) DEFAULT 0
	banco	DECIMAL(192) DEFAULT 0
	cash	DECIMAL(192) DEFAULT 0
	tranferencia	DECIMAL(192) DEFAULT 0
	estado	= Column(Integer) DEFAULT 1
	extenso = Column(String(255))
	ano	= Column(Integer)
	mes	= Column(Integer)
	obs	varchar (255)
	created = Column(Date)
	modified = Column(Date)
	modified_by = Column(String(255))
	created_by = Column(String(255))
	finalizado	= Column(Integer) DEFAULT 0
	caixa = Column(String(255)) NOT NULL
	PRIMARY KEY(cod)
	FOREIGN KEY(codcliente) REFERENCES clientes(cod)
	FOREIGN KEY(codfactura) REFERENCES facturacao(cod)
	FOREIGN KEY(caixa) REFERENCES caixa(cod)
	FOREIGN KEY (created_by) REFERENCES users(cod)
	FOREIGN KEY (modified_by) REFERENCES users(cod)


class recibosdetalhe (
	cod	= Column(Integer) NOT NULL Sequence
	codrecibo = Column(String(255)) NOT NULL
	factura	= Column(Integer) NOT NULL
	pago	DECIMAL(192) DEFAULT 0
	saldo	DECIMAL(192) DEFAULT 0
	descricao = Column(String(255))
	codfactura = Column(String(255))
	PRIMARY KEY(cod)
	FOREIGN KEY(codrecibo) REFERENCES recibos(cod)


class pagamentos (
	cod = Column(Integer) Sequence NOT NULL PRIMARY KEY
	codfornecedor = Column(String(255))
	codstock = Column(String(255))
	debito DECIMAL(192) DEFAULT '0'
	credito DECIMAL(192) DEFAULT '0'
	saldo DECIMAL(192) DEFAULT '0'
	documento = Column(String(255))
	`created` = Column(Date)
	`modified` = Column(Date)
	`modified_by` = Column(String(255)) DEFAULT ""
	`created_by` = Column(String(255)) DEFAULT ""
	FOREIGN KEY (codfornecedor) REFERENCES fornecedores(cod)
	FOREIGN KEY (codstock) REFERENCES stock(cod)
	FOREIGN KEY (created_by) REFERENCES users(cod)
	FOREIGN KEY (modified_by) REFERENCES users(cod)
)

class config(
	empresa = Column(String(255)) UNIQUE NOT NULL PRIMARY KEY 
	f_template = Column(String(255)) DEFAULT ""
	rec_template = Column(String(255)) DEFAULT ""
	req_template = Column(String(255)) DEFAULT ""
	c_cliente = Column(Integer) DEFAULT 1
	cliente_n = Column(Integer) DEFAULT 1
	saldo = Column(Integer) DEFAULT 1
	c_inactivo = Column(Integer) DEFAULT 1
	desc_automatico = Column(Integer) DEFAULT 1
	ac_credito = Column(Integer) DEFAULT 1
	pos1 = Column(String(255)) DEFAULT ""
	pos2 = Column(String(255)) DEFAULT ""
	pos3 = Column(String(255)) DEFAULT ""
	pos4 = Column(String(255)) DEFAULT ""
	pos5 = Column(String(255)) DEFAULT ""
	so_vd = Column(Integer) DEFAULT 0
	iva_incluso = Column(Integer) DEFAULT 1
	regime = Column(Integer) DEFAULT 1
	isento = Column(Integer) DEFAULT 1
	vendas_zero = Column(Integer) DEFAULT 1
	cop1 = Column(Integer) DEFAULT 1
	cop2 = Column(Integer) DEFAULT 1
	cop3 = Column(Integer) DEFAULT 1
	cop4 = Column(Integer) DEFAULT 1
	cop5 = Column(Integer) DEFAULT 1)

class `hospedes` (
	`cod` varchar(50) NOT NULL
	`nome` varchar(255)) NOT NULL
	`apelido` varchar(255)) DEFAULT ""
	`endereco` varchar(255)) DEFAULT ""
	`sexo` varchar(15) DEFAULT ""
	`email` varchar(255)) DEFAULT ""
	`nascimento` varchar(50) DEFAULT ""
	`contactos` varchar(255)) DEFAULT ""
	`emergencia` varchar(255)) DEFAULT ""
	`tipo_id` varchar(20) DEFAULT ""
	`numero_id` varchar(20) DEFAULT ""
	`validade_id` varchar(50) DEFAULT ""
	`nacionalidade` varchar(50) DEFAULT ""
	`obs` varchar(255)) DEFAULT ""
	`estado` int(11) DEFAULT '1'
	`created` = Column(Date)
	`modified` = Column(Date)
	`modified_by` varchar(255)) DEFAULT ""
	`created_by` varchar(255)) DEFAULT ""
	PRIMARY KEY (`cod`)
	FOREIGN KEY (created_by) REFERENCES users(cod)
	FOREIGN KEY (modified_by) REFERENCES users(cod)
) ENGINE=InnoDB

class `categorias` (
	`cod` int(11) NOT NULL Sequence
	`valor` decimal(192) DEFAULT '0.00'
	`categoria` varchar(255)) NOT NULL
	`obs` varchar(255)) DEFAULT ""
	`created` = Column(Date)
	`modified` = Column(Date)
	`modified_by` varchar(255)) DEFAULT ""
	`created_by` varchar(255)) DEFAULT ""
	PRIMARY KEY (`cod`)
	FOREIGN KEY (created_by) REFERENCES users(cod)
	FOREIGN KEY (modified_by) REFERENCES users(cod)
) ENGINE=InnoDB

class `quartos` (
	`cod` int(11) NOT NULL
	`cod_preco` int(11) NOT NULL
	`preco` decimal(192) DEFAULT '0.00'
	`estado` int(11) DEFAULT '1'
	`ocupado` int(11) DEFAULT '0'
	`obs` varchar(255)) DEFAULT ""
	`created` = Column(Date)
	`modified` = Column(Date)
	`modified_by` varchar(255)) DEFAULT ""
	`created_by` varchar(255)) DEFAULT ""
	PRIMARY KEY (`cod`)
	KEY `cod_preco` (`cod_preco`)
	FOREIGN KEY (`cod_preco`) REFERENCES `categorias` (`cod`)
	FOREIGN KEY (created_by) REFERENCES users(cod)
	FOREIGN KEY (modified_by) REFERENCES users(cod)
) ENGINE=InnoDB

class reservas(
	cod int(11) not null Sequence
	data_entrada = Column(Date)
	data_saida = Column(Date)
	cod_cliente varchar(255))
	obs varchar(255))
	`created` = Column(Date)
	`modified` = Column(Date)
	`modified_by` = Column(String(255)) DEFAULT ""
	`created_by` = Column(String(255)) DEFAULT ""
	PRIMARY KEY (cod)
	FOREIGN KEY (cod_cliente) REFERENCES hospedes(cod)
	FOREIGN KEY (created_by) REFERENCES users(cod)
	FOREIGN KEY (modified_by) REFERENCES users(cod)


ALTER TABLE reservas ADD COLUMN `cod_quarto` = Column(Integer)(11) AFTER cod_cliente
ALTER TABLE reservas ADD COLUMN estado int default 1 DEFAULT 1 AFTER created_by
ALTER TABLE reservas ADD COLUMN `hospede` = Column(String(255)) DEFAULT "" AFTER estado
ALTER TABLE reservas ADD COLUMN `voucher` = Column(String(50) DEFAULT ""
ALTER TABLE reservas ADD COLUMN `pagamento` = Column(String(50) DEFAULT ""
ALTER TABLE reservas ADD COLUMN `moeda` = Column(String(50) DEFAULT ""
ALTER TABLE reservas ADD COLUMN `codfacturacao` = Column(String(50) DEFAULT ""
ALTER TABLE reservas ADD FOREIGN KEY (`cod_quarto`) REFERENCES `quartos` (`cod`)


class `check_in` (
	`cod` = Column(Integer)(11) NOT NULL Sequence
	`data_entrada` = Column(Date)
	`data_saida` = Column(Date)
	`cod_cliente` = Column(String(255))
	`cod_quarto` = Column(Integer)(11)
	`total` DECIMAL(192) DEFAULT '0.00'
	`pago` DECIMAL(192) DEFAULT '0.00'
	`divida` DECIMAL(192) DEFAULT '0.00'
	`obs` = Column(String(255)) DEFAULT ""
	`created` = Column(Date)
	`modified` = Column(Date)
	`modified_by` = Column(String(255)) DEFAULT ""
	`created_by` = Column(String(255)) DEFAULT ""
	`estado` = Column(Integer)(11) DEFAULT '0'
	PRIMARY KEY (`cod`)
	INDEX `cod_cliente` (`cod_cliente`)
	INDEX `cod_quarto` (`cod_quarto`)
	FOREIGN KEY (`cod_cliente`) REFERENCES `hospedes` (`cod`)
	FOREIGN KEY (`cod_quarto`) REFERENCES `quartos` (`cod`)
	FOREIGN KEY (created_by) REFERENCES users(cod)
	FOREIGN KEY (modified_by) REFERENCES users(cod)
)
ENGINE=InnoDB

ALTER TABLE check_in ADD COLUMN `hospede` = Column(String(255)) DEFAULT ""
ALTER TABLE check_in ADD COLUMN `voucher` = Column(String(50) DEFAULT ""
ALTER TABLE check_in ADD COLUMN `pagamento` = Column(String(50) DEFAULT ""
ALTER TABLE check_in ADD COLUMN `moeda` = Column(String(50) DEFAULT ""
ALTER TABLE check_in ADD COLUMN `codfacturacao` = Column(String(50) DEFAULT ""

class `alunos` (
	`cod` varchar(50) NOT NULL
	`nome` varchar(255)) NOT NULL
	`apelido` varchar(255)) DEFAULT ""
	`endereco` varchar(255)) DEFAULT ""
	`sexo` varchar(15) DEFAULT ""
	`email` varchar(255)) DEFAULT ""
	`nascimento` varchar(50) DEFAULT ""
	`contactos` varchar(255)) DEFAULT ""
	`emergencia` varchar(255)) DEFAULT ""
	`tipo_id` varchar(20) DEFAULT ""
	`numero_id` varchar(20) DEFAULT ""
	`validade_id` varchar(50) DEFAULT ""
	`nacionalidade` varchar(50) DEFAULT ""
	`obs` varchar(255)) DEFAULT ""
	`estado` int(11) DEFAULT '1'
	`created` = Column(Date)
	`modified` = Column(Date)
	`modified_by` varchar(255)) DEFAULT ""
	`created_by` varchar(255)) DEFAULT ""
	foto varchar(255)) DEFAULT ""
	PRIMARY KEY (`cod`)
	FOREIGN KEY (created_by) REFERENCES users(cod)
	FOREIGN KEY (modified_by) REFERENCES users(cod)
) ENGINE=InnoDB

class `estudantes` (
	`cod` varchar(50) NOT NULL
	`nome` varchar(255)) NOT NULL
	`apelido` varchar(255)) DEFAULT ""
	`endereco` varchar(255)) DEFAULT ""
	`sexo` varchar(15) DEFAULT ""
	`email` varchar(255)) DEFAULT ""
	`nascimento` varchar(50) DEFAULT ""
	`contactos` varchar(255)) DEFAULT ""
	`emergencia` varchar(255)) DEFAULT ""
	`tipo_id` varchar(20) DEFAULT ""
	`numero_id` varchar(20) DEFAULT ""
	`validade_id` varchar(50) DEFAULT ""
	`nacionalidade` varchar(50) DEFAULT ""
	`obs` varchar(255)) DEFAULT ""
	`estado` int(11) DEFAULT '1'
	`created` = Column(Date)
	`modified` = Column(Date)
	`modified_by` varchar(255)) DEFAULT ""
	`created_by` varchar(255)) DEFAULT ""
	foto varchar(255)) DEFAULT ""
	empresa varchar(50)
	PRIMARY KEY (`cod`)
	FOREIGN KEY (`empresa`) REFERENCES `clientes`(`cod`)
	FOREIGN KEY (created_by) REFERENCES users(cod)
	FOREIGN KEY (modified_by) REFERENCES users(cod)
)ENGINE=InnoDB

class `instrutores` (
	`cod` varchar(50) NOT NULL
	`nome` varchar(255)) NOT NULL
	`apelido` varchar(255)) DEFAULT ""
	`endereco` varchar(255)) DEFAULT ""
	`sexo` varchar(15) DEFAULT ""
	`email` varchar(255)) DEFAULT ""
	`nascimento` varchar(50) DEFAULT ""
	`contactos` varchar(255)) DEFAULT ""
	`emergencia` varchar(255)) DEFAULT ""
	`tipo_id` varchar(20) DEFAULT ""
	`numero_id` varchar(20) DEFAULT ""
	`validade_id` varchar(50) DEFAULT ""
	`nacionalidade` varchar(50) DEFAULT ""
	`obs` varchar(255)) DEFAULT ""
	`estado` int(11) DEFAULT '1'
	`created` = Column(Date)
	`modified` = Column(Date)
	`modified_by` varchar(255)) DEFAULT ""
	`created_by` varchar(255)) DEFAULT ""
	foto varchar(255)) DEFAULT ""
	PRIMARY KEY (`cod`)
	FOREIGN KEY (created_by) REFERENCES users(cod)
	FOREIGN KEY (modified_by) REFERENCES users(cod)
)ENGINE=InnoDB

class cursos(
	cod = Column(Integer) Sequence NOT NULL PRIMARY KEY
	nome varchar(255))
	data_inicio = Column(Date)
	data_final = Column(Date)
	duracao DECIMAL (6 2)
	valor DECIMAL(19 2) default 0
	percentagem DECIMAL(10 2) default 0
	`obs` varchar(255)) DEFAULT ""
	`estado` int(11) DEFAULT 1
	`created` = Column(Date)
	`modified` = Column(Date)
	`modified_by` varchar(255)) DEFAULT ""
	`created_by` varchar(255)) DEFAULT ""
	FOREIGN KEY (created_by) REFERENCES users(cod)
	FOREIGN KEY (modified_by) REFERENCES users(cod)
)ENGINE=InnoDB

class `formacao` (
	cod = Column(Integer) Sequence NOT NULL PRIMARY KEY
	nome varchar(255)) not NULL UNIQUE
	`codcurso` = Column(Integer)
	codempresa = Column(String(50)
	codestudante = Column(String(50)
	valor DECIMAL(19 2) default 0
	valor_primeira DECIMAL(19 2) default 0
	valor_segunda DECIMAL(19 2) default 0
	valor_saldo DECIMAL(19 2) default 0
	teoria DECIMAL(10 2) default 0
	pratica DECIMAL(10 2) default 0
	comportamento varchar(15) DEFAULT ""
	resultado varchar(15) DEFAULT ""
	`obs` varchar(255)) DEFAULT ""
	`estado` int(11) DEFAULT '1'
	`created` = Column(Date)
	`modified` = Column(Date)
	`modified_by` varchar(255)) DEFAULT ""
	`created_by` varchar(255)) DEFAULT ""
	FOREIGN KEY (`codcurso`) REFERENCES `cursos`(`cod`)
	FOREIGN KEY (`codempresa`) REFERENCES `clientes`(`cod`)
	FOREIGN KEY (codestudante) REFERENCES `estudantes`(`cod`)
	FOREIGN KEY (created_by) REFERENCES users(cod)
	FOREIGN KEY (modified_by) REFERENCES users(cod)
)ENGINE=InnoDB
alter table formacao add column data_inicio timestamp default now()
alter table formacao add column data_final timestamp default now()

class `certificado` (
	cod = Column(String(50) NOT NULL PRIMARY KEY
	numero = Column(String(50) NOT NULL UNIQUE
	`codformacao` = Column(Integer)
	codempresa = Column(String(50)
	codestudante = Column(String(50)
	`data` = Column(Date)
	`validade` = Column(Date)
	`obs` varchar(255)) DEFAULT ""
	`estado` int(11) DEFAULT '1'
	`created` = Column(Date)
	`modified` = Column(Date)
	`modified_by` varchar(255)) DEFAULT ""
	`created_by` varchar(255)) DEFAULT ""
	FOREIGN KEY (`codformacao`) REFERENCES `formacao`(`cod`)
	FOREIGN KEY (`codempresa`) REFERENCES `clientes`(`cod`)
	FOREIGN KEY (codestudante) REFERENCES `estudantes`(`cod`)
	FOREIGN KEY (created_by) REFERENCES users(cod)
	FOREIGN KEY (modified_by) REFERENCES users(cod)
)ENGINE=InnoDB

class mesas(
	cod int Sequence not null primary key
	numero int not null
	descricao varchar(50)
	codfacturacao varchar(50)
	estado	= Column(Integer) DEFAULT 0
	created = Column(Date)
	modified = Column(Date)
	modified_by = Column(String(255))
	created_by = Column(String(255))
	obs = Column(String(255))
	foreign key(codfacturacao) references facturacao(cod) ON DELETE CASCADE
	FOREIGN KEY (created_by) REFERENCES users(cod)
	FOREIGN KEY (modified_by) REFERENCES users(cod)


class cozinha (
	cod = Column(String(255)) NOT NULL UNIQUE
	numero	= Column(Integer)
	coddocumento = Column(String(255))
	codcliente = Column(String(255))
	codarmazem = Column(String(255))
	data = Column(Date)
	custo	DECIMAL(192) DEFAULT 0
	subtotal	DECIMAL(192) DEFAULT 0
	desconto	DECIMAL(192) DEFAULT 0
	taxa	DECIMAL(192) DEFAULT 0
	total	DECIMAL(192) DEFAULT 0
	lucro	DECIMAL(192) DEFAULT 0
	debito	DECIMAL(192) DEFAULT 0
	credito	DECIMAL(192) DEFAULT 0
	saldo	DECIMAL(192) DEFAULT 0
	troco	DECIMAL(192) DEFAULT 0
	banco	DECIMAL(192) DEFAULT 0
	cash	DECIMAL(192) DEFAULT 0
	tranferencia	DECIMAL(192) DEFAULT 0
	estado	= Column(Integer) DEFAULT 1
	extenso = Column(String(255))
	ano	= Column(Integer)
	mes	= Column(Integer)
	obs	varchar (255)
	created = Column(Date)
	modified = Column(Date)
	created_by = Column(String(255))
	finalizado	= Column(Integer) DEFAULT 0
	modified_by = Column(String(255))
	caixa = Column(String(255)) NOT NULL
	pago	DECIMAL(192) DEFAULT 0
	validade = Column(Date)
	mesa = Column(Integer)
	FOREIGN KEY(caixa) REFERENCES caixa(cod)
	FOREIGN KEY(codcliente) REFERENCES clientes(cod)
	FOREIGN KEY(codarmazem) REFERENCES armazem(cod)
	PRIMARY KEY(cod)
	FOREIGN KEY (created_by) REFERENCES users(cod)
	FOREIGN KEY (modified_by) REFERENCES users(cod)


class cozinhadetalhe(
	cod	= Column(Integer) NOT NULL Sequence
	codcozinha = Column(String(255)) NOT NULL
	codarmazem = Column(String(50) DEFAULT 'AR201875cNP1'
	mesa = Column(Integer)
	codproduto = Column(String(255))
	custo	DECIMAL(192) DEFAULT 0
	preco	DECIMAL(192) DEFAULT 0
	quantidade	DECIMAL(192) DEFAULT 0
	subtotal	DECIMAL(192) DEFAULT 0
	desconto	DECIMAL(192) DEFAULT 0
	taxa	DECIMAL(192) DEFAULT 0
	total	DECIMAL(192) DEFAULT 0
	lucro	DECIMAL(192) DEFAULT 0
	PRIMARY KEY(cod)
	FOREIGN KEY(codcozinha) REFERENCES cozinha(cod)
	FOREIGN KEY(codarmazem) REFERENCES armazem(cod)

