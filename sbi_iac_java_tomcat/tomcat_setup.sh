#!/bin/bash

# Update system and install required packages
sudo dnf update -y
sudo dnf install -y java-17-amazon-corretto-devel.x86_64 wget tar

# Create Tomcat user
sudo useradd -r -m -U -d /opt/tomcat -s /bin/false tomcat

# Download and extract Tomcat
wget -c https://downloads.apache.org/tomcat/tomcat-9/v9.0.98/bin/apache-tomcat-9.0.98.tar.gz
sudo tar xf apache-tomcat-9.0.98.tar.gz -C /opt/tomcat
sudo ln -s /opt/tomcat/apache-tomcat-9.0.98 /opt/tomcat/updated

# Change ownership and permissions
sudo chown -R tomcat:tomcat /opt/tomcat/*
sudo chmod +x /opt/tomcat/updated/bin/*.sh

# Comment out default RemoteAddrValve restriction
sudo sed -i 's|<Valve className="org.apache.catalina.valves.RemoteAddrValve".*|<!-- <Valve className="org.apache.catalina.valves.RemoteAddrValve" -->|' \
  /opt/tomcat/updated/webapps/manager/META-INF/context.xml

# Add user roles and credentials for Tomcat users
sudo tee /opt/tomcat/updated/conf/tomcat-users.xml > /dev/null <<EOL
<tomcat-users xmlns="http://tomcat.apache.org/xml"
               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xsi:schemaLocation="http://tomcat.apache.org/xml tomcat-users.xsd"
               version="1.0">
  <role rolename="manager-gui"/>
  <role rolename="manager-script"/>
  <role rolename="manager-jmx"/>
  <role rolename="manager-status"/>
  <user username="admin" password="admin" roles="manager-gui,manager-script,manager-jmx,manager-status"/>
  <user username="deployer" password="deployer" roles="manager-script"/>
  <user username="tomcat" password="s3cret" roles="manager-gui"/>
</tomcat-users>
EOL

# Create systemd service for Tomcat
sudo tee /etc/systemd/system/tomcat.service > /dev/null <<EOL
[Unit]
Description=Apache Tomcat Web Application Container
After=network.target

[Service]
Type=forking
Environment="JAVA_HOME=/usr/lib/jvm/java-17-amazon-corretto.x86_64"
Environment="CATALINA_PID=/opt/tomcat/updated/temp/tomcat.pid"
Environment="CATALINA_HOME=/opt/tomcat/updated/"
Environment="CATALINA_BASE=/opt/tomcat/updated/"
ExecStart=/opt/tomcat/updated/bin/startup.sh
ExecStop=/opt/tomcat/updated/bin/shutdown.sh
User=tomcat
Group=tomcat
UMask=0007
RestartSec=10
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# Enable and start Tomcat service
sudo systemctl daemon-reload
sudo systemctl enable tomcat
sudo systemctl start tomcat

# Check Tomcat status
sudo systemctl status tomcat
