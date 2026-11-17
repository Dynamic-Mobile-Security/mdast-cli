package assets

import (
	"archive/zip"
	"bytes"
	"crypto/rand"
	"io"
	"testing"
)

type countedArchive struct {
	*bytes.Reader
	calls int
}

func (r *countedArchive) ReadAt(p []byte, offset int64) (int, error) {
	r.calls++
	return r.Reader.ReadAt(p, offset)
}

func TestBufferedKernelArchive(t *testing.T) {
	input := make([]byte, 2<<20)
	if _, err := rand.Read(input); err != nil {
		t.Fatal(err)
	}
	var buffer bytes.Buffer
	writer := zip.NewWriter(&buffer)
	file, err := writer.Create("kernel")
	if err != nil {
		t.Fatal(err)
	}
	if _, err = file.Write(input); err != nil {
		t.Fatal(err)
	}
	if err = writer.Close(); err != nil {
		t.Fatal(err)
	}
	counted := &countedArchive{Reader: bytes.NewReader(buffer.Bytes())}
	archive, err := zip.NewReader(counted, int64(buffer.Len()))
	if err != nil {
		t.Fatal(err)
	}
	counted.calls = 0
	data, err := readBufferedZipEntry(archive.File[0], 4<<20)
	if err != nil || !bytes.Equal(data, input) {
		t.Fatalf("invalid decoded entry: %v", err)
	}
	if counted.calls > 20 {
		t.Fatalf("too many remote range requests: %d", counted.calls)
	}
	if _, err = readBufferedZipEntry(archive.File[0], 1024); err == nil {
		t.Fatal("accepted oversized entry")
	}
	archive.File[0].CRC32 ^= 1
	if _, err = readBufferedZipEntry(archive.File[0], 4<<20); err != zip.ErrChecksum {
		t.Fatalf("missing CRC failure: %v", err)
	}
	archive.File[0].CRC32 ^= 1
	offset, err := archive.File[0].DataOffset()
	if err != nil {
		t.Fatal(err)
	}
	buffer.Bytes()[offset+100] ^= 1
	if _, err = readBufferedZipEntry(archive.File[0], 4<<20); err == nil || err == io.EOF {
		t.Fatal("accepted corrupt compressed entry")
	}
}
