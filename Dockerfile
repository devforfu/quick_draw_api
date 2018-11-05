FROM python:3.7-slim-stretch

RUN apt update
RUN apt install -y python3-dev gcc

RUN pip install torch_nightly -f https://download.pytorch.org/whl/nightly/cpu/torch_nightly.html
RUN pip install torchvision_nightly
RUN pip install fastai==1.0.19
RUN pip install starlette uvicorn python-multipart aiohttp

WORKDIR /app

COPY . /app

EXPOSE 8080

CMD ["python", "app.py", "serve"]