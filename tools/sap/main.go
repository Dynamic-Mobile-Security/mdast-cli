// Built inside pinned ipatool sources to use its internal SAP implementation.
package main

import (
	"bufio"
	"context"
	"encoding/base64"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"os"
	"regexp"
	"strings"
	"time"

	"github.com/majd/ipatool/v2/internal/sap"
	"github.com/majd/ipatool/v2/internal/sap/assets"
	"github.com/majd/ipatool/v2/internal/sap/machine"
	"github.com/majd/ipatool/v2/internal/storeauth"
)

type request struct {
	State          []byte            `json:"state"`
	Endpoint       string            `json:"endpoint"`
	Challenge      string            `json:"challenge"`
	Headers        map[string]string `json:"headers"`
	Operation      string            `json:"op"`
	Version        uint32            `json:"version"`
	SetupURL       string            `json:"setup_url"`
	CertificateURL string            `json:"certificate_url"`
	HardwareID     string            `json:"hardware_id"`
	Payload        []byte            `json:"payload"`
	DSID           uint64            `json:"dsid"`
}

type response struct {
	State     []byte            `json:"state,omitempty"`
	Headers   map[string]string `json:"headers,omitempty"`
	OK        bool              `json:"ok"`
	Signature []byte            `json:"signature,omitempty"`
	KBSync    []byte            `json:"kbsync,omitempty"`
	Error     string            `json:"error,omitempty"`
	Detail    string            `json:"detail,omitempty"`
}

func validAMDEndpoint(endpoint string) bool {
	parsed, err := url.Parse(endpoint)
	if err != nil || parsed.Scheme != "https" || parsed.User != nil || strings.Contains(endpoint, "#") || parsed.RawPath != "" || (parsed.Port() != "" && parsed.Port() != "443") {
		return false
	}
	host := strings.ToLower(parsed.Hostname())
	if host == "auth.itunes.apple.com" && parsed.Path == "/auth/v1/native" {
		return true
	}
	query, err := url.ParseQuery(parsed.RawQuery)
	if err != nil || len(query) != 1 || len(query["guid"]) != 1 || query.Get("guid") == "" {
		return false
	}
	if host == "downloaddispatch.itunes.apple.com" {
		switch parsed.Path {
		case "/WebObjects/DownloadDispatch.woa/wa/ent/download", "/WebObjects/DownloadDispatch.woa/wa/redownloadProduct", "/WebObjects/DownloadDispatch.woa/wa/updateProduct":
			return true
		}
	}
	if regexp.MustCompile(`^(p[0-9]+-)?buy\.itunes\.apple\.com$`).MatchString(host) {
		return parsed.Path == "/WebObjects/MZFinance.woa/wa/volumeStoreDownloadProduct"
	}
	return false
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
		case "anisette", "store_provision", "store_amd":
			hardware, err := hex.DecodeString(req.HardwareID)
			if err != nil || len(hardware) != 6 || len(req.State) > 512*1024 {
				return encoder.Encode(response{Error: "invalid_store_identity"})
			}
			ctx, cancel := context.WithTimeout(context.Background(), 30*time.Minute)
			var state []byte
			headers := make(map[string]string)
			client := storeauth.NewHTTPClient(nil)
			switch req.Operation {
			case "anisette":
				var proof http.Header
				proof, state, err = storeauth.AnisetteHeaders(ctx, client, req.State)
				for key := range proof {
					headers[key] = proof.Get(key)
				}
			case "store_amd":
				if !validAMDEndpoint(req.Endpoint) {
					cancel()
					return encoder.Encode(response{Error: "invalid_store_endpoint"})
				}
				headers, state, err = storeauth.StoreAMDHeaders(ctx, req.State, req.Endpoint, hardware)
			case "store_provision":
				var bundle assets.Bundle
				bundle, err = assets.Load(ctx)
				if err == nil {
					var data []byte
					data, err = machine.GenerateKBSync(ctx, bundle, hardware, ^uint64(1))
					if err == nil {
						identity := make(http.Header)
						for key, value := range req.Headers {
							identity.Set(key, value)
						}
						state, err = storeauth.ProvisionStoreAnisette(ctx, client, req.State, req.Challenge,
							"https://auth.itunes.apple.com/auth/v1/otp/1.5/finish",
							"Configurator/2.21 (Macintosh; OS X 27.0.1; 26A434) AppleWebKit/0625.2.5.11.6",
							base64.StdEncoding.EncodeToString(data), hardware, identity)
					}
				}
			}
			cancel()
			if err != nil {
				return encoder.Encode(response{Error: "store_identity_failed"})
			}
			if err := encoder.Encode(response{OK: true, State: state, Headers: headers}); err != nil {
				return err
			}
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
