import pyspark as ps
from pyspark import SparkConf, SparkContext
from __future__ import unicode_literals
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
import json
import gzip
import spacy
%matplotlib inline
np.random.seed(32113)
import pickle

from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
from nltk.corpus import stopwords
from spacy.en import English
import string
import data_prep_new as dp 
parser = English()
from pyspark.sql.types import *
from pyspark.sql.functions import monotonically_increasing_id
from pyspark.sql.functions import col,isnan,count,when
import pyspark.sql.functions as pys_fun
 
import math

hc = ps.HiveContext(sc)
sql = ps.SQLContext(sc)


path = './reviews_Video_Games.json.gz'
meta_path = './meta_Video_Games.json.gz'
start_time = time.time()
meta = dp.getDF(meta_path)

def review_data_clean(path, min_vote = 100):
    '''
    description:
    - prepares review data
    - drop unused features
    - add additional feature "helpful_total_votes","num_of_helpful_votes","helpful_percentage" and "Text_length"
    - returns review_data that is ready to be merged with meta data.
    
    NOTES:
    Should run this with good amount of memory. storing the dataframe may cause memory issue if ran with small cpus.
    '''
    
    #de-json file
    dataframe = dp.getDF(path)
    #dropping unused features
    d2 = dataframe.drop(['unixReviewTime','reviewTime','reviewerName','reviewerID','summary'],axis = 1)
    #set a schema and create hive dataframe.
    schema = StructType([
            StructField('asin', StringType(), True),
            StructField('helpful', ArrayType(IntegerType()), True),
            StructField('reviewText', StringType(), True),
            StructField('overall', FloatType(), True)])
    df = hc.createDataFrame(d2,schema)
    # create 2 new features for number of total votes and number of positive votes
    df = df.withColumn("helpful_total_votes", df["helpful"].getItem(1)).withColumn("num_of_helpful_votes", df["helpful"].getItem(0))
    df = df.drop(df["helpful"])
    # run SQL query to reduce size of dataframe by number of total votes > min_votes. 
    # create new features for helpful percentage and text length.
    df.registerTempTable('review')
    result = hc.sql('SELECT R.*,ROUND(R.num_of_helpful_votes/R.helpful_total_votes,2) as helpful_percentage,LENGTH(R.reviewText) as Text_length FROM review as R WHERE R.helpful_total_votes >"{}"'.format(min_vote))
    return result
 
    
def meta_data_clean(meta_path, cate = "Video Games"):
    '''
    description:
    - prepares meta data
    - drop unused features
    - add new features 
        - number of category
        - category names (this could increase features 80-100)
        - rank_keys
        - rank_values
    - returns meta_data that is ready to be merged with review data.
    - returns parameter called max_of_rank_val. the parameter stores rank values used to fill in null values for rank_values feature.
    
    NOTES:
    Should run this with good amount of memory. storing the dataframe may cause memory issue if ran with small cpus.
    '''
    #dejson file
    meta = dp.getDF(path)
    #drops unused features
    meta = meta.drop(['imUrl','related','title','brand','description'],axis = 1)
    #access to a dictionary and add rank_keys and rank_values
    meta, max_of_rank_val = dp._add_rankings(meta, cate)
    #now that I extracted information form salesRank feature, I'm taking out this dictionary feature. yuck!! 
    meta = meta.drop(['salesRank'],axis = 1)
    #set schema
    schema = StructType([
        StructField('asin', StringType(), True),
        StructField('price',FloatType(),True),
        StructField('categories', ArrayType(ArrayType(StringType())), True),
        StructField('rank_keys', StringType(), True),
        StructField('rank_values', IntegerType(), True)])
    # making a hive dataframe for the meta data
    df_meta = hc.createDataFrame(meta,schema)
    # create id feature for this dataframe
    df_meta = df_meta.withColumn("id", monotonically_increasing_id())
    
    # making a another dataframe which contain length of categories feature.
    number_of_category = df_meta.select('categories').rdd.flatMap(lambda x: x).map(lambda x: len(x)).collect()
    nc= hc.createDataFrame(number_of_category,IntegerType())
    nc = nc.withColumn("id", monotonically_increasing_id())
    
    # adding length of categories as a new feature in my meta dataframe through sql query.
    df_meta.registerTempTable('meta')
    nc.registerTempTable('nc')
    df_meta = hc.sql('SELECT m.*, nc.value AS num_category FROM meta AS m JOIN nc ON m.id == nc.id ORDER BY id')

    
    #adding category names as a feature (python. not spark)
    category_word = df_meta.select('categories').rdd.flatMap(lambda x: x)\
                    .flatMap(lambda x: x).flatMap(lambda x3: [word for word in x3 if x3[0] == cate]).collect()
    word_list = list(set(category_word))
    np_cat_case = np.zeros((len(meta3),len(word_list)))
    df_category= pd.DataFrame(np_cat_case)
    df_category.columns = word_list
    df_category = dp._category_fill(meta3['categories'],df_category, cate)

    cat_df= hc.createDataFrame(df_category)
    cat_df = cat_df.withColumn("id", monotonically_increasing_id())

    df_meta.registerTempTable('meta')
    cat_df.registerTempTable('cat_df')
    
    #joining two dataframe.
    df_meta = hc.sql('''
    SELECT m.asin, m.price, m.rank_keys, m.rank_values, m.num_category, cd.* 
    FROM meta AS m JOIN cat_df AS cd ON m.id == cd.id ORDER BY cd.id''')

    # The only reason why I am running my code this way is because 'categories' feature is stored as a list of list.
    # If it was not stored as this format, I would just use SQL query with window function instead of making multiple dataframes.
    
    return df_meta, max_of_rank_values



