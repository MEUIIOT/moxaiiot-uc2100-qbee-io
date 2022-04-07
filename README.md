
![image](https://user-images.githubusercontent.com/102030308/162206179-2de6b0bb-73ca-4207-8369-e31c3135a208.png)


# Getting Started
By default on UC computer Debian9 linux python is not pre-installed.

Run following commands to install python3 and package manager (pip3)

   - `sudo apt-get update`

   - `sudo apt-get install python3`

   - `sudo apt install python3-pip`

   - `sudo apt-get install mosquitto`

## Run application from source

1. Clone repository 
   - `sudo apt-get install git`
   - `git clone -b main https://github.com/MEUIIOT/moxaiiot-uc2100-qbee-io.git`
2. Install python dependencies given in the requirements.txt file 
   -  `cd moxaiiot-uc2100-qbee-io/`
   - `sudo pip3 install -r requirements.txt`
3. Adapt the device app and cloud app configuration json file to your needs
4. Run device app example modbus master via command line with sudo
    - `cd moxaiiot-uc2100-qbee-io/device-app/modbus`
    - `sudo python3 modbus.py`
5. Run cloud app example mqtt client via command line with sudo
    - `cd moxaiiot-uc2100-qbee-io/cloud-app/mqtt`
    - `sudo python3 main.py`
