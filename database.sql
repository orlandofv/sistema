-- Main database file
-- Last update 22-10-2021: Changed all DATE columns to TIMESTAMP with CURRENT_TIMESTAMP as DEFAULT;
-- Added column apagar on users
-- Author: Orlando Filipe Vilanculos, vilankazi@gmail.com

CREATE TABLE IF NOT EXISTS users (
 cod VARCHAR (50) NOT NULL,
 senha VARCHAR(255),
 senha2 VARCHAR(255),
 nome VARCHAR(255) NOT NULL,
 endereco VARCHAR (255),
 sexo VARCHAR ( 10 ),
 email VARCHAR (255),
 nascimento DATE DEFAULT CURRENT_DATE,
 contacto VARCHAR (255),
 tipo VARCHAR(255),
 numero VARCHAR ( 20 ),
 nacionalidade VARCHAR(255) default 'Moçambique',
 obs TEXT,
 created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 modified_by VARCHAR(255),
 created_by VARCHAR(255),
 estado INT DEFAULT 1,
 admin INT DEFAULT 1,
 PRIMARY KEY(cod)
)ENGINE=INNODB;

ALTER TABLE users ADD COLUMN gestor INT DEFAULT 0;
ALTER TABLE users ADD COLUMN apagar INT DEFAULT 0;

CREATE TABLE IF NOT EXISTS armazem (
 cod VARCHAR(255) NOT NULL UNIQUE,
 nome VARCHAR(255) NOT NULL UNIQUE,
 endereco VARCHAR(255),
 obs TEXT,
 estado INT DEFAULT 1,
 created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 modified_by VARCHAR(255),
 created_by VARCHAR(255),
 PRIMARY KEY(cod),
 FOREIGN KEY(modified_by) REFERENCES users(cod),
 FOREIGN KEY(created_by) REFERENCES users(cod)
)ENGINE=INNODB;

ALTER TABLE armazem ADD COLUMN mostrar INT DEFAULT 1;

CREATE TABLE IF NOT EXISTS caixa (
 cod VARCHAR(255) NOT NULL UNIQUE,
 valor_inicial DECIMAL(19,2) DEFAULT 0,
 receitas DECIMAL(19,2) DEFAULT 0,
 despesas DECIMAL(19,2) DEFAULT 0,
 estado INT DEFAULT 0,
 created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 modified_by VARCHAR(255),
 created_by VARCHAR(255),
 obs TEXT,
 PRIMARY KEY(cod),
 FOREIGN KEY(modified_by) REFERENCES users(cod),
 FOREIGN KEY(created_by) REFERENCES users(cod)
)ENGINE=INNODB;
alter table caixa add column codarmazem VARCHAR(50) DEFAULT 'AR201875cNP1';
ALTER TABLE caixa ADD CONSTRAINT codarmazem FOREIGN KEY(codarmazem) REFERENCES armazem(cod);

CREATE TABLE IF NOT EXISTS caixadetalhe(
 cod INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
 caixacod VARCHAR(255),
 despesas INT,
 receitas INT,
 created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 modified_by VARCHAR(255),
 created_by VARCHAR(255),
 obs TEXT,
 FOREIGN KEY(caixacod) REFERENCES caixa(cod),
 FOREIGN KEY(modified_by) REFERENCES users(cod),
 FOREIGN KEY(created_by) REFERENCES users(cod)
)ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS receitas(
 cod INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
 descricao VARCHAR(255),
 valor DECIMAL(19, 2),
 codcaixa VARCHAR(50),
 codarmazem VARCHAR(50),
 created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 modified_by VARCHAR(50),
 created_by VARCHAR(50),
 obs TEXT,
 tipo INT DEFAULT 0,
 estado INT DEFAULT 1,
 FOREIGN KEY(codcaixa) REFERENCES caixa(cod), 
 FOREIGN KEY(created_by) REFERENCES users(cod),
 FOREIGN KEY(modified_by) REFERENCES users(cod), 
 FOREIGN KEY(codarmazem) REFERENCES armazem(cod)
)ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS taxas (
 cod VARCHAR(255) NOT NULL UNIQUE,
 nome VARCHAR ( 40 ) NOT NULL UNIQUE,
 valor INT UNIQUE,
 obs TEXT,
 created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 modified_by VARCHAR(255),
 created_by VARCHAR(255),
 PRIMARY KEY(cod),
 FOREIGN KEY(modified_by) REFERENCES users(cod),
 FOREIGN KEY(created_by) REFERENCES users(cod)
)ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS familia (
 cod VARCHAR(255) NOT NULL UNIQUE,
 nome VARCHAR(255) NOT NULL UNIQUE,
 obs TEXT,
 estado INT DEFAULT 1,
 created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 created_by VARCHAR(255),
 modified_by VARCHAR(255),
 stock INT DEFAULT 1,
 PRIMARY KEY(cod),
 FOREIGN KEY(modified_by) REFERENCES users(cod),
 FOREIGN KEY(created_by) REFERENCES users(cod)
)ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS subfamilia (
 cod VARCHAR(255) NOT NULL UNIQUE,
 nome VARCHAR(255) NOT NULL UNIQUE,
 codfamilia VARCHAR(255) NOT NULL,
 obs TEXT,
 estado INT DEFAULT 1,
 created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 created_by VARCHAR(255),
 modified_by VARCHAR(255),
 PRIMARY KEY(cod),
 FOREIGN KEY(codfamilia) REFERENCES familia(cod),
 FOREIGN KEY(modified_by) REFERENCES users(cod),
 FOREIGN KEY(created_by) REFERENCES users(cod)
)ENGINE=INNODB;

ALTER TABLE subfamilia DROP INDEX nome;
-- ALTER TABLE subfamilia ADD PRIMARY KEY (nome);

CREATE TABLE IF NOT EXISTS produtos (
 cod VARCHAR(255) NOT NULL UNIQUE,
 nome VARCHAR(255) NOT NULL UNIQUE,
 cod_barras VARCHAR(255),
 codfamilia VARCHAR(255),
 codsubfamilia VARCHAR(255),
 custo DECIMAL(19,2),
 preco DECIMAL(19,2),
 quantidade DECIMAL(19,2),
 quantidade_m DECIMAL(19,2),
 unidade VARCHAR(255),
 obs TEXT,
 estado INT,
 foto VARCHAR(255),
 created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 modified_by VARCHAR(255),
 created_by VARCHAR(255),
 PRIMARY KEY(cod),
 FOREIGN KEY(codfamilia) REFERENCES familia(cod),
 FOREIGN KEY(codsubfamilia) REFERENCES subfamilia(cod),
 FOREIGN KEY(modified_by) REFERENCES users(cod),
 FOREIGN KEY(created_by) REFERENCES users(cod)
)ENGINE=INNODB;

