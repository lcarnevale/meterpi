sudo apt-get update && sudo apt-get upgrade

echo("Installing Python dependencies ...")
sudo apt install python3-pip python3-venv -y

mkdir tmp
cd tmp
wget http://ftp.debian.org/debian/pool/main/libs/libseccomp/libseccomp2_2.5.1-1_armhf.deb
sudo dpkg -i libseccomp2_2.5.1-1_armhf.deb

echo("Installing Docker dependency ...")
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker Pi