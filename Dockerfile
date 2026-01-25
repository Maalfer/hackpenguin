FROM kalilinux/kali-rolling:latest

# Instalación de dependencias básicas
RUN apt update && apt upgrade -y && \
    apt install -y curl git nmap net-tools golang nano wget sqlmap iputils-ping zsh subfinder wpscan whois dirb ffuf seclists python3 python3-pip trufflehog python3-aiohttp jq

# Configuración de PATH para ZSH
RUN echo 'export PATH=$PATH:/root/.local/bin' >> ~/.zshrc && \
    echo 'export GOPATH=$HOME/go' >> ~/.zshrc && \
    echo 'export PATH=$PATH:$GOPATH/bin' >> ~/.zshrc

# Instalación de herramientas en Go
RUN go install github.com/projectdiscovery/httpx/cmd/httpx@latest && \
    ln -s /root/go/bin/httpx /usr/bin/httpx && \
    go install github.com/projectdiscovery/katana/cmd/katana@latest && \
    ln -s /root/go/bin/katana /usr/bin/katana && \
    go install github.com/tomnomnom/waybackurls@latest && \
    ln -s /root/go/bin/waybackurls /usr/bin/waybackurls && \
    go install github.com/tomnomnom/anew@latest && \
    ln -s /root/go/bin/anew /usr/bin/anew && \
    go install github.com/lc/gau/v2/cmd/gau@latest && \
    ln -s /root/go/bin/gau /usr/bin/gau && \
    go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest && \
    ln -s /root/go/bin/nuclei /usr/bin/nuclei

# --- Instalación de XSStrike ---
WORKDIR /opt
RUN git clone https://github.com/s0md3v/XSStrike.git
WORKDIR /opt/XSStrike
RUN pip install -r requirements.txt --break-system-packages && \
    chmod +x xsstrike.py && \
    ln -s /opt/XSStrike/xsstrike.py /usr/local/bin/xsstrike

# --- Instalación de DOMChecker ---
WORKDIR /opt
RUN git clone https://github.com/Maalfer/domchecker.git
WORKDIR /opt/domchecker
RUN sed -i '1i #!/usr/bin/env python3' domchecker.py && \
    chmod +x domchecker.py && \
    ln -s /opt/domchecker/domchecker.py /usr/local/bin/domchecker

# --- Instalación de PinguAsset ---
WORKDIR /opt
RUN git clone https://github.com/Maalfer/PinguAsset.git
WORKDIR /opt/PinguAsset
RUN chmod +x pinguasset.sh && \
    sed -i 's|PATTERNS_FILE="patterns.json"|PATTERNS_FILE="/usr/local/bin/patterns.json"|g' pinguasset.sh && \
    mv patterns.json /usr/local/bin/ && \
    ln -s /opt/PinguAsset/pinguasset.sh /usr/local/bin/PinguAsset

RUN apt autoremove -y && apt clean

WORKDIR /home
CMD ["/bin/zsh", "-i", "-c", "source ~/.zshrc && exec /bin/zsh"]
