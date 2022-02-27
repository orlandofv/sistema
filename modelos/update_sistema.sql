-- ALTER TABLE cozinha ADD COLUMN codfacturacao VARCHAR(255);
-- ALTER TABLE cozinha ADD CONSTRAINT `codfacturacao` FOREIGN KEY (codfacturacao) REFERENCES facturacao(cod);
-- ALTER TABLE facturacaodetalhe ADD COLUMN created DATETIME DEFAULT NOW();
-- ALTER TABLE facturacaodetalhe ADD COLUMN ordem int DEFAULT 0;


SELECT * from facturacaodetalhe WHERE codfacturacao="FT2020112C2LA"
