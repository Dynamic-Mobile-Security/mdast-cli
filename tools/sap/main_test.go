package main

import "testing"

func TestAMDEndpoints(t *testing.T) {
	accepted := []string{
		"https://auth.itunes.apple.com/auth/v1/native",
		"https://auth.itunes.apple.com/auth/v1/native?guid=001122334455",
		"https://p7-buy.itunes.apple.com/WebObjects/MZFinance.woa/wa/volumeStoreDownloadProduct?guid=001122334455",
		"https://downloaddispatch.itunes.apple.com/WebObjects/DownloadDispatch.woa/wa/ent/download?guid=001122334455",
	}
	rejected := []string{
		"http://auth.itunes.apple.com/auth/v1/native",
		"https://auth.itunes.apple.com/auth/v1/native#",
		"https://auth.itunes.apple.com/auth/v1/native/",
		"https://auth.itunes.apple.com/auth/v1/%6eative",
		"https://evil.apple.com/auth/v1/native",
		"https://user@auth.itunes.apple.com/auth/v1/native",
		"https://auth.itunes.apple.com:444/auth/v1/native",
		"https://p7-buy.itunes.apple.com.evil.example/WebObjects/MZFinance.woa/wa/volumeStoreDownloadProduct?guid=A",
		"https://downloaddispatch.itunes.apple.com/WebObjects/DownloadDispatch.woa/wa/ent/download?guid=A&guid=B",
		"https://downloaddispatch.itunes.apple.com/WebObjects/DownloadDispatch.woa/wa/ent/download",
	}
	for _, endpoint := range accepted {
		if !validAMDEndpoint(endpoint) {
			t.Errorf("rejected %s", endpoint)
		}
	}
	for _, endpoint := range rejected {
		if validAMDEndpoint(endpoint) {
			t.Errorf("accepted %s", endpoint)
		}
	}
}
