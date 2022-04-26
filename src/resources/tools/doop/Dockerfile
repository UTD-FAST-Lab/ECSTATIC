# Copied from DOOP's repository (https://bitbucket.org/yanniss/doop/src/master/docs/docker/Dockerfile)
# on 2022-03-30

FROM checkmate/base-image AS base-image
USER root
## package update
RUN apt-get update -y && apt-get upgrade -y

FROM gfour/doop:4.24.9
COPY --from=base-image /checkmate /checkmate
COPY --from=base-image /venv /venv
ENV PATH=/venv/bin:$PATH