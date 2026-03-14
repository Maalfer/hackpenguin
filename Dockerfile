FROM kalilinux/kali-rolling:latest

ENV DEBIAN_FRONTEND=noninteractive

# 1. Fix de Mirror y Certificados + Instalación de Compiladores (build-essential, gcc)
RUN echo "deb http://http.kali.org/kali kali-rolling main contrib non-free non-free-firmware" > /etc/apt/sources.list && \
    apt-get update -o Acquire::https::Verify-Peer=false && \
    apt-get install -y --no-install-recommends -o Acquire::https::Verify-Peer=false ca-certificates && \
    apt-get clean

# Añadimos build-essential, gcc y libpcap-dev (necesario para herramientas de red en Go)
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    build-essential gcc git curl wget golang nano net-tools iputils-ping \
    zsh subfinder wpscan whois dirb ffuf seclists python3 python3-pip \
    trufflehog python3-aiohttp jq libpcap-dev && \
    apt-get clean

# Configuración de PATH para ZSH
RUN echo 'export PATH=$PATH:/root/.local/bin' >> ~/.zshrc && \
    echo 'export GOPATH=$HOME/go' >> ~/.zshrc && \
    echo 'export PATH=$PATH:$GOPATH/bin' >> ~/.zshrc

# 2. Instalación de herramientas en Go (CGO_ENABLED=1 es por defecto, pero ahora tenemos GCC)
RUN go install github.com/projectdiscovery/httpx/cmd/httpx@latest && \
    ln -sf /root/go/bin/httpx /usr/bin/httpx && \
    go install github.com/projectdiscovery/katana/cmd/katana@latest && \
    ln -sf /root/go/bin/katana /usr/bin/katana && \
    go install github.com/tomnomnom/waybackurls@latest && \
    ln -sf /root/go/bin/waybackurls /usr/bin/waybackurls && \
    go install github.com/tomnomnom/anew@latest && \
    ln -sf /root/go/bin/anew /usr/bin/anew && \
    go install github.com/lc/gau/v2/cmd/gau@latest && \
    ln -sf /root/go/bin/gau /usr/bin/gau && \
    go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest && \
    ln -sf /root/go/bin/nuclei /usr/bin/nuclei

# --- Instalación de DOMChecker ---
WORKDIR /opt
RUN git clone https://github.com/Maalfer/domchecker.git && \
    cd domchecker && \
    pip install --no-cache-dir -r requirements.txt --break-system-packages || true

RUN echo '#!/bin/bash\npython3 /opt/domchecker/domchecker.py "$@"' > /usr/local/bin/domchecker && \
    chmod +x /usr/local/bin/domchecker

RUN apt-get autoremove -y && apt-get clean

WORKDIR /home
CMD ["/bin/zsh", "-i", "-c", "source ~/.zshrc && exec /bin/zsh"]
