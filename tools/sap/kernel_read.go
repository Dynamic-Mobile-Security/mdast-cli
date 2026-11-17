package assets

import (
	"archive/zip"
	"bufio"
	"compress/flate"
	"errors"
	"hash/crc32"
	"io"
)

// ZIP's flate reader requests a few KiB at a time. On remote ReaderAt each
// request is a round trip. Buffer only this sequential, size-pinned entry.
func readBufferedZipEntry(entry *zip.File, maximum int64) ([]byte, error) {
	if maximum <= 0 || entry.UncompressedSize64 > uint64(maximum) || entry.CompressedSize64 > uint64(maximum) {
		return nil, errors.New("kernel archive entry exceeds size limit")
	}
	raw, err := entry.OpenRaw()
	if err != nil {
		return nil, err
	}
	buffered := bufio.NewReaderSize(raw, 2<<20)
	var reader io.ReadCloser
	switch entry.Method {
	case zip.Deflate:
		reader = flate.NewReader(buffered)
	case zip.Store:
		reader = io.NopCloser(buffered)
	default:
		return nil, errors.New("unsupported kernel archive compression")
	}
	data, readErr := io.ReadAll(io.LimitReader(reader, maximum+1))
	closeErr := reader.Close()
	if readErr != nil || closeErr != nil {
		return nil, errors.Join(readErr, closeErr)
	}
	if int64(len(data)) > maximum || uint64(len(data)) != entry.UncompressedSize64 {
		return nil, errors.New("kernel archive entry has invalid size")
	}
	if crc32.ChecksumIEEE(data) != entry.CRC32 {
		return nil, zip.ErrChecksum
	}
	return data, nil
}
