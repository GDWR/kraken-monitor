FROM python:3.12

ENV PYTHONUNBUFFERED="true"


ADD requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt


ADD main.py .

CMD ["python3", "main.py"]
