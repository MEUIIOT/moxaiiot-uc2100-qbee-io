# mqtt-aws-iotcore

1) Register Device to AWS IoT Core 
![image](https://user-images.githubusercontent.com/22453359/175786090-38a78863-cb31-4d4e-93ba-e7243fda3808.png)

2) Enter Device/Thing Name 
![image](https://user-images.githubusercontent.com/22453359/175786159-08702ec9-3a8e-4c0f-b25d-cbb596868384.png)

3) Configure Device Certificates
![image](https://user-images.githubusercontent.com/22453359/175786217-d3417a0a-30f4-4a22-87e3-6fbf61ca9962.png)

4) Create Policy 
![image](https://user-images.githubusercontent.com/22453359/175786255-2ec39212-df88-4530-a9e0-78e6d91d42e6.png)

5) Provide Policy Name and Selct JSON Botton Right
![image](https://user-images.githubusercontent.com/22453359/175786519-6535154f-ca3b-4ba4-b853-a63a4d5d2a7c.png)

Select JSON and replace with follwoing content
```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "iot:*",
      "Resource": "*"
    }
  ]
}
```

See more details here 
https://docs.aws.amazon.com/iot/latest/developerguide/iot-policy-actions.html?icmpid=docs_iot_hp_secure

6) Create thing
![image](https://user-images.githubusercontent.com/22453359/175786607-f20eadf9-131a-44bd-b833-3033fca38c54.png)

7) Download all certificates and select Done
![image](https://user-images.githubusercontent.com/22453359/175786694-7b31da9f-329a-431d-a70b-47964aebf081.png)

8) Copy Root CA, X509 and Private key under /certs folder

## ISSUE 
```
Issue Paho-MQTT x.509 device certificate

context.load_cert_chain(certfile, keyfile)
FileNotFoundError: [Errno 2] No such file or directory

device-certificate.pem.crt (downloaded from AWS)

Fix:

Add .cert before .pem.crt see example in resources/config-external-broker.json

 "certificates": {
                "trusted_root_ca": "certs/AmazonRootCA1.pem",
                "x509_certificate": "certs/device-certificate.cert.pem.crt",
                "private_key": "certs/device-certificate.private.pem.key"
        },
```

9) Test MQTT messages on AWS IoT Core 
![image](https://user-images.githubusercontent.com/22453359/176219318-fe958db1-878e-4247-94a2-554d1f918a8f.png)
