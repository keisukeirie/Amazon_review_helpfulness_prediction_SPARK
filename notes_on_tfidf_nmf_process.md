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
  
### StopWordsRemover
This function will apply stopwords to your tokenized word list.  
You can:
1. set your own custom stopwords and assign it by adjusting parameter called stopWords.  
ex: StopWordsRemover(inputCol="words", outputCol="stopword_applied" ,stopWords = stopwordlistImade)
2. apply stopwords that is prepared by spark. you can do this by not specifying stopWords.  

My assumption is that...  
1. tokenizer/lemmatizer for SpaCy is a bit smarter than the one from Spark.
2. but the tokenizer and stopwordsremover from spark is much easier than one in spaCy/TextaCy in my opinion.  


### TF-IDF
I think this part is straightforward.  
from pyspark.ml.feature import HashingTF, IDF  
and run codes just like on the [documentation](https://spark.apache.org/docs/2.1.1/ml-features.html#tf-idf):  
  
"""  
from pyspark.ml.feature import HashingTF, IDF  
  
hashingTF = HashingTF(inputCol="words", outputCol="rawFeatures", numFeatures=20)  
featurizedData = hashingTF.transform(wordsData)  
  
idf = IDF(inputCol="rawFeatures", outputCol="features")  
idfModel = idf.fit(featurizedData)  
tf-idfmodel = idfModel.transform(featurizedData)  
  
tf-idfmodel.select("label", "features").show()  
"""  
  
the tf-idf model will be stored as a list of [*sparse vectors*](https://spark.apache.org/docs/1.1.0/api/python/pyspark.mllib.linalg.SparseVector-class.html).    
  
## NMF:
So this is the part I had a problem with.  
Unlike Sklearn NMF, NMF is not meant to use with TF-IDF terms in spark.  
there is no NMF class in Spark but instead, it is contained in the collaborative filtering in recommendation module.  
Don't be alarmed. you just need to set nonnegative = True in pyspark.ml.recommendation.ALS.  
  
The biggest problem I had was that the input matrix for this ALS class called rating matrix.
a rating matrix is one form of sparse matrix where columns are User,Item and Rating.
User = data sample  
Item = columns/features, column number 
Rating = value (in our case TF-IDF term)  
  
For example, the rating matrix can look like this.  
  
|   USER ID   |   ITEM ID   |   Rating   |  
|:----------- |:-----------:| ----------:|  
|      0      |      1      |    1.03    |    
|      0      |      4      |    2.54    |  
|      0      |      9      |    9.02    |  
|      1      |      2      |    6.78    |  
|      1      |      3      |    4.99    |  
|      1      |      4      |    5.80    |   
|      2      |      7      |    0.80    |   
|      2      |      8      |   10.22    |   
|      2      |      9      |    8.77    |   
  
However, the sparse vector format of the same matrix in spark looks like this:  
[(0,(10,[1,4,9],[1.03,2.54,9.02]))  
(1,(10,[2,3,4],[6.78,4.99,5.80]))  
(2,(10,[7,8,9],[0.80,10.22,8.77]))]  
  
**SO THE QUESTION IS HOW CAN WE CONVERT A LIST OF SPARSE VECTORS TO A RATING MATRIX?**
  
From what I understand (and if you know the better solution, please tell me!), there is no easy and fast way to convert your data.  
the process I used was following:  
  
1. From your dataframe that contains your tfidf terms, run a code to create a rdd for user_id, item_id (column names), rating(tf_idf values).  
for user_id, I just called id feature and multiply it by the length of TFIDF_feature indices.  
for item_id, I'm calling indices from every sparse vector matrix.    
for rating, I'm calling values from every sparse vector matrix.  
  
rdd_id = TFIDF_model.rdd.map(lambda x: [x.id2] * len(x.TFIDF_features.indices)).flatMap(lambda x: x)    
rdd_indices = TFIDF_model.rdd.map(lambda x: x.TFIDF_features.indices).flatMap(lambda x: x)  
rdd_tfidf = TFIDF_model.rdd.map(lambda x: x.TFIDF_features.values).flatMap(lambda x: x)  
    
2. Zip your rdds that you created in the previous step.  
rd_zip1 = rdd_id.zip(rdd_indices)  
rdd_zipped = rd_zip1.zip(rdd_tfidf).map(lambda x: (int(x[0][0]),int(x[0][1]),float(x[1])))  
  
3. create a dataframe with zipped rdd and change data types for each column.  
for a rating matrix, user_id = IntegerType, Item = IntegerType, Rating = FloatType.  
  
test = hc.createDataFrame(rdd_zipped)  
test = test.select(col('_ 1').alias("USER_ID").cast(IntegerType()), col('_ 2').alias("tfidf_index").cast(IntegerType()), col('_ 3').alias("tfidf_term"))  
test = test.withColumn("tfidf_ROUND", pys_fun.format_number(test.tfidf_term, 3).cast(FloatType()))  
test = test.drop('tfidf_term')  
