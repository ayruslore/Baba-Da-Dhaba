FROM node:carbon

WORKDIR /new

ADD . /new

EXPOSE 3000

RUN npm install express
RUN npm install body-parser
RUN npm install request
RUN npm install path
RUN npm install apiai
RUN npm install http
RUN npm install bluebird

ENV NAME node_server

CMD ["node","www.js"]
