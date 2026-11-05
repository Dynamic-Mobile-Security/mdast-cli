// Built inside pinned ipatool sources to use its internal SAP implementation.
package main

import (
	"bufio"
	"context"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
	"time"

	"github.com/majd/ipatool/v2/internal/sap"
	"github.com/majd/ipatool/v2/internal/sap/assets"
	"github.com/majd/ipatool/v2/internal/sap/machine"
)

type request struct {
	Operation      string `json:"op"`
	Version        uint32 `json:"version"`
	SetupURL       string `json:"setup_url"`
	CertificateURL string `json:"certificate_url"`
	HardwareID     string `json:"hardware_id"`
	Payload        []byte `json:"payload"`
	DSID           uint64 `json:"dsid"`
}

type response struct {
	OK        bool   `json:"ok"`
	Signature []byte `json:"signature,omitempty"`
	KBSync    []byte `json:"kbsync,omitempty"`
	Error     string `json:"error,omitempty"`
	Detail    string `json:"detail,omitempty"`
}

func run() error {
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Buffer(make([]byte, 4096), 1<<20)
	encoder := json.NewEncoder(os.Stdout)
	var signer sap.ActionSigner
	defer func() {
		if signer != nil {
			_ = signer.Close()
		}
	}()
	deadline := time.AfterFunc(35*time.Minute, func() { os.Exit(124) })
	defer deadline.Stop()
	for scanner.Scan() {
		var req request
		if err := json.Unmarshal(scanner.Bytes(), &req); err != nil {
			return encoder.Encode(response{Error: "invalid_request"})
		}
		switch req.Operation {
		case "init":
			if signer != nil {
				return encoder.Encode(response{Error: "already_initialized"})
			}
			hardware, err := hex.DecodeString(req.HardwareID)
			if err != nil || len(hardware) != 6 {
				return encoder.Encode(response{Error: "invalid_hardware_id"})
			}
			ctx, cancel := context.WithTimeout(context.Background(), 30*time.Minute)
			signer, err = sap.NewSigner(ctx, sap.Config{
				SetupURL: req.SetupURL, CertificateURL: req.CertificateURL,
				Version: req.Version, HardwareID: hardware,
			})
			cancel()
			if err != nil {
				return encoder.Encode(response{Error: "initialization_failed", Detail: err.Error()})
			}
			if err := encoder.Encode(response{OK: true}); err != nil {
				return err
			}
		case "kbsync":
			hardware, err := hex.DecodeString(req.HardwareID)
			if err != nil || len(hardware) != 6 || req.DSID == 0 {
				return encoder.Encode(response{Error: "invalid_kbsync_identity"})
			}
			ctx, cancel := context.WithTimeout(context.Background(), 2*time.Minute)
			bundle, err := assets.Load(ctx)
			var data []byte
			if err == nil {
				data, err = machine.GenerateKBSync(ctx, bundle, hardware, req.DSID)
			}
			cancel()
			if err != nil || len(data) == 0 || len(data) > 65536 {
				return encoder.Encode(response{Error: "kbsync_failed"})
			}
			if err := encoder.Encode(response{OK: true, KBSync: data}); err != nil {
				return err
			}
		case "sign":
			if signer == nil || len(req.Payload) == 0 {
				return encoder.Encode(response{Error: "invalid_sign_state"})
			}
			signature, err := signer.Sign(req.Payload)
			if err != nil {
				return encoder.Encode(response{Error: "signing_failed"})
			}
			if err := encoder.Encode(response{OK: true, Signature: signature}); err != nil {
				return err
			}
		case "close":
			return nil
		default:
			return encoder.Encode(response{Error: "unknown_operation"})
		}
	}
	return scanner.Err()
}

func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, "SAP helper protocol failed")
		os.Exit(1)
	}
}
