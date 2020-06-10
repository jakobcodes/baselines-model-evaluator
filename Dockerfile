FROM python:3.6

ENV POLICY_PATH=/srv/prod_policy/model.bin

RUN pip3 install waitress \
      cloudpickle==0.5.2 \
      numpy \
      pandas \
      psutil \
      scipy \
      tensorflow==1.15.2 \
      Flask \
      joblib 

RUN pip3 install git+https://github.com/openai/baselines#egg=baselines

COPY . /tmp

RUN cd /tmp \
    && mkdir -p /srv \
    && cp -ar /tmp/prod_policy /srv \
    && pip3 install . \
    && cd / \
    && rm -rf /tmp/*

WORKDIR /srv

CMD ["waitress-serve", "baselinesme.api:app"]
