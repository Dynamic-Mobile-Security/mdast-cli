// Local optional runtime cache for checksum-pinned public SAP assets.
package cachepath

import (
	"fmt"
	"os"
	"path/filepath"
)

func Directory() (string, error) {
	if directory := os.Getenv("MDAST_SAP_CACHE_DIR"); directory != "" {
		if !filepath.IsAbs(directory) {
			return "", fmt.Errorf("SAP runtime cache must be an absolute directory")
		}
		return directory, nil
	}
	return os.UserCacheDir()
}
