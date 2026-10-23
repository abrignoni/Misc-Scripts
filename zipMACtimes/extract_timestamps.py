"""Print the timestamps a zip file stores for one member.

Full file system extractions in zip keep file times in extra fields, not only in
the zip's own modified time. That modified time (DOS date/time) is the local
wall clock of the machine that wrote the zip, has 2 second resolution and holds
no time zone, so it is shown here for reference only.

Extra fields read:
  0x5455  Extended timestamp, Unix seconds, UTC. Values follow the flag bits in
          order. Info-ZIP defines bit 1 modified, bit 2 accessed, bit 4 created.
          GrayKey style files_full.zip extractions set a fourth bit (0x08) and
          store four values. For those, the third value behaves as the change
          time and the fourth as the creation (birth) time. Sources: gkls by
          slo-sleuth (github.com/slo-sleuth/gkls, commit 1b86903, README), AXIOM
          displays shown in public CTF writeups, and photo EXIF capture times.
  0x000a  NTFS, FILETIME, UTC: modified, accessed, created.

Cellebrite CLBX zips (a root "version" file reading CLBX-...) also carry
metadata<suffix>/metadata.msgpack, which the CLBX spec calls the authoritative
per file record (github.com/cellebrite-labs/clbx). On the CLBX-0.3.1 zips
tested, every 0x5455 value equals the file's access time, so for CLBX the
metadata record is printed when the msgpack package is installed
(pip install msgpack).

Usage:
  python3 extract_timestamps.py <zip> <member path inside the zip>
"""
import argparse
import datetime
import struct
import zipfile

INT64_MIN = -(2 ** 63)
FILETIME_EPOCH = datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc)


def utc(seconds):
    return datetime.datetime.fromtimestamp(seconds, datetime.timezone.utc)


def extra_fields(extra):
    """Yield (header id, data) for each extra field, bounded by its declared size."""
    offset = 0
    while offset + 4 <= len(extra):
        header_id, size = struct.unpack_from('<HH', extra, offset)
        data = extra[offset + 4:offset + 4 + size]
        offset += 4 + size
        if len(data) < size:
            break
        yield header_id, data


def decode_extended_timestamp(data):
    """Return [(label, datetime)] for an 0x5455 field, in flag bit order."""
    if not data:
        return []
    flags = data[0]
    four_values = bool(flags & 0x08)
    labels = {
        0x01: 'Modified Time',
        0x02: 'Access Time',
        0x04: 'Change Time (third value; GrayKey style four value field)' if four_values
              else 'Creation Time',
        0x08: 'Creation Time (birth; fourth value)',
    }
    times = []
    offset = 1
    for bit in (0x01, 0x02, 0x04, 0x08):
        if not flags & bit:
            continue
        if offset + 4 > len(data):
            break
        times.append((labels[bit], utc(struct.unpack_from('<I', data, offset)[0])))
        offset += 4
    return times


def decode_ntfs(data):
    """Return [(label, datetime)] for an NTFS 0x000a field (tag 0x0001)."""
    times = []
    offset = 4  # reserved
    while offset + 4 <= len(data):
        tag, size = struct.unpack_from('<HH', data, offset)
        offset += 4
        if tag == 0x0001 and size >= 24:
            for label, value in zip(('Modified Time', 'Access Time', 'Creation Time'),
                                    struct.unpack_from('<3Q', data, offset)):
                times.append((label, FILETIME_EPOCH + datetime.timedelta(microseconds=value // 10)))
        offset += size
    return times


def clbx_record(archive, member_name):
    """Return (version, record) from a CLBX metadata.msgpack, or (version, reason)."""
    try:
        version = archive.read('version').decode('ascii', 'replace').strip()
    except KeyError:
        return None
    if not version.startswith('CLBX-'):
        return None
    first, _, rest = member_name.partition('/')
    if not first.startswith('filesystem'):
        return version, 'member is not under a filesystem folder'
    meta_name = f'metadata{first[len("filesystem"):]}/metadata.msgpack'
    try:
        import msgpack
    except ImportError:
        return version, 'install msgpack (pip install msgpack) to read ' + meta_name
    try:
        with archive.open(meta_name) as handle:
            metadata = msgpack.unpack(handle, raw=False, strict_map_key=False)
    except KeyError:
        return version, meta_name + ' not found'
    record = metadata.get(rest)
    if record is None:
        return version, 'no record for this file in ' + meta_name
    return version, record


def main(zip_path, target_filename):
    try:
        with zipfile.ZipFile(zip_path, mode='r') as archive:
            try:
                info = archive.getinfo(target_filename)
            except KeyError:
                print(f"File '{target_filename}' not found in the ZIP archive.")
                return
            print(f'Filename: {info.filename}')
            print(f'Normal size: {info.file_size} bytes')
            print(f'Compressed size: {info.compress_size} bytes')
            print(f'Zip modified time (writer local time, no zone): {datetime.datetime(*info.date_time)}')

            found = False
            for header_id, data in extra_fields(info.extra):
                if header_id == 0x5455:
                    print('Extended timestamp field (0x5455), UTC:')
                    times = decode_extended_timestamp(data)
                elif header_id == 0x000a:
                    print('NTFS field (0x000a), UTC:')
                    times = decode_ntfs(data)
                else:
                    continue
                found = True
                for label, value in times:
                    print(f'  {label}: {value}')
            if not found:
                print('No extended timestamp or NTFS time field found.')

            clbx = clbx_record(archive, info.filename)
            if clbx:
                version, record = clbx
                print(f'Cellebrite {version}: the 0x5455 values above hold the access time on '
                      'the CLBX zips tested. Times from metadata.msgpack, UTC:')
                if isinstance(record, str):
                    print(f'  {record}')
                else:
                    for key, label in (('mtime', 'Modified Time'), ('atime', 'Access Time'),
                                       ('ctime', 'Change Time'), ('btime', 'Creation Time (birth)')):
                        value = record.get(key)
                        if not isinstance(value, int) or value == INT64_MIN:
                            print(f'  {label}: not recorded')
                        else:
                            seconds, nanos = divmod(value, 1_000_000_000)
                            print(f'  {label}: {utc(seconds)} (+{nanos} ns)')
            print('-' * 20)
    except FileNotFoundError:
        print(f"ZIP file '{zip_path}' not found.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract and print file timestamps from a ZIP archive.')
    parser.add_argument('zip_path', help='Path to the ZIP file')
    parser.add_argument('target_filename', help='Path and filename to find within the ZIP file')
    args = parser.parse_args()
    main(args.zip_path, args.target_filename)
