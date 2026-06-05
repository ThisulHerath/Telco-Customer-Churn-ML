from sklearn.metrics import classification_report, confusion_matrix

def evaluate_model(model, X_test, y_test):
    """
    Evaluates the performance of a trained model on test data.

    Args:
        model: Trained machine learning model.
        X_test: Test features.
        y_test: Test labels.
    """

    preds = model.predict(X_test)
    print("Classification Report:\n", classification_report(y_test, preds))
    print("Confusion Matrix:\n", confusion_matrix(y_test, preds))