FROM codercom/code-server:latest

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    build-essential \
    ca-certificates \
    curl \
    git \
    gnupg \
    gosu \
    jq \
    locales \
    make \
    openssh-client \
    postgresql-client \
    python3 \
    python3-pip \
    python3-venv \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Node.js 22
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get update \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# GitHub CLI
RUN mkdir -p -m 755 /etc/apt/keyrings \
    && wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg \
       | tee /etc/apt/keyrings/githubcli-archive-keyring.gpg >/dev/null \
    && chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
       > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update \
    && apt-get install -y gh \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g pnpm eas-cli @anthropic-ai/claude-code

COPY extensions.txt /tmp/extensions.txt
RUN while IFS= read -r extension; do \
      [ -z "$extension" ] && continue; \
      gosu coder code-server --install-extension "$extension" || true; \
    done < /tmp/extensions.txt

COPY entrypoint.sh /usr/local/bin/project-entrypoint.sh
COPY git-bootstrap.sh /usr/local/bin/git-bootstrap.sh
RUN chmod +x /usr/local/bin/project-entrypoint.sh /usr/local/bin/git-bootstrap.sh \
    && printf '\n# Configuração inicial Git/GitHub\nif [[ $- == *i* ]]; then /usr/local/bin/git-bootstrap.sh; fi\n' >> /home/coder/.bashrc

ENTRYPOINT ["/usr/local/bin/project-entrypoint.sh"]
CMD ["--bind-addr", "0.0.0.0:8080", "--auth", "password", "--locale", "pt-BR", "/home/coder/workspace"]
