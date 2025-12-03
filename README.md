# MLflow Model Serving with Ray Serve

POC of Production-ready model serving backend using Ray Serve and MLflow, with Gradio UI.

## Features

- **Signature-aware API**: Automatically generates API from MLflow model signature
- **Version multiplexing**: Serve multiple model versions from single endpoint
- **Signature validation**: Prevents incompatible model versions from being served
- **Health checks**: Built-in health monitoring
- **Gradio UI**: User-friendly interface for model inference


```

### Gradio UI - Local deployment, Otherwise a Separate Railway or deployed service you need. 

1. Open browser to `http://localhost:7860`
2. Enter input text
3. Optionally specify model version
4. Click Submit

## Deployment

### Railway

1. Create new Railway service
2. Add environment variables from `.env.example`
3. Deploy `serve_backend.py`
4. Deploy `gradio_ui.py` as separate service with `BACKEND_URL` pointing to backend

### Docker (TODO)

```bash
docker build -t model-serving .
docker run -p 8000:8000 --env-file .env model-serving
```

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────┐
│  Gradio UI  │────────▶│  Ray Serve   │────────▶│ MLflow  │
│   (7860)    │         │   Backend    │         │Registry │
└─────────────┘         │   (8000)     │         └─────────┘
                        └──────────────┘
```

## Model Requirements

Your MLflow model must:
1. Be logged with `mlflow.pyfunc.log_model()`
2. Have an input signature defined
3. Be registered in MLflow Model Registry

## Troubleshooting

**Connection error**: Check `MLFLOW_TRACKING_URI` is correct and accessible

**Signature mismatch**: Ensure model versions have compatible signatures

**Port already in use**: Change ports in the Python files or kill existing processes
