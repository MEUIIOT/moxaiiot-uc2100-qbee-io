
# Industrial IoT on a shoestring -Solution Architecture (Python)

![](media/solution-architecture-v3.png)

# Getting Started
-	Apply now and win Free IIoT shoestring starterkit: https://pages.moxa.com/eu-uc-2100-giveaway-EN.html?utm_medium=website&utm_source=github&utm_campaign=2022-05-MEU-EN-UC-2100-Campaign

-	Application Note: https://pages.moxa.com/eu-uc-2100-application-note-gated-EN.html?utm_medium=website&utm_source=github&utm_campaign=2022-05-MEU-EN-UC-2100-Campaign

-	Webinar Recording: https://vimeo.com/713744866

- Moxa and Qbee IIoT Partner Profile: https://moxa-europe.com/partner/qbee/

# How to deploy software from Git repository to Moxa UC-2100 using CI/CD pipeline

## Prequisites: 
 - UC-2100 or any other UC series embedded computer  
 - Device is registered and connected to Qbee Account
 - Must have Github account

### 1) Create qbee account
How to create see here: https://www.app.qbee.io/#/register?regtype=trial

### 2) Register UC-2100 on qbee account
![image](https://user-images.githubusercontent.com/22453359/175902827-19d97195-c668-4e07-91a2-e117af18a3a8.png)

### 3) Generate bootstrap key
![image](https://user-images.githubusercontent.com/22453359/175904490-50dc9f01-dbd7-4251-9c41-f1d8eb1f7216.png)

### 4) Install qbee agent on UC-2100 
How to install see here: https://qbee.io/docs/qbee-install-agent.html

Login into Moxa UC-2100 computer via serial or LAN interface. Make sure UC-2100 has internet access. 
You can check by ping 8.8.8.8 or ping google.com 

sudo wget https://cdn.qbee.io/software/qbee-agent/qbee-agent_1.2.1_armhf.deb
sudo dpkg -i qbee-agent_1.2.1_armhf.deb
sudo /opt/qbee/bin/qbee-bootstrap -k ENTER-BOOTSTRAP-KEY-HERE

### 5) Confirm status of the UC-2100 
![image](https://user-images.githubusercontent.com/22453359/175909105-9ff7a425-ad16-410e-b231-2438fc72f82c.png)

### 6) Create a new fork repository
https://github.com/MEUIIOT/moxaiiot-uc2100-qbee-io

A fork is a copy of a repository. Forking a repository allows you to freely experiment with changes without affecting the original project.
How to fork see here: https://docs.github.com/en/get-started/quickstart/fork-a-repo

### 7) Connect Github to your Qbee account
Copy the Group ID into notepad

![image](https://user-images.githubusercontent.com/22453359/175912690-5a6279e8-bb4e-470f-ba3d-9c107e81ba9f.png)

Configure secrets on Github forked repository 
![image](https://user-images.githubusercontent.com/22453359/175932954-8d17a5dd-1ba8-40dc-a5a7-7cd7196171e9.png)


### 8) Trigger CI/CD pipeline to deploy soruce code onto Moxa UC-2100

The pipleline is configured to trigger on push (E.g: when you edit the code commit the change, the chnage will be deploye dto the device automaically)

You can check the triiger under Actions 
![image](https://user-images.githubusercontent.com/22453359/175932705-6aae5005-f8c9-43f5-9bf5-363b702d15b9.png)


A successfull build shows following output
![image](https://user-images.githubusercontent.com/22453359/176025223-07a79bad-1547-4fa6-ad04-90c485b11ba0.png)

### 9) Verify app running successfully on UC-2100 

You can acesss the device via SSH on your Qbee account. 
![image](https://user-images.githubusercontent.com/22453359/176029299-9197970f-db4f-4bc3-a6f4-48f8244764a3.png)

Verify status of Modbus Service 
![image](https://user-images.githubusercontent.com/22453359/176029993-e408a3cc-d129-4b98-b741-766163d7dac9.png)

Verify status of Plot Server
![image](https://user-images.githubusercontent.com/22453359/176029916-f1de0e0a-5a0d-4277-82df-98749d45abbe.png)


### 10) Access plot Server listening on port 8080 

Both cpuLoading and pushButton is real sensor data being published via ModbusTCP protocol to Internal MQTT Broker

Modbus configuration has been used in this demo found here:
https://github.com/abadar05/moxaiiot-uc2100-qbee-io/blob/main/device-app/modbus/resources/config-modbus-master.json

Modbus template has been used in this demo found here:
https://github.com/abadar05/moxaiiot-uc2100-qbee-io/blob/main/device-app/modbus/resources/modbus_templates/ioLogik-demokit-right.json

Plot Server configurtion found here
https://github.com/abadar05/moxaiiot-uc2100-qbee-io/blob/main/cloud-app/local-visualization/resources/transformation_config.json

![image](https://user-images.githubusercontent.com/22453359/176030378-dba99bcd-77f6-4c8b-9c10-4997175abc77.png)







