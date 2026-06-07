from fastapi import FastAPI
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
import gradio as gr
import os
import sys

# Ensure we can import from src/serving when running "uvicorn src.app.app:app"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from serving.inference import predict  # our single source of truth for inference

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/manifest.json")
def manifest():
    return JSONResponse(
        {
            "name": "Telco Churn Predictor",
            "short_name": "Churn Predictor",
            "start_url": "/ui",
            "display": "standalone",
            "background_color": "#ffffff",
            "theme_color": "#ffffff",
        }
    )


@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)

# Request schema (same fields you collect in the UI)
class CustomerData(BaseModel):
    gender: str
    Partner: str
    Dependents: str
    PhoneService: str
    MultipleLines: str
    InternetService: str
    OnlineSecurity: str
    OnlineBackup: str
    DeviceProtection: str
    TechSupport: str
    StreamingTV: str
    StreamingMovies: str
    Contract: str
    PaperlessBilling: str
    PaymentMethod: str
    tenure: int
    MonthlyCharges: float
    TotalCharges: float

@app.post("/predict")
def api_predict(data: CustomerData):
    try:
        out = predict(data.dict())
        return {"prediction": out}
    except Exception as e:
        return {"error": str(e)}

# --- Gradio UI wrappers the same predict() ---
def gradio_interface(
    gender, Partner, Dependents, PhoneService, MultipleLines,
    InternetService, OnlineSecurity, OnlineBackup, DeviceProtection,
    TechSupport, StreamingTV, StreamingMovies, Contract,
    PaperlessBilling, PaymentMethod, tenure, MonthlyCharges, TotalCharges
):
    payload = {
        "gender": gender,
        "Partner": Partner,
        "Dependents": Dependents,
        "PhoneService": PhoneService,
        "MultipleLines": MultipleLines,
        "InternetService": InternetService,
        "OnlineSecurity": OnlineSecurity,
        "OnlineBackup": OnlineBackup,
        "DeviceProtection": DeviceProtection,
        "TechSupport": TechSupport,
        "StreamingTV": StreamingTV,
        "StreamingMovies": StreamingMovies,
        "Contract": Contract,
        "PaperlessBilling": PaperlessBilling,
        "PaymentMethod": PaymentMethod,
        "tenure": int(tenure),
        "MonthlyCharges": float(MonthlyCharges),
        "TotalCharges": float(TotalCharges),
    }
    out = predict(payload)
    return str(out)


with gr.Blocks(theme=gr.themes.Soft(), title="Telco Churn Predictor") as demo:
    gr.Markdown(
        "# Telco Churn Predictor\n"
        "Use the form below to estimate whether a customer is likely to churn. "
        "The prediction appears at the top so you do not need to scroll back down."
    )

    prediction_output = gr.Textbox(
        label="Churn Prediction",
        value="Fill the form and click Predict",
        interactive=False,
        lines=2,
    )

    with gr.Row():
        predict_button = gr.Button("Predict", variant="primary")
        clear_button = gr.Button("Clear")

    with gr.Accordion("Customer Profile", open=True):
        with gr.Row():
            with gr.Column():
                gender = gr.Dropdown(["Male", "Female"], label="Gender")
                Partner = gr.Dropdown(["Yes", "No"], label="Partner")
                Dependents = gr.Dropdown(["Yes", "No"], label="Dependents")
            with gr.Column():
                tenure = gr.Number(label="Tenure (months)")
                MonthlyCharges = gr.Number(label="Monthly Charges ($)")
                TotalCharges = gr.Number(label="Total Charges ($)")

    with gr.Accordion("Service Details", open=True):
        with gr.Row():
            with gr.Column():
                PhoneService = gr.Dropdown(["Yes", "No"], label="Phone Service")
                MultipleLines = gr.Dropdown(["Yes", "No", "No phone service"], label="Multiple Lines")
                InternetService = gr.Dropdown(["DSL", "Fiber optic", "No"], label="Internet Service")
            with gr.Column():
                OnlineSecurity = gr.Dropdown(["Yes", "No", "No internet service"], label="Online Security")
                OnlineBackup = gr.Dropdown(["Yes", "No", "No internet service"], label="Online Backup")
                DeviceProtection = gr.Dropdown(["Yes", "No", "No internet service"], label="Device Protection")
            with gr.Column():
                TechSupport = gr.Dropdown(["Yes", "No", "No internet service"], label="Tech Support")
                StreamingTV = gr.Dropdown(["Yes", "No", "No internet service"], label="Streaming TV")
                StreamingMovies = gr.Dropdown(["Yes", "No", "No internet service"], label="Streaming Movies")

    with gr.Accordion("Billing and Contract", open=True):
        with gr.Row():
            with gr.Column():
                Contract = gr.Dropdown(["Month-to-month", "One year", "Two year"], label="Contract")
                PaperlessBilling = gr.Dropdown(["Yes", "No"], label="Paperless Billing")
            with gr.Column():
                PaymentMethod = gr.Dropdown(
                    ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"],
                    label="Payment Method"
                )

    inputs = [
        gender, Partner, Dependents, PhoneService, MultipleLines,
        InternetService, OnlineSecurity, OnlineBackup, DeviceProtection,
        TechSupport, StreamingTV, StreamingMovies, Contract,
        PaperlessBilling, PaymentMethod, tenure, MonthlyCharges, TotalCharges,
    ]

    predict_button.click(fn=gradio_interface, inputs=inputs, outputs=prediction_output)
    clear_button.click(lambda: "Fill the form and click Predict", outputs=prediction_output)

app = gr.mount_gradio_app(app, demo, path="/ui")
