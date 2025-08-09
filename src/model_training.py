import os
import pandas as pd
import joblib
import lightgbm as lgb
from sklearn.metrics import accuracy_score, classification_report, f1_score, recall_score, precision_score
from src.logger import get_logger
from src.custom_exception import CustomException    
from config.paths_config import *
from config.model_params import *
from utils.common_functions import load_data
import mlflow
import mlflow.sklearn

logger = get_logger(__name__)

class ModelTraning:
    def __init__(self, train_path, test_path, model_output_path):
        self.train_path = train_path
        self.test_path = test_path
        self.model_output_path = model_output_path

    def load_and_split_data(self):
        try:
            logger.info(f"Loading data from {self.train_path}")
            train_df = load_data(self.train_path)

            logger.info(f"Loading data from {self.test_path}")
            test_df = load_data(self.test_path)

            X_train = train_df.drop(columns=['booking_status'])
            y_train = train_df['booking_status']

            X_test = test_df.drop(columns=['booking_status'])
            y_test = test_df['booking_status']

            logger.info("Data loaded and split into features and target variable")

            return X_train, y_train, X_test, y_test
        except Exception as e:
            logger.error(f"Error while loading and splitting data: {e}")
            raise CustomException("Failed to load and split data", e)

    def train_lgbm(self, X_train, y_train):
        try:
            logger.info("Initializing the LightGBM model with default/fixed parameters")

            lgbm_model = lgb.LGBMClassifier(
                n_estimators=100,
                learning_rate=0.1,
                num_leaves=31,
                max_depth=-1,
                random_state=42
            )

            lgbm_model.fit(X_train, y_train)

            logger.info("Model training completed without hyperparameter tuning")

            return lgbm_model

        except Exception as e:
            logger.error(f"Error while training model: {e}")
            raise CustomException("Failed to train model", e)

    def evaluate_model(self, model, X_test, y_test):
        try:
            logger.info("Evaluating our model")

            y_pred = model.predict(X_test)

            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred)
            recall = recall_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)

            logger.info(f"Accuracy Score : {accuracy}")
            logger.info(f"Precision Score : {precision}")
            logger.info(f"Recall Score : {recall}")
            logger.info(f"F1 Score : {f1}")

            return {
                "accuracy": accuracy,
                "precison": precision,
                "recall": recall,
                "f1": f1
            }
        except Exception as e:
            logger.error(f"Error while evaluating model: {e}")
            raise CustomException("Failed to evaluate model", e)

    def save_model(self, model):
        try:
            os.makedirs(os.path.dirname(self.model_output_path), exist_ok=True)

            logger.info("Saving the model")
            joblib.dump(model, self.model_output_path)
            logger.info(f"Model saved to {self.model_output_path}")

        except Exception as e:
            logger.error(f"Error while saving model: {e}")
            raise CustomException("Failed to save model", e)

    def run(self):
        try:
            with mlflow.start_run():
                logger.info("Started model training")
                logger.info("Starting our MLflow experimentation")

                logger.info("Logging the training and testing dataset to MLflow")
                mlflow.log_artifact(self.train_path, artifact_path="datasets")
                mlflow.log_artifact(self.test_path, artifact_path="datasets")

                X_train, y_train, X_test, y_test = self.load_and_split_data()
                model = self.train_lgbm(X_train, y_train)
                metrics = self.evaluate_model(model, X_test, y_test)
                self.save_model(model)

                logger.info("Logging the model to MLflow")
                mlflow.log_artifact(self.model_output_path, artifact_path="models")

                mlflow.log_params(model.get_params())
                mlflow.log_metrics(metrics)

                logger.info("Model training completed successfully")

        except CustomException as ce:
            logger.error(f"CustomException: {str(ce)}")


if __name__ == "__main__":
    model_training = ModelTraning(PROCESSED_TRAIN_DATA_PATH, PROCESSED_TEST_DATA_PATH, MODEL_OUTPUT_PATH)
    model_training.run()
