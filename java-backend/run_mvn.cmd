@echo off
set "JAVA_HOME=C:\Program Files\Java\jdk-23"
set "MAVEN_HOME=%~dp0apache-maven-3.9.6"
set "PATH=%JAVA_HOME%\bin;%MAVEN_HOME%\bin;%PATH%"
echo Starting Spring Boot via Maven...
call mvn spring-boot:run
