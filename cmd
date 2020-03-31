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

sudo python3 noobchain/main.py 

sudo python3 noobchain/main.py -p 2000 -bootstrap False -ip_bootstrap 83.212.77.3

sudo python3 noobchain/main.py -p 3000 -bootstrap False -ip_bootstrap 83.212.77.3

sudo python3 noobchain/main.py -p 4000 -bootstrap False -ip_bootstrap 83.212.77.3

sudo python3 noobchain/main.py -p 5000 -bootstrap False -ip_bootstrap 83.212.77.3

------------------------------------------------------------
######## To setup NAT configuration ########
sudo apt-get install ufw

sudo ufw allow from fe80::cc00:13ff:fea1:9544/64 (n1)
sudo ufw allow from fe80::cc00:13ff:fedf:7972/64 (n2)
sudo ufw allow from fe80::cc00:13ff:feca:68df/64 (n3)
sudo ufw allow from fe80::cc00:13ff:fe9e:e58d/64 (n4)
sudo ufw allow from fe80::cc00:13ff:fe54:53bb/64 (n5)

sudo ufw allow 1000 

ip6tables -t nat -A PREROUTING -p tcp --dport 2000 -j DNAT --to-destination cc00:13ff:fedf:7972::22

$
sudo nano /etc/sysctl.conf
net.ipv4.ip_forward = 1
net.ipv6.conf.all.forwarding = 1

ip6tables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

ip6tables -t nat -A PREROUTING -p tcp --dport 2000 -j DNAT --to-destination [2001:648:2ffe:501:cc00:13ff:fe91:1b0f]:22


ip6tables -t nat -A POSTROUTING -o sixxs -s fe80::/64 -j MASQUERADE

ip6tables -t nat -A PREROUTING -i sixxs -p tcp --dport 2000 -j DNAT --to-destination [fe80::cc00:13ff:fe91:1b0f]:22


ip6tables -t nat -A POSTROUTING -o sixxs -s 2001::/64 -j MASQUERADE

ip6tables -t nat -A PREROUTING -i sixxs -p tcp --dport 2000 -j DNAT --to-destination [2001:648:2ffe:501:cc00:13ff:fe91:1b0f]:22

ping6 -c3 -I eth0 2001:648:2ffe:501:cc00:13ff:fe91:1b0f

ip6tables -L -t nat

sudo ufw enable -> NOP

ip6tables -t nat -A POSTROUTING -o eth0 -s 2001::/64 -j MASQUERADE

ip6tables -t nat -A PREROUTING -i eth0 -p tcp --dport 2000 -j DNAT --to-destination [2001:648:2ffe:501:cc00:13ff:fe91:1b0f]:22

route -6 -n
(sta alla vms)
sudo route -6 add default gw 2001:648:2ffe:501:cc00:13ff:fe6d:176e

https://okeanos.grnet.gr/support/user-guide/cyclades-how-can-i-access-all-my-vms-using-one-public-ip-nat/



$$$$$$$
vm1
sudo python3 noobchain/main.py -ip snf-12646.ok-kno.grnetcloud.net -p 1000 -ip_bootstrap snf-12646.ok-kno.grnetcloud.net -nodes 5 -cap 2 - dif 4
vm2
sudo python3 noobchain/main.py -ip snf-12647.ok-kno.grnetcloud.net -p 2000 -bootstrap False -ip_bootstrap snf-12646.ok-kno.grnetcloud.net  -nodes 5 -cap 2 - dif 4
vm3
sudo python3 noobchain/main.py -ip snf-12648.ok-kno.grnetcloud.net -p 3000 -bootstrap False -ip_bootstrap snf-12646.ok-kno.grnetcloud.net  -nodes 5 -cap 2 - dif 4
vm4
sudo python3 noobchain/main.py -ip snf-12649.ok-kno.grnetcloud.net -p 4000 -bootstrap False -ip_bootstrap snf-12646.ok-kno.grnetcloud.net  -nodes 5 -cap 2 - dif 4
vm5
sudo python3 noobchain/main.py -ip snf-12650.ok-kno.grnetcloud.net -p 5000 -bootstrap False -ip_bootstrap snf-12646.ok-kno.grnetcloud.net  -nodes 5 -cap 2 - dif 4