ALTER TABLE produtos ADD COLUMN preco1 DECIMAL(19,2) DEFAULT 0;
ALTER TABLE produtos ADD COLUMN preco2 DECIMAL(19,2) DEFAULT 0;
ALTER TABLE produtos ADD COLUMN preco3 DECIMAL(19,2) DEFAULT 0;
ALTER TABLE produtos ADD COLUMN preco4 DECIMAL(19,2) DEFAULT 0;
ALTER TABLE produtos ADD COLUMN tipo INT DEFAULT 0;
ALTER TABLE produtos ADD COLUMN codtaxa VARCHAR(255) DEFAULT 'TX20182222222';
ALTER TABLE produtos ADD CONSTRAINT taxa FOREIGN KEY(codtaxa) REFERENCES taxas(cod); 
ALTER TABLE produtos ADD COLUMN quantidade_max DECIMAL(19,2) DEFAULT 0;
ALTER TABLE produtos ADD COLUMN favorito INT default 0;
ALTER TABLE produtos ADD COLUMN promocao INT default 0;
ALTER TABLE produtos ADD COLUMN preco_de_venda INT default 0;
ALTER TABLE produtos ADD COLUMN descricao TEXT; -- 10-09-2021

CREATE TABLE IF NOT EXISTS produtosdetalhe (
 cod INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
 codproduto VARCHAR(255) NOT NULL,
 codarmazem VARCHAR(255) NOT NULL,
 quantidade DECIMAL(19,2),
 created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 modified_by VARCHAR(255),
 created_by VARCHAR(255),
 FOREIGN KEY(codproduto) REFERENCES produtos(cod),
 FOREIGN KEY (codarmazem) REFERENCES armazem(cod),
 FOREIGN KEY(modified_by) REFERENCES users(cod),
 FOREIGN KEY(created_by) REFERENCES users(cod)
)ENGINE=INNODB;

ALTER TABLE produtosdetalhe ADD COLUMN validade TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;
ALTER TABLE produtosdetalhe ADD COLUMN contagem INT default 0;

CREATE TABLE IF NOT EXISTS relacoes(
 cod INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
 codproduto1 VARCHAR(100) NOT NULL,
 quantidade1 DECIMAL(19,2) DEFAULT 0,
 codproduto2 VARCHAR(100) NOT NULL,
 quantidade2 DECIMAL(19,2) DEFAULT 0,
 codarmazem VARCHAR(50),
 created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 modified_by VARCHAR(100),
 created_by VARCHAR(100),
 obs TEXT,
 FOREIGN KEY (codproduto1) REFERENCES produtos(cod),
 FOREIGN KEY (codproduto2) REFERENCES produtos(cod),
 FOREIGN KEY (codarmazem) REFERENCES armazem(cod),
 FOREIGN KEY (created_by) REFERENCES users(cod),
 FOREIGN KEY (modified_by) REFERENCES users(cod)
)ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS clientes (
 cod VARCHAR(255) NOT NULL UNIQUE,
 nome VARCHAR(255) NOT NULL UNIQUE,
 endereco VARCHAR(255),
 NUIT VARCHAR(255),
 email VARCHAR(255),
 contactos VARCHAR(255),
 desconto DECIMAL(19,2),
 valor_minimo DECIMAL(19,2),
 obs TEXT,
 estado INT default 1,
 created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 modified_by VARCHAR(255),
 created_by VARCHAR(255),
 PRIMARY KEY(cod),
 FOREIGN KEY (created_by) REFERENCES users(cod),
 FOREIGN KEY (modified_by) REFERENCES users(cod)
)ENGINE=INNODB;

ALTER TABLE clientes ADD COLUMN credito DECIMAL(19,2) DEFAULT 0;

CREATE TABLE IF NOT EXISTS fornecedores (
 cod VARCHAR(255) NOT NULL UNIQUE,
 nome VARCHAR(255) NOT NULL UNIQUE,
 endereco VARCHAR(255),
 NUIT VARCHAR(255),
 email VARCHAR(255),
 contactos VARCHAR(255),
 obs TEXT,
 estado INT default 1,
 created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 modified_by VARCHAR(255),
 created_by VARCHAR(255),
 PRIMARY KEY(cod),
 FOREIGN KEY (created_by) REFERENCES users(cod),
 FOREIGN KEY (modified_by) REFERENCES users(cod)
)ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS stock (
 cod VARCHAR(255) NOT NULL UNIQUE,
 fornecedor VARCHAR(255),
 numero DECIMAL(19,2),
 data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 valor DECIMAL(19,2) DEFAULT 0,
 pago DECIMAL(19,2) DEFAULT 0,
 taxa DECIMAL(19,2) DEFAULT 0,
 subtotal DECIMAL(19,2) DEFAULT 0,
 total DECIMAL(19,2) DEFAULT 0,
 created DATE ,
 modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 modified_by VARCHAR(255),
 created_by VARCHAR(255),
 estado INT DEFAULT 0,
 PRIMARY KEY(cod),
 FOREIGN KEY (created_by) REFERENCES users(cod),
 FOREIGN KEY (modified_by) REFERENCES users(cod)
)ENGINE=INNODB;

ALTER TABLE stock ADD COLUMN saldo DECIMAL(19,2) DEFAULT 0;
ALTER TABLE stock CHANGE COLUMN numero numero VARCHAR(255) DEFAULT "" AFTER fornecedor;

CREATE TABLE IF NOT EXISTS stockdetalhe (
 cod INT NOT NULL AUTO_INCREMENT,
 codstock VARCHAR(255),
 codproduto VARCHAR(255),
 codarmazem VARCHAR(255),
 quantidade DECIMAL(19,2) DEFAULT 0,
 valor DECIMAL(19,2) DEFAULT 0,
 taxa DECIMAL(19,2) DEFAULT 0,
 subtotal DECIMAL(19,2) DEFAULT 0,
 total DECIMAL(19,2) DEFAULT 0,
 PRIMARY KEY(cod),
 FOREIGN KEY(codstock) REFERENCES stock(cod),
 FOREIGN KEY(codproduto) REFERENCES produtos(cod),
 FOREIGN KEY(codarmazem) REFERENCES armazem(cod)
)ENGINE=INNODB;

ALTER TABLE stockdetalhe ADD COLUMN custo decimal(19, 2) default 0;
ALTER TABLE stockdetalhe ADD COLUMN validade TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

CREATE TABLE IF NOT EXISTS documentos (
 cod VARCHAR(255) NOT NULL UNIQUE,
 nome VARCHAR(255) NOT NULL UNIQUE,
 subtotal INT DEFAULT 1,
 desconto INT DEFAULT 1,
 taxa INT DEFAULT 1,
 total INT DEFAULT 1,
 obs TEXT,
 created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 modified_by VARCHAR(255),
 created_by VARCHAR(255),
 stock INT DEFAULT 0,
 PRIMARY KEY (cod),
 FOREIGN KEY (created_by) REFERENCES users(cod),
 FOREIGN KEY (modified_by) REFERENCES users(cod)
)ENGINE=INNODB;

ALTER TABLE documentos ADD COLUMN estado INT(11) default 1;
alter table documentos add Column visivel INT default 1;

