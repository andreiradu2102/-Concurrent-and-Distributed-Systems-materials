FROM python:3.11
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
COPY /src /app
WORKDIR /app
EXPOSE 80
CMD ["python", "main.py"]
