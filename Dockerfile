FROM python:3.7

EXPOSE 8080
ENV PYTHONPATH=/app
WORKDIR /app/test
COPY . /app/test
RUN pip install  --no-cache-dir -r requirements.txt
RUN ls -l
RUN pwd
CMD ["python", "/app/test/app.py"]