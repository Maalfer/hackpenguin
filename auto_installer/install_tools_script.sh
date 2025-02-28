# Actualizar el sistema
echo "Actualizando el sistema..."
apt update && apt upgrade -y

# Instalar dependencias necesarias
echo "Instalando dependencias..."
apt install -y curl git nmap net-tools golang subfinder sqlmap nuclei sqlmap curl

echo 'export GOPATH=$HOME/go' >> ~/.bashrc
echo 'export PATH=$PATH:$GOPATH/bin' >> ~/.bashrc

mkdir /opt/nuclei-templates

git clone https://github.com/coffinxp/nuclei-templates.git

mv nuclei-templates/* /opt/nuclei-templates

rm -r nuclei-templates

go install github.com/projectdiscovery/httpx/cmd/httpx@latest && \
go install github.com/projectdiscovery/katana/cmd/katana@latest && \
go install github.com/tomnomnom/waybackurls@latest && \
go install -v github.com/projectdiscovery/urlfinder/cmd/urlfinder@latest && \
go install -v github.com/tomnomnom/anew@latest && \
go install github.com/lc/gau/v2/cmd/gau@latest

echo 'subfinder -d example.com -silent | gau | katana -silent | waybackurls | grep -Ei "confidential|secret|bak|api|key|auth|token|password|config|credential"' >> /opt/bug_bounty_dorks.txt
echo 'subfinder -d example.com -silent | gau --subs | grep -Ei "(\?|&)(q|search|id|name|query|redirect|url)=[^&]*" | httpx -silent -status-code -content-type | grep "200" | sort -u' >> /opt/bug_bounty_dorks.txt
echo 'katana -u https://example.com/ -d 5 -jc | grep "\.js$" | tee alljs.txt'  >> /opt/finding_aws_buckets.txt
echo 'cat alljs.txt | xargs -I {} curl -s {} | grep -oE "http[s]?://[^"]*.s3.amaxonaws.com" | sort -u' >> /opt/finding_aws_buckets.txt

apt autoremove -y

source ~/.bashrc
