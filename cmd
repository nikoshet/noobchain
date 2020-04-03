# To run one docker node instance
docker build -t noobcash:latest .

sudo docker run -p 1000:1000 noobcash:latest 

------------------------------------------------------------
######## To run 5 node instances in docker containers ########
docker-compose build
docker-compose up

------------------------------------------------------------
######## Commands for VMs ########
ssh user@snf-12646.ok-kno.grnetcloud.net

sudo apt-get update && sudo apt-get upgrade
sudo apt-get install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa 
sudo apt-get update
sudo apt-get install python3.8
ls /usr/bin/python*
sudo rm /usr/bin/python3
sudo ln -s /usr/bin/python3.8 /usr/bin/python3
python3 --version

sudo apt install python3.8-dev python3.8-distutils python3.8-gdbm
sudo apt install python3-pip
sudo apt remove python3-pip
sudo python3.8 -m easy_install pip
pip3 --version

----
scp -r noobchain/ ssh user@snf-12646.ok-kno.grnetcloud.net:~/
cd noobchain
sudo pip install --ignore-installed -r requirements.txt

$$$$$$$
vm1
sudo python3 noobchain/main.py -ip snf-12646.ok-kno.grnetcloud.net -p 1000 -ip_bootstrap snf-12646.ok-kno.grnetcloud.net -nodes 5 -cap 5 - dif 4
vm2
sudo python3 noobchain/main.py -ip snf-12647.ok-kno.grnetcloud.net -p 2000 -bootstrap False -ip_bootstrap snf-12646.ok-kno.grnetcloud.net -nodes 5 -cap 5 -dif 4
vm3
sudo python3 noobchain/main.py -ip snf-12648.ok-kno.grnetcloud.net -p 3000 -bootstrap False -ip_bootstrap snf-12646.ok-kno.grnetcloud.net -nodes 5 -cap 5 -dif 4
vm4
sudo python3 noobchain/main.py -ip snf-12649.ok-kno.grnetcloud.net -p 4000 -bootstrap False -ip_bootstrap snf-12646.ok-kno.grnetcloud.net -nodes 5 -cap 5 -dif 4
vm5
sudo python3 noobchain/main.py -ip snf-12650.ok-kno.grnetcloud.net -p 5000 -bootstrap False -ip_bootstrap snf-12646.ok-kno.grnetcloud.net -nodes 5 -cap 5 -dif 4





