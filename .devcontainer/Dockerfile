FROM mcr.microsoft.com/devcontainers/python:3.13

USER root

RUN sudo apt-get update \
  && apt-get install -y --no-install-recommends \
  bash-completion \
  postgresql-common \
  && /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh -y \
  && apt-get install -y --no-install-recommends \
  postgresql-client \
  && rm -rf /var/lib/apt/lists/*

USER vscode

RUN pipx install poetry \
  && poetry completions bash >> ~/.bash_completion
