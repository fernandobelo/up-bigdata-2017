## CRIANDO UMA KEYSPACE 

	CREATE KEYSPACE fbelo WITH replication = { 'class' : 'SimpleStrategy', 'replication_factor' : 1	};

## SELECIONANDO UMA KEYSPACE 

	USE fbelo;

## CRIANDO A TABELA aluno e clusterize por Materia 
### id
### nome  
### materia  
### nota  
### falta  

	CREATE TABLE fbelo.aluno ( id uuid, nome text, materia text, nota double, falta int, PRIMARY KEY (id, materia));

## INSIRA 5 registros  NA TABELA aluno 

	INSERT INTO fbelo.aluno (id, nome, materia, nota, falta) VALUES (uuid(), 'John Doe', 'Cassandra', 9, 0);
	INSERT INTO fbelo.aluno (id, nome, materia, nota, falta) VALUES (uuid(), 'John Doe', 'Spark', 8.5, 1);
	INSERT INTO fbelo.aluno (id, nome, materia, nota, falta) VALUES (uuid(), 'John McAfee', 'Cassandra', 10, 0);
	INSERT INTO fbelo.aluno (id, nome, materia, nota, falta) VALUES (uuid(), 'John McAfee', 'Spark', 6, 4);
	INSERT INTO fbelo.aluno (id, nome, materia, nota, falta) VALUES (uuid(), 'Bill Gates', 'MapReduce', 7, 1);
	
## EXTRAIA OS DADOS DA TABELA aluno DO CASSANDRA em RDDs No SPARK  

  val qryPart1 = sc.cassandraTable("fbelo", "aluno");

## UTILIZANDO OS MÉTODOS MAP E REDUCE PARA SOMAR AS FALTAS 
  
  val faltasTotal = qryPart1.map(x => x.getInt("falta")).reduce{case(x,y) => x + y};

## EXIBINDO O TOTAL DE FALTAS 

  println(faltasTotal);

## CONTANDO O TOTAL DE NOTAS

  val totalNotas = qryPart1.select("nota").count;

## UTILIZANDO OS MÉTODOS MAP E REDUCE PARA CALCULAR A MÉDIA 

  val mediaNotas = qryPart1.map(x => x.getDouble("nota")).reduce{case(x,y) => x + y} / totalNotas;

## EXIBINDO A MÉDIA DAS NOTAS

  println(mediaNotas);
