# Pós-graduação UP - Big Data - Primeiro Semestre 2017

Aluno: Fernando Dias Belo

Disciplina: HBase

## Comandos e exemplos da aula de HBase

### Iniciando o shell

hbase shell

### Criando a tabela

create 'emp','br'

### Populando com dados de exemplo

put 'emp','1','br:nome','Joao'
put 'emp','1','br:idade','31'
put 'emp','1','br:funcao','Tecnico'
put 'emp','1','br:cidade','Curitiba'
put 'emp','1','br:bairro','bairro1'

put 'emp','2','br:nome','Maria'
put 'emp','2','br:idade','42'
put 'emp','2','br:funcao','Analista'
put 'emp','2','br:cidade','Matinhos'
put 'emp','2','br:bairro','bairro2'

put 'emp','3','br:nome','Bruno'
put 'emp','3','br:idade','53'
put 'emp','3','br:funcao','Contador'
put 'emp','3','br:cidade','Antonina'
put 'emp','3','br:bairro','bairro3'

put 'emp','4','br:nome','Rodolfo'
put 'emp','4','br:idade','24'
put 'emp','4','br:funcao','Adm'
put 'emp','4','br:cidade','Paranagua'
put 'emp','4','br:bairro','bairro4'

put 'emp','5','br:nome','Manoel'
put 'emp','5','br:idade','35'
put 'emp','5','br:funcao','Medico'
put 'emp','5','br:cidade','Pinhais'
put 'emp','5','br:bairro','bairro5'

put 'emp','6','br:nome','Leticia'
put 'emp','6','br:idade','46'
put 'emp','6','br:funcao','Dentista'
put 'emp','6','br:cidade','Colombo'
put 'emp','6','br:bairro','bairro6'

### Apagando um registro

deleteall 'emp','6'

### Alterando a coluna cidade de todos os registros

put 'emp','1','br:cidade','Cidade1'
put 'emp','2','br:cidade','Cidade2'
put 'emp','3','br:cidade','Cidade3'
put 'emp','4','br:cidade','Cidade4'
put 'emp','5','br:cidade','Cidade5'

### Mostrando uma célula específica

get 'emp','1',{COLUMN=>'br:nome'}

### Apagando uma versão de célula através do timestamp 

delete 'emp','2','br:cidade',1518873331300

### Contando linhas

count ‘emp’

### Limpando tabela

truncate ‘emp’

### Desabilitando para atualização

disable ‘emp’

### Apagando a tabela

drop ‘emp’

### Listando todas as tabelas

list

### Shorturl: Criando tabela 

create 'acesso','user','shorturl','url','click'

### Adicionado dados de teste

put 'acesso','1','user:username','Fernando'
put 'acesso','1','shorturl:shorturl','valorShortUrl'
put 'acesso','1','url:url','valorUrl'
put 'acesso','1','click:category','valorCategory'

### Rodando script a partir de arquivo

hbase shell arquivo.txt

### Rodando scripts dentro do HBase

create 'testtable', 'colfam1'

for i in 'a'..'z' do for j in 'a'..'z' do \
put 'testtable', "row-#{i}#{j}", "colfam1:#{j}", "#{j}" end end


create 'shortUrl', 'cf'

for i in 1..1000 do for j in 1..1000 do \
put 'shortUrl', "row-#{i}#{j}", "cf:url", "shortUrl" end end

create 'frota', 'cf'

alter 'frota',{NAME=>'cf',VERSIONS=>10}

for i in 'a'..'j' do for j in 1..10 do \
put 'frota', "row-#{i}#{i}#{i}#{i}", "cf:posX", "#{j}"
put 'frota', "row-#{i}#{i}#{i}#{i}", "cf:posY", "#{j*-1}"
end end

get 'frota','row-aaaa',{COLUMN=>'cf:posX',VERSIONS=>10}

### Criando tabela 

create ‘teste’,’cf’,’cf2’

### Adicionando mais uma família de coluna na tabela

alter ‘teste’,’cf3’

### Deletando uma família de coluna

alter ‘teste’,’delete’,’cf’

### Alterando o número de versões para uma família de coluna

alter 'teste',{NAME => 'cf2', VERSIONS =>5},{NAME => 'cf3', VERSION =>5}

### Verificar se a tabela ainda existe

exists ‘teste’

## Exercício Nota Fiscal Eletrônica

### Modelagem da tabela

Row Id => ESTABELECIMENTO_NOTA (XX_XXX)
FC => TIPO (NFE/NFS ou CTE)
Colunas => Data, Valor, Cpf

### Criando tabela

create 'nfe', 'pr'
alter 'nfe', 'nfe', 'nfs', 'cte'

### Dados de exemplo para validar modelo

put 'nfe', '01_001', 'nfs:data','02/03/2018'
put 'nfe', '01_001', 'nfs:valor','55.55'
put 'nfe', '01_001', 'nfs:cpf','036.853.849-45'


#### Scripts para popular automaticamente com exemplos

for estabelecimento in '1'..'99' do for nota in '1'..'999' do \
put 'nfe', "#{estabelecimento.to_s.rjust(2, '0')}_#{nota.to_s.rjust(3, '0')}", "nfe:data","#{Time.now.getutc.iso8601}"
put 'nfe', "#{estabelecimento.to_s.rjust(2, '0')}_#{nota.to_s.rjust(3, '0')}", "nfe:valor","#{rand(1000)}.#{rand(99)}"
put 'nfe', "#{estabelecimento.to_s.rjust(2, '0')}_#{nota.to_s.rjust(3, '0')}", "nfe:cpf","#{rand(999)}.#{rand(999)}.#{rand(999)}-#{rand(99)}"
end end


### Buscar por estabelecimento:

scan 'nfe', {STARTROW => '10', ENDROW => '11' } ou
scan 'nfe', { FILTER => "PrefixFilter('11')" }


### Buscar por nota
scan 'nfe', { FILTER => "RowFilter(=,'substring:_112')" } ou
scan 'nfe', { FILTER => "RowFilter(=,'regexstring:.._113')", COLUMNS => 'nfe:cpf'}



