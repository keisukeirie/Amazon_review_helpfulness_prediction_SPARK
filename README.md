# Amazon_review_helpfulness_prediction PYSPARK EDITION
this is my repository for the Amazon Review Helpfulness prediction model project using Pyspark for ML and data cleaning.  
_last updated: 10/26/2017_  
  
## OBJECTIVE:
The motivation here is to repeat/improve what I did for the Amazon review helpfulness prediction all in pyspark.  
  
### BUT WHY?:
1. spark can do data cleaning and tfidf and machine learning computationally faster.  
2. Learning experience. Learn more about Spark, Hive and SQL.
  
## PROCEDURES:
1. Rewrite/improve original python codes to pyspark codes.  
2. compare the original result to the pyspark result (accuracy and computation time).  
3. Connect to EMR and run with AWS support for even bigger dataset (Home&kitchen data?).  


## NOTES:
unlike my previous project, on this repo, I will post lots of notes.  
I figure that there aren't much stackoverflow postings on pyspark compare to other language that Spark can handle (scala, Java).  
So I want to put notes on my repo just so that it can maybe help someone who is new to spark (just like myself).  
  
### Note file:
notes_on_data_cleaning_process.md  
  - will have notes on the first process of data cleaning.  
notes_on_tfidf_nmf_process.md  
  - will have notes on the tfidf, nmf, nlp related functions.
notes_on_ml.md (in the future)
  - will have notes on the ML library used in this project.
notes_on_EMR.md (in the future)
  - will have notes on the EMR. How to set up EMR.

## CHANGE MADE FROM THE PREVIOUS VERSION:

#### data samples with no Rank_Values and no Price:

#### Rank_Value imputation:
For the Rank_Value feature, null values were replaced with average value.  
Because the Rank_Value feature represents the rank of products, I figure it will not be realistic to impute it with the average value.  
Instead, I am imputating these nulls with (Max of Rank_Value) + 1

#### Price imputation:
Previously, I imputed price feature with the average values and then ran train and test split.  
Since the price feature was the most important feature, I figure I should look back and see if I didn't make a mistake.  
The mistake I made was that imputing it with the average vale before train,test split causes some error.
Because average values should be different between train and test data, I needed some other way to impute this price feature.  
What I end up doing was that I replaced pruce values into categorical values.
1. below20  
2. below50  
3. below100  
4. below300  
5. above300  
6. unknown (nulls)  
  
With these change, I can make train-test split after running my data cleaning process.  
  
## RESULTS:
### Computation time:
**Video Game Product reviews:**    
- Ran the original ver. in my laptop (MacBookPro 2015)  
- Ran the pyspark with 4 CPU in my laptop and with 9 R3.xlarge EMR instances (1master,8nodes).  
(data cleaning reduce samples to about 4,300 samples) 
training: 2800 samples, test: 636 samples   
  
|               |   Original ver.   |  Pyspark laptop  |   Pyspark EMR   |
| ------------- |:-----------------:|:----------------:| ---------------:|
| data cleaning |    00:06:12:38    |   00:10:39:36    |   00:00:00:00   |
|   TFIDF+NMF   |    00:04:46:44    |   Memory prob.   |   00:00:00:00   |
| Random Forest |    00:00:22:00    |   00:00:00:00    |   00:00:00:00   |
|    Total      |    00:11:20:82    |   00:00:00:00    |   00:00:00:00   |
  
  
#### Original Ver result:
  
 **TOP10 Important Features**   
enjoy : 0.907305699071%  
percent_GROUP_4 : 0.960251319721%  
sort : 1.10448132333%  
die : 1.12857298946%  
surprise : 1.22353217363%  
price : 1.42303649998%  
gamecube : 1.61354571494%  
rank_values : 3.45245920816%  
text_length : 6.00004820027%  
overall : 8.50613117299%  

 |                      | NOT HELPFUL TRUE | HIGHLY HELPFUL TRUE |
 | -------------------- |:----------------:| -------------------:|
 |   NOT HELPFUL PRED   |      205.0       |         50.0        |
 | HIGHLY HELPFUL PRED  |       37.0       |        344.0        |

LOW prediction rate: 84.71%
HIGH prediction rate: 87.31%
  
#### Pyspark Ver with laptop result:
Used 4CPU from my laptop (2015 MBP) to do the same process in pyspark.  
The data cleaning process was much slower than running it without spark.  
TFIDF calculation worked just fine. However, when I set up a rating matrix for NMF,  
I started to have a memory issue. the sparse matrix containing TFIDF terms contained about 70000 samples  
and I started to see more error message as I prepare a rating matrix for NMF collaborative filtering.  
(in fact, it did not run ALS with my rating matrix).  

So I decided to use AWS EMR instances instead.  

**Homeandkitchen Product reviews:**
- Ran the original ver. with AWS EC2 instance (m4.2xlarge)
- Ran the pyspark ver. with AWS EMR instances (1master, 8nodes)  
(data cleaning reduce samples to about 81,775 samples)  

|               |   Original ver.   |   Pyspark ver.   |
| ------------- |:-----------------:| ----------------:|
| data cleaning |    00:12:58:33    |   00:00:00:00    |
|   TFIDF+NMF   |    00:28:28:17    |   00:00:00:00    |
| Random Forest |    00:03:49:10    |   00:00:00:00    |
|    Total      |    00:45:15:60    |   00:00:00:00    |


## CONCLUSION:

