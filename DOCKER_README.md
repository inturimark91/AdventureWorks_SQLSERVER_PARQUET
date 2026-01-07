# SQL Server 2022 Docker Setup

This guide covers setting up SQL Server 2022 in Docker and restoring the AdventureWorksDW2022 database.

## Prerequisites

- Docker installed and running
- Azure Data Studio (optional, for GUI access)

## Docker Compose Configuration

The `docker-compose.yml` file defines the SQL Server container:

```yaml
version: '3.8'

services:
  sqlserver:
    image: mcr.microsoft.com/mssql/server:2022-latest
    container_name: sqlserver
    environment:
      ACCEPT_EULA: "Y"
      MSSQL_SA_PASSWORD: "YourStrong!Passw0rd"
    ports:
      - "1433:1433"
    volumes:
      - sqlserverdata:/var/opt/mssql

volumes:
  sqlserverdata:
```

## Commands

### 1. Start SQL Server Container

```bash
docker-compose up -d
```

### 2. Check Running Containers

```bash
docker ps
```

### 3. Get Container ID

```bash
docker ps -q -f name=sqlserver
```

### 4. Get SQL Server Container IP Address

```bash
docker inspect -f "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}" sqlserver
```

### 5. Check SQL Server Logs

```bash
docker logs sqlserver --tail 30
```

### 6. Test Port Connectivity (PowerShell)

```powershell
Test-NetConnection -ComputerName localhost -Port 1433
```

## Restoring AdventureWorksDW2022 Database

### 1. Create Backup Directory in Container

```bash
docker exec sqlserver mkdir -p /var/opt/mssql/backup
```

### 2. Copy Backup File to Container

```bash
docker cp "AdventureWorksDW2022.bak" sqlserver:/var/opt/mssql/backup/
```

### 3. Get Logical File Names from Backup

```bash
docker exec sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "YourStrong!Passw0rd" -C -Q "RESTORE FILELISTONLY FROM DISK = '/var/opt/mssql/backup/AdventureWorksDW2022.bak'"
```

### 4. Restore the Database

```bash
docker exec sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "YourStrong!Passw0rd" -C -Q "RESTORE DATABASE AdventureWorksDW2022 FROM DISK = '/var/opt/mssql/backup/AdventureWorksDW2022.bak' WITH MOVE 'AdventureWorksDW2022' TO '/var/opt/mssql/data/AdventureWorksDW2022.mdf', MOVE 'AdventureWorksDW2022_log' TO '/var/opt/mssql/data/AdventureWorksDW2022_log.ldf'"
```

## Connecting to SQL Server

### From Azure Data Studio

- **Server**: `localhost,1433` or `127.0.0.1,1433`
- **Authentication type**: SQL Login
- **User name**: `sa`
- **Password**: `YourStrong!Passw0rd`
- **Database**: `AdventureWorksDW2022`
- **Trust server certificate**: ✅ Enabled (Important!)

### From Terminal (inside container)

```bash
docker exec -it sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "YourStrong!Passw0rd" -C
```

## Stopping the Container

```bash
docker-compose down
```

## Notes

- The `-C` flag in sqlcmd commands is used to trust the server certificate.
- Make sure to enable "Trust server certificate" in Azure Data Studio connection settings.
- The backup file version must be compatible with the SQL Server version running in the container (SQL Server 2022 supports backups from 2022 and earlier versions).
