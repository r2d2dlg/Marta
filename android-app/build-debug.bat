@echo off
setlocal

:: Set Java home to JDK 17
set JAVA_HOME=F:\Java17
set PATH=%JAVA_HOME%\bin;%PATH%

:: Set Gradle user home to F:\.gradle
set GRADLE_USER_HOME=F:\.gradle

:: Disable Gradle daemon and parallel execution
set GRADLE_OPTS=-Dorg.gradle.daemon=false -Dorg.gradle.parallel=false

echo Using Java from: %JAVA_HOME%
java -version

echo.
echo Building Android app...
call gradlew assembleDebug --no-daemon --stacktrace --info

endlocal
