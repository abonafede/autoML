# This file has been autogenerated by version 1.51.0 of the Azure Automated Machine Learning SDK.


import numpy
import numpy as np
import pandas as pd
import pickle
import argparse


# For information on AzureML packages: https://docs.microsoft.com/en-us/python/api/?view=azure-ml-py
from azureml.training.tabular._diagnostics import logging_utilities


def setup_instrumentation(automl_run_id):
    import logging
    import sys

    from azureml.core import Run
    from azureml.telemetry import INSTRUMENTATION_KEY, get_telemetry_log_handler
    from azureml.telemetry._telemetry_formatter import ExceptionFormatter

    logger = logging.getLogger("azureml.training.tabular")

    try:
        logger.setLevel(logging.INFO)

        # Add logging to STDOUT
        stdout_handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(stdout_handler)

        # Add telemetry logging with formatter to strip identifying info
        telemetry_handler = get_telemetry_log_handler(
            instrumentation_key=INSTRUMENTATION_KEY, component_name="azureml.training.tabular"
        )
        telemetry_handler.setFormatter(ExceptionFormatter())
        logger.addHandler(telemetry_handler)

        # Attach run IDs to logging info for correlation if running inside AzureML
        try:
            run = Run.get_context()
            return logging.LoggerAdapter(logger, extra={
                "properties": {
                    "codegen_run_id": run.id,
                    "automl_run_id": automl_run_id
                }
            })
        except Exception:
            pass
    except Exception:
        pass

    return logger


automl_run_id = 'AutoML_8f1c75c4-1d06-4e3e-9450-78b6d63d6274_20'
logger = setup_instrumentation(automl_run_id)


def split_dataset(X, y, weights, split_ratio, should_stratify):
    '''
    Splits the dataset into a training and testing set.

    Splits the dataset using the given split ratio. The default ratio given is 0.25 but can be
    changed in the main function. If should_stratify is true the data will be split in a stratified
    way, meaning that each new set will have the same distribution of the target value as the
    original dataset. should_stratify is true for a classification run, false otherwise.
    '''
    from sklearn.model_selection import train_test_split

    random_state = 42
    if should_stratify:
        stratify = y
    else:
        stratify = None

    if weights is not None:
        X_train, X_test, y_train, y_test, weights_train, weights_test = train_test_split(
            X, y, weights, stratify=stratify, test_size=split_ratio, random_state=random_state
        )
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, stratify=stratify, test_size=split_ratio, random_state=random_state
        )
        weights_train, weights_test = None, None

    return (X_train, y_train, weights_train), (X_test, y_test, weights_test)


def get_training_dataset(dataset_id):
    '''
    Loads the previously used dataset.
    
    It assumes that the script is run in an AzureML command job under the same workspace as the original experiment.
    '''
    
    from azureml.core.dataset import Dataset
    from azureml.core.run import Run
    
    logger.info("Running get_training_dataset")
    ws = Run.get_context().experiment.workspace
    dataset = Dataset.get_by_id(workspace=ws, id=dataset_id)
    return dataset.to_pandas_dataframe()


def prepare_data(dataframe):
    '''
    Prepares data for training.
    
    Cleans the data, splits out the feature and sample weight columns and prepares the data for use in training.
    This function can vary depending on the type of dataset and the experiment task type: classification,
    regression, or time-series forecasting.
    '''
    
    from azureml.training.tabular.preprocessing import data_cleaning
    
    logger.info("Running prepare_data")
    label_column_name = 'Species'
    
    # extract the features, target and sample weight arrays
    y = dataframe[label_column_name].values
    X = dataframe.drop([label_column_name], axis=1)
    sample_weights = None
    
    # Split training data into train/test datasets and take only the train dataset
    split_ratio = 0.2
    try:
        (X, y, sample_weights), _ = split_dataset(X, y, sample_weights, split_ratio, should_stratify=True)
    except Exception:
        (X, y, sample_weights), _ = split_dataset(X, y, sample_weights, split_ratio, should_stratify=False)
    X, y, sample_weights = data_cleaning._remove_nan_rows_in_X_y(X, y, sample_weights,
     is_timeseries=False, target_column=label_column_name)
    
    return X, y, sample_weights


def get_mapper_0(column_names):
    from sklearn.impute import SimpleImputer
    from sklearn_pandas.dataframe_mapper import DataFrameMapper
    from sklearn_pandas.features_generator import gen_features
    
    definition = gen_features(
        columns=column_names,
        classes=[
            {
                'class': SimpleImputer,
                'add_indicator': False,
                'copy': True,
                'fill_value': None,
                'missing_values': numpy.nan,
                'strategy': 'mean',
                'verbose': 0,
            },
        ]
    )
    mapper = DataFrameMapper(features=definition, input_df=True, sparse=True)
    
    return mapper
    
    
