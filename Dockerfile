FROM python:3.10-slim

WORKDIR /app

# Install the exact dependencies we need
RUN pip install --no-cache-dir openenv-core fastapi uvicorn pydantic openai

# Copy the entire project into the container
COPY . .

# Hugging Face Spaces strictly requires port 7860
EXPOSE 7860

# Run the FastAPI server
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]