FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for RDKit and build tools
RUN apt-get update && apt-get install -y \
    build-essential \
    libxrender1 \
    libxext6 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download models to cache them in the Docker image
RUN python -c "from sentence_transformers import SentenceTransformer, CrossEncoder; SentenceTransformer('pritamdeka/S-PubMedBert-MS-MARCO'); CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')"

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