def merging_data(review,meta,max_value,cate = "video Games",num_of_cate_sample=100):

    #mergning review and meta:
    df_meta2.registerTempTable('meta')
    result.registerTempTable('review')
    
    query ='SELECT R.reviewText,R.overall, R.helpful_total_votes, R.num_of_helpful_votes, R.helpful_percentage, R.Text_length, meta_2.* FROM review as R JOIN (SELECT meta.*, COUNT(rank_keys) OVER(PARTITION BY rank_keys) AS count_cat FROM meta) meta_2 ON R.asin = meta_2.asin WHERE meta_2.count_cat >"{}"'.format(num_of_cate_sample) 
    result2 = hc.sql(query)

    # important thing you need to know here is that I'm filtering data by rank_keys.
    # I'm only interested in the data where rank_keys feature is IN imp_cate_list. 
    
    #making a new id for each review data. the current id is for meta so lets drop it!
    result2 = result2.drop("id","count_cat)
    result2 = result2.withColumn("id", monotonically_increasing_id())

    #making categorical values for rank_values. need to 
    panda_result=result2.toPandas()
    dum = pd.get_dummies(panda_result.rank_keys, drop_first=True)
    dum = dum.rename(columns={cate: 'Main_Category'}
    dum2 =pd.concat([panda_result.id,dum], axis = 1)
    dum_spark = hc.createDataFrame(dum2)
    dum_spark.registerTempTable('dummy')
    result2.registerTempTable('merged_df')

    df_merged = hc.sql('''
    SELECT m.*, dum.software, dum.Main_Category FROM merged_df AS m JOIN dummy AS dum ON m.id=dum.id''')

                     
                    #NEED TO WORK HERE
                     
#price
ifquery = pys_fun.expr(
    """IF(price == "NaN","price_unknown", IF(price <=20, "below20", 
    IF(price>20 AND price<=50, 'below50', IF(price>50 AND price<=100, 'below100', 
    IF(price>100 AND price<=300, 'below300', 'above300')))))""")
df_merged = (df_merged.withColumn("new_price", ifquery))
panda_df=df_merged.toPandas()
dum3 = pd.get_dummies(panda_df.new_price, drop_first=True)
dum4 =pd.concat([panda_df.id,dum3], axis = 1)
price_dum = hc.createDataFrame(dum4)
price_dum.registerTempTable('dummy2')
df_merged.registerTempTable('merged_df')

df_2 = hc.sql('''
SELECT m.*, dum.below20, dum.below50,dum.below100,dum.below300,dum.price_unknown FROM merged_df AS m JOIN dummy2 AS dum ON m.id=dum.id''')
df_2 = df_2.drop('price','new_price','rank_keys')
df_2_1 = df_2.where(~((df_2.price_unknown==1)&(df_2.rank_values == max_of_rank_val)))
df_2_1.write.csv('test_datacleaning.csv', mode="overwrite", header=True)
print("--- %s seconds ---" % (time.time() - start_time))