CREATE TABLE IF NOT EXISTS facturacao (
 cod VARCHAR(255) NOT NULL UNIQUE,
 numero INT,
 coddocumento VARCHAR(255),
 codcliente VARCHAR(255),
 data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 custo DECIMAL(19,2) DEFAULT 0,
 subtotal DECIMAL(19,2) DEFAULT 0,
 desconto DECIMAL(19,2) DEFAULT 0,
 taxa DECIMAL(19,2) DEFAULT 0,
 total DECIMAL(19,2) DEFAULT 0,
 lucro DECIMAL(19,2) DEFAULT 0,
 debito DECIMAL(19,2) DEFAULT 0,
 credito DECIMAL(19,2) DEFAULT 0,
 saldo DECIMAL(19,2) DEFAULT 0,
 troco DECIMAL(19,2) DEFAULT 0,
 banco DECIMAL(19,2) DEFAULT 0,
 cash DECIMAL(19,2) DEFAULT 0,
 tranferencia DECIMAL(19,2) DEFAULT 0,
 estado INT DEFAULT 1,
 extenso VARCHAR(255),
 ano INT,
 mes INT,
 obs varchar (255),
 created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 modified_by VARCHAR(255),
 created_by VARCHAR(255),
 finalizado INT DEFAULT 0,
 caixa VARCHAR(255) NOT NULL,
 pago DECIMAL(19,2) DEFAULT 0,
 validade TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(caixa) REFERENCES caixa(cod),
 FOREIGN KEY(codcliente) REFERENCES clientes(cod),
 PRIMARY KEY(cod),
 FOREIGN KEY (created_by) REFERENCES users(cod),
 FOREIGN KEY (modified_by) REFERENCES users(cod)
)ENGINE=INNODB;

-- Update 10-04-2019 as duas colunas sao usadas para agencia de Viagem apenas
ALTER TABLE facturacao ADD COLUMN comissao DECIMAL(19,2) DEFAULT 0;
ALTER TABLE facturacao ADD COLUMN pagamento DECIMAL(19,2) DEFAULT 0;
-- para por o nome ao gravar o documento 
ALTER TABLE facturacao ADD COLUMN nome varchar(255);

CREATE TABLE IF NOT EXISTS facturacaodetalhe (
 cod INT NOT NULL AUTO_INCREMENT,
 codfacturacao VARCHAR(255) NOT NULL,
 codproduto VARCHAR(255),
 custo DECIMAL(19,2) DEFAULT 0,
 preco DECIMAL(19,2) DEFAULT 0,
 quantidade DECIMAL(19,2) DEFAULT 0,
 subtotal DECIMAL(19,2) DEFAULT 0,
 desconto DECIMAL(19,2) DEFAULT 0,
 taxa DECIMAL(19,2) DEFAULT 0,
 total DECIMAL(19,2) DEFAULT 0,
 lucro DECIMAL(19,2) DEFAULT 0,
 PRIMARY KEY(cod),
 FOREIGN KEY(codfacturacao) REFERENCES facturacao(cod)
)ENGINE=INNODB;
ALTER TABLE facturacaodetalhe ADD COLUMN codarmazem VARCHAR(50) DEFAULT 'AR201875cNP1';
ALTER TABLE facturacaodetalhe ADD CONSTRAINT armazem FOREIGN KEY(codarmazem) REFERENCES armazem(cod);
-- UPDATE 13-12-2018, precisamos saber em que stock o produto saiu
ALTER TABLE facturacaodetalhe ADD COLUMN codstock VARCHAR(50);
ALTER TABLE facturacaodetalhe ADD CONSTRAINT codstock FOREIGN KEY(codstock) REFERENCES stock(cod);
-- UPDATE 06-01-2021
ALTER TABLE facturacaodetalhe ADD COLUMN created TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE facturacaodetalhe ADD COLUMN ordem INT DEFAULT 0;
ALTER TABLE facturacaodetalhe ADD COLUMN prINT INT DEFAULT 1;


CREATE TABLE IF NOT EXISTS requisicao (
 cod VARCHAR(255) NOT NULL UNIQUE,
 numero INT,
 coddocumento VARCHAR(255),
 codcliente VARCHAR(255),
 codarmazem VARCHAR(255),
 data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 custo DECIMAL(19,2) DEFAULT 0,
 subtotal DECIMAL(19,2) DEFAULT 0,
 desconto DECIMAL(19,2) DEFAULT 0,
 taxa DECIMAL(19,2) DEFAULT 0,
 total DECIMAL(19,2) DEFAULT 0,
 lucro DECIMAL(19,2) DEFAULT 0,
 debito DECIMAL(19,2) DEFAULT 0,
 credito DECIMAL(19,2) DEFAULT 0,
 saldo DECIMAL(19,2) DEFAULT 0,
 troco DECIMAL(19,2) DEFAULT 0,
 banco DECIMAL(19,2) DEFAULT 0,
 cash DECIMAL(19,2) DEFAULT 0,
 tranferencia DECIMAL(19,2) DEFAULT 0,
 estado INT DEFAULT 1,
 extenso VARCHAR(255),
 ano INT,
 mes INT,
 obs varchar (255),
 created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 created_by VARCHAR(255),
 finalizado INT DEFAULT 0,
 modified_by VARCHAR(255),
 caixa VARCHAR(255) NOT NULL,
 pago DECIMAL(19,2) DEFAULT 0,
 validade TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(caixa) REFERENCES caixa(cod),
 FOREIGN KEY(codcliente) REFERENCES clientes(cod),
 FOREIGN KEY(codarmazem) REFERENCES armazem(cod),
 PRIMARY KEY(cod),
 FOREIGN KEY (created_by) REFERENCES users(cod),
 FOREIGN KEY (modified_by) REFERENCES users(cod)
)ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS requisicaodetalhe (
 cod INT NOT NULL AUTO_INCREMENT,
 codrequisicao VARCHAR(255) NOT NULL,
 codarmazem1 VARCHAR(50) DEFAULT 'AR201875cNP1',
 codarmazem2 VARCHAR(50) DEFAULT 'AR201875cNP1',
 codproduto VARCHAR(255),
 custo DECIMAL(19,2) DEFAULT 0,
 preco DECIMAL(19,2) DEFAULT 0,
 quantidade DECIMAL(19,2) DEFAULT 0,
 subtotal DECIMAL(19,2) DEFAULT 0,
 desconto DECIMAL(19,2) DEFAULT 0,
 taxa DECIMAL(19,2) DEFAULT 0,
 total DECIMAL(19,2) DEFAULT 0,
 lucro DECIMAL(19,2) DEFAULT 0,
 PRIMARY KEY(cod),
 FOREIGN KEY(codrequisicao) REFERENCES requisicao(cod)
)ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS recibos (
 cod VARCHAR(255) NOT NULL UNIQUE,
 numero INT,
 codfactura VARCHAR(255),
 codcliente VARCHAR(255),
 data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 total DECIMAL(19,2) DEFAULT 0,
 troco DECIMAL(19,2) DEFAULT 0,
 banco DECIMAL(19,2) DEFAULT 0,
 cash DECIMAL(19,2) DEFAULT 0,
 tranferencia DECIMAL(19,2) DEFAULT 0,
 estado INT DEFAULT 1,
 extenso VARCHAR(255),
 ano INT,
 mes INT,
 obs varchar (255),
 created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 modified_by VARCHAR(255),
 created_by VARCHAR(255),
 finalizado INT DEFAULT 0,
 caixa VARCHAR(255) NOT NULL,
 PRIMARY KEY(cod),
 FOREIGN KEY(codcliente) REFERENCES clientes(cod),
 FOREIGN KEY(codfactura) REFERENCES facturacao(cod),
 FOREIGN KEY(caixa) REFERENCES caixa(cod),
 FOREIGN KEY (created_by) REFERENCES users(cod),
 FOREIGN KEY (modified_by) REFERENCES users(cod)
)ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS recibosdetalhe (
 cod INT NOT NULL AUTO_INCREMENT,
 codrecibo VARCHAR(255) NOT NULL,
 factura INT NOT NULL,
 pago DECIMAL(19,2) DEFAULT 0,
 saldo DECIMAL(19,2) DEFAULT 0,
 descricao VARCHAR(255),
 codfactura VARCHAR(255),
 PRIMARY KEY(cod),
 FOREIGN KEY(codrecibo) REFERENCES recibos(cod)
)ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS pagamentos (
 cod INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
 codfornecedor VARCHAR(255),
 codstock VARCHAR(255),
 debito DECIMAL(19,2) DEFAULT '0',
 credito DECIMAL(19,2) DEFAULT '0',
 saldo DECIMAL(19,2) DEFAULT '0',
 documento VARCHAR(255),
 created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 modified_by VARCHAR(255) DEFAULT "",
 created_by VARCHAR(255) DEFAULT "",
 FOREIGN KEY (codfornecedor) REFERENCES fornecedores(cod),
 FOREIGN KEY (codstock) REFERENCES stock(cod),
 FOREIGN KEY (created_by) REFERENCES users(cod),
 FOREIGN KEY (modified_by) REFERENCES users(cod)
);

