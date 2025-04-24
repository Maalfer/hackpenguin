FROM kalilinux/kali-rolling:latest

RUN apt update && apt upgrade -y && \
    apt install -y curl git nmap net-tools golang nano wget sqlmap iputils-ping zsh subfinder wpscan metasploit-framework impacket-scripts seclists smbclient smbmap python3 python3-pip python3-venv pipx

RUN pipx ensurepath && \
    pipx install git+https://github.com/Santitub/WPAT.git && \
    /bin/bash -c "source ~/.bashrc"

RUN echo 'export PATH=$PATH:/root/.local/bin' >> ~/.zshrc && \
    echo 'export GOPATH=$HOME/go' >> ~/.zshrc && \
    echo 'export PATH=$PATH:$GOPATH/bin' >> ~/.zshrc

RUN wget https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt -O /usr/share/rockyou.txt

RUN mkdir /opt/nuclei-templates

RUN git clone https://github.com/coffinxp/nuclei-templates.git && \
    mv nuclei-templates/* /opt/nuclei-templates && \
    rm -r nuclei-templates

RUN go install github.com/projectdiscovery/httpx/cmd/httpx@latest && \
    go install github.com/projectdiscovery/katana/cmd/katana@latest && \
    go install github.com/tomnomnom/waybackurls@latest && \
    go install -v github.com/projectdiscovery/urlfinder/cmd/urlfinder@latest && \
    go install -v github.com/tomnomnom/anew@latest && \
    go install github.com/lc/gau/v2/cmd/gau@latest && \
    go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

RUN echo 'subfinder -d example.com -silent | gau | katana -silent | waybackurls | grep -Ei "confidential|secret|bak|api|key|auth|token|password|config|credential"' >> /opt/bug_bounty_dorks.txt

RUN echo 'subfinder -d example.com -silent | gau --subs | grep -Ei "(\?|&)(q|search|id|name|query|redirect|url)=[^&]*" | httpx -silent -status-code -content-type | grep "200" | sort -u' >> /opt/bug_bounty_dorks.txt

RUN echo 'katana -u https://example.com/ -d 5 -jc | grep "\.js$" | tee alljs.txt'  >> /opt/finding_aws_buckets.txt

RUN echo 'cat alljs.txt | xargs -I {} curl -s {} | grep -oE "http[s]?://[^"]*.s3.amaxonaws.com" | sort -u' >> /opt/finding_aws_buckets.txt

WORKDIR /opt

RUN wget -O ReconSpider.zip https://academy.hackthebox.com/storage/modules/144/ReconSpider.v1.2.zip && unzip ReconSpider.zip 

RUN apt autoremove -y

CMD ["/bin/zsh", "-i", "-c", "source ~/.zshrc && exec /bin/zsh"]
