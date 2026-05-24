FROM kalilinux/kali-rolling:latest

ENV DEBIAN_FRONTEND=noninteractive \
    GOPATH=/root/go \
    PATH=/root/go/bin:/root/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# Paquetes APT en una sola capa: actualizar índices, instalar, limpiar.
# No tocamos /etc/apt/sources.list para evitar duplicar la fuente que ya trae
# /etc/apt/sources.list.d/kali.sources en la imagen base.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        build-essential gcc \
        git curl wget \
        golang \
        nano net-tools iputils-ping \
        zsh \
        python3 python3-pip python3-aiohttp \
        jq libpcap-dev \
        subfinder wpscan whois dirb ffuf seclists trufflehog && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Variables de entorno globales (cualquier shell login las verá).
RUN printf '%s\n' \
        'export GOPATH=/root/go' \
        'export PATH=$PATH:/root/go/bin:/root/.local/bin' \
        > /etc/profile.d/go.sh && \
    chmod +x /etc/profile.d/go.sh

# Herramientas Go. Si una falla, paramos el build (sin '|| true').
RUN go install github.com/projectdiscovery/httpx/cmd/httpx@latest && \
    go install github.com/projectdiscovery/katana/cmd/katana@latest && \
    go install github.com/tomnomnom/waybackurls@latest && \
    go install github.com/tomnomnom/anew@latest && \
    go install github.com/lc/gau/v2/cmd/gau@latest && \
    go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest && \
    for bin in httpx katana waybackurls anew gau nuclei; do \
        ln -sf /root/go/bin/$bin /usr/local/bin/$bin; \
    done && \
    rm -rf /root/.cache/go-build /root/go/pkg

# DOMChecker: clonar e instalar deps solo si existe requirements.txt.
WORKDIR /opt
RUN git clone --depth 1 https://github.com/Maalfer/domchecker.git && \
    if [ -f /opt/domchecker/requirements.txt ]; then \
        pip install --no-cache-dir --break-system-packages -r /opt/domchecker/requirements.txt; \
    else \
        echo "domchecker: sin requirements.txt, salto pip install"; \
    fi

# Wrapper de DOMChecker. printf en vez de heredoc para no depender de BuildKit.
RUN printf '#!/bin/bash\nexec python3 /opt/domchecker/domchecker.py "$@"\n' \
        > /usr/local/bin/domchecker && \
    chmod +x /usr/local/bin/domchecker && \
    ls -la /usr/local/bin/domchecker && \
    cat /usr/local/bin/domchecker

WORKDIR /home
CMD ["/bin/zsh", "-l"]
