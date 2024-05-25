import datetime
import zipfile
import struct
import argparse

def decode_extended_timestamp(extra_data):
    offset = 0
    length = len(extra_data)
    while offset < length:
        header_id, data_size = struct.unpack_from('<HH', extra_data, offset)
        offset += 4
        if header_id == 0x5455:  # Extended Timestamp Extra Field
            flags = struct.unpack_from('B', extra_data, offset)[0]
            offset += 1
            timestamps = {}
            if flags & 1:  # Modification time
                mtime, = struct.unpack_from('<I', extra_data, offset)
                timestamps['mtime'] = datetime.datetime.fromtimestamp(mtime, datetime.timezone.utc)
                offset += 4
            if flags & 2:  # Access time
                atime, = struct.unpack_from('<I', extra_data, offset)
                timestamps['atime'] = datetime.datetime.fromtimestamp(atime, datetime.timezone.utc)
                offset += 4
            if flags & 4:  # Creation time
                ctime, = struct.unpack_from('<I', extra_data, offset)
                timestamps['ctime'] = datetime.datetime.fromtimestamp(ctime, datetime.timezone.utc)
                offset += 4
            return timestamps
        else:
            offset += data_size
    return None

def main(zip_path, target_filename):
    try:
        with zipfile.ZipFile(zip_path, mode="r") as archive:
            try:
                info = archive.getinfo(target_filename)
                print(f"Filename: {info.filename}")
                print(f"Modified: {datetime.datetime(*info.date_time)}")
                print(f"Normal size: {info.file_size} bytes")
                print(f"Compressed size: {info.compress_size} bytes")
                
                timestamps = decode_extended_timestamp(info.extra)
                if timestamps and 'ctime' in timestamps:
                    print(f"Creation Time: {timestamps['ctime']}")
                else:
                    print("No creation time found.")
                if timestamps and 'atime' in timestamps:
                    print(f"Access Time: {timestamps['atime']}")
                else:
                    print("No access time found.")
                if timestamps and 'mtime' in timestamps:
                    print(f"Modified Time: {timestamps['mtime']}")
                else:
                    print("No modified time found.")
                print("-" * 20)
            except KeyError:
                print(f"File '{target_filename}' not found in the ZIP archive.")
    except FileNotFoundError:
        print(f"ZIP file '{zip_path}' not found.")
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract and print file timestamps from a ZIP archive.")
    parser.add_argument("zip_path", help="Path to the ZIP file")
    parser.add_argument("target_filename", help="Path and filename to find within the ZIP file")
    args = parser.parse_args()
    main(args.zip_path, args.target_filename)
    