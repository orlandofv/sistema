-- --------------------------------------------------------
-- Anfitrião:                    127.0.0.1
-- Versão do servidor:           5.7.22-log - MySQL Community Server (GPL)
-- Server OS:                    Win64
-- HeidiSQL Versão:              10.3.0.5771
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;

-- Dumping structure for table agencia_boa.alunos
CREATE TABLE IF NOT EXISTS `alunos` (
  `cod` varchar(50) NOT NULL,
  `nome` varchar(255) NOT NULL,
  `apelido` varchar(255) DEFAULT NULL,
  `endereco` varchar(255) DEFAULT NULL,
  `sexo` varchar(15) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `nascimento` varchar(50) DEFAULT NULL,
  `contactos` varchar(255) DEFAULT NULL,
  `emergencia` varchar(255) DEFAULT NULL,
  `tipo_id` varchar(20) DEFAULT NULL,
  `numero_id` varchar(20) DEFAULT NULL,
  `validade_id` varchar(50) DEFAULT NULL,
  `nacionalidade` varchar(50) DEFAULT NULL,
  `obs` varchar(255) DEFAULT NULL,
  `estado` int(11) DEFAULT '1',
  `created` date DEFAULT NULL,
  `modified` date DEFAULT NULL,
  `modified_by` varchar(255) DEFAULT NULL,
  `created_by` varchar(255) DEFAULT NULL,
  `foto` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`cod`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table agencia_boa.armazem
CREATE TABLE IF NOT EXISTS `armazem` (
  `cod` varchar(255) NOT NULL,
  `nome` varchar(255) NOT NULL,
  `endereco` varchar(255) DEFAULT NULL,
  `obs` varchar(255) DEFAULT NULL,
  `estado` int(11) DEFAULT '1',
  `created` date DEFAULT NULL,
  `modified` date DEFAULT NULL,
  `modified_by` varchar(255) DEFAULT NULL,
  `created_by` varchar(255) DEFAULT NULL,
  `mostrar` int(11) DEFAULT '1',
  PRIMARY KEY (`cod`),
  UNIQUE KEY `cod` (`cod`),
  UNIQUE KEY `nome` (`nome`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table agencia_boa.caixa
CREATE TABLE IF NOT EXISTS `caixa` (
  `cod` varchar(255) NOT NULL,
  `valor_inicial` decimal(19,2) DEFAULT '0.00',
  `receitas` decimal(19,2) DEFAULT '0.00',
  `despesas` decimal(19,2) DEFAULT '0.00',
  `estado` int(11) DEFAULT '0',
  `created` date DEFAULT NULL,
  `modified` date DEFAULT NULL,
  `modified_by` varchar(255) DEFAULT NULL,
  `created_by` varchar(255) DEFAULT NULL,
  `obs` varchar(255) DEFAULT NULL,
  `codarmazem` varchar(50) DEFAULT 'AR201875cNP1',
  PRIMARY KEY (`cod`),
  UNIQUE KEY `cod` (`cod`),
  KEY `codarmazem` (`codarmazem`),
  CONSTRAINT `codarmazem` FOREIGN KEY (`codarmazem`) REFERENCES `armazem` (`cod`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for visualização agencia_boa.caixa_geral
-- Creating temporary table to overcome VIEW dependency errors
CREATE TABLE `caixa_geral` (
	`cod_facturacao` VARCHAR(255) NULL COLLATE 'latin1_swedish_ci',
	`numero` INT(11) NULL,
	`ano` INT(11) NULL,
	`mes` INT(11) NULL,
	`custo_produto` DECIMAL(19,2) NULL,
	`desconto_produto` DECIMAL(19,2) NULL,
	`subtotal_produtos` DECIMAL(19,2) NULL,
	`preco_produtos` DECIMAL(19,2) NULL,
	`lucro_produtos` DECIMAL(19,2) NULL,
	`quantidade_produtos` DECIMAL(19,2) NULL,
	`taxa_produtos` DECIMAL(19,2) NULL,
	`total_produtos` DECIMAL(19,2) NULL,
	`cod` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`valor_inicial` DECIMAL(19,2) NULL,
	`despesas` DECIMAL(19,2) NULL,
	`receitas` DECIMAL(19,2) NULL,
	`data_abertura` DATE NULL,
	`aberta_por` VARCHAR(255) NULL COLLATE 'latin1_swedish_ci',
	`data_feixo` DATE NULL,
	`fechada_por` VARCHAR(255) NULL COLLATE 'latin1_swedish_ci',
	`produtos_nome` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`produtos_cliente` VARCHAR(255) NULL COLLATE 'latin1_swedish_ci',
	`nome_documento` VARCHAR(255) NULL COLLATE 'latin1_swedish_ci',
	`caixa_obs` VARCHAR(255) NULL COLLATE 'latin1_swedish_ci',
	`comissao` DECIMAL(19,2) NULL,
	`pagamento` DECIMAL(19,2) NULL,
	`user` VARCHAR(255) NULL COLLATE 'latin1_swedish_ci'
) ENGINE=MyISAM;

-- Dumping structure for table agencia_boa.categorias
CREATE TABLE IF NOT EXISTS `categorias` (
  `cod` int(11) NOT NULL AUTO_INCREMENT,
  `valor` decimal(19,2) DEFAULT '0.00',
  `categoria` varchar(255) NOT NULL,
  `obs` varchar(255) DEFAULT NULL,
  `created` datetime DEFAULT NULL,
  `modified` datetime DEFAULT NULL,
  `modified_by` varchar(255) DEFAULT NULL,
  `created_by` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`cod`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table agencia_boa.cc_clientes
CREATE TABLE IF NOT EXISTS `cc_clientes` (
  `cod` int(11) NOT NULL AUTO_INCREMENT,
  `cliente` varchar(50) DEFAULT NULL,
  `documento` varchar(20) DEFAULT NULL,
  `data` date DEFAULT NULL,
  `iva` decimal(19,2) DEFAULT NULL,
  `valor_a_pagar` decimal(19,2) DEFAULT NULL,
  `valor_pago` decimal(19,2) DEFAULT NULL,
  `saldo` decimal(19,2) DEFAULT NULL,
  `estado` int(11) DEFAULT '1',
  `obs` text,
  `created` date DEFAULT NULL,
  `modified` date DEFAULT NULL,
  `modified_by` varchar(20) DEFAULT NULL,
  `created_by` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`cod`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table agencia_boa.cc_fornecedores
CREATE TABLE IF NOT EXISTS `cc_fornecedores` (
  `cod` int(11) NOT NULL AUTO_INCREMENT,
  `fornecedor` varchar(50) DEFAULT NULL,
  `documento` varchar(20) DEFAULT NULL,
  `data` date DEFAULT NULL,
  `iva` decimal(19,2) DEFAULT NULL,
  `valor_a_pagar` decimal(19,2) DEFAULT NULL,
  `valor_pago` decimal(19,2) DEFAULT NULL,
  `saldo` decimal(19,2) DEFAULT NULL,
  `estado` int(11) DEFAULT '1',
  `obs` text,
  `created` date DEFAULT NULL,
  `modified` date DEFAULT NULL,
  `modified_by` varchar(20) DEFAULT NULL,
  `created_by` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`cod`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table agencia_boa.certificado
CREATE TABLE IF NOT EXISTS `certificado` (
  `cod` int(11) NOT NULL AUTO_INCREMENT,
  `numero` varchar(50) NOT NULL,
  `codformacao` int(11) DEFAULT NULL,
  `codempresa` varchar(50) DEFAULT NULL,
  `codestudante` varchar(50) DEFAULT NULL,
  `data` date DEFAULT NULL,
  `validade` date DEFAULT NULL,
  `obs` varchar(255) DEFAULT NULL,
  `estado` int(11) DEFAULT '1',
  `created` date DEFAULT NULL,
  `modified` date DEFAULT NULL,
  `modified_by` varchar(255) DEFAULT NULL,
  `created_by` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`cod`),
  UNIQUE KEY `numero` (`numero`),
  KEY `codformacao` (`codformacao`),
  KEY `codempresa` (`codempresa`),
  KEY `codestudante` (`codestudante`),
  CONSTRAINT `certificado_ibfk_1` FOREIGN KEY (`codformacao`) REFERENCES `formacao` (`cod`),
  CONSTRAINT `certificado_ibfk_2` FOREIGN KEY (`codempresa`) REFERENCES `clientes` (`cod`),
  CONSTRAINT `certificado_ibfk_3` FOREIGN KEY (`codestudante`) REFERENCES `estudantes` (`cod`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table agencia_boa.check_in
CREATE TABLE IF NOT EXISTS `check_in` (
  `cod` int(11) NOT NULL AUTO_INCREMENT,
  `data_entrada` date DEFAULT NULL,
  `data_saida` date DEFAULT NULL,
  `cod_cliente` varchar(255) DEFAULT NULL,
  `cod_quarto` int(11) DEFAULT NULL,
  `total` decimal(19,2) DEFAULT '0.00',
  `pago` decimal(19,2) DEFAULT '0.00',
  `divida` decimal(19,2) DEFAULT '0.00',
  `obs` varchar(255) DEFAULT NULL,
  `created` date DEFAULT NULL,
  `modified` date DEFAULT NULL,
  `modified_by` varchar(255) DEFAULT NULL,
  `created_by` varchar(255) DEFAULT NULL,
  `estado` int(11) DEFAULT '0',
  `hospede` varchar(255) DEFAULT NULL,
  `voucher` varchar(50) DEFAULT NULL,
  `pagamento` varchar(50) DEFAULT NULL,
  `moeda` varchar(50) DEFAULT NULL,
  `codfacturacao` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`cod`),
  KEY `cod_cliente` (`cod_cliente`),
  KEY `cod_quarto` (`cod_quarto`),
  CONSTRAINT `check_in_ibfk_1` FOREIGN KEY (`cod_cliente`) REFERENCES `hospedes` (`cod`),
  CONSTRAINT `check_in_ibfk_2` FOREIGN KEY (`cod_quarto`) REFERENCES `quartos` (`cod`)
) ENGINE=InnoDB AUTO_INCREMENT=44 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for visualização agencia_boa.check_in_view
-- Creating temporary table to overcome VIEW dependency errors
CREATE TABLE `check_in_view` (
	`cod` INT(11) NOT NULL,
	`data_entrada` DATE NULL,
	`data_saida` DATE NULL,
	`nome` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`cod_quarto` INT(11) NULL,
	`voucher` VARCHAR(50) NULL COLLATE 'latin1_swedish_ci',
	`pagamento` VARCHAR(50) NULL COLLATE 'latin1_swedish_ci',
	`moeda` VARCHAR(50) NULL COLLATE 'latin1_swedish_ci',
	`codfacturacao` VARCHAR(50) NULL COLLATE 'latin1_swedish_ci'
) ENGINE=MyISAM;

-- Dumping structure for table agencia_boa.check_out
CREATE TABLE IF NOT EXISTS `check_out` (
  `cod` int(11) NOT NULL AUTO_INCREMENT,
  `data_saida` date DEFAULT NULL,
  `cod_cliente` varchar(255) DEFAULT NULL,
  `cod_quarto` int(11) DEFAULT NULL,
  `obs` varchar(255) DEFAULT NULL,
  `created` date DEFAULT NULL,
  `modified` date DEFAULT NULL,
  `modified_by` varchar(255) DEFAULT NULL,
  `created_by` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`cod`),
  KEY `cod_quarto` (`cod_quarto`),
  KEY `cod_cliente` (`cod_cliente`),
  CONSTRAINT `check_out_ibfk_1` FOREIGN KEY (`cod_quarto`) REFERENCES `quartos` (`cod`),
  CONSTRAINT `check_out_ibfk_2` FOREIGN KEY (`cod_cliente`) REFERENCES `hospedes` (`cod`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table agencia_boa.cheques
CREATE TABLE IF NOT EXISTS `cheques` (
  `cod` int(11) NOT NULL AUTO_INCREMENT,
  `cod_cliente` varchar(50) NOT NULL,
  `cheque_numero` varchar(50) DEFAULT NULL,
  `banco` varchar(50) DEFAULT NULL,
  `valor` decimal(19,2) DEFAULT NULL,
  `data_entrada` date DEFAULT NULL,
  `data_vencimento` date DEFAULT NULL,
  `estado` int(11) DEFAULT '1',
  `obs` text,
  `created` date DEFAULT NULL,
  `modified` date DEFAULT NULL,
  `modified_by` varchar(20) DEFAULT NULL,
  `created_by` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`cod`),
  KEY `cod_cliente` (`cod_cliente`),
  CONSTRAINT `cheques_ibfk_1` FOREIGN KEY (`cod_cliente`) REFERENCES `clientes` (`cod`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table agencia_boa.clientes
CREATE TABLE IF NOT EXISTS `clientes` (
  `cod` varchar(255) NOT NULL,
  `nome` varchar(255) NOT NULL,
  `endereco` varchar(255) DEFAULT NULL,
  `NUIT` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `contactos` varchar(255) DEFAULT NULL,
  `desconto` decimal(19,2) DEFAULT NULL,
  `valor_minimo` decimal(19,2) DEFAULT NULL,
  `obs` varchar(255) DEFAULT NULL,
  `estado` int(11) DEFAULT '1',
  `created` date DEFAULT NULL,
  `modified` date DEFAULT NULL,
  `modified_by` varchar(255) DEFAULT NULL,
  `created_by` varchar(255) DEFAULT NULL,
  `credito` decimal(19,2) DEFAULT '0.00',
  PRIMARY KEY (`cod`),
  UNIQUE KEY `cod` (`cod`),
  UNIQUE KEY `nome` (`nome`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table agencia_boa.config
CREATE TABLE IF NOT EXISTS `config` (
  `empresa` varchar(255) NOT NULL,
  `f_template` varchar(255) DEFAULT '',
  `rec_template` varchar(255) DEFAULT '',
  `req_template` varchar(255) DEFAULT '',
  `c_cliente` int(11) DEFAULT '1',
  `cliente_n` int(11) DEFAULT '1',
  `saldo` int(11) DEFAULT '1',
  `c_inactivo` int(11) DEFAULT '1',
  `desc_automatico` int(11) DEFAULT '1',
  `ac_credito` int(11) DEFAULT '1',
  `pos1` varchar(255) DEFAULT '',
  `pos2` varchar(255) DEFAULT '',
  `pos3` varchar(255) DEFAULT '',
  `pos4` varchar(255) DEFAULT '',
  `pos5` varchar(255) DEFAULT '',
  `so_vd` int(11) DEFAULT '0',
  `iva_incluso` int(11) DEFAULT '1',
  `regime` int(11) DEFAULT '1',
  `isento` int(11) DEFAULT '1',
  `vendas_zero` int(11) DEFAULT '1',
  `cop1` int(11) DEFAULT '1',
  `cop2` int(11) DEFAULT '1',
  `cop3` int(11) DEFAULT '1',
  `cop4` int(11) DEFAULT '1',
  `cop5` int(11) DEFAULT '1',
  PRIMARY KEY (`empresa`),
  UNIQUE KEY `empresa` (`empresa`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table agencia_boa.contas
CREATE TABLE IF NOT EXISTS `contas` (
  `cod` int(11) NOT NULL AUTO_INCREMENT,
  `nome_banco` varchar(50) NOT NULL,
  `conta` varchar(20) NOT NULL,
  `nib` varchar(20) DEFAULT NULL,
  `swift` varchar(20) DEFAULT NULL,
  `endereco` varchar(255) DEFAULT NULL,
  `estado` int(11) DEFAULT NULL,
  `obs` varchar(255) DEFAULT NULL,
  `created` date DEFAULT NULL,
  `modified` date DEFAULT NULL,
  `modified_by` varchar(255) DEFAULT NULL,
  `created_by` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`cod`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table agencia_boa.cozinha
CREATE TABLE IF NOT EXISTS `cozinha` (
  `cod` varchar(255) NOT NULL,
  `numero` int(11) DEFAULT NULL,
  `coddocumento` varchar(255) DEFAULT NULL,
  `codcliente` varchar(255) DEFAULT NULL,
  `codarmazem` varchar(255) DEFAULT NULL,
  `data` date DEFAULT NULL,
  `custo` decimal(19,2) DEFAULT '0.00',
  `subtotal` decimal(19,2) DEFAULT '0.00',
  `desconto` decimal(19,2) DEFAULT '0.00',
  `taxa` decimal(19,2) DEFAULT '0.00',
  `total` decimal(19,2) DEFAULT '0.00',
  `lucro` decimal(19,2) DEFAULT '0.00',
  `debito` decimal(19,2) DEFAULT '0.00',
  `credito` decimal(19,2) DEFAULT '0.00',
  `saldo` decimal(19,2) DEFAULT '0.00',
  `troco` decimal(19,2) DEFAULT '0.00',
  `banco` decimal(19,2) DEFAULT '0.00',
  `cash` decimal(19,2) DEFAULT '0.00',
  `tranferencia` decimal(19,2) DEFAULT '0.00',
  `estado` int(11) DEFAULT '1',
  `extenso` varchar(255) DEFAULT NULL,
  `ano` int(11) DEFAULT NULL,
  `mes` int(11) DEFAULT NULL,
  `obs` varchar(255) DEFAULT NULL,
  `created` date DEFAULT NULL,
  `modified` date DEFAULT NULL,
  `created_by` varchar(255) DEFAULT NULL,
  `finalizado` int(11) DEFAULT '0',
  `modified_by` varchar(255) DEFAULT NULL,
  `caixa` varchar(255) NOT NULL,
  `pago` decimal(19,2) DEFAULT '0.00',
  `validade` date DEFAULT NULL,
  `mesa` int(11) DEFAULT NULL,
  `codfacturacao` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`cod`),
  UNIQUE KEY `cod` (`cod`),
  KEY `caixa` (`caixa`),
  KEY `codcliente` (`codcliente`),
  KEY `codarmazem` (`codarmazem`),
  KEY `codfacturacao` (`codfacturacao`),
  CONSTRAINT `codfacturacao` FOREIGN KEY (`codfacturacao`) REFERENCES `facturacao` (`cod`),
  CONSTRAINT `cozinha_ibfk_1` FOREIGN KEY (`caixa`) REFERENCES `caixa` (`cod`),
  CONSTRAINT `cozinha_ibfk_2` FOREIGN KEY (`codcliente`) REFERENCES `clientes` (`cod`),
  CONSTRAINT `cozinha_ibfk_3` FOREIGN KEY (`codarmazem`) REFERENCES `armazem` (`cod`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table agencia_boa.cozinhadetalhe
CREATE TABLE IF NOT EXISTS `cozinhadetalhe` (
  `cod` int(11) NOT NULL AUTO_INCREMENT,
  `codcozinha` varchar(255) NOT NULL,
  `codarmazem` varchar(50) DEFAULT 'AR201875cNP1',
  `mesa` int(11) DEFAULT NULL,
  `codproduto` varchar(255) DEFAULT NULL,
  `custo` decimal(19,2) DEFAULT '0.00',
  `preco` decimal(19,2) DEFAULT '0.00',
  `quantidade` decimal(19,2) DEFAULT '0.00',
  `subtotal` decimal(19,2) DEFAULT '0.00',
  `desconto` decimal(19,2) DEFAULT '0.00',
  `taxa` decimal(19,2) DEFAULT '0.00',
  `total` decimal(19,2) DEFAULT '0.00',
  `lucro` decimal(19,2) DEFAULT '0.00',
  PRIMARY KEY (`cod`),
  KEY `codcozinha` (`codcozinha`),
  KEY `codarmazem` (`codarmazem`),
  CONSTRAINT `cozinhadetalhe_ibfk_1` FOREIGN KEY (`codcozinha`) REFERENCES `cozinha` (`cod`),
  CONSTRAINT `cozinhadetalhe_ibfk_2` FOREIGN KEY (`codarmazem`) REFERENCES `armazem` (`cod`)
) ENGINE=InnoDB AUTO_INCREMENT=154 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table agencia_boa.cursos
CREATE TABLE IF NOT EXISTS `cursos` (
  `cod` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(255) DEFAULT NULL,
  `data_inicio` date DEFAULT NULL,
  `data_final` date DEFAULT NULL,
  `duracao` decimal(6,2) DEFAULT NULL,
  `valor` decimal(19,2) DEFAULT '0.00',
  `percentagem` decimal(10,2) DEFAULT NULL,
  `obs` varchar(255) DEFAULT NULL,
  `estado` int(11) DEFAULT '1',
  `created` date DEFAULT NULL,
  `modified` date DEFAULT NULL,
  `modified_by` varchar(255) DEFAULT NULL,
  `created_by` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`cod`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table agencia_boa.documentos
CREATE TABLE IF NOT EXISTS `documentos` (
  `cod` varchar(255) NOT NULL,
  `nome` varchar(255) NOT NULL,
  `subtotal` int(11) DEFAULT '1',
  `desconto` int(11) DEFAULT '1',
  `taxa` int(11) DEFAULT '1',
  `total` int(11) DEFAULT '1',
  `obs` varchar(255) DEFAULT NULL,
  `created` date DEFAULT NULL,
  `modified` date DEFAULT NULL,
  `modified_by` varchar(255) DEFAULT NULL,
  `created_by` varchar(255) DEFAULT NULL,
  `stock` int(11) DEFAULT '0',
  `estado` int(11) DEFAULT '1',
  `visivel` int(11) DEFAULT '1',
  UNIQUE KEY `cod` (`cod`),
  UNIQUE KEY `nome` (`nome`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for visualização agencia_boa.entradas
-- Creating temporary table to overcome VIEW dependency errors
CREATE TABLE `entradas` (
	`cod_documento` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`doc_numero` VARCHAR(255) NULL COLLATE 'latin1_swedish_ci',
	`cod_produto` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`nome` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`qty` DECIMAL(19,2) NULL,
	`preco` DECIMAL(19,2) NULL,
	`total` DECIMAL(38,4) NULL,
	`entidade` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`date_created` DATE NULL,
	`nomearmazem` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`user` VARCHAR(50) NOT NULL COLLATE 'latin1_swedish_ci'
) ENGINE=MyISAM;

-- Dumping structure for table agencia_boa.estudantes
CREATE TABLE IF NOT EXISTS `estudantes` (
  `cod` varchar(50) NOT NULL,
  `nome` varchar(255) NOT NULL,
  `apelido` varchar(255) DEFAULT NULL,
  `endereco` varchar(255) DEFAULT NULL,
  `sexo` varchar(15) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `nascimento` varchar(50) DEFAULT NULL,
  `contactos` varchar(255) DEFAULT NULL,
  `emergencia` varchar(255) DEFAULT NULL,
  `tipo_id` varchar(20) DEFAULT NULL,
  `numero_id` varchar(20) DEFAULT NULL,
  `validade_id` varchar(50) DEFAULT NULL,
  `nacionalidade` varchar(50) DEFAULT NULL,
  `obs` varchar(255) DEFAULT NULL,
  `estado` int(11) DEFAULT '1',
  `created` date DEFAULT NULL,
  `modified` date DEFAULT NULL,
  `modified_by` varchar(255) DEFAULT NULL,
  `created_by` varchar(255) DEFAULT NULL,
  `foto` varchar(255) DEFAULT NULL,
  `empresa` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`cod`),
  KEY `empresa` (`empresa`),
  CONSTRAINT `estudantes_ibfk_1` FOREIGN KEY (`empresa`) REFERENCES `clientes` (`cod`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table agencia_boa.facturacao
CREATE TABLE IF NOT EXISTS `facturacao` (
  `cod` varchar(255) NOT NULL,
  `numero` int(11) DEFAULT NULL,
  `coddocumento` varchar(255) DEFAULT NULL,
  `codcliente` varchar(255) DEFAULT NULL,
  `data` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `custo` decimal(19,2) DEFAULT '0.00',
  `subtotal` decimal(19,2) DEFAULT '0.00',
  `desconto` decimal(19,2) DEFAULT '0.00',
  `taxa` decimal(19,2) DEFAULT '0.00',
  `total` decimal(19,2) DEFAULT '0.00',
  `lucro` decimal(19,2) DEFAULT '0.00',
  `debito` decimal(19,2) DEFAULT '0.00',
  `credito` decimal(19,2) DEFAULT '0.00',
  `saldo` decimal(19,2) DEFAULT '0.00',
  `troco` decimal(19,2) DEFAULT '0.00',
  `banco` decimal(19,2) DEFAULT '0.00',
  `cash` decimal(19,2) DEFAULT '0.00',
  `tranferencia` decimal(19,2) DEFAULT '0.00',
  `estado` int(11) DEFAULT '1',
  `extenso` varchar(255) DEFAULT NULL,
  `ano` int(11) DEFAULT NULL,
  `mes` int(11) DEFAULT NULL,
  `obs` varchar(255) DEFAULT NULL,
  `created` date DEFAULT NULL,
  `modified` date DEFAULT NULL,
  `modified_by` varchar(255) DEFAULT NULL,
  `created_by` varchar(255) DEFAULT NULL,
  `finalizado` int(11) DEFAULT '0',
  `caixa` varchar(255) NOT NULL,
  `pago` decimal(19,2) DEFAULT '0.00',
  `comissao` decimal(19,2) DEFAULT '0.00',
  `pagamento` decimal(19,2) DEFAULT '0.00',
  `validade` date DEFAULT '1980-01-01',
  `nome` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`cod`),
  UNIQUE KEY `cod` (`cod`),
  KEY `caixa` (`caixa`),
  KEY `codcliente` (`codcliente`),
  CONSTRAINT `facturacao_ibfk_1` FOREIGN KEY (`caixa`) REFERENCES `caixa` (`cod`),
  CONSTRAINT `facturacao_ibfk_2` FOREIGN KEY (`codcliente`) REFERENCES `clientes` (`cod`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table agencia_boa.facturacaodetalhe
CREATE TABLE IF NOT EXISTS `facturacaodetalhe` (
  `cod` int(11) NOT NULL AUTO_INCREMENT,
  `codfacturacao` varchar(255) NOT NULL,
  `codproduto` varchar(255) DEFAULT NULL,
  `custo` decimal(19,2) DEFAULT '0.00',
  `preco` decimal(19,2) DEFAULT '0.00',
  `quantidade` decimal(19,2) DEFAULT '0.00',
  `subtotal` decimal(19,2) DEFAULT '0.00',
  `desconto` decimal(19,2) DEFAULT '0.00',
  `taxa` decimal(19,2) DEFAULT '0.00',
  `total` decimal(19,2) DEFAULT '0.00',
  `lucro` decimal(19,2) DEFAULT '0.00',
  `codarmazem` varchar(50) DEFAULT 'AR201875cNP1',
  `codstock` varchar(50) DEFAULT NULL,
  `created` datetime DEFAULT CURRENT_TIMESTAMP,
  `ordem` int(11) DEFAULT '0',
  PRIMARY KEY (`cod`),
  KEY `codfacturacao` (`codfacturacao`),
  KEY `armazem` (`codarmazem`),
  KEY `codstock` (`codstock`),
  CONSTRAINT `armazem` FOREIGN KEY (`codarmazem`) REFERENCES `armazem` (`cod`),
  CONSTRAINT `codstock` FOREIGN KEY (`codstock`) REFERENCES `stock` (`cod`),
  CONSTRAINT `facturacaodetalhe_ibfk_1` FOREIGN KEY (`codfacturacao`) REFERENCES `facturacao` (`cod`)
) ENGINE=InnoDB AUTO_INCREMENT=5022 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for visualização agencia_boa.facturas_nao_pagas
-- Creating temporary table to overcome VIEW dependency errors
CREATE TABLE `facturas_nao_pagas` (
	`cod` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`numero` INT(11) NULL,
	`data` TIMESTAMP NOT NULL,
	`cliente` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`total` DECIMAL(19,2) NULL,
	`saldo` DECIMAL(19,2) NULL,
	`debito` DECIMAL(19,2) NULL,
	`credito` DECIMAL(19,2) NULL,
	`obs` VARCHAR(255) NULL COLLATE 'latin1_swedish_ci'
) ENGINE=MyISAM;

-- Dumping structure for visualização agencia_boa.factura_geral
-- Creating temporary table to overcome VIEW dependency errors
CREATE TABLE `factura_geral` (
	`codfacturacao` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`numerofactura` INT(11) NULL,
	`nomedocumento` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`data` DATE NULL,
	`user` VARCHAR(255) NULL COLLATE 'latin1_swedish_ci',
	`subtotal_geral` DECIMAL(19,2) NULL,
	`desconto_geral` DECIMAL(19,2) NULL,
	`taxa_geral` DECIMAL(19,2) NULL,
	`total_geral` DECIMAL(19,2) NULL,
	`extenso` VARCHAR(255) NULL COLLATE 'latin1_swedish_ci',
	`cliente` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`endereco` VARCHAR(255) NULL COLLATE 'latin1_swedish_ci',
	`NUIT` VARCHAR(255) NULL COLLATE 'latin1_swedish_ci',
	`email` VARCHAR(255) NULL COLLATE 'latin1_swedish_ci',
	`codproduto` VARCHAR(255) NULL COLLATE 'latin1_swedish_ci',
	`produto` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`quantidade` DECIMAL(19,2) NULL,
	`preco` DECIMAL(19,2) NULL,
	`desconto` DECIMAL(19,2) NULL,
	`taxa` DECIMAL(19,2) NULL,
	`subtotal` DECIMAL(19,2) NULL,
	`total` DECIMAL(19,2) NULL,
	`ano` INT(11) NULL,
	`mes` INT(11) NULL,
	`pago` DECIMAL(19,2) NULL,
	`troco` DECIMAL(19,2) NULL,
	`coddocumento` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`contactos` VARCHAR(255) NULL COLLATE 'latin1_swedish_ci',
	`validade` DATE NULL,
	`obs` VARCHAR(255) NULL COLLATE 'latin1_swedish_ci',
	`nome` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci'
) ENGINE=MyISAM;

-- Dumping structure for table agencia_boa.familia
CREATE TABLE IF NOT EXISTS `familia` (
  `cod` varchar(255) NOT NULL,
  `nome` varchar(255) NOT NULL,
  `obs` varchar(255) DEFAULT NULL,
  `estado` int(11) DEFAULT '1',
  `created` date DEFAULT NULL,
  `modified` date DEFAULT NULL,
  `created_by` varchar(255) DEFAULT NULL,
  `modified_by` varchar(255) DEFAULT NULL,
  `stock` int(11) DEFAULT '1',
  PRIMARY KEY (`cod`),
  UNIQUE KEY `cod` (`cod`),
  UNIQUE KEY `nome` (`nome`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for visualização agencia_boa.fecho_caixa
-- Creating temporary table to overcome VIEW dependency errors
CREATE TABLE `fecho_caixa` (
	`valor_inicial` DECIMAL(19,2) NULL,
	`receitas` DECIMAL(19,2) NULL,
	`despesas` DECIMAL(19,2) NULL,
	`CRIADA_POR` VARCHAR(255) NULL COLLATE 'latin1_swedish_ci',
	`FECHADA_POR` VARCHAR(255) NULL COLLATE 'latin1_swedish_ci',
	`ABERTURA` DATE NULL,
	`FECHO` DATE NULL,
	`DOCUMENTO` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`numero` INT(11) NULL,
	`CLIENTE` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`subtotal` DECIMAL(19,2) NULL,
	`desconto` DECIMAL(19,2) NULL,
	`taxa` DECIMAL(19,2) NULL,
	`total` DECIMAL(19,2) NULL,
	`CHEQUE` DECIMAL(19,2) NULL,
	`NUMERARIO` DECIMAL(19,2) NULL,
	`POS` DECIMAL(19,2) NULL,
	`estado_caixa` INT(11) NULL,
	`estado_factura` INT(11) NULL,
	`caixa_numero` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`doc` VARCHAR(255) NULL COLLATE 'latin1_swedish_ci',
	`comissao` DECIMAL(19,2) NULL,
	`pagamento` DECIMAL(19,2) NULL,
	`lucro` DECIMAL(19,2) NULL,
	`modified` DATE NULL,
	`user` VARCHAR(255) NULL COLLATE 'latin1_swedish_ci'
) ENGINE=MyISAM;

-- Dumping structure for visualização agencia_boa.fecho_caixa_detalhada
-- Creating temporary table to overcome VIEW dependency errors
CREATE TABLE `fecho_caixa_detalhada` (
	`valor_inicial` DECIMAL(19,2) NULL,
	`receitas` DECIMAL(19,2) NULL,
	`despesas` DECIMAL(19,2) NULL,
	`CRIADA_POR` VARCHAR(255) NULL COLLATE 'latin1_swedish_ci',
	`FECHADA_POR` VARCHAR(255) NULL COLLATE 'latin1_swedish_ci',
	`ABERTURA` DATE NULL,
	`FECHO` DATE NULL,
	`DOCUMENTO` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`numero` INT(11) NULL,
	`CLIENTE` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`subtotal` DECIMAL(19,2) NULL,
	`desconto` DECIMAL(19,2) NULL,
	`taxa` DECIMAL(19,2) NULL,
	`total` DECIMAL(19,2) NULL,
	`CHEQUE` DECIMAL(19,2) NULL,
	`NUMERARIO` DECIMAL(19,2) NULL,
	`POS` DECIMAL(19,2) NULL,
	`estado_caixa` INT(11) NULL,
	`estado_factura` INT(11) NULL,
	`caixa_numero` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`doc` VARCHAR(255) NULL COLLATE 'latin1_swedish_ci',
	`comissao` DECIMAL(19,2) NULL,
	`pagamento` DECIMAL(19,2) NULL,
	`lucro` DECIMAL(19,2) NULL,
	`nome` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`quantidade` DECIMAL(19,2) NULL,
	`total_geral` DECIMAL(19,2) NULL,
	`preco_unitario` DECIMAL(19,2) NULL,
	`iva_produto` DECIMAL(19,2) NULL,
	`desconto_unitario` DECIMAL(19,2) NULL,
	`subtotal_produto` DECIMAL(19,2) NULL,
	`user` VARCHAR(255) NULL COLLATE 'latin1_swedish_ci',
	`prod_cod` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`custo` DECIMAL(19,2) NULL
) ENGINE=MyISAM;

-- Dumping structure for table agencia_boa.formacao
CREATE TABLE IF NOT EXISTS `formacao` (
  `cod` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(255) NOT NULL,
  `codcurso` int(11) DEFAULT NULL,
  `codempresa` varchar(50) DEFAULT NULL,
  `codestudante` varchar(50) DEFAULT NULL,
  `valor` decimal(19,2) DEFAULT '0.00',
  `valor_primeira` decimal(19,2) DEFAULT '0.00',
  `valor_segunda` decimal(19,2) DEFAULT '0.00',
  `valor_saldo` decimal(19,2) DEFAULT '0.00',
  `teoria` decimal(10,2) DEFAULT NULL,
  `pratica` decimal(10,2) DEFAULT NULL,
  `comportamento` varchar(15) DEFAULT NULL,
  `resultado` varchar(15) DEFAULT NULL,
  `obs` varchar(255) DEFAULT NULL,
  `estado` int(11) DEFAULT '1',
  `created` date DEFAULT NULL,
  `modified` date DEFAULT NULL,
  `modified_by` varchar(255) DEFAULT NULL,
  `created_by` varchar(255) DEFAULT NULL,
  `instrutor` varchar(50) DEFAULT NULL,
  `data_inicio` date DEFAULT '0000-00-00',
  `data_final` date DEFAULT '0000-00-00',
  PRIMARY KEY (`cod`),
  KEY `codcurso` (`codcurso`),
  KEY `codempresa` (`codempresa`),
  KEY `codestudante` (`codestudante`),
  KEY `instrutor` (`instrutor`),
  CONSTRAINT `formacao_ibfk_1` FOREIGN KEY (`codcurso`) REFERENCES `cursos` (`cod`),
  CONSTRAINT `formacao_ibfk_2` FOREIGN KEY (`codempresa`) REFERENCES `clientes` (`cod`),
  CONSTRAINT `formacao_ibfk_3` FOREIGN KEY (`codestudante`) REFERENCES `estudantes` (`cod`),
  CONSTRAINT `instrutor` FOREIGN KEY (`instrutor`) REFERENCES `instrutores` (`cod`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table agencia_boa.fornecedores
CREATE TABLE IF NOT EXISTS `fornecedores` (
  `cod` varchar(255) NOT NULL,
  `nome` varchar(255) NOT NULL,
  `endereco` varchar(255) DEFAULT NULL,
  `NUIT` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `contactos` varchar(255) DEFAULT NULL,
  `obs` varchar(255) DEFAULT NULL,
  `estado` int(11) DEFAULT '1',
  `created` date DEFAULT NULL,
  `modified` date DEFAULT NULL,
  `modified_by` varchar(255) DEFAULT NULL,
  `created_by` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`cod`),
  UNIQUE KEY `cod` (`cod`),
  UNIQUE KEY `nome` (`nome`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table agencia_boa.hospedes
CREATE TABLE IF NOT EXISTS `hospedes` (
  `cod` varchar(50) NOT NULL,
  `nome` varchar(255) NOT NULL,
  `apelido` varchar(255) DEFAULT NULL,
  `endereco` varchar(255) DEFAULT NULL,
  `sexo` varchar(15) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `nascimento` varchar(50) DEFAULT NULL,
  `contactos` varchar(255) DEFAULT NULL,
  `emergencia` varchar(255) DEFAULT NULL,
  `tipo_id` varchar(20) DEFAULT NULL,
  `numero_id` varchar(20) DEFAULT NULL,
  `validade_id` varchar(50) DEFAULT NULL,
  `nacionalidade` varchar(50) DEFAULT NULL,
  `obs` varchar(255) DEFAULT NULL,
  `estado` int(11) DEFAULT '1',
  `created` date DEFAULT NULL,
  `modified` date DEFAULT NULL,
  `modified_by` varchar(255) DEFAULT NULL,
  `created_by` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`cod`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table agencia_boa.instrutores
CREATE TABLE IF NOT EXISTS `instrutores` (
  `cod` varchar(50) NOT NULL,
  `nome` varchar(255) NOT NULL,
  `apelido` varchar(255) DEFAULT NULL,
  `endereco` varchar(255) DEFAULT NULL,
  `sexo` varchar(15) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `nascimento` varchar(50) DEFAULT NULL,
  `contactos` varchar(255) DEFAULT NULL,
  `emergencia` varchar(255) DEFAULT NULL,
  `tipo_id` varchar(20) DEFAULT NULL,
  `numero_id` varchar(20) DEFAULT NULL,
  `validade_id` varchar(50) DEFAULT NULL,
  `nacionalidade` varchar(50) DEFAULT NULL,
  `obs` varchar(255) DEFAULT NULL,
  `estado` int(11) DEFAULT '1',
  `created` date DEFAULT NULL,
  `modified` date DEFAULT NULL,
  `modified_by` varchar(255) DEFAULT NULL,
  `created_by` varchar(255) DEFAULT NULL,
  `foto` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`cod`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table agencia_boa.mesas
CREATE TABLE IF NOT EXISTS `mesas` (
  `cod` int(11) NOT NULL AUTO_INCREMENT,
  `numero` int(11) NOT NULL,
  `descricao` varchar(50) DEFAULT NULL,
  `codfacturacao` varchar(50) DEFAULT NULL,
  `estado` int(11) DEFAULT '0',
  `created` date DEFAULT NULL,
  `modified` date DEFAULT NULL,
  `modified_by` varchar(255) DEFAULT NULL,
  `created_by` varchar(255) DEFAULT NULL,
  `obs` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`cod`),
  KEY `codfacturacao` (`codfacturacao`),
  CONSTRAINT `mesas_ibfk_1` FOREIGN KEY (`codfacturacao`) REFERENCES `facturacao` (`cod`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=244 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for visualização agencia_boa.movimento_stock
-- Creating temporary table to overcome VIEW dependency errors
CREATE TABLE `movimento_stock` (
	`cod_documento` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`doc_numero` VARCHAR(267) NULL COLLATE 'latin1_swedish_ci',
	`cod_produto` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`nome` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`qty` DECIMAL(19,2) NULL,
	`preco` DECIMAL(19,2) NULL,
	`total` DECIMAL(38,4) NULL,
	`entidade` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`date_created` DATE NULL,
	`nomearmazem` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`user` VARCHAR(50) NOT NULL COLLATE 'latin1_swedish_ci'
) ENGINE=MyISAM;

-- Dumping structure for table agencia_boa.pagamentos
CREATE TABLE IF NOT EXISTS `pagamentos` (
  `cod` int(11) NOT NULL AUTO_INCREMENT,
  `codfornecedor` varchar(255) DEFAULT NULL,
  `codstock` varchar(255) DEFAULT NULL,
  `debito` decimal(19,2) DEFAULT '0.00',
  `credito` decimal(19,2) DEFAULT '0.00',
  `saldo` decimal(19,2) DEFAULT '0.00',
  `documento` varchar(255) DEFAULT NULL,
  `created` date DEFAULT NULL,
  `modified` date DEFAULT NULL,
  `modified_by` varchar(255) DEFAULT NULL,
  `created_by` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`cod`),
  KEY `codfornecedor` (`codfornecedor`),
  KEY `codstock` (`codstock`),
  CONSTRAINT `pagamentos_ibfk_1` FOREIGN KEY (`codfornecedor`) REFERENCES `fornecedores` (`cod`),
  CONSTRAINT `pagamentos_ibfk_2` FOREIGN KEY (`codstock`) REFERENCES `stock` (`cod`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table agencia_boa.pagamento_a_fornecedores
CREATE TABLE IF NOT EXISTS `pagamento_a_fornecedores` (
  `cod` int(11) NOT NULL AUTO_INCREMENT,
  `codcc` int(11) DEFAULT NULL,
  `data` date DEFAULT NULL,
  `saldo_anterior` decimal(19,2) DEFAULT NULL,
  `valor_pago` decimal(19,2) DEFAULT NULL,
  `saldo_actual` decimal(19,2) DEFAULT NULL,
  `estado` int(11) DEFAULT '1',
  `obs` text,
  `created` date DEFAULT NULL,
  `modified` date DEFAULT NULL,
  `modified_by` varchar(20) DEFAULT NULL,
  `created_by` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`cod`),
  KEY `codcc` (`codcc`),
  CONSTRAINT `pagamento_a_fornecedores_ibfk_1` FOREIGN KEY (`codcc`) REFERENCES `cc_fornecedores` (`cod`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table agencia_boa.pagamento_de_clientes
CREATE TABLE IF NOT EXISTS `pagamento_de_clientes` (
  `cod` int(11) NOT NULL AUTO_INCREMENT,
  `codcc` int(11) DEFAULT NULL,
  `data` date DEFAULT NULL,
  `saldo_anterior` decimal(19,2) DEFAULT NULL,
  `valor_pago` decimal(19,2) DEFAULT NULL,
  `saldo_actual` decimal(19,2) DEFAULT NULL,
  `estado` int(11) DEFAULT '1',
  `obs` text,
  `created` date DEFAULT NULL,
  `modified` date DEFAULT NULL,
  `modified_by` varchar(20) DEFAULT NULL,
  `created_by` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`cod`),
  KEY `codcc` (`codcc`),
  CONSTRAINT `pagamento_de_clientes_ibfk_1` FOREIGN KEY (`codcc`) REFERENCES `cc_clientes` (`cod`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table agencia_boa.produtos
CREATE TABLE IF NOT EXISTS `produtos` (
  `cod` varchar(255) NOT NULL,
  `nome` varchar(255) NOT NULL,
  `cod_barras` varchar(255) DEFAULT NULL,
  `codfamilia` varchar(255) DEFAULT NULL,
  `codsubfamilia` varchar(255) DEFAULT NULL,
  `custo` decimal(19,2) DEFAULT NULL,
  `preco` decimal(19,2) DEFAULT NULL,
  `quantidade` decimal(19,2) DEFAULT NULL,
  `quantidade_m` decimal(19,2) DEFAULT NULL,
  `unidade` varchar(255) DEFAULT NULL,
  `obs` varchar(255) DEFAULT NULL,
  `estado` int(11) DEFAULT NULL,
  `foto` varchar(255) DEFAULT NULL,
  `created` date DEFAULT NULL,
  `modified` date DEFAULT NULL,
  `modified_by` varchar(255) DEFAULT NULL,
  `created_by` varchar(255) DEFAULT NULL,
  `preco1` decimal(19,2) DEFAULT '0.00',
  `preco2` decimal(19,2) DEFAULT '0.00',
  `preco3` decimal(19,2) DEFAULT '0.00',
  `preco4` decimal(19,2) DEFAULT '0.00',
  `tipo` int(11) DEFAULT '0',
  `codtaxa` varchar(255) DEFAULT 'TX20182222222',
  `quantidade_max` decimal(19,2) DEFAULT '0.00',
  `favorito` int(11) DEFAULT '0',
  `promocao` int(11) DEFAULT '0',
  `preco_de_venda` int(11) DEFAULT '0',
  PRIMARY KEY (`cod`),
  UNIQUE KEY `cod` (`cod`),
  UNIQUE KEY `nome` (`nome`),
  KEY `codfamilia` (`codfamilia`),
  KEY `taxa` (`codtaxa`),
  CONSTRAINT `produtos_ibfk_1` FOREIGN KEY (`codfamilia`) REFERENCES `familia` (`cod`),
  CONSTRAINT `taxa` FOREIGN KEY (`codtaxa`) REFERENCES `taxas` (`cod`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table agencia_boa.produtosdetalhe
CREATE TABLE IF NOT EXISTS `produtosdetalhe` (
  `cod` int(11) NOT NULL AUTO_INCREMENT,
  `codproduto` varchar(255) NOT NULL,
  `codarmazem` varchar(255) NOT NULL,
  `quantidade` decimal(19,2) DEFAULT NULL,
  `created` date DEFAULT NULL,
  `modified` date DEFAULT NULL,
  `modified_by` varchar(255) DEFAULT NULL,
  `created_by` varchar(255) DEFAULT NULL,
  `validade` date DEFAULT '1980-01-01',
  `contagem` int(11) DEFAULT '0',
  PRIMARY KEY (`cod`),
  KEY `codproduto` (`codproduto`),
  KEY `codarmazem` (`codarmazem`),
  CONSTRAINT `produtosdetalhe_ibfk_1` FOREIGN KEY (`codproduto`) REFERENCES `produtos` (`cod`),
  CONSTRAINT `produtosdetalhe_ibfk_2` FOREIGN KEY (`codarmazem`) REFERENCES `armazem` (`cod`)
) ENGINE=InnoDB AUTO_INCREMENT=3891 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table agencia_boa.quartos
CREATE TABLE IF NOT EXISTS `quartos` (
  `cod` int(11) NOT NULL,
  `cod_preco` int(11) NOT NULL,
  `preco` decimal(19,2) DEFAULT '0.00',
  `estado` int(11) DEFAULT '1',
  `ocupado` int(11) DEFAULT '0',
  `obs` varchar(255) DEFAULT NULL,
  `created` datetime DEFAULT NULL,
  `modified` datetime DEFAULT NULL,
  `modified_by` varchar(255) DEFAULT NULL,
  `created_by` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`cod`),
  KEY `cod_preco` (`cod_preco`),
  CONSTRAINT `quartos_ibfk_1` FOREIGN KEY (`cod_preco`) REFERENCES `categorias` (`cod`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table agencia_boa.receitas
CREATE TABLE IF NOT EXISTS `receitas` (
  `cod` int(11) NOT NULL AUTO_INCREMENT,
  `descricao` varchar(255) DEFAULT NULL,
  `valor` decimal(19,2) DEFAULT NULL,
  `codcaixa` varchar(50) DEFAULT NULL,
  `codarmazem` varchar(50) DEFAULT NULL,
  `created` datetime DEFAULT NULL,
  `modified` datetime DEFAULT NULL,
  `modified_by` varchar(50) DEFAULT NULL,
  `created_by` varchar(50) DEFAULT NULL,
  `obs` text,
  `tipo` int(11) DEFAULT '0',
  `estado` int(11) DEFAULT '1',
  PRIMARY KEY (`cod`),
  KEY `codcaixa` (`codcaixa`),
  KEY `created_by` (`created_by`),
  KEY `modified_by` (`modified_by`),
  KEY `codarmazem` (`codarmazem`),
  CONSTRAINT `receitas_ibfk_1` FOREIGN KEY (`codcaixa`) REFERENCES `caixa` (`cod`),
  CONSTRAINT `receitas_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`cod`),
  CONSTRAINT `receitas_ibfk_3` FOREIGN KEY (`modified_by`) REFERENCES `users` (`cod`),
  CONSTRAINT `receitas_ibfk_4` FOREIGN KEY (`codarmazem`) REFERENCES `armazem` (`cod`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table agencia_boa.recibos
CREATE TABLE IF NOT EXISTS `recibos` (
  `cod` varchar(255) NOT NULL,
  `numero` int(11) DEFAULT NULL,
  `codfactura` varchar(255) DEFAULT NULL,
  `codcliente` varchar(255) DEFAULT NULL,
  `data` date DEFAULT NULL,
  `total` decimal(19,2) DEFAULT '0.00',
  `troco` decimal(19,2) DEFAULT '0.00',
  `banco` decimal(19,2) DEFAULT '0.00',
  `cash` decimal(19,2) DEFAULT '0.00',
  `tranferencia` decimal(19,2) DEFAULT '0.00',
  `estado` int(11) DEFAULT '1',
  `extenso` varchar(255) DEFAULT NULL,
  `ano` int(11) DEFAULT NULL,
  `mes` int(11) DEFAULT NULL,
  `obs` varchar(255) DEFAULT NULL,
  `created` date DEFAULT NULL,
  `modified` date DEFAULT NULL,
  `modified_by` varchar(255) DEFAULT NULL,
  `created_by` varchar(255) DEFAULT NULL,
  `finalizado` int(11) DEFAULT '0',
  `caixa` varchar(255) NOT NULL,
  PRIMARY KEY (`cod`),
  UNIQUE KEY `cod` (`cod`),
  KEY `codcliente` (`codcliente`),
  KEY `codfactura` (`codfactura`),
  KEY `caixa` (`caixa`),
  CONSTRAINT `recibos_ibfk_1` FOREIGN KEY (`codcliente`) REFERENCES `clientes` (`cod`),
  CONSTRAINT `recibos_ibfk_2` FOREIGN KEY (`codfactura`) REFERENCES `facturacao` (`cod`),
  CONSTRAINT `recibos_ibfk_3` FOREIGN KEY (`caixa`) REFERENCES `caixa` (`cod`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table agencia_boa.recibosdetalhe
CREATE TABLE IF NOT EXISTS `recibosdetalhe` (
  `cod` int(11) NOT NULL AUTO_INCREMENT,
  `codrecibo` varchar(255) NOT NULL,
  `factura` int(11) NOT NULL,
  `pago` decimal(19,2) DEFAULT '0.00',
  `saldo` decimal(19,2) DEFAULT '0.00',
  `descricao` varchar(255) DEFAULT NULL,
  `codfactura` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`cod`),
  KEY `codrecibo` (`codrecibo`),
  CONSTRAINT `recibosdetalhe_ibfk_1` FOREIGN KEY (`codrecibo`) REFERENCES `recibos` (`cod`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for visualização agencia_boa.recibo_geral
-- Creating temporary table to overcome VIEW dependency errors
CREATE TABLE `recibo_geral` (
	`cod` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`total` DECIMAL(19,2) NULL,
	`created` DATE NULL,
	`codcliente` VARCHAR(255) NULL COLLATE 'latin1_swedish_ci',
	`extenso` VARCHAR(255) NULL COLLATE 'latin1_swedish_ci',
	`descricao` VARCHAR(255) NULL COLLATE 'latin1_swedish_ci',
	`factura` INT(11) NOT NULL,
	`pago` DECIMAL(19,2) NULL,
	`nome` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`endereco` VARCHAR(255) NULL COLLATE 'latin1_swedish_ci',
	`NUIT` VARCHAR(255) NULL COLLATE 'latin1_swedish_ci',
	`email` VARCHAR(255) NULL COLLATE 'latin1_swedish_ci',
	`finalizado` INT(11) NULL,
	`estado` INT(11) NULL,
	`numero` INT(11) NULL,
	`mes` INT(11) NULL,
	`ano` INT(11) NULL,
	`data` DATE NULL,
	`user` VARCHAR(255) NULL COLLATE 'latin1_swedish_ci',
	`contactos` VARCHAR(255) NULL COLLATE 'latin1_swedish_ci',
	`obs` VARCHAR(255) NULL COLLATE 'latin1_swedish_ci'
) ENGINE=MyISAM;

-- Dumping structure for table agencia_boa.relacoes
CREATE TABLE IF NOT EXISTS `relacoes` (
  `cod` int(11) NOT NULL AUTO_INCREMENT,
  `codproduto1` varchar(100) NOT NULL,
  `quantidade1` decimal(19,2) DEFAULT '0.00',
  `codproduto2` varchar(100) NOT NULL,
  `quantidade2` decimal(19,2) DEFAULT '0.00',
  `codarmazem` varchar(50) DEFAULT NULL,
  `created` date DEFAULT NULL,
  `modified` date DEFAULT NULL,
  `modified_by` varchar(100) DEFAULT NULL,
  `created_by` varchar(100) DEFAULT NULL,
  `obs` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`cod`),
  KEY `codproduto1` (`codproduto1`),
  KEY `codproduto2` (`codproduto2`),
  KEY `codarmazem` (`codarmazem`),
  KEY `created_by` (`created_by`),
  KEY `modified_by` (`modified_by`),
  CONSTRAINT `relacoes_ibfk_1` FOREIGN KEY (`codproduto1`) REFERENCES `produtos` (`cod`),
  CONSTRAINT `relacoes_ibfk_2` FOREIGN KEY (`codproduto2`) REFERENCES `produtos` (`cod`),
  CONSTRAINT `relacoes_ibfk_3` FOREIGN KEY (`codarmazem`) REFERENCES `armazem` (`cod`),
  CONSTRAINT `relacoes_ibfk_4` FOREIGN KEY (`created_by`) REFERENCES `users` (`cod`),
  CONSTRAINT `relacoes_ibfk_5` FOREIGN KEY (`modified_by`) REFERENCES `users` (`cod`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table agencia_boa.requisicao
CREATE TABLE IF NOT EXISTS `requisicao` (
  `cod` varchar(255) NOT NULL,
  `numero` int(11) DEFAULT NULL,
  `coddocumento` varchar(255) DEFAULT NULL,
  `codcliente` varchar(255) DEFAULT NULL,
  `codarmazem` varchar(255) DEFAULT NULL,
  `data` date DEFAULT NULL,
  `custo` decimal(19,2) DEFAULT '0.00',
  `subtotal` decimal(19,2) DEFAULT '0.00',
  `desconto` decimal(19,2) DEFAULT '0.00',
  `taxa` decimal(19,2) DEFAULT '0.00',
  `total` decimal(19,2) DEFAULT '0.00',
  `lucro` decimal(19,2) DEFAULT '0.00',
  `debito` decimal(19,2) DEFAULT '0.00',
  `credito` decimal(19,2) DEFAULT '0.00',
  `saldo` decimal(19,2) DEFAULT '0.00',
  `troco` decimal(19,2) DEFAULT '0.00',
  `banco` decimal(19,2) DEFAULT '0.00',
  `cash` decimal(19,2) DEFAULT '0.00',
  `tranferencia` decimal(19,2) DEFAULT '0.00',
  `estado` int(11) DEFAULT '1',
  `extenso` varchar(255) DEFAULT NULL,
  `ano` int(11) DEFAULT NULL,
  `mes` int(11) DEFAULT NULL,
  `obs` varchar(255) DEFAULT NULL,
  `created` date DEFAULT NULL,
  `modified` date DEFAULT NULL,
  `created_by` varchar(255) DEFAULT NULL,
  `finalizado` int(11) DEFAULT '0',
  `modified_by` varchar(255) DEFAULT NULL,
  `caixa` varchar(255) NOT NULL,
  `pago` decimal(19,2) DEFAULT '0.00',
  `validade` date DEFAULT NULL,
  PRIMARY KEY (`cod`),
  UNIQUE KEY `cod` (`cod`),
  KEY `caixa` (`caixa`),
  KEY `codcliente` (`codcliente`),
  KEY `codarmazem` (`codarmazem`),
  CONSTRAINT `requisicao_ibfk_1` FOREIGN KEY (`caixa`) REFERENCES `caixa` (`cod`),
  CONSTRAINT `requisicao_ibfk_2` FOREIGN KEY (`codcliente`) REFERENCES `clientes` (`cod`),
  CONSTRAINT `requisicao_ibfk_3` FOREIGN KEY (`codarmazem`) REFERENCES `armazem` (`cod`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table agencia_boa.requisicaodetalhe
CREATE TABLE IF NOT EXISTS `requisicaodetalhe` (
  `cod` int(11) NOT NULL AUTO_INCREMENT,
  `codrequisicao` varchar(255) NOT NULL,
  `codarmazem1` varchar(50) DEFAULT 'AR201875cNP1',
  `codarmazem2` varchar(50) DEFAULT 'AR201875cNP1',
  `codproduto` varchar(255) DEFAULT NULL,
  `custo` decimal(19,2) DEFAULT '0.00',
  `preco` decimal(19,2) DEFAULT '0.00',
  `quantidade` decimal(19,2) DEFAULT '0.00',
  `subtotal` decimal(19,2) DEFAULT '0.00',
  `desconto` decimal(19,2) DEFAULT '0.00',
  `taxa` decimal(19,2) DEFAULT '0.00',
  `total` decimal(19,2) DEFAULT '0.00',
  `lucro` decimal(19,2) DEFAULT '0.00',
  PRIMARY KEY (`cod`),
  KEY `codrequisicao` (`codrequisicao`),
  KEY `codarmazem1` (`codarmazem1`),
  KEY `codarmazem2` (`codarmazem2`),
  CONSTRAINT `requisicaodetalhe_ibfk_1` FOREIGN KEY (`codrequisicao`) REFERENCES `requisicao` (`cod`),
  CONSTRAINT `requisicaodetalhe_ibfk_2` FOREIGN KEY (`codarmazem1`) REFERENCES `armazem` (`cod`),
  CONSTRAINT `requisicaodetalhe_ibfk_3` FOREIGN KEY (`codarmazem2`) REFERENCES `armazem` (`cod`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table agencia_boa.reservas
CREATE TABLE IF NOT EXISTS `reservas` (
  `cod` int(11) NOT NULL AUTO_INCREMENT,
  `data_entrada` date DEFAULT NULL,
  `data_saida` date DEFAULT NULL,
  `cod_cliente` varchar(255) DEFAULT NULL,
  `cod_quarto` int(11) DEFAULT NULL,
  `obs` varchar(255) DEFAULT NULL,
  `created` date DEFAULT NULL,
  `modified` date DEFAULT NULL,
  `modified_by` varchar(255) DEFAULT NULL,
  `created_by` varchar(255) DEFAULT NULL,
  `estado` int(11) DEFAULT '1',
  `hospede` varchar(255) DEFAULT NULL,
  `voucher` varchar(50) DEFAULT NULL,
  `pagamento` varchar(50) DEFAULT NULL,
  `moeda` varchar(50) DEFAULT NULL,
  `codfacturacao` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`cod`),
  KEY `cod_cliente` (`cod_cliente`),
  CONSTRAINT `reservas_ibfk_1` FOREIGN KEY (`cod_cliente`) REFERENCES `hospedes` (`cod`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for visualização agencia_boa.reservas_view
-- Creating temporary table to overcome VIEW dependency errors
CREATE TABLE `reservas_view` (
	`cod` INT(11) NOT NULL,
	`data_entrada` DATE NULL,
	`data_saida` DATE NULL,
	`nome` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`cod_quarto` INT(11) NULL,
	`voucher` VARCHAR(50) NULL COLLATE 'latin1_swedish_ci',
	`pagamento` VARCHAR(50) NULL COLLATE 'latin1_swedish_ci',
	`moeda` VARCHAR(50) NULL COLLATE 'latin1_swedish_ci',
	`codfacturacao` VARCHAR(50) NULL COLLATE 'latin1_swedish_ci'
) ENGINE=MyISAM;

-- Dumping structure for visualização agencia_boa.saidas
-- Creating temporary table to overcome VIEW dependency errors
CREATE TABLE `saidas` (
	`cod_documento` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`doc_numero` VARCHAR(267) NULL COLLATE 'latin1_swedish_ci',
	`cod_produto` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`nome` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`quantidade` DECIMAL(19,2) NULL,
	`preco` DECIMAL(19,2) NULL,
	`total` DECIMAL(38,4) NULL,
	`entidade` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`date_created` DATE NULL,
	`nomearmazem` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`user` VARCHAR(50) NOT NULL COLLATE 'latin1_swedish_ci'
) ENGINE=MyISAM;

-- Dumping structure for table agencia_boa.stock
CREATE TABLE IF NOT EXISTS `stock` (
  `cod` varchar(255) NOT NULL,
  `fornecedor` varchar(255) DEFAULT NULL,
  `numero` varchar(255) DEFAULT NULL,
  `data` date DEFAULT NULL,
  `valor` decimal(19,2) DEFAULT '0.00',
  `pago` decimal(19,2) DEFAULT '0.00',
  `taxa` decimal(19,2) DEFAULT '0.00',
  `subtotal` decimal(19,2) DEFAULT '0.00',
  `total` decimal(19,2) DEFAULT '0.00',
  `created` date DEFAULT NULL,
  `modified` date DEFAULT NULL,
  `modified_by` varchar(255) DEFAULT NULL,
  `created_by` varchar(255) DEFAULT NULL,
  `estado` int(11) DEFAULT '0',
  `saldo` decimal(19,2) DEFAULT '0.00',
  PRIMARY KEY (`cod`),
  UNIQUE KEY `cod` (`cod`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table agencia_boa.stockdetalhe
CREATE TABLE IF NOT EXISTS `stockdetalhe` (
  `cod` int(11) NOT NULL AUTO_INCREMENT,
  `codstock` varchar(255) DEFAULT NULL,
  `codproduto` varchar(255) DEFAULT NULL,
  `codarmazem` varchar(255) DEFAULT NULL,
  `quantidade` decimal(19,2) DEFAULT '0.00',
  `valor` decimal(19,2) DEFAULT '0.00',
  `taxa` decimal(19,2) DEFAULT '0.00',
  `subtotal` decimal(19,2) DEFAULT '0.00',
  `total` decimal(19,2) DEFAULT '0.00',
  `custo` decimal(19,2) DEFAULT '0.00',
  `validade` datetime DEFAULT '2021-01-01 00:00:00',
  PRIMARY KEY (`cod`),
  KEY `codstock` (`codstock`),
  KEY `codproduto` (`codproduto`),
  KEY `codarmazem` (`codarmazem`),
  CONSTRAINT `stockdetalhe_ibfk_1` FOREIGN KEY (`codstock`) REFERENCES `stock` (`cod`),
  CONSTRAINT `stockdetalhe_ibfk_2` FOREIGN KEY (`codproduto`) REFERENCES `produtos` (`cod`),
  CONSTRAINT `stockdetalhe_ibfk_3` FOREIGN KEY (`codarmazem`) REFERENCES `armazem` (`cod`)
) ENGINE=InnoDB AUTO_INCREMENT=90 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for visualização agencia_boa.stock_actual
-- Creating temporary table to overcome VIEW dependency errors
CREATE TABLE `stock_actual` (
	`cod` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`nome` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`quantidade` DECIMAL(19,2) NULL,
	`preco` DECIMAL(19,2) NULL,
	`preco1` DECIMAL(19,2) NULL,
	`preco2` DECIMAL(19,2) NULL,
	`preco3` DECIMAL(19,2) NULL,
	`preco4` DECIMAL(19,2) NULL,
	`quantidade_m` DECIMAL(19,2) NULL,
	`quantidade_max` DECIMAL(19,2) NULL,
	`estado` INT(11) NULL,
	`tipo` INT(11) NULL,
	`armazem` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci'
) ENGINE=MyISAM;

-- Dumping structure for visualização agencia_boa.stock_geral
-- Creating temporary table to overcome VIEW dependency errors
CREATE TABLE `stock_geral` (
	`cod` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`nome` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci',
	`qt` DECIMAL(41,2) NULL,
	`preco` DECIMAL(19,2) NULL,
	`preco1` DECIMAL(19,2) NULL,
	`preco2` DECIMAL(19,2) NULL,
	`preco3` DECIMAL(19,2) NULL,
	`preco4` DECIMAL(19,2) NULL,
	`quantidade_m` DECIMAL(19,2) NULL,
	`quantidade_max` DECIMAL(19,2) NULL,
	`estado` INT(11) NULL,
	`tipo` INT(11) NULL,
	`nomearmazem` VARCHAR(255) NOT NULL COLLATE 'latin1_swedish_ci'
) ENGINE=MyISAM;

-- Dumping structure for table agencia_boa.subfamilia
CREATE TABLE IF NOT EXISTS `subfamilia` (
  `cod` varchar(255) NOT NULL,
  `nome` varchar(255) NOT NULL,
  `codfamilia` varchar(255) NOT NULL,
  `obs` varchar(255) DEFAULT NULL,
  `estado` int(11) DEFAULT '1',
  `created` date DEFAULT NULL,
  `modified` date DEFAULT NULL,
  `created_by` varchar(255) DEFAULT NULL,
  `modified_by` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`cod`),
  UNIQUE KEY `cod` (`cod`),
  KEY `codfamilia` (`codfamilia`),
  CONSTRAINT `subfamilia_ibfk_1` FOREIGN KEY (`codfamilia`) REFERENCES `familia` (`cod`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table agencia_boa.taxas
CREATE TABLE IF NOT EXISTS `taxas` (
  `cod` varchar(255) NOT NULL,
  `nome` varchar(40) NOT NULL,
  `valor` int(11) DEFAULT NULL,
  `obs` varchar(255) DEFAULT NULL,
  `created` date DEFAULT NULL,
  `modified` date DEFAULT NULL,
  `modified_by` varchar(255) DEFAULT NULL,
  `created_by` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`cod`),
  UNIQUE KEY `cod` (`cod`),
  UNIQUE KEY `nome` (`nome`),
  UNIQUE KEY `valor` (`valor`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table agencia_boa.transacoes
CREATE TABLE IF NOT EXISTS `transacoes` (
  `cod` int(11) NOT NULL AUTO_INCREMENT,
  `tipo_trasacao` varchar(20) DEFAULT NULL,
  `conta` int(11) DEFAULT NULL,
  `data` date DEFAULT NULL,
  `valor` decimal(10,0) DEFAULT NULL,
  `usuario` varchar(20) DEFAULT NULL,
  `estado` int(11) DEFAULT NULL,
  `obs` text,
  `created` date DEFAULT NULL,
  `modified` date DEFAULT NULL,
  `modified_by` varchar(20) DEFAULT NULL,
  `created_by` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`cod`),
  KEY `conta` (`conta`),
  CONSTRAINT `transacoes_ibfk_1` FOREIGN KEY (`conta`) REFERENCES `contas` (`cod`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table agencia_boa.users
CREATE TABLE IF NOT EXISTS `users` (
  `cod` varchar(50) NOT NULL,
  `senha` varchar(255) DEFAULT NULL,
  `senha2` varchar(255) DEFAULT NULL,
  `nome` varchar(255) DEFAULT NULL,
  `endereco` varchar(255) DEFAULT NULL,
  `sexo` varchar(10) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `nascimento` date DEFAULT '1980-01-01',
  `contacto` varchar(255) DEFAULT NULL,
  `tipo` varchar(255) DEFAULT NULL,
  `numero` varchar(20) DEFAULT NULL,
  `nacionalidade` varchar(255) DEFAULT 'Moçambique',
  `obs` varchar(255) DEFAULT NULL,
  `created` date DEFAULT NULL,
  `modified` date DEFAULT NULL,
  `modified_by` varchar(255) DEFAULT NULL,
  `created_by` varchar(255) DEFAULT NULL,
  `estado` tinyint(1) DEFAULT NULL,
  `admin` int(11) DEFAULT '1',
  `gestor` int(11) DEFAULT '0',
  PRIMARY KEY (`cod`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for visualização agencia_boa.caixa_geral
-- Removing temporary table and create final VIEW structure
DROP TABLE IF EXISTS `caixa_geral`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `caixa_geral` AS select `facturacao`.`cod` AS `cod_facturacao`,`facturacao`.`numero` AS `numero`,`facturacao`.`ano` AS `ano`,`facturacao`.`mes` AS `mes`,`facturacaodetalhe`.`custo` AS `custo_produto`,`facturacaodetalhe`.`desconto` AS `desconto_produto`,`facturacaodetalhe`.`subtotal` AS `subtotal_produtos`,`facturacaodetalhe`.`preco` AS `preco_produtos`,`facturacaodetalhe`.`lucro` AS `lucro_produtos`,`facturacaodetalhe`.`quantidade` AS `quantidade_produtos`,`facturacaodetalhe`.`taxa` AS `taxa_produtos`,`facturacaodetalhe`.`total` AS `total_produtos`,`caixa`.`cod` AS `cod`,`caixa`.`valor_inicial` AS `valor_inicial`,`caixa`.`despesas` AS `despesas`,`caixa`.`receitas` AS `receitas`,`caixa`.`created` AS `data_abertura`,`caixa`.`created_by` AS `aberta_por`,`caixa`.`modified` AS `data_feixo`,`caixa`.`modified_by` AS `fechada_por`,`produtos`.`nome` AS `produtos_nome`,`clientes`.`nome` AS `produtos_cliente`,`documentos`.`nome` AS `nome_documento`,`caixa`.`obs` AS `caixa_obs`,`facturacao`.`comissao` AS `comissao`,`facturacao`.`pagamento` AS `pagamento`,`facturacao`.`modified_by` AS `user` from (((((`facturacaodetalhe` left join `facturacao` on((`facturacao`.`cod` = `facturacaodetalhe`.`codfacturacao`))) left join `documentos` on((`documentos`.`cod` = `facturacao`.`coddocumento`))) left join `clientes` on((`clientes`.`cod` = `facturacao`.`codcliente`))) join `produtos` on((`produtos`.`cod` = `facturacaodetalhe`.`codproduto`))) join `caixa` on((`caixa`.`cod` = `facturacao`.`caixa`)));

-- Dumping structure for visualização agencia_boa.check_in_view
-- Removing temporary table and create final VIEW structure
DROP TABLE IF EXISTS `check_in_view`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `check_in_view` AS select `check_in`.`cod` AS `cod`,`check_in`.`data_entrada` AS `data_entrada`,`check_in`.`data_saida` AS `data_saida`,`hospedes`.`nome` AS `nome`,`check_in`.`cod_quarto` AS `cod_quarto`,`check_in`.`voucher` AS `voucher`,`check_in`.`pagamento` AS `pagamento`,`check_in`.`moeda` AS `moeda`,`check_in`.`codfacturacao` AS `codfacturacao` from (`check_in` join `hospedes` on((`hospedes`.`cod` = `check_in`.`cod_cliente`)));

-- Dumping structure for visualização agencia_boa.entradas
-- Removing temporary table and create final VIEW structure
DROP TABLE IF EXISTS `entradas`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `entradas` AS select `s`.`cod` AS `cod_documento`,`s`.`numero` AS `doc_numero`,`p`.`cod` AS `cod_produto`,`p`.`nome` AS `nome`,`sd`.`quantidade` AS `qty`,`sd`.`custo` AS `preco`,(`sd`.`quantidade` * `sd`.`custo`) AS `total`,`f`.`nome` AS `entidade`,`s`.`created` AS `date_created`,`ar`.`nome` AS `nomearmazem`,`u`.`cod` AS `user` from (((((`stock` `s` join `stockdetalhe` `sd` on((`sd`.`codstock` = `s`.`cod`))) join `produtos` `p` on((`sd`.`codproduto` = `p`.`cod`))) join `fornecedores` `f` on((`s`.`fornecedor` = `f`.`cod`))) join `armazem` `ar` on((`sd`.`codarmazem` = `ar`.`cod`))) join `users` `u` on((`s`.`modified_by` = `u`.`cod`))) where (`s`.`estado` = 1);

-- Dumping structure for visualização agencia_boa.facturas_nao_pagas
-- Removing temporary table and create final VIEW structure
DROP TABLE IF EXISTS `facturas_nao_pagas`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `facturas_nao_pagas` AS select `facturacao`.`cod` AS `cod`,`facturacao`.`numero` AS `numero`,`facturacao`.`data` AS `data`,`clientes`.`nome` AS `cliente`,`facturacao`.`total` AS `total`,`facturacao`.`saldo` AS `saldo`,`facturacao`.`debito` AS `debito`,`facturacao`.`credito` AS `credito`,`facturacao`.`obs` AS `obs` from (`facturacao` join `clientes` on((`facturacao`.`codcliente` = `clientes`.`cod`))) where ((`facturacao`.`coddocumento` = 'DC20182222222') and (`facturacao`.`estado` = 1) and (`facturacao`.`saldo` > 0));

-- Dumping structure for visualização agencia_boa.factura_geral
-- Removing temporary table and create final VIEW structure
DROP TABLE IF EXISTS `factura_geral`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `factura_geral` AS select `facturacao`.`cod` AS `codfacturacao`,`facturacao`.`numero` AS `numerofactura`,`documentos`.`nome` AS `nomedocumento`,`facturacao`.`created` AS `data`,`facturacao`.`created_by` AS `user`,`facturacao`.`subtotal` AS `subtotal_geral`,`facturacao`.`desconto` AS `desconto_geral`,`facturacao`.`taxa` AS `taxa_geral`,`facturacao`.`total` AS `total_geral`,`facturacao`.`extenso` AS `extenso`,`clientes`.`nome` AS `cliente`,`clientes`.`endereco` AS `endereco`,`clientes`.`NUIT` AS `NUIT`,`clientes`.`email` AS `email`,`facturacaodetalhe`.`codproduto` AS `codproduto`,`produtos`.`nome` AS `produto`,`facturacaodetalhe`.`quantidade` AS `quantidade`,`facturacaodetalhe`.`preco` AS `preco`,`facturacaodetalhe`.`desconto` AS `desconto`,`facturacaodetalhe`.`taxa` AS `taxa`,`facturacaodetalhe`.`subtotal` AS `subtotal`,`facturacaodetalhe`.`total` AS `total`,`facturacao`.`ano` AS `ano`,`facturacao`.`mes` AS `mes`,`facturacao`.`pago` AS `pago`,`facturacao`.`troco` AS `troco`,`documentos`.`cod` AS `coddocumento`,`clientes`.`contactos` AS `contactos`,`facturacao`.`validade` AS `validade`,`facturacao`.`obs` AS `obs`,`armazem`.`nome` AS `nome` from (((((`facturacao` join `facturacaodetalhe` on((`facturacao`.`cod` = `facturacaodetalhe`.`codfacturacao`))) join `clientes` on((`clientes`.`cod` = `facturacao`.`codcliente`))) join `produtos` on((`produtos`.`cod` = `facturacaodetalhe`.`codproduto`))) join `documentos` on((`documentos`.`cod` = `facturacao`.`coddocumento`))) join `armazem` on((`armazem`.`cod` = `facturacaodetalhe`.`codarmazem`)));

-- Dumping structure for visualização agencia_boa.fecho_caixa
-- Removing temporary table and create final VIEW structure
DROP TABLE IF EXISTS `fecho_caixa`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `fecho_caixa` AS select `caixa`.`valor_inicial` AS `valor_inicial`,`caixa`.`receitas` AS `receitas`,`caixa`.`despesas` AS `despesas`,`caixa`.`created_by` AS `CRIADA_POR`,`caixa`.`modified_by` AS `FECHADA_POR`,`caixa`.`created` AS `ABERTURA`,`caixa`.`modified` AS `FECHO`,`documentos`.`nome` AS `DOCUMENTO`,`facturacao`.`numero` AS `numero`,`clientes`.`nome` AS `CLIENTE`,`facturacao`.`subtotal` AS `subtotal`,`facturacao`.`desconto` AS `desconto`,`facturacao`.`taxa` AS `taxa`,`facturacao`.`total` AS `total`,`facturacao`.`banco` AS `CHEQUE`,`facturacao`.`cash` AS `NUMERARIO`,`facturacao`.`tranferencia` AS `POS`,`caixa`.`estado` AS `estado_caixa`,`facturacao`.`estado` AS `estado_factura`,`caixa`.`cod` AS `caixa_numero`,`facturacao`.`coddocumento` AS `doc`,`facturacao`.`comissao` AS `comissao`,`facturacao`.`pagamento` AS `pagamento`,`facturacao`.`lucro` AS `lucro`,`facturacao`.`modified` AS `modified`,`facturacao`.`modified_by` AS `user` from (((`facturacao` join `caixa` on((`caixa`.`cod` = `facturacao`.`caixa`))) join `documentos` on((`documentos`.`cod` = `facturacao`.`coddocumento`))) join `clientes` on((`clientes`.`cod` = `facturacao`.`codcliente`))) where (`facturacao`.`finalizado` = 1);

-- Dumping structure for visualização agencia_boa.fecho_caixa_detalhada
-- Removing temporary table and create final VIEW structure
DROP TABLE IF EXISTS `fecho_caixa_detalhada`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `fecho_caixa_detalhada` AS select `caixa`.`valor_inicial` AS `valor_inicial`,`caixa`.`receitas` AS `receitas`,`caixa`.`despesas` AS `despesas`,`caixa`.`created_by` AS `CRIADA_POR`,`caixa`.`modified_by` AS `FECHADA_POR`,`caixa`.`created` AS `ABERTURA`,`caixa`.`modified` AS `FECHO`,`documentos`.`nome` AS `DOCUMENTO`,`facturacao`.`numero` AS `numero`,`clientes`.`nome` AS `CLIENTE`,`facturacao`.`subtotal` AS `subtotal`,`facturacao`.`desconto` AS `desconto`,`facturacao`.`taxa` AS `taxa`,`facturacao`.`total` AS `total`,`facturacao`.`banco` AS `CHEQUE`,`facturacao`.`cash` AS `NUMERARIO`,`facturacao`.`tranferencia` AS `POS`,`caixa`.`estado` AS `estado_caixa`,`facturacao`.`estado` AS `estado_factura`,`caixa`.`cod` AS `caixa_numero`,`facturacao`.`coddocumento` AS `doc`,`facturacao`.`comissao` AS `comissao`,`facturacao`.`pagamento` AS `pagamento`,`facturacao`.`lucro` AS `lucro`,`produtos`.`nome` AS `nome`,`facturacaodetalhe`.`quantidade` AS `quantidade`,`facturacaodetalhe`.`total` AS `total_geral`,`facturacaodetalhe`.`preco` AS `preco_unitario`,`facturacaodetalhe`.`taxa` AS `iva_produto`,`facturacaodetalhe`.`desconto` AS `desconto_unitario`,`facturacaodetalhe`.`subtotal` AS `subtotal_produto`,`facturacao`.`modified_by` AS `user`,`produtos`.`cod` AS `prod_cod`,`facturacaodetalhe`.`custo` AS `custo` from (((((`facturacao` join `caixa` on((`caixa`.`cod` = `facturacao`.`caixa`))) join `documentos` on((`documentos`.`cod` = `facturacao`.`coddocumento`))) join `clientes` on((`clientes`.`cod` = `facturacao`.`codcliente`))) join `facturacaodetalhe` on((`facturacao`.`cod` = `facturacaodetalhe`.`codfacturacao`))) join `produtos` on((`produtos`.`cod` = `facturacaodetalhe`.`codproduto`))) where (`facturacao`.`finalizado` = 1);

-- Dumping structure for visualização agencia_boa.movimento_stock
-- Removing temporary table and create final VIEW structure
DROP TABLE IF EXISTS `movimento_stock`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `movimento_stock` AS select `entradas`.`cod_documento` AS `cod_documento`,`entradas`.`doc_numero` AS `doc_numero`,`entradas`.`cod_produto` AS `cod_produto`,`entradas`.`nome` AS `nome`,`entradas`.`qty` AS `qty`,`entradas`.`preco` AS `preco`,`entradas`.`total` AS `total`,`entradas`.`entidade` AS `entidade`,`entradas`.`date_created` AS `date_created`,`entradas`.`nomearmazem` AS `nomearmazem`,`entradas`.`user` AS `user` from `entradas` union select `saidas`.`cod_documento` AS `cod_documento`,`saidas`.`doc_numero` AS `doc_numero`,`saidas`.`cod_produto` AS `cod_produto`,`saidas`.`nome` AS `nome`,`saidas`.`quantidade` AS `quantidade`,`saidas`.`preco` AS `preco`,`saidas`.`total` AS `total`,`saidas`.`entidade` AS `entidade`,`saidas`.`date_created` AS `date_created`,`saidas`.`nomearmazem` AS `nomearmazem`,`saidas`.`user` AS `user` from `saidas`;

-- Dumping structure for visualização agencia_boa.recibo_geral
-- Removing temporary table and create final VIEW structure
DROP TABLE IF EXISTS `recibo_geral`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `recibo_geral` AS select `recibos`.`cod` AS `cod`,`recibos`.`total` AS `total`,`recibos`.`created` AS `created`,`recibos`.`codcliente` AS `codcliente`,`recibos`.`extenso` AS `extenso`,`recibosdetalhe`.`descricao` AS `descricao`,`recibosdetalhe`.`factura` AS `factura`,`recibosdetalhe`.`pago` AS `pago`,`clientes`.`nome` AS `nome`,`clientes`.`endereco` AS `endereco`,`clientes`.`NUIT` AS `NUIT`,`clientes`.`email` AS `email`,`recibos`.`finalizado` AS `finalizado`,`recibos`.`estado` AS `estado`,`recibos`.`numero` AS `numero`,`recibos`.`mes` AS `mes`,`recibos`.`ano` AS `ano`,`recibos`.`data` AS `data`,`recibos`.`created_by` AS `user`,`clientes`.`contactos` AS `contactos`,`recibos`.`obs` AS `obs` from ((`recibos` join `clientes` on((`clientes`.`cod` = `recibos`.`codcliente`))) join `recibosdetalhe` on((`recibos`.`cod` = `recibosdetalhe`.`codrecibo`)));

-- Dumping structure for visualização agencia_boa.reservas_view
-- Removing temporary table and create final VIEW structure
DROP TABLE IF EXISTS `reservas_view`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `reservas_view` AS select `reservas`.`cod` AS `cod`,`reservas`.`data_entrada` AS `data_entrada`,`reservas`.`data_saida` AS `data_saida`,`hospedes`.`nome` AS `nome`,`reservas`.`cod_quarto` AS `cod_quarto`,`reservas`.`voucher` AS `voucher`,`reservas`.`pagamento` AS `pagamento`,`reservas`.`moeda` AS `moeda`,`reservas`.`codfacturacao` AS `codfacturacao` from (`reservas` join `hospedes` on((`hospedes`.`cod` = `reservas`.`cod_cliente`)));

-- Dumping structure for visualização agencia_boa.saidas
-- Removing temporary table and create final VIEW structure
DROP TABLE IF EXISTS `saidas`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `saidas` AS select `f`.`cod` AS `cod_documento`,concat(`d`.`nome`,' ',`f`.`numero`) AS `doc_numero`,`p`.`cod` AS `cod_produto`,`p`.`nome` AS `nome`,`fd`.`quantidade` AS `quantidade`,`fd`.`preco` AS `preco`,(`fd`.`quantidade` * `fd`.`preco`) AS `total`,`c`.`nome` AS `entidade`,`f`.`created` AS `date_created`,`ar`.`nome` AS `nomearmazem`,`u`.`cod` AS `user` from ((((((`facturacao` `f` join `facturacaodetalhe` `fd` on((`fd`.`codfacturacao` = `f`.`cod`))) join `produtos` `p` on((`fd`.`codproduto` = `p`.`cod`))) join `documentos` `d` on((`f`.`coddocumento` = `d`.`cod`))) join `clientes` `c` on((`f`.`codcliente` = `c`.`cod`))) join `armazem` `ar` on((`fd`.`codarmazem` = `ar`.`cod`))) join `users` `u` on((`f`.`modified_by` = `u`.`cod`))) where ((`f`.`finalizado` = 1) and (`f`.`estado` = 1) and (`d`.`estado` = 1) and (`d`.`stock` = 1));

-- Dumping structure for visualização agencia_boa.stock_actual
-- Removing temporary table and create final VIEW structure
DROP TABLE IF EXISTS `stock_actual`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `stock_actual` AS select `produtos`.`cod` AS `cod`,`produtos`.`nome` AS `nome`,`stockdetalhe`.`quantidade` AS `quantidade`,`produtos`.`preco` AS `preco`,`produtos`.`preco1` AS `preco1`,`produtos`.`preco2` AS `preco2`,`produtos`.`preco3` AS `preco3`,`produtos`.`preco4` AS `preco4`,`produtos`.`quantidade_m` AS `quantidade_m`,`produtos`.`quantidade` AS `quantidade_max`,`produtos`.`estado` AS `estado`,`produtos`.`tipo` AS `tipo`,`armazem`.`nome` AS `armazem` from ((`produtos` join `stockdetalhe`) join `armazem`) where ((`produtos`.`cod` = `stockdetalhe`.`codproduto`) and (`armazem`.`cod` = `stockdetalhe`.`codarmazem`));

-- Dumping structure for visualização agencia_boa.stock_geral
-- Removing temporary table and create final VIEW structure
DROP TABLE IF EXISTS `stock_geral`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `stock_geral` AS select `produtos`.`cod` AS `cod`,`produtos`.`nome` AS `nome`,sum(`stockdetalhe`.`quantidade`) AS `qt`,`produtos`.`preco` AS `preco`,`produtos`.`preco1` AS `preco1`,`produtos`.`preco2` AS `preco2`,`produtos`.`preco3` AS `preco3`,`produtos`.`preco4` AS `preco4`,`produtos`.`quantidade_m` AS `quantidade_m`,`produtos`.`quantidade` AS `quantidade_max`,`produtos`.`estado` AS `estado`,`produtos`.`tipo` AS `tipo`,`armazem`.`nome` AS `nomearmazem` from ((`produtos` join `stockdetalhe` on((`produtos`.`cod` = `stockdetalhe`.`codproduto`))) join `armazem` on((`armazem`.`cod` = `stockdetalhe`.`codarmazem`))) where (`produtos`.`estado` = 1) group by `armazem`.`cod`,`produtos`.`cod`;

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
