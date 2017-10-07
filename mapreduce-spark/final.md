# Trabalho Final - MapReduce e Spark

## Etapas

### 1) Faça um processo de mapReduce que liste todas as palavras dos textos em um dado diretório, no sentido da ordem alfabética. Envie o projeto zipado (ou o link do github) e o jar do projeto.



### 2) Faça o mesmo utilizando Spark

```scala
val rddLinhas = sc.textFile("/user/cloudera/fernando/input")
val rddPalavras = rddLinhas.flatMap(linha => linha.split(" "))
val rddPalavrasTrim = rddPalavras.map(linha => linha.trim())
rddPalavrasTrim.distinct.toDF("palavras").sort(desc("palavras")).show
```

### 3) Faça o mesmo utilizando Spark e SparkSql

```scala
val rddLinhas = sc.textFile("/user/cloudera/fernando/input")
rddLinhas.toDF.registerTempTable("linhas")

sqlContext.sql("SELECT DISTINCT explode(split(linha, ' ')) as palavras FROM linhas ORDER BY palavras DESC").show
```
