# Create a non-root user
FROM python:3.11-slim-buster AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y libxml2-dev libxslt-dev build-essential
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .
USER appuser

# Final image
FROM python:3.11-slim-buster
WORKDIR /app
COPY --from=builder /app .
USER appuser
EXPOSE 8000
CMD ["python", "-m", "gunicorn", "thecart_commerce.wsgi:application", "-k", "uvicorn.workers.UvicornWorker"]
     
     