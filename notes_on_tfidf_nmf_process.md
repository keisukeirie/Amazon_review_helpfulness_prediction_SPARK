#notes on tfidf nmf processes
I am putting my notes on tfidf, nmf process for pyspark.  
I hope this helps others!  

## Tokenizer, TFIDF
[Tokenizer, TFIDF and NLP related function documentation:](https://spark.apache.org/docs/1.6.0/ml-features.html#tf-idf-hashingtf-and-idf)  
the process is really simple.... if you documents/texts are ready for Tokenizer, TFIDF etc.  

### before running these functions:
Always Check your corpus. if you happen to have a null values for your text/document column,  
everything fails and you will feel miserable for half hour to few hours.  
  
1. following code will check if there is any null values in your dataframe called df  
note that you need to import col,count,isnan,when from pyspark.sql.functions  
*df.select([count(when(isnan(c) | col(c).isNull(), c)).alias(c) for c in df.columns]).show()*  

2. If you know the name of column that you want to check null values for, try this code:  
*df.filter(df.reviewText.isNull()).count()*  
(for dataframe called df with column called reviewText)  
  
### Tokenizer:
Tokenizer is really simple to use for pyspark.  
you can:  
1. run tokenizer by specifying input column name and the output to store tokenized words.  
2. choose between normal tokenizer and regextokenizer.  
the regextokenizer uses Java regular expression to make some restriction when tokenizing.  
For example, if you want to take out non-word character, set pattern = \\W+.  
There are many way to set this restriction but I am not the regex expert so please google regular expression for java.  
  
###StopWordsRemover
This function will apply stopwords to your tokenized word list.  
You can:
1. set your own custom stopwords and assign it by adjusting parameter called stopWords.  
ex: StopWordsRemover(inputCol="words", outputCol="stopword_applied" ,stopWords = stopwordlistImade)
2. apply stopwords that is prepared by spark. you can do this by not specifying stopWords.  

My assumption is that...  
1. tokenizer/lemmatizer for SpaCy is a bit smarter than the one from Spark.
2. but the tokenizer and stopwordsremover from spark is much easier than one in spaCy/TextaCy in my opinion.  
