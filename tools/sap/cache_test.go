package cachepath

import (
	"os"
	"testing"
)

func TestExplicitCache(t *testing.T) {
	directory := t.TempDir()
	t.Setenv("MDAST_SAP_CACHE_DIR", directory)
	actual, err := Directory()
	if err != nil || actual != directory {
		t.Fatalf("explicit cache was not selected")
	}
}

func TestRelativeCacheRejected(t *testing.T) {
	t.Setenv("MDAST_SAP_CACHE_DIR", "relative/cache")
	if _, err := Directory(); err == nil {
		t.Fatal("relative cache accepted")
	}
}

func TestDefaultCacheUnchanged(t *testing.T) {
	t.Setenv("MDAST_SAP_CACHE_DIR", "")
	want, wantErr := os.UserCacheDir()
	actual, err := Directory()
	if (err != nil) != (wantErr != nil) || actual != want {
		t.Fatal("default user cache changed")
	}
}
