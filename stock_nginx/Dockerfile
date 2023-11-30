FROM nginx

ENV HOME=/home/app
RUN mkdir $HOME
RUN mkdir $HOME/static

RUN rm /etc/nginx/conf.d/default.conf
COPY ./default.conf /etc/nginx/conf.d/default.conf

