docker build -t noobcash:latest .

sudo docker run -p 1000:1000 -p 2000:2000 -p 3000:3000 -p 4000:4000 -p 5000:5000 noobcash:latest 


---------
ssh user@snf-12256.ok-kno.grnetcloud.net

scp -r noobchain/ user@snf-12256.ok-kno.grnetcloud.net:~/

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


cd noobchain
sudo pip install --ignore-installed -r requirements.txt



sudo apt-get install ufw

sudo ufw allow from fe80::cc00:13ff:fea1:9544/64 (n1)
sudo ufw allow from fe80::cc00:13ff:fedf:7972/64 (n2)
sudo ufw allow from fe80::cc00:13ff:feca:68df/64 (n3)
sudo ufw allow from fe80::cc00:13ff:fe9e:e58d/64 (n4)
sudo ufw allow from fe80::cc00:13ff:fe54:53bb/64 (n5)

sudo ufw allow 1000 



sudo python3 noobchain/main_het.py 

sudo python3 noobchain/main_het.py -p 2000 -bootstrap False -ip_bootstrap 83.212.77.3

sudo python3 noobchain/main_het.py -p 3000 -bootstrap False -ip_bootstrap 83.212.77.3

sudo python3 noobchain/main_het.py -p 4000 -bootstrap False -ip_bootstrap 83.212.77.3

sudo python3 noobchain/main_het.py -p 5000 -bootstrap False -ip_bootstrap 83.212.77.3



ip6tables -t nat -A PREROUTING -p tcp --dport 2000 -j DNAT --to-destination cc00:13ff:fedf:7972::22









