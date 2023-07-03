# AutoML
This is my second project for Duke's AIPI 5461 - Operationalizing AI. The main goal of this project was to get familiar with the key concepts and applications of AutoML. AutoML, short for Automated Machine Learning, is a process that automates various stages of machine learning model development, including data preprocessing, feature engineering, and model selection, allowing users with limited expertise to create effective machine learning models. It aims to simplify the machine learning workflow and democratize the accessibility and application of machine learning techniques.

## Azure Machine Learning Studio
Azure Machine Learning Studio is a cloud-based integrated development environment (IDE) provided by Microsoft that facilitates the creation, deployment, and management of machine learning models. It offers a graphical interface and drag-and-drop functionality, allowing users to easily design, experiment, and iterate on their models. Azure Machine Learning Studio's AutoML functionality further enhances the platform by automating the end-to-end machine learning process. It automates tasks such as data preprocessing, feature engineering, algorithm selection, hyperparameter tuning, and model evaluation, enabling users to quickly build and deploy high-performing machine learning models without extensive manual effort. The AutoML functionality in Azure Machine Learning Studio helps democratize machine learning by enabling non-experts to leverage advanced techniques and accelerate their data-driven decision-making processes.

## Data 
The [Kaggle Iris Dataset](https://www.kaggle.com/datasets/uciml/iris) is a widely used benchmark dataset in machine learning and statistics. It consists of measurements of four features (sepal length, sepal width, petal length, and petal width) from three different species of Iris flowers (setosa, versicolor, and virginica). The dataset contains 150 instances, with 50 instances for each species. The objective of the dataset is to classify the Iris flowers into their respective species based on the given measurements. The Iris dataset is often used for tasks such as classification, clustering, and pattern recognition, making it a popular choice for evaluating and comparing different machine learning algorithms.

## Modeling 
First, the data is transformed and scaled using a StandardScaler from the sklearn.preprocessing module. The provided parameters "with_mean" and "with_std" are set to false, indicating that the scaler will not center the data around zero or scale it to unit variance.

The model itself is an XGBoostClassifier from the automl.client.core.common.model_wrappers module. It is a classifier based on the gradient boosting framework called XGBoost. The model's parameters include various settings such as the booster type ("gbtree"), the fraction of features to consider for each tree ("colsample_bytree"), learning rate ("eta"), maximum tree depth ("max_depth"), number of maximum leaves ("max_leaves"), number of estimators ("n_estimators"), objective function ("reg:logistic"), regularization parameters ("reg_alpha" and "reg_lambda"), subsampling ratio ("subsample"), and tree method ("auto").

## Results
As we can see,
<img width="479" alt="prcurve" src="https://github.com/abonafede/autoML/assets/60437669/0ad28241-dfbc-4f5a-bbcf-9b853e3a601e">
our average precision and recall scores are near perfect.

Our ROC score,
<img width="480" alt="poc" src="https://github.com/abonafede/autoML/assets/60437669/23fcabca-4e72-4e20-a0e3-70bbb7ce5479">
is also near perfect.

And our confusion matrix,
<img width="496" alt="confusion" src="https://github.com/abonafede/autoML/assets/60437669/45ea4a19-9cf9-4b13-b8be-cfb452108875">
is almost 100% accurate.

These metrics were calculated on 20% test set, with .991 accuracy and .999 AUC.

## Running the Project 
This project was run on Azure Machine Learning Studio. To run locally, please install all dependencies, and run [script.py](https://github.com/abonafede/autoML/tree/main/script.py).
