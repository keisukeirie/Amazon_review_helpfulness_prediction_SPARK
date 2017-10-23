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
3. After adjusting null values for price feature, remove samples that contained nulls for both price AND rank_values.  
  - the process is done with NAND bitwise operator: df.where(~((df.price_unknown == 1) & (df.rank_values == max_rank_value)))  
  
dataframe size: 4234 data samples, 111 features for pyspark ver. model.
  
### number of features:
for some reason, number of features were 111 for the pyspark editon and 85 for the original.  
there were around 20 category features that were not captured in the original ver. I really don't know why.  

### computation time for data cleaning:  
the original ver. around **6 minutes**.  
the pyspark ver. around **10 minutes**.  
  
a bit dissapointing result. I wonder if this result change if I used bigger dataset or use EMR from AWS....  
  
