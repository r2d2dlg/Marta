@echo off
setlocal

:: Set Java home to JDK 17
set JAVA_HOME=F:\Java17

:: Set PATH to prioritize Java 17
set PATH=%JAVA_HOME%\bin;%PATH%

:: Set Gradle user home to F:\.gradle
set GRADLE_USER_HOME=F:\.gradle

:: Verify Java version
echo Using Java from: %JAVA_HOME%
java -version

:: Run Gradle with the specified arguments
call gradlew %*

endlocal
