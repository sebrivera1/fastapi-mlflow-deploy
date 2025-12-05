import os
import gradio as gr
import requests

# Backend configuration from environment
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Fix Railway internal URL if needed
if BACKEND_URL and not BACKEND_URL.startswith(("http://", "https://")):
    # Add http:// scheme if missing
    BACKEND_URL = f"http://{BACKEND_URL}"

# If Railway internal URL has no port or wrong port, fix it
if "railway.internal" in BACKEND_URL:
    # Check if it has :80 and replace with :8080
    if ":80/" in BACKEND_URL or BACKEND_URL.endswith(":80"):
        BACKEND_URL = BACKEND_URL.replace(":80", ":8080")
    # Check if it has no port at all
    elif not any(f":{port}" in BACKEND_URL for port in ["8080", "443", "8000"]):
        # Add port 8080 right after railway.internal
        BACKEND_URL = BACKEND_URL.replace("railway.internal", "railway.internal:8080")

#debug print
#print(f"[INFO] Backend URL configured as: {BACKEND_URL}")

def predict(name, bodyweight, squat, sex, cluster, long_distance_travel, total):
    """Send prediction request to backend"""

    # Prepare request
    url = f"{BACKEND_URL}/predict"
    headers = {}

    # Prepare payload matching the model's expected features
    payload = {
        "model_input": {
            "Squat1Kg": squat,
            "BodyweightKg": bodyweight,
            "Sex": sex,
            "Cluster": cluster,
            "long_distance_travel": long_distance_travel,
            "TotalKg": total
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            result = response.json()
            prediction = result.get("prediction", "No prediction returned")
            return f"Prediction for {name}:\n{prediction}"
        else:
            # Fallback if backend unavailable
            result = f"""
Prediction for {name}:
- Bodyweight: {bodyweight} kg
- Squat: {squat} kg
- Sex: {sex}
- Cluster: {cluster}
- Long Distance Travel: {long_distance_travel}
- Total: {total} kg

Note: Backend unavailable (status {response.status_code}), showing input summary only.
"""
            return result

    except Exception as e:
        # Fallback if backend unavailable
        result = f"""
Prediction for {name}:
- Bodyweight: {bodyweight} kg
- Squat: {squat} kg
- Sex: {sex}
- Cluster: {cluster}
- Long Distance Travel: {long_distance_travel}
- Total: {total} kg

Note: Cannot connect to backend ({str(e)}), showing input summary only.
"""
        return result

def check_health():
    """Check backend health status"""
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            data = response.json()
            return f"✓ Backend healthy - Model: {data.get('model', 'unknown')}"
        else:
            return f"✗ Backend unhealthy (status {response.status_code})"
    except Exception as e:
        return f"✗ Cannot connect to backend: {str(e)}"

# Create Gradio interface
with gr.Blocks(title="Power Lifting SBD Predictor") as demo:
    gr.Markdown("# Power Lifting SBD Predictor")
    #debugging print
    # gr.Markdown(f"Backend: `{BACKEND_URL}`")

    with gr.Row():
        health_output = gr.Textbox(label="Backend Status", interactive=False)
        health_btn = gr.Button("Check Health")

    gr.Markdown("## Enter Your Athlete Information")

    with gr.Row():
        with gr.Column():
            name_input = gr.Textbox(label="Name", placeholder="Enter your name")
            bodyweight_input = gr.Slider(minimum=30, maximum=200, value=75, label="Bodyweight (kg)")
            squat_input = gr.Slider(minimum=0, maximum=500, value=150, label="Squat 1RM (kg)")
            total_input = gr.Slider(minimum=0, maximum=1500, value=400, label="Total (kg)")

        with gr.Column():
            sex_input = gr.Radio(choices=["M", "F"], value="M", label="Sex")
            cluster_input = gr.Slider(minimum=0, maximum=14, step=1, value=5, label="Cluster")
            long_distance_input = gr.Checkbox(label="Long Distance Travel", value=False)

    submit_btn = gr.Button("Get Prediction", variant="primary")

    output = gr.Textbox(
        label="Prediction Result",
        lines=8,
        interactive=False
    )

    # Wire up events
    health_btn.click(fn=check_health, outputs=health_output)
    submit_btn.click(
        fn=predict,
        inputs=[name_input, bodyweight_input, squat_input, sex_input, cluster_input, long_distance_input, total_input],
        outputs=output
    )

    # Check health on load
    demo.load(fn=check_health, outputs=health_output)

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
