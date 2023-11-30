FROM python:3.10.12

RUN pip install --upgrade pip

RUN python --version

COPY ./requirements.txt .
RUN pip install -r requirements.txt

ENV HOME=/home/app

RUN mkdir $HOME
RUN mkdir $HOME/static
COPY ./stock $HOME

WORKDIR $HOME

COPY ./entrypoint.sh /
ENTRYPOINT [ "bash", "/entrypoint.sh" ]


