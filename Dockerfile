FROM kalilinux/kali-rolling:latest

RUN apt update && apt upgrade -y && \
    apt install -y curl git nmap net-tools golang nano wget sqlmap iputils-ping zsh subfinder wpscan whois dirb ffuf seclists python3 python3-pip trufflehog

RUN echo 'export PATH=$PATH:/root/.local/bin' >> ~/.zshrc && \
    echo 'export GOPATH=$HOME/go' >> ~/.zshrc && \
    echo 'export PATH=$PATH:$GOPATH/bin' >> ~/.zshrc

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

WORKDIR /opt

RUN git clone https://github.com/s0md3v/XSStrike.git 

WORKDIR /opt/XSStrike 

RUN pip install -r requirements.txt --break-system-packages && chmod +x xsstrike.py && mv xsstrike.py xsstrike && mv * /usr/local/bin/

WORKDIR /opt

RUN rm -r /opt/XSStrike

WORKDIR /home

RUN apt autoremove -y

CMD ["/bin/zsh", "-i", "-c", "source ~/.zshrc && exec /bin/zsh"]
