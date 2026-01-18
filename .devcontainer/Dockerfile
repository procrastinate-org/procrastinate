FROM mcr.microsoft.com/devcontainers/python:3.14

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

# Add /home/vscode/.local/bin to PATH for uv tool installs
ENV PATH="/home/vscode/.local/bin:${PATH}"
