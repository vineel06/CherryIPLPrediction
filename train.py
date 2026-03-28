import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import os

def train():
    X = np.load("data/processed/X.npy")
    y = np.load("data/processed/y.npy")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = xgb.XGBClassifier(n_estimators=200, max_depth=6, learning_rate=0.1, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"Test accuracy: {acc:.3f}")

    os.makedirs("model", exist_ok=True)
    joblib.dump(model, "model/xgb_model.pkl")
    print("Model saved to model/xgb_model.pkl")

if __name__ == "__main__":
    train()