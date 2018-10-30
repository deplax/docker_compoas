FROM python:3

RUN apt-get update

WORKDIR /crawl
ADD    ./*   /crawl/
RUN    pip install -r requirements.txt

CMD ["python", "index.py"]