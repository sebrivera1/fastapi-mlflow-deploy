# MLflow Model Serving with FastAPI

Production-ready model serving backend using FastAPI and MLflow, with Gradio UI.

## Features

- **FastAPI Backend**: Lightweight, async model serving API
- **MLflow Integration**: Load and serve models from MLflow Model Registry
- **Version multiplexing**: Serve multiple model versions from single endpoint
- **Signature validation**: Prevents incompatible model versions from being served
- **Health checks**: Built-in health monitoring
- **Gradio UI**: User-friendly interface for model inference
- **Railway Deployment**: Optimized for Railway platform (FastAPI instead of Ray Serve due to PIDs limit)

## Local Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Edit `.env`:
```
MLFLOW_TRACKING_URI=http://your-mlflow-railway-url.up.railway.app
MODEL_NAME=your_model_name
MODEL_VERSION=1
BACKEND_URL=http://localhost:8000
```

### 3. Run Backend

```bash
python main.py
```

Backend will start on `http://0.0.0.0:8000` (or port specified by `PORT` env var)

### 4. Run Gradio UI (in separate terminal)

```bash
python app.py
```

UI will be available at `http://localhost:7860`

## Usage

### API Endpoints

**Predict**: `POST /predict`
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "model_input": {
      "height": 150,
      "weight": 90,
      "squat": 50,
      "bench": 60,
      "deadlift": 110
    }
  }'
```

**Predict with specific version**: Add version to payload or header
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "model_input": {
      "height": 150,
      "weight": 90,
      "squat": 50,
      "bench": 60,
      "deadlift": 110
    },
    "version": "2"
  }'
```

**Health check**: `GET /health`
```bash
curl http://localhost:8000/health
```

### Gradio UI

1. Open browser to `http://localhost:7860`
2. Enter your fitness metrics (height, weight, squat, bench, deadlift)
3. Click "Predict Cluster"
4. View prediction results

**Note**: For production, deploy Gradio UI as a separate Railway service

## Deployment

### Railway

**Why FastAPI instead of Ray Serve?**
Railway has a PIDs (process IDs) limit that prevents Ray Serve from running properly. FastAPI provides a lightweight alternative for model serving.

**Backend Service** (`main.py`):
1. Create new Railway service
2. Add environment variables:
   ```
   MLFLOW_TRACKING_URI=http://your-mlflow-service.railway.internal
   MODEL_NAME=Demo-DummyModel
   MODEL_VERSION=1
   PORT=8080
   ```
3. Deploy and note the service URL

**Gradio UI Service** (`app.py`):
1. Create separate Railway service
2. Add environment variables:
   ```
   BACKEND_URL=http://your-backend-service.railway.internal:8080
   ```
   or use public URL:
   ```
   BACKEND_URL=https://your-backend-service.up.railway.app
   ```
3. Deploy

### Docker (TODO)

```bash
docker build -t model-serving .
docker run -p 8000:8000 --env-file .env model-serving
```

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────┐
│  Gradio UI  │────────▶│   FastAPI    │────────▶│ MLflow  │
│   (7860)    │         │   Backend    │         │Registry │
└─────────────┘         │   (8080)     │         └─────────┘
                        └──────────────┘
                             main.py
```

**Note**: A Ray Serve implementation is available but cannot be used on Railway due to PIDs limit.

## Model Requirements

Your MLflow model must:
1. Be logged with `mlflow.pyfunc.log_model()`
2. Have an input signature defined
3. Be registered in MLflow Model Registry

## Troubleshooting

**Connection error**: Check `MLFLOW_TRACKING_URI` is correct and accessible

**Signature mismatch**: Ensure model versions have compatible signatures

**Port already in use**: Change ports in the Python files or kill existing processes

**Railway Gradio can't connect to backend**:
- Ensure `BACKEND_URL` includes the correct port (`:8080`)
- Use Railway internal URL: `http://service-name.railway.internal:8080`
- Or use public URL: `https://service-name.up.railway.app`

**String to float conversion error**:
- Ensure you're only sending numeric features to the model
- Non-numeric fields (like `name`) are automatically filtered out

**FastAPI deprecation warnings**:
- Code uses modern `lifespan` event handlers instead of deprecated `on_event`