CREATE TABLE IF NOT EXISTS config(
 empresa VARCHAR(255) UNIQUE NOT NULL PRIMARY KEY ,
 f_template VARCHAR(255) DEFAULT "",
 rec_template VARCHAR(255) DEFAULT "",
 req_template VARCHAR(255) DEFAULT "",
 c_cliente INT DEFAULT 1,
 cliente_n INT DEFAULT 1,
 saldo INT DEFAULT 1,
 c_inactivo INT DEFAULT 1,
 desc_automatico INT DEFAULT 1,
 ac_credito INT DEFAULT 1,
 pos1 VARCHAR(255) DEFAULT "",
 pos2 VARCHAR(255) DEFAULT "",
 pos3 VARCHAR(255) DEFAULT "",
 pos4 VARCHAR(255) DEFAULT "",
 pos5 VARCHAR(255) DEFAULT "",
 so_vd INT DEFAULT 0,
 iva_incluso INT DEFAULT 1,
 regime INT DEFAULT 1,
 isento INT DEFAULT 1,
 vendas_zero INT DEFAULT 1,
 cop1 INT DEFAULT 1,
 cop2 INT DEFAULT 1,
 cop3 INT DEFAULT 1,
 cop4 INT DEFAULT 1,
 cop5 INT DEFAULT 1);

CREATE TABLE IF NOT EXISTS hospedes (
 cod varchar(50) NOT NULL,
 nome varchar(255) NOT NULL,
 apelido varchar(255) DEFAULT "",
 endereco varchar(255) DEFAULT "",
 sexo varchar(15) DEFAULT "",
 email varchar(255) DEFAULT "",
 nascimento varchar(50) DEFAULT "",
 contactos varchar(255) DEFAULT "",
 emergencia varchar(255) DEFAULT "",
 tipo_id varchar(20) DEFAULT "",
 numero_id varchar(20) DEFAULT "",
 validade_id varchar(50) DEFAULT "",
 nacionalidade varchar(50) DEFAULT "",
 obs varchar(255) DEFAULT "",
 estado INT(11) DEFAULT '1',
 created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 modified_by varchar(255) DEFAULT "",
 created_by varchar(255) DEFAULT "",
 PRIMARY KEY (cod),
 FOREIGN KEY (created_by) REFERENCES users(cod),
 FOREIGN KEY (modified_by) REFERENCES users(cod)
) ENGINE=InnoDB;

ALTER table hospedes add column foto varchar(255); -- Armazenar o link da foto


