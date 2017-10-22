# Notes on data cleaning process
I am adding notes on data cleaning.  
where I got stuck, how did I handle the problem, what I could not do etc. etc. etc.  

# Overview:
So the data cleaning process was done in pandas dataframe and numpy on the original prediction model.  
I want to test if Spark would help reduce computation time for data cleaning process.  
  
### Test setting:
1. using Video Games category product review from the Amazon product review datasets.
2. Running Spark on my laptop with 4 CPU nodes.
3. the pyspark ver. model is slightly different from the original model.  
  - The original model impute null values for the price and the rank_values features with Average values.
  - The pyspark model impute rank_values with ((max of rank_values) + 1). Which means any product with null values for rank_value is ranked at the bottom.  
  - The pyspark model impute price values by turning price features into categorical features.  
    - unknown value is used for the null values.  
  
### parameter settings:
1. categories with more than 50 products  
  - 'Toys & Games', 'Video Games', 'Electronics', 'Software'  
2. reviews with more than 100 total votes  
  
dataframe size: 4739 data samples, 111 features for pyspark ver. model.
  
  
