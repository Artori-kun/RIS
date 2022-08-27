FROM python:3.8-alpine

COPY . /ris
WORKDIR /ris
RUN pip install -r requirements.txt

ENTRYPOINT ["python"]

EXPOSE 5000

CMD ["app.py"]

