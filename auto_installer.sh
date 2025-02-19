# Actualizar el sistema
echo "Actualizando el sistema..."
apt update && apt upgrade -y

# Instalar dependencias necesarias
echo "Instalando dependencias..."
apt install -y curl git nmap net-tools golang subfinder sqlmap nuclei

echo 'export GOPATH=$HOME/go' >> ~/.zshrc
echo 'export PATH=$PATH:$GOPATH/bin' >> ~/.zshrc

mkdir /opt/nuclei-templates

git clone https://github.com/coffinxp/nuclei-templates.git

mv nuclei-templates/* /opt/nuclei-templates

rm -r nuclei-templates

go install github.com/projectdiscovery/httpx/cmd/httpx@latest
go install github.com/projectdiscovery/katana/cmd/katana@latest
go install github.com/tomnomnom/waybackurls@latest
go install -v github.com/projectdiscovery/urlfinder/cmd/urlfinder@latest
go install -v github.com/tomnomnom/anew@latest

apt autoremove -y

source ~/.zshrc