def generate_data_transformation_config():
    '''
    Specifies the featurization step in the final scikit-learn pipeline.
    
    If you have many columns that need to have the same featurization/transformation applied (for example,
    50 columns in several column groups), these columns are handled by grouping based on type. Each column
    group then has a unique mapper applied to all columns in the group.
    '''
    from sklearn.pipeline import FeatureUnion
    
    column_group_0 = [['Id'], ['SepalLengthCm'], ['SepalWidthCm'], ['PetalLengthCm'], ['PetalWidthCm']]
    
    mapper = get_mapper_0(column_group_0)
    return mapper
    
    
def generate_preprocessor_config():
    '''
    Specifies a preprocessing step to be done after featurization in the final scikit-learn pipeline.
    
    Normally, this preprocessing step only consists of data standardization/normalization that is
    accomplished with sklearn.preprocessing. Automated ML only specifies a preprocessing step for
    non-ensemble classification and regression models.
    '''
    from sklearn.preprocessing import StandardScaler
    
    preproc = StandardScaler(
        copy=True,
        with_mean=False,
        with_std=False
    )
    
    return preproc
    
    
def generate_algorithm_config():
    '''
    Specifies the actual algorithm and hyperparameters for training the model.
    
    It is the last stage of the final scikit-learn pipeline. For ensemble models, generate_preprocessor_config_N()
    (if needed) and generate_algorithm_config_N() are defined for each learner in the ensemble model,
    where N represents the placement of each learner in the ensemble model's list. For stack ensemble
    models, the meta learner generate_algorithm_config_meta() is defined.
    '''
    from xgboost.sklearn import XGBClassifier
    
    algorithm = XGBClassifier(
        base_score=0.5,
        booster='gbtree',
        colsample_bylevel=1,
        colsample_bynode=1,
        colsample_bytree=0.9,
        eta=0.1,
        gamma=0,
        gpu_id=-1,
        importance_type='gain',
        interaction_constraints='',
        learning_rate=0.100000001,
        max_delta_step=0,
        max_depth=6,
        max_leaves=3,
        min_child_weight=1,
        missing=numpy.nan,
        monotone_constraints='()',
        n_estimators=25,
        n_jobs=0,
        num_parallel_tree=1,
        objective='multi:softprob',
        random_state=0,
        reg_alpha=0,
        reg_lambda=0.7291666666666667,
        scale_pos_weight=None,
        subsample=0.5,
        tree_method='auto',
        use_label_encoder=True,
        validate_parameters=1,
        verbose=-10,
        verbosity=0
    )
    
    return algorithm
    
    
def generate_pipeline_with_ytransformer(pipeline):
    
    from azureml.training.tabular.models.pipeline_with_ytransformations import PipelineWithYTransformations
    from sklearn.preprocessing import LabelEncoder
    
    transformer = LabelEncoder()
    transformer_name = "LabelEncoder"
    return PipelineWithYTransformations(pipeline, transformer_name, transformer)
    
def build_model_pipeline():
    '''
    Defines the scikit-learn pipeline steps.
    '''
    from sklearn.pipeline import Pipeline
    
    logger.info("Running build_model_pipeline")
    pipeline = Pipeline(
        steps=[
            ('featurization', generate_data_transformation_config()),
            ('preproc', generate_preprocessor_config()),
            ('model', generate_algorithm_config()),
        ]
    )
    
    return generate_pipeline_with_ytransformer(pipeline)


def train_model(X, y, sample_weights=None, transformer=None):
    '''
    Calls the fit() method to train the model.
    
    The return value is the model fitted/trained on the input data.
    '''
    
    logger.info("Running train_model")
    model_pipeline = build_model_pipeline()
    
    model = model_pipeline.fit(X, y)
    return model


def calculate_metrics(model, X, y, sample_weights, X_test, y_test, cv_splits=None):
    '''
    Calculates the metrics that can be used to evaluate the model's performance.
    
    Metrics calculated vary depending on the experiment type. Classification, regression and time-series
    forecasting jobs each have their own set of metrics that are calculated.'''
    
    from azureml.training.tabular.score.scoring import score_classification
    
    y_pred_probs = model.predict_proba(X_test)
    if isinstance(y_pred_probs, pd.DataFrame):
        y_pred_probs = y_pred_probs.values
    class_labels = np.unique(y)
    train_labels = model.classes_
    metrics = score_classification(
        y_test, y_pred_probs, get_metrics_names(), class_labels, train_labels, use_binary=True)
    return metrics


