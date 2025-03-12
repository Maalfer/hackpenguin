# Actualizar el sistema
echo "Actualizando el sistema..."
apt update && apt upgrade -y

snap install enum4linux
snap install john-the-ripper

# Instalar dependencias necesarias
echo "Instalando dependencias..."
apt install -y curl git nmap net-tools golang sqlmap curl flatpak gobuster docker.io hydra wget wfuzz john wireshark arp-scan nano python3-requests smbclient smbmap python3-flask dirb

wget https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt

mv rockyou.txt /usr/share/

systemctl start docker && systemctl enable docker

docker pull wpscanteam/wpscan
docker pull metasploitframework/metasploit-framework

echo "alias wpscan='sudo docker run -it --rm wpscanteam/wpscan'" >> ~/.bashrc
echo "alias msfconsole='sudo docker run -it --network=host --rm metasploitframework/metasploit-framework'" >> ~/.bashrc

flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo

echo 'export GOPATH=$HOME/go' >> ~/.bashrc
echo 'export PATH=$PATH:$GOPATH/bin' >> ~/.bashrc

mkdir /opt/nuclei-templates

git clone https://github.com/coffinxp/nuclei-templates.git

mv nuclei-templates/* /opt/nuclei-templates

rm -r nuclei-templates

git clone https://github.com/danielhidalgo2/JSEXPOSURES.git /opt/JSEXPOSURES
mv /opt/JSEXPOSURES/jsexposures.py /opt/jsexposures.py
rm -rf /opt/JSEXPOSURES

go install github.com/projectdiscovery/httpx/cmd/httpx@latest && \
go install github.com/projectdiscovery/katana/cmd/katana@latest && \
go install github.com/tomnomnom/waybackurls@latest && \
go install -v github.com/projectdiscovery/urlfinder/cmd/urlfinder@latest && \
go install -v github.com/tomnomnom/anew@latest && \
go install github.com/lc/gau/v2/cmd/gau@latest && \
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest && \
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

wget -q https://packages.mozilla.org/apt/repo-signing-key.gpg -O- | tee /etc/apt/keyrings/packages.mozilla.org.asc > /dev/null

echo "deb [signed-by=/etc/apt/keyrings/packages.mozilla.org.asc] https://packages.mozilla.org/apt mozilla main" | tee -a /etc/apt/sources.list.d/mozilla.list > /dev/null

echo '
Package: *
Pin: origin packages.mozilla.org
Pin-Priority: 1000
' | tee /etc/apt/preferences.d/mozilla

snap remove firefox

apt update && apt install firefox


echo 'subfinder -d example.com -silent | gau | katana -silent | waybackurls | grep -Ei "confidential|secret|bak|api|key|auth|token|password|config|credential"' >> /opt/bug_bounty_dorks.txt
echo 'subfinder -d example.com -silent | gau --subs | grep -Ei "(\?|&)(q|search|id|name|query|redirect|url)=[^&]*" | httpx -silent -status-code -content-type | grep "200" | sort -u' >> /opt/bug_bounty_dorks.txt
echo 'katana -u https://example.com/ -d 5 -jc | grep "\.js$" | tee alljs.txt'  >> /opt/finding_aws_buckets.txt
echo 'cat alljs.txt | xargs -I {} curl -s {} | grep -oE "http[s]?://[^"]*.s3.amaxonaws.com" | sort -u' >> /opt/finding_aws_buckets.txt

apt autoremove -y

source ~/.bashrc
