# Installing Java for AirSense

AirSense requires Java 11 or higher to run Apache Spark for data processing.

## Why Java is Needed

Apache Spark (used for big data processing) runs on the Java Virtual Machine (JVM). Without Java, you cannot:
- Process raw data files
- Run the data pipeline
- Use Spark-based analytics

You CAN still run:
- API server (if processed data already exists)
- Dashboard (if processed data already exists)

## Installation Options

### Option 1: Eclipse Temurin (Recommended)

1. **Download:**
   - Visit: https://adoptium.net/
   - Select: Java 11 (LTS) or Java 17 (LTS)
   - Choose: Windows x64 installer (.msi)

2. **Install:**
   - Run the downloaded .msi file
   - ✅ Check "Set JAVA_HOME variable"
   - ✅ Check "Add to PATH"
   - Click Install

3. **Verify:**
   ```cmd
   java -version
   ```
   Should show: `openjdk version "11.x.x"` or `"17.x.x"`

### Option 2: Oracle JDK

1. **Download:**
   - Visit: https://www.oracle.com/java/technologies/downloads/
   - Select: Java 11 or Java 17
   - Download Windows installer

2. **Install:**
   - Run installer
   - Follow installation wizard

3. **Set Environment Variables:**
   - Open System Properties → Environment Variables
   - Add `JAVA_HOME`: `C:\Program Files\Java\jdk-11.x.x`
   - Add to `PATH`: `%JAVA_HOME%\bin`

4. **Verify:**
   ```cmd
   java -version
   ```

### Option 3: Using Chocolatey (Package Manager)

If you have Chocolatey installed:

```powershell
# Install Chocolatey first (if not installed)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install Java
choco install openjdk11
```

### Option 4: Using Scoop (Package Manager)

If you have Scoop installed:

```powershell
scoop bucket add java
scoop install openjdk11
```

## After Installation

1. **Restart your terminal/PowerShell**

2. **Verify Java is working:**
   ```cmd
   java -version
   javac -version
   echo %JAVA_HOME%
   ```

3. **Run AirSense:**
   ```cmd
   # Full system with data processing
   run_system.bat
   
   # Or use Python directly
   .venv\Scripts\python.exe src\main.py all
   ```

## Troubleshooting

### Java command not found

**Problem:** `java : The term 'java' is not recognized`

**Solution:**
1. Check if Java is installed: `"C:\Program Files\Java\jdk-11.x.x\bin\java.exe" -version`
2. If yes, add to PATH:
   - System Properties → Environment Variables
   - Edit PATH variable
   - Add: `C:\Program Files\Java\jdk-11.x.x\bin`
3. Restart terminal

### JAVA_HOME not set

**Problem:** Spark says `JAVA_HOME is not set`

**Solution:**
1. Find Java installation: `where java` or check `C:\Program Files\Java\`
2. Set JAVA_HOME:
   ```cmd
   setx JAVA_HOME "C:\Program Files\Java\jdk-11.x.x"
   ```
3. Restart terminal

### Wrong Java version

**Problem:** You have Java 8 or older

**Solution:**
1. Uninstall old Java (optional)
2. Install Java 11+ using steps above
3. Verify: `java -version` shows 11 or higher

## Quick Start After Java Installation

```cmd
# 1. Verify Java
java -version

# 2. Run the system
run_system.bat

# Or step by step:
# Process data
.venv\Scripts\python.exe src\main.py pipeline

# Start API
.venv\Scripts\python.exe src\main.py api

# Start Dashboard (in another terminal)
.venv\Scripts\python.exe src\main.py dashboard
```

## Alternative: Use Docker (No Java Required)

If you don't want to install Java, use Docker:

```cmd
# Install Docker Desktop from https://www.docker.com/products/docker-desktop

# Build and run
docker-compose up -d

# Access services
# API: http://localhost:8000
# Dashboard: http://localhost:8501
```

Docker includes Java inside the container, so you don't need it on your system.

## Need Help?

- Java installation issues: https://adoptium.net/support/
- AirSense issues: Check TROUBLESHOOTING.md
- Spark issues: Check logs in `logs/` directory
