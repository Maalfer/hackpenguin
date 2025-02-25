FROM kalilinux/kali-rolling:latest

RUN apt update && apt upgrade -y && \
    apt install -y curl git nmap net-tools golang sqlmap iputils-ping zsh

RUN echo 'export GOPATH=$HOME/go' >> ~/.zshrc && \
    echo 'export PATH=$PATH:$GOPATH/bin' >> ~/.zshrc

RUN mkdir /opt/nuclei-templates

RUN git clone https://github.com/coffinxp/nuclei-templates.git && \
    mv nuclei-templates/* /opt/nuclei-templates && \
    rm -r nuclei-templates

RUN go install github.com/projectdiscovery/httpx/cmd/httpx@latest && \
    go install github.com/projectdiscovery/katana/cmd/katana@latest && \
    go install github.com/tomnomnom/waybackurls@latest && \
    go install -v github.com/projectdiscovery/urlfinder/cmd/urlfinder@latest && \
    go install -v github.com/tomnomnom/anew@latest && \
    go install github.com/lc/gau/v2/cmd/gau@latest

RUN apt autoremove -y

CMD ["/bin/zsh", "-i", "-c", "source ~/.zshrc && exec zsh"]