def get_metrics_names():
    
    metrics_names = [
        'accuracy',
        'iou',
        'recall_score_classwise',
        'f1_score_binary',
        'AUC_classwise',
        'accuracy_table',
        'precision_score_micro',
        'AUC_micro',
        'precision_score_binary',
        'AUC_binary',
        'iou_weighted',
        'average_precision_score_classwise',
        'average_precision_score_binary',
        'AUC_macro',
        'recall_score_weighted',
        'precision_score_weighted',
        'average_precision_score_micro',
        'average_precision_score_macro',
        'iou_macro',
        'average_precision_score_weighted',
        'f1_score_weighted',
        'f1_score_macro',
        'matthews_correlation',
        'balanced_accuracy',
        'iou_classwise',
        'AUC_weighted',
        'f1_score_classwise',
        'precision_score_classwise',
        'weighted_accuracy',
        'classification_report',
        'precision_score_macro',
        'recall_score_micro',
        'iou_micro',
        'recall_score_binary',
        'f1_score_micro',
        'recall_score_macro',
        'norm_macro_recall',
        'log_loss',
        'confusion_matrix',
    ]
    return metrics_names


def get_metrics_log_methods():
    
    metrics_log_methods = {
        'accuracy': 'log',
        'iou': 'Skip',
        'recall_score_classwise': 'Skip',
        'f1_score_binary': 'log',
        'AUC_classwise': 'Skip',
        'accuracy_table': 'log_accuracy_table',
        'precision_score_micro': 'log',
        'AUC_micro': 'log',
        'precision_score_binary': 'log',
        'AUC_binary': 'log',
        'iou_weighted': 'Skip',
        'average_precision_score_classwise': 'Skip',
        'average_precision_score_binary': 'log',
        'AUC_macro': 'log',
        'recall_score_weighted': 'log',
        'precision_score_weighted': 'log',
        'average_precision_score_micro': 'log',
        'average_precision_score_macro': 'log',
        'iou_macro': 'Skip',
        'average_precision_score_weighted': 'log',
        'f1_score_weighted': 'log',
        'f1_score_macro': 'log',
        'matthews_correlation': 'log',
        'balanced_accuracy': 'log',
        'iou_classwise': 'Skip',
        'AUC_weighted': 'log',
        'f1_score_classwise': 'Skip',
        'precision_score_classwise': 'Skip',
        'weighted_accuracy': 'log',
        'classification_report': 'Skip',
        'precision_score_macro': 'log',
        'recall_score_micro': 'log',
        'iou_micro': 'Skip',
        'recall_score_binary': 'log',
        'f1_score_micro': 'log',
        'recall_score_macro': 'log',
        'norm_macro_recall': 'log',
        'log_loss': 'log',
        'confusion_matrix': 'log_confusion_matrix',
    }
    return metrics_log_methods


def main(training_dataset_id=None):
    '''
    Runs all functions defined above.
    '''
    
    from azureml.automl.core.inference import inference
    from azureml.core.run import Run
    
    import mlflow
    
    # The following code is for when running this code as part of an AzureML script run.
    run = Run.get_context()
    
    df = get_training_dataset(training_dataset_id)
    X, y, sample_weights = prepare_data(df)
    split_ratio = 0.25
    try:
        (X_train, y_train, sample_weights_train), (X_valid, y_valid, sample_weights_valid) = split_dataset(X, y, sample_weights, split_ratio, should_stratify=True)
    except Exception:
        (X_train, y_train, sample_weights_train), (X_valid, y_valid, sample_weights_valid) = split_dataset(X, y, sample_weights, split_ratio, should_stratify=False)
    model = train_model(X_train, y_train, sample_weights_train)
    
    metrics = calculate_metrics(model, X, y, sample_weights, X_test=X_valid, y_test=y_valid)
    metrics_log_methods = get_metrics_log_methods()
    print(metrics)
    for metric in metrics:
        if metrics_log_methods[metric] == 'None':
            logger.warning("Unsupported non-scalar metric {}. Will not log.".format(metric))
        elif metrics_log_methods[metric] == 'Skip':
            pass # Forecasting non-scalar metrics and unsupported classification metrics are not logged
        else:
            getattr(run, metrics_log_methods[metric])(metric, metrics[metric])
    cd = inference.get_conda_deps_as_dict(True)
    
    # Saving ML model to outputs/.
    signature = mlflow.models.signature.infer_signature(X, y)
    mlflow.sklearn.log_model(
        sk_model=model,
        artifact_path='outputs/',
        conda_env=cd,
        signature=signature,
        serialization_format=mlflow.sklearn.SERIALIZATION_FORMAT_PICKLE)
    
    run.upload_folder('outputs/', 'outputs/')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--training_dataset_id', type=str, default='eb16f48c-a45e-4dc9-9638-f6f51b302015',     help='Default training dataset id is populated from the parent run')
    args = parser.parse_args()
    
    try:
        main(args.training_dataset_id)
    except Exception as e:
        logging_utilities.log_traceback(e, logger)
        raise