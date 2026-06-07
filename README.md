# Telco Churn Prediction Project

## Model artifacts

After training, the pipeline exports a self-contained serving bundle to [src/serving/model](src/serving/model) and also logs the same bundle to MLflow under the run's `artifacts/model/` folder.

The exported bundle includes:

* `MLmodel` and the serialized model files
* `feature_columns.txt` and `feature_columns.json`
* `preprocessing.pkl`

## Train the model

Run the pipeline with your raw CSV input:

```bash
python scripts/run_pipeline.py --input data/raw/Telco-Customer-Churn.csv --target Churn
```

The FastAPI/Gradio serving code loads from [src/serving/inference.py](src/serving/inference.py), which now prefers the local serving bundle first and falls back to MLflow artifacts if needed.