CREATE TABLE IF NOT EXISTS categorias (
 cod INT(11) NOT NULL AUTO_INCREMENT,
 valor decimal(19,2) DEFAULT '0.00',
 categoria varchar(255) NOT NULL,
 obs varchar(255) DEFAULT "",
 created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 modified_by varchar(255) DEFAULT "",
 created_by varchar(255) DEFAULT "",
 PRIMARY KEY (cod),
 FOREIGN KEY (created_by) REFERENCES users(cod),
 FOREIGN KEY (modified_by) REFERENCES users(cod)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS quartos (
 cod INT(11) NOT NULL,
 cod_preco INT(11) NOT NULL,
 preco decimal(19,2) DEFAULT '0.00',
 estado INT(11) DEFAULT '1',
 ocupado INT(11) DEFAULT '0',
 obs varchar(255) DEFAULT "",
 created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 modified_by varchar(255) DEFAULT "",
 created_by varchar(255) DEFAULT "",
 PRIMARY KEY (cod),
 KEY cod_preco (cod_preco),
 FOREIGN KEY (cod_preco) REFERENCES categorias (cod),
 FOREIGN KEY (created_by) REFERENCES users(cod),
 FOREIGN KEY (modified_by) REFERENCES users(cod)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS reservas(
 cod INT(11) not null AUTO_INCREMENT,
 data_entrada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 data_saida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 cod_cliente varchar(255),
 obs TEXT,
 created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 modified_by VARCHAR(255) DEFAULT "",
 created_by VARCHAR(255) DEFAULT "",
 PRIMARY KEY (cod),
 FOREIGN KEY (cod_cliente) REFERENCES hospedes(cod),
 FOREIGN KEY (created_by) REFERENCES users(cod),
 FOREIGN KEY (modified_by) REFERENCES users(cod)
)ENGINE=INNODB;

ALTER TABLE reservas ADD COLUMN cod_quarto INT(11) AFTER cod_cliente;
ALTER TABLE reservas ADD COLUMN estado INT default 1 DEFAULT 1 AFTER created_by;
ALTER TABLE reservas ADD COLUMN hospede VARCHAR(255) DEFAULT "" AFTER estado;
ALTER TABLE reservas ADD COLUMN voucher VARCHAR(50) DEFAULT "";
ALTER TABLE reservas ADD COLUMN pagamento VARCHAR(50) DEFAULT "";
ALTER TABLE reservas ADD COLUMN moeda VARCHAR(50) DEFAULT "";
ALTER TABLE reservas ADD COLUMN codfacturacao VARCHAR(50) DEFAULT "";
ALTER TABLE reservas ADD FOREIGN KEY (cod_quarto) REFERENCES quartos (cod);


CREATE TABLE IF NOT EXISTS check_in (
 cod INT(11) NOT NULL AUTO_INCREMENT,
 data_entrada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 data_saida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 cod_cliente VARCHAR(255),
 cod_quarto INT(11),
 total DECIMAL(19,2) DEFAULT '0.00',
 pago DECIMAL(19,2) DEFAULT '0.00',
 divida DECIMAL(19,2) DEFAULT '0.00',
 obs VARCHAR(255) DEFAULT "",
 created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 modified_by VARCHAR(255) DEFAULT "",
 created_by VARCHAR(255) DEFAULT "",
 estado INT(11) DEFAULT '0',
 PRIMARY KEY (cod),
 INDEX cod_cliente (cod_cliente),
 INDEX cod_quarto (cod_quarto),
 FOREIGN KEY (cod_cliente) REFERENCES hospedes (cod),
 FOREIGN KEY (cod_quarto) REFERENCES quartos (cod),
 FOREIGN KEY (created_by) REFERENCES users(cod),
 FOREIGN KEY (modified_by) REFERENCES users(cod)
)
ENGINE=InnoDB;

ALTER TABLE check_in ADD COLUMN hospede VARCHAR(255) DEFAULT "";
ALTER TABLE check_in ADD COLUMN voucher VARCHAR(50) DEFAULT "";
ALTER TABLE check_in ADD COLUMN pagamento VARCHAR(50) DEFAULT "";
ALTER TABLE check_in ADD COLUMN moeda VARCHAR(50) DEFAULT "";
ALTER TABLE check_in ADD COLUMN codfacturacao VARCHAR(50) DEFAULT "";

CREATE TABLE IF NOT EXISTS alunos (
 cod varchar(50) NOT NULL,
 nome varchar(255) NOT NULL,
 apelido varchar(255) DEFAULT "",
 endereco varchar(255) DEFAULT "",
 sexo varchar(15) DEFAULT "",
 email varchar(255) DEFAULT "",
 nascimento varchar(50) DEFAULT "",
 contactos varchar(255) DEFAULT "",
 emergencia varchar(255) DEFAULT "",
 tipo_id varchar(20) DEFAULT "",
 numero_id varchar(20) DEFAULT "",
 validade_id varchar(50) DEFAULT "",
 nacionalidade varchar(50) DEFAULT "",
 obs varchar(255) DEFAULT "",
 estado INT(11) DEFAULT '1',
 created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 modified_by varchar(255) DEFAULT "",
 created_by varchar(255) DEFAULT "",
 foto varchar(255) DEFAULT "",
 PRIMARY KEY (cod),
 FOREIGN KEY (created_by) REFERENCES users(cod),
 FOREIGN KEY (modified_by) REFERENCES users(cod)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS estudantes (
 cod varchar(50) NOT NULL,
 nome varchar(255) NOT NULL,
 apelido varchar(255) DEFAULT "",
 endereco varchar(255) DEFAULT "",
 sexo varchar(15) DEFAULT "",
 email varchar(255) DEFAULT "",
 nascimento varchar(50) DEFAULT "",
 contactos varchar(255) DEFAULT "",
 emergencia varchar(255) DEFAULT "",
 tipo_id varchar(20) DEFAULT "",
 numero_id varchar(20) DEFAULT "",
 validade_id varchar(50) DEFAULT "",
 nacionalidade varchar(50) DEFAULT "",
 obs varchar(255) DEFAULT "",
 estado INT(11) DEFAULT '1',
 created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 modified_by varchar(255) DEFAULT "",
 created_by varchar(255) DEFAULT "",
 foto varchar(255) DEFAULT "",
 empresa varchar(50),
 PRIMARY KEY (cod),
 FOREIGN KEY (empresa) REFERENCES clientes(cod),
 FOREIGN KEY (created_by) REFERENCES users(cod),
 FOREIGN KEY (modified_by) REFERENCES users(cod)
)ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS instrutores (
 cod varchar(50) NOT NULL,
 nome varchar(255) NOT NULL,
 apelido varchar(255) DEFAULT "",
 endereco varchar(255) DEFAULT "",
 sexo varchar(15) DEFAULT "",
 email varchar(255) DEFAULT "",
 nascimento varchar(50) DEFAULT "",
 contactos varchar(255) DEFAULT "",
 emergencia varchar(255) DEFAULT "",
 tipo_id varchar(20) DEFAULT "",
 numero_id varchar(20) DEFAULT "",
 validade_id varchar(50) DEFAULT "",
 nacionalidade varchar(50) DEFAULT "",
 obs varchar(255) DEFAULT "",
 estado INT(11) DEFAULT '1',
 created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 modified_by varchar(255) DEFAULT "",
 created_by varchar(255) DEFAULT "",
 foto varchar(255) DEFAULT "",
 PRIMARY KEY (cod),
 FOREIGN KEY (created_by) REFERENCES users(cod),
 FOREIGN KEY (modified_by) REFERENCES users(cod)
)ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS cursos(
 cod INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
 nome varchar(255),
 data_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 data_final TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 duracao DECIMAL (6, 2),
 valor DECIMAL(19, 2) default 0,
 percentagem DECIMAL(10, 2) default 0,
 obs varchar(255) DEFAULT "",
 estado INT(11) DEFAULT 1,
 created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 modified_by varchar(255) DEFAULT "",
 created_by varchar(255) DEFAULT "",
 FOREIGN KEY (created_by) REFERENCES users(cod),
 FOREIGN KEY (modified_by) REFERENCES users(cod)
)ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS formacao (
 cod INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
 nome varchar(255) not NULL UNIQUE,
 codcurso INT,
 codempresa VARCHAR(50),
 codestudante VARCHAR(50),
 valor DECIMAL(19, 2) default 0,
 valor_primeira DECIMAL(19, 2) default 0,
 valor_segunda DECIMAL(19, 2) default 0,
 valor_saldo DECIMAL(19, 2) default 0,
 teoria DECIMAL(10, 2) default 0,
 pratica DECIMAL(10, 2) default 0,
 comportamento varchar(15) DEFAULT "",
 resultado varchar(15) DEFAULT "",
 obs varchar(255) DEFAULT "",
 estado INT(11) DEFAULT '1',
 created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 modified_by varchar(255) DEFAULT "",
 created_by varchar(255) DEFAULT "",
 FOREIGN KEY (codcurso) REFERENCES cursos(cod),
 FOREIGN KEY (codempresa) REFERENCES clientes(cod),
 FOREIGN KEY (codestudante) REFERENCES estudantes(cod),
 FOREIGN KEY (created_by) REFERENCES users(cod),
 FOREIGN KEY (modified_by) REFERENCES users(cod)
)ENGINE=InnoDB;
alter table formacao add column data_inicio timestamp default now();
alter table formacao add column data_final timestamp default now();

CREATE TABLE IF NOT EXISTS certificado (
 cod VARCHAR(50) NOT NULL PRIMARY KEY,
 numero VARCHAR(50) NOT NULL UNIQUE,
 codformacao INT,
 codempresa VARCHAR(50),
 codestudante VARCHAR(50),
 data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 validade TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 obs varchar(255) DEFAULT "",
 estado INT(11) DEFAULT '1',
 created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 modified_by varchar(255) DEFAULT "",
 created_by varchar(255) DEFAULT "",
 FOREIGN KEY (codformacao) REFERENCES formacao(cod),
 FOREIGN KEY (codempresa) REFERENCES clientes(cod),
 FOREIGN KEY (codestudante) REFERENCES estudantes(cod),
 FOREIGN KEY (created_by) REFERENCES users(cod),
 FOREIGN KEY (modified_by) REFERENCES users(cod)
)ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS mesas(
 cod INT AUTO_INCREMENT not null primary key,
 numero INT not null,
 descricao varchar(50),
 codfacturacao varchar(50),
 estado INT DEFAULT 0,
 created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 modified_by VARCHAR(255),
 created_by VARCHAR(255),
 obs TEXT,
 foreign key(codfacturacao) references facturacao(cod) ON DELETE CASCADE,
 FOREIGN KEY (created_by) REFERENCES users(cod),
 FOREIGN KEY (modified_by) REFERENCES users(cod)
)ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS cozinha (
 cod VARCHAR(255) NOT NULL UNIQUE,
 numero INT,
 coddocumento VARCHAR(255),
 codcliente VARCHAR(255),
 codarmazem VARCHAR(255),
 data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 custo DECIMAL(19,2) DEFAULT 0,
 subtotal DECIMAL(19,2) DEFAULT 0,
 desconto DECIMAL(19,2) DEFAULT 0,
 taxa DECIMAL(19,2) DEFAULT 0,
 total DECIMAL(19,2) DEFAULT 0,
 lucro DECIMAL(19,2) DEFAULT 0,
 debito DECIMAL(19,2) DEFAULT 0,
 credito DECIMAL(19,2) DEFAULT 0,
 saldo DECIMAL(19,2) DEFAULT 0,
 troco DECIMAL(19,2) DEFAULT 0,
 banco DECIMAL(19,2) DEFAULT 0,
 cash DECIMAL(19,2) DEFAULT 0,
 tranferencia DECIMAL(19,2) DEFAULT 0,
 estado INT DEFAULT 1,
 extenso VARCHAR(255),
 ano INT,
 mes INT,
 obs varchar (255),
 created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 created_by VARCHAR(255),
 finalizado INT DEFAULT 0,
 modified_by VARCHAR(255),
 caixa VARCHAR(255) NOT NULL,
 pago DECIMAL(19,2) DEFAULT 0,
 validade TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 mesa INT,
 FOREIGN KEY(caixa) REFERENCES caixa(cod),
 FOREIGN KEY(codcliente) REFERENCES clientes(cod),
 FOREIGN KEY(codarmazem) REFERENCES armazem(cod),
 PRIMARY KEY(cod),
 FOREIGN KEY (created_by) REFERENCES users(cod),
 FOREIGN KEY (modified_by) REFERENCES users(cod)
)ENGINE=INNODB;

-- UPDATE 06-01-2021
ALTER TABLE cozinha ADD COLUMN codfacturacao VARCHAR(255);
ALTER TABLE cozinha ADD CONSTRAINT codfacturacao FOREIGN KEY (codfacturacao) REFERENCES facturacao(cod);

CREATE TABLE IF NOT EXISTS cozinhadetalhe(
 cod INT NOT NULL AUTO_INCREMENT,
 codcozinha VARCHAR(255) NOT NULL,
 codarmazem VARCHAR(50) DEFAULT 'AR201875cNP1',
 mesa INT,
 codproduto VARCHAR(255),
 custo DECIMAL(19,2) DEFAULT 0,
 preco DECIMAL(19,2) DEFAULT 0,
 quantidade DECIMAL(19,2) DEFAULT 0,
 subtotal DECIMAL(19,2) DEFAULT 0,
 desconto DECIMAL(19,2) DEFAULT 0,
 taxa DECIMAL(19,2) DEFAULT 0,
 total DECIMAL(19,2) DEFAULT 0,
 lucro DECIMAL(19,2) DEFAULT 0,
 PRIMARY KEY(cod),
 FOREIGN KEY(codcozinha) REFERENCES cozinha(cod),
 FOREIGN KEY(codarmazem) REFERENCES armazem(cod)
)ENGINE=INNODB;

INSERT IGNORE INTO users (cod,senha,senha2,nome,endereco,sexo,email,nascimento,contacto,tipo,numero,nacionalidade,obs,created,modified,modified_by,created_by,estado,admin) VALUES ('user','123456','123456','user','Maputo',
'Masculino','','1980-01-01','','BI','','Moçambique ','User Normal','2018-07-09','2018-07-09','administrador','administrador',1,0);
INSERT IGNORE INTO users (cod,senha,senha2,nome,endereco,sexo,email,nascimento,contacto,tipo,numero,nacionalidade,obs,created,modified,modified_by,created_by,estado,admin, gestor) VALUES ('administrador','123456','123456','','','Masculino','','1980-01-01','','BI','','Moçambique ','Administrador do Sistema','2018-07-09','2018-07-09','administrador','administrador', 1, 1, 1);

INSERT IGNORE INTO clientes (cod,nome,endereco,NUIT,email,contactos,desconto,valor_minimo,obs,estado,created,modified,modified_by,created_by) VALUES ('CL20181111111','Cliente Normal','','','administrador','administrador',0.0,0.0,'','1','2018-07-13','2018-07-13','administrador','administrador');
INSERT IGNORE INTO documentos (cod,nome,subtotal,desconto,taxa,total,obs,created,modified,modified_by,created_by,stock) VALUES ('DC20181111111','VD',1,1,1,1,'','2018-06-23','2018-06-23','administrador','administrador',1);
INSERT IGNORE INTO documentos (cod,nome,subtotal,desconto,taxa,total,obs,created,modified,modified_by,created_by,stock) VALUES ('DC20182222222','Factura',1,1,1,1,'','2018-06-23','2018-06-23','administrador','administrador',1);
INSERT IGNORE INTO documentos (cod,nome,subtotal,desconto,taxa,total,obs,created,modified,modified_by,created_by,stock) VALUES ('DC20183333333','Recibo',0,0,0,1,'','2018-07-05','2018-07-05','administrador','administrador',0);
INSERT IGNORE INTO documentos (cod,nome,subtotal,desconto,taxa,total,obs,created,modified,modified_by,created_by,stock) VALUES ('DC20184444444','Cotação',1,1,1,1,'','2018-07-05','2018-07-05','administrador','administrador',0);
INSERT IGNORE INTO documentos (cod,nome,subtotal,desconto,taxa,total,obs,created,modified,modified_by,created_by,stock) VALUES ('DC20185555555','Requisição',1,1,1,1,'','2018-07-05','2018-07-05','administrador','administrador',0);
INSERT IGNORE INTO documentos (cod,nome,subtotal,desconto,taxa,total,obs,created,modified,modified_by,created_by,stock) VALUES ('DC2018713LmiU','Guia de Entrega',0,0,0,0,'','2018-07-13','2018-07-13','administrador','administrador',0);
INSERT IGNORE INTO documentos (cod,nome,subtotal,desconto,taxa,total,obs,created,modified,modified_by,created_by,stock) VALUES ('DC2018713oISd','Nota de Crédito',1,1,1,1,'','2018-07-13','2018-07-13','administrador','administrador',0);

INSERT IGNORE INTO taxas (cod,nome,valor,obs,created,modified,modified_by,created_by) VALUES ('TX20181111111','ISENTO',0,'','2018-01-16','2018-01-16',
'administrador','administrador');
INSERT IGNORE INTO taxas (cod,nome,valor,obs,created,modified,modified_by,created_by) VALUES ('TX20182222222','IVA',17,'','2018-06-12','2018-06-12','administrador','administrador');

INSERT IGNORE INTO armazem (cod,nome,endereco,obs,estado,created,modified,modified_by,created_by) VALUES ('AR201875cNP1','Armazém Local','','Armazém Padrão.',1,'2018-07-05','2018-07-05','administrador','administrador');

INSERT IGNORE INTO fornecedores (cod,nome,endereco,NUIT,email,contactos,obs,estado,created,modified,modified_by,created_by) VALUES ('FR20181111111','Fornecedor Padrão','','','','','Fornecedor Padrão','1','2018-07-05','2018-07-05','administrador','administrador');

INSERT IGNORE INTO familia (cod,nome,obs,estado,created,modified,created_by,modified_by,stock) VALUES ('FM20181111111','Diversos','',1,'2018-07-04','2018-07-04','administrador','administrador',1);

INSERT IGNORE INTO subfamilia (cod,nome,codfamilia,obs,estado,created,modified,created_by,modified_by) VALUES ('SF20181111111','Diversos','FM20181111111','',1,'2018-06-12','2018-06-12','administrador','administrador');

DROP VIEW IF EXISTS recibo_geral;
CREATE VIEW recibo_geral as select recibos.cod AS cod,recibos.total AS total,recibos.created AS created,recibos.codcliente AS codcliente,recibos.extenso AS extenso,recibosdetalhe.descricao AS descricao,recibosdetalhe.factura AS factura,recibosdetalhe.pago AS pago,clientes.nome AS nome,clientes.endereco AS endereco,clientes.NUIT AS NUIT,clientes.email AS email,recibos.finalizado AS finalizado,recibos.estado AS estado,recibos.numero AS numero,recibos.mes AS mes,recibos.ano AS ano,recibos.data AS data,recibos.created_by AS user,clientes.contactos AS contactos,recibos.obs AS obs from ((recibos join clientes on((clientes.cod = recibos.codcliente))) join recibosdetalhe on((recibos.cod = recibosdetalhe.codrecibo)));

DROP VIEW IF EXISTS facturas_nao_pagas;
CREATE VIEW facturas_nao_pagas as select facturacao.cod, facturacao.numero, facturacao.data, clientes.nome as cliente, facturacao.total, facturacao.saldo, facturacao.debito, facturacao.credito, facturacao.obs from facturacao INNER JOIN clientes on facturacao.codcliente=clientes.cod WHERE facturacao.coddocumento = "DC20182222222" and facturacao.estado = 1 and facturacao.saldo > 0;

DROP VIEW IF EXISTS reservas_view;
CREATE VIEW reservas_view as SELECT reservas.cod, reservas.data_entrada, reservas.data_saida, hospedes.nome,
reservas.cod_quarto, reservas.voucher, reservas.pagamento, reservas.moeda, reservas.codfacturacao
FROM reservas INNER join hospedes ON hospedes.cod=reservas.cod_cliente; 

DROP VIEW IF EXISTS check_in_view;
CREATE VIEW check_in_view as SELECT check_in.cod, check_in.data_entrada, check_in.data_saida, hospedes.nome,
check_in.cod_quarto, check_in.voucher, check_in.pagamento, check_in.moeda, check_in.codfacturacao
FROM check_in INNER join hospedes ON hospedes.cod=check_in.cod_cliente; 

DROP VIEW IF EXISTS factura_geral;
CREATE VIEW factura_geral as select facturacao.cod AS codfacturacao,facturacao.numero AS numerofactura,
documentos.nome AS nomedocumento,facturacao.created AS data,facturacao.created_by AS user,
facturacao.subtotal AS subtotal_geral,facturacao.desconto AS desconto_geral,facturacao.taxa AS taxa_geral,
facturacao.total AS total_geral,facturacao.extenso AS extenso,clientes.nome AS cliente,
clientes.endereco AS endereco,clientes.NUIT AS NUIT,clientes.email AS email,
facturacaodetalhe.codproduto AS codproduto, produtos.nome AS produto,
facturacaodetalhe.quantidade AS quantidade,facturacaodetalhe.preco AS preco,
facturacaodetalhe.desconto AS desconto,facturacaodetalhe.taxa AS taxa,
facturacaodetalhe.subtotal AS subtotal,facturacaodetalhe.total AS total,
facturacao.ano AS ano,facturacao.mes AS mes,facturacao.pago AS pago,
facturacao.troco AS troco,documentos.cod AS coddocumento,clientes.contactos AS contactos,
facturacao.validade AS validade,facturacao.obs AS obs, armazem.nome, 
facturacaodetalhe.print, produtos.descricao from ((((facturacao 
join facturacaodetalhe on((facturacao.cod = facturacaodetalhe.codfacturacao))) 
join clientes on((clientes.cod = facturacao.codcliente))) 
join produtos on((produtos.cod = facturacaodetalhe.codproduto))) 
join documentos on((documentos.cod = facturacao.coddocumento)) 
join armazem on((armazem.cod = facturacaodetalhe.codarmazem)));

DROP VIEW IF EXISTS caixa_geral;
CREATE VIEW caixa_geral as SELECT
facturacao.cod as cod_facturacao, facturacao.numero, facturacao.ano, facturacao.mes, 
facturacaodetalhe.custo as custo_produto, facturacaodetalhe.desconto as desconto_produto, 
facturacaodetalhe.subtotal as subtotal_produtos, facturacaodetalhe.preco as preco_produtos, 
facturacaodetalhe.lucro as lucro_produtos, facturacaodetalhe.quantidade as quantidade_produtos,
facturacaodetalhe.taxa as taxa_produtos, facturacaodetalhe.total as total_produtos, 
caixa.cod, caixa.valor_inicial, caixa.despesas, caixa.receitas,
caixa.created as data_abertura, caixa.created_by as aberta_por, 
caixa.modified as data_feixo, caixa.modified_by as fechada_por,
produtos.nome as produtos_nome,
clientes.nome as produtos_cliente, 
documentos.nome as nome_documento, 
caixa.obs as caixa_obs, facturacao.comissao, facturacao.pagamento, facturacao.modified_by as user
from facturacaodetalhe left join facturacao
on facturacao.cod=facturacaodetalhe.codfacturacao left join documentos on documentos.cod=facturacao.coddocumento
left join clientes on clientes.cod=facturacao.codcliente INNER JOIN produtos on produtos.cod=facturacaodetalhe.codproduto
INNER JOIN caixa on caixa.cod=facturacao.caixa;

DROP VIEW IF EXISTS FECHO_CAIXA;
CREATE VIEW FECHO_CAIXA AS SELECT CAIXA.valor_inicial, caixa.receitas, caixa.despesas, 
caixa.created_by AS CRIADA_POR, caixa.modified_by AS FECHADA_POR, caixa.created AS ABERTURA, 
caixa.modified AS FECHO, documentos.nome AS DOCUMENTO, facturacao.numero, clientes.nome AS CLIENTE, 
facturacao.subtotal, facturacao.desconto, facturacao.taxa, facturacao.total, facturacao.banco AS CHEQUE, 
facturacao.cash AS NUMERARIO, facturacao.tranferencia AS POS, caixa.estado as estado_caixa, facturacao.estado as estado_factura, caixa.cod as caixa_numero, facturacao.coddocumento as doc, facturacao.comissao, facturacao.pagamento,
facturacao.lucro, facturacao.modified, facturacao.modified_by as user
FROM facturacao INNER JOIN CAIXA ON caixa.cod = facturacao.caixa inner JOIN documentos ON documentos.cod=facturacao.coddocumento INNER JOIN CLIENTES ON clientes.cod=facturacao.codcliente WHERE facturacao.finalizado = 1;

DROP VIEW IF EXISTS FECHO_CAIXA_DETALHADA;
CREATE VIEW FECHO_CAIXA_DETALHADA AS SELECT CAIXA.valor_inicial, caixa.receitas, caixa.despesas, caixa.created_by AS CRIADA_POR, caixa.modified_by AS FECHADA_POR, caixa.created AS ABERTURA, caixa.modified AS FECHO, documentos.nome AS DOCUMENTO, facturacao.numero, clientes.nome AS CLIENTE, facturacao.subtotal, facturacao.desconto, facturacao.taxa, facturacao.total, facturacao.banco AS CHEQUE, facturacao.cash AS NUMERARIO, facturacao.tranferencia AS POS, caixa.estado as estado_caixa, facturacao.estado as estado_factura, caixa.cod as caixa_numero, facturacao.coddocumento as doc, facturacao.comissao, facturacao.pagamento,
facturacao.lucro, produtos.nome, facturacaodetalhe.quantidade, facturacaodetalhe.total as total_geral, facturacaodetalhe.preco AS preco_unitario, facturacaodetalhe.taxa as iva_produto,
facturacaodetalhe.desconto AS desconto_unitario, facturacaodetalhe.subtotal as subtotal_produto, 
facturacao.modified_by as user, produtos.cod as prod_cod, facturacaodetalhe.custo
FROM facturacao INNER JOIN CAIXA ON caixa.cod = facturacao.caixa 
inner JOIN documentos ON documentos.cod=facturacao.coddocumento 
INNER JOIN CLIENTES ON clientes.cod=facturacao.codcliente
INNER JOIN facturacaodetalhe ON facturacao.cod=facturacaodetalhe.codfacturacao
INNER JOIN produtos ON produtos.cod=facturacaodetalhe.codproduto 
WHERE facturacao.finalizado = 1 AND facturacaodetalhe.print=1;

DROP VIEW IF EXISTS stock_actual;
CREATE VIEW stock_actual as SELECT produtos.cod, produtos.nome, stockdetalhe.quantidade, produtos.preco, produtos.preco1, produtos.preco2,
produtos.preco3, produtos.preco4, produtos.quantidade_m, produtos.quantidade as quantidade_max, produtos.estado, produtos.tipo, armazem.nome as armazem
FROM produtos, stockdetalhe, armazem WHERE produtos.cod=stockdetalhe.codproduto and armazem.cod=stockdetalhe.codarmazem;

DROP VIEW IF EXISTS stock_geral;
CREATE VIEW stock_geral as SELECT produtos.cod, produtos.nome, sum(stockdetalhe.quantidade) as qt , produtos.preco, produtos.preco1, produtos.preco2,
produtos.preco3, produtos.preco4, produtos.quantidade_m, produtos.quantidade as quantidade_max, produtos.estado, 
produtos.tipo, armazem.nome as nomearmazem
FROM produtos INNER JOIN stockdetalhe ON produtos.cod=stockdetalhe.codproduto
INNER JOIN armazem ON armazem.cod=stockdetalhe.codarmazem WHERE produtos.estado=1
GROUP BY armazem.cod, produtos.cod;

DROP VIEW IF EXISTS entradas;
CREATE VIEW entradas AS SELECT s.cod AS cod_documento, s.numero AS doc_numero, 
p.cod AS cod_produto, p.nome AS nome, sd.quantidade as qty, sd.custo as preco, sd.subtotal, 
(sd.quantidade * sd.custo) as total, f.nome AS entidade, s.created AS date_created,
ar.nome AS nomearmazem, u.cod AS user 
FROM stock s
JOIN stockdetalhe sd ON sd.codstock = s.cod
JOIN produtos p ON sd.codproduto = p.cod
JOIN fornecedores f ON s.fornecedor = f.cod
JOIN armazem ar ON sd.codarmazem = ar.cod 
JOIN users u ON s.modified_by = u.cod 
WHERE s.estado = 1;

DROP VIEW IF EXISTS saidas;
CREATE VIEW saidas AS SELECT f.cod AS cod_documento, CONCAT(d.nome, " " ,f.numero) AS doc_numero, 
p.cod AS cod_produto, p.nome AS nome, fd.quantidade, fd.preco, fd.custo, (fd.quantidade * fd.preco) as total, c.nome AS entidade, f.created AS date_created,
ar.nome AS nomearmazem, u.cod AS user
FROM facturacao f
JOIN facturacaodetalhe fd ON fd.codfacturacao = f.cod
JOIN produtos p ON fd.codproduto = p.cod
JOIN documentos d ON f.coddocumento = d.cod
JOIN clientes c ON f.codcliente = c.cod
JOIN armazem ar ON fd.codarmazem = ar.cod 
JOIN users u ON f.modified_by = u.cod 
WHERE f.finalizado = 1 AND f.estado = 1 AND d.estado=1 AND d.stock=1;

DROP VIEW IF EXISTS movimento_stock;
CREATE VIEW movimento_stock as 
SELECT * from entradas
UNION 
SELECT * from saidas
