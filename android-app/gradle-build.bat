@echo off
setlocal

:: Set Java home to JDK 17
set JAVA_HOME=F:\Java17
set PATH=%JAVA_HOME%\bin;%PATH%

:: Set Gradle user home to F:\.gradle
set GRADLE_USER_HOME=F:\.gradle

:: Run Gradle with the specified arguments
call gradlew %*

endlocal
