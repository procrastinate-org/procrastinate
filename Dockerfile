FROM python:3

RUN pip install uv

ARG UID=1000
ARG GID=1000
WORKDIR /src/
RUN chown -R $UID:$GID /src
USER $UID:$GID
ENV HOME="/src"

COPY pyproject.toml ./
COPY uv.lock ./
RUN uv sync
ENTRYPOINT ["uv", "run"]
CMD ["procrastinate", "worker"]
