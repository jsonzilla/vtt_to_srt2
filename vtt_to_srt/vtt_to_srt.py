#!/usr/bin/python
# Jansen A. Simanullang / Jeison Cardoso

"""Convert of vtt to srt format"""

import os
import re
import argparse
from string import Template
from stat import S_ISDIR, ST_MODE, S_ISREG


class VttToStr:
    """Convert vtt to srt"""

    def __init__(self) -> None:
        pass

    def convert_header(self, contents):
        """Convert of vtt header to srt format

        Keyword arguments:
        contents
        """
        replacement = re.sub(r"WEBVTT\n", "", contents)
        replacement = re.sub(r"Kind:[ \-\w]+\n", "", replacement)
        replacement = re.sub(r"Language:[ \-\w]+\n", "", replacement)
        return replacement

    def add_padding_to_timestamp(self, contents):
        """Add 00 to padding timestamp of to srt format

        Keyword arguments:
        contents
        """
        find_srt = Template(r'$a,$b --> $a,$b(?:[ \-\w]+:[\w\%\d:,.]+)*\n')
        minute = r"((?:\d\d:){1}\d\d)"
        second = r"((?:\d\d:){0}\d\d)"
        padding_minute = find_srt.substitute(a=minute, b=r"(\d{0,3})")
        padding_second = find_srt.substitute(a=second, b=r"(\d{0,3})")
        replacement = re.sub(
            padding_minute, r"00:\1,\2 --> 00:\3,\4\n", contents)
        return re.sub(padding_second, r"00:00:\1,\2 --> 00:00:\3,\4\n", replacement)

    def convert_timestamp(self, contents):
        """Convert timestamp of vtt file to srt format

        Keyword arguments:
        contents
        """
        find_vtt = Template(r'$a.$b --> $a.$b(?:[ \-\w]+:[\w\%\d:,.]+)*\n')
        all_timestamp = find_vtt.substitute(
            a=r"((?:\d\d:){0,2}\d\d)", b=r"(\d{0,3})")
        return self.add_padding_to_timestamp(re.sub(all_timestamp, r"\1,\2 --> \3,\4\n", contents))

    def convert_content(self, contents):
        """Convert content of vtt file to srt format

        Keyword arguments:
        contents
        """
        replacement = self.convert_timestamp(contents)
        replacement = self.convert_header(replacement)
        replacement = re.sub(r"<c[.\w\d]*>", "", replacement)
        replacement = re.sub(r"</c>", "", replacement)
        replacement = re.sub(r"<\d\d:\d\d:\d\d.\d\d\d>", "", replacement)
        replacement = re.sub(
            r"::[\-\w]+\([\-.\w\d]+\)[ ]*{[.,:;\(\) \-\w\d]+\n }\n", "", replacement)
        replacement = re.sub(r"Style:\n##\n", "", replacement)
        replacement = self.add_sequence_numbers(replacement)

        return replacement

    def has_timestamp(self, content):
        """Check if line is a timestamp srt format

        Keyword arguments:
        contents
        """
        return re.match(r"((\d\d:){2}\d\d),(\d{3}) --> ((\d\d:){2}\d\d),(\d{3})", content) is not None

    def add_sequence_numbers(self, contents):
        """Adds sequence numbers to subtitle contents and returns new subtitle contents

        Keyword arguments:
        contents
        """
        output = ''
        lines = contents.split('\n')
        i = 1
        for line in lines:
            if self.has_timestamp(line):
                output += str(i) + '\n'
                i += 1
            output += line + '\n'
        return output

    def write_file(self, filename: str, data, encoding_format: str = "utf-8"):
        """Create a file with some data

        Keyword arguments:
        filename -- filename pat
        data -- data to write
        encoding_format -- encoding format
        """
        try:
            with open(filename, "w", encoding=encoding_format) as file:
                file.writelines(str(data))
        except IOError:
            filename = filename.split(os.sep)[-1]
            with open(filename, "w", encoding=encoding_format) as file:
                file.writelines(str(data))
        print(f"file created {filename}\n")

    def read_file(self, filename: str, encoding_format: str = "utf-8"):
        """Read a file text

        Keyword arguments:
        filename -- filename path
        encoding_format -- encoding format
        """
        content: str = ''
        with open(filename, mode="r", encoding=encoding_format) as file:
            print(f"file being read: {filename}\n")
            content = file.read()

        return content

    def process(self, filename: str, encoding_format: str = "utf-8"):
        """Convert vtt file to a srt file

        Keyword arguments:
        str_name_file -- filename path
        encoding_format -- encoding format
        """
        file_contents: str = self.read_file(filename, encoding_format)
        str_data: str = ""
        str_data = str_data + self.convert_content(file_contents)
        filename = filename.replace(".vtt", ".srt")
        self.write_file(filename, str_data, encoding_format)


class ConvertFile:
    """Convert vtt file to srt file"""

    def __init__(self, pathname: str, encoding_format: str):
        """Constructor

           Keyword arguments:
           pathname -- path to file or directory
           encoding_format -- encoding format
           """
        self.pathname = pathname
        self.encoding_format = encoding_format
        self.vtt_to_str = VttToStr()

    def convert(self):
        """Convert vtt file to srt file"""
        if ".vtt" in self.pathname:
            self.vtt_to_str.process(self.pathname, self.encoding_format)


class ConvertDirectories:
    """Convert vtt files to srt files"""

    def __init__(self, pathname: str, enable_recursive: bool, encoding_format: str):
        """Constructor

           Keyword arguments:
           pathname -- path to file or directory
           enable_recursive -- enable recursive
           encoding_format -- encoding format
           """
        self.pathname = pathname
        self.enable_recursive = enable_recursive
        self.encoding_format = encoding_format
        self.vtt_to_str = VttToStr()

    def _walk_dir(self, top_most_path: str, callback):
        """Walk a directory

           Keyword arguments:
           top_most_path -- parent directory
           callback -- function to call
           """
        for file in os.listdir(top_most_path):
            pathname = os.path.join(top_most_path, file)
            if not os.path.isdir(pathname):
                # It"s a file, call the callback function
                callback(pathname)

    def _walk_tree(self, top_most_path, callback):
        """Recursively descend the directory tree rooted at top_most_path,
        calling the callback function for each regular file

        Keyword arguments:
        top_most_path -- parent directory
        callback -- function to call
        """
        for file in os.listdir(top_most_path):
            pathname = os.path.join(top_most_path, file)
            mode = os.stat(pathname)[ST_MODE]
            if S_ISDIR(mode):
                # It's a directory, recurse into it
                self._walk_tree(pathname, callback)
            elif S_ISREG(mode):
                # It's a file, call the callback function
                callback(pathname)
            else:
                # Unknown file type, print a message
                print(f"Skipping {pathname}")

    def convert_vtt_to_str(self, file: str):
        """Convert vtt file to string

        Keyword arguments:
        f -- file to convert
        encoding_format -- encoding format
        """
        if ".vtt" in file:
            try:
                self.vtt_to_str.process(file, self.encoding_format)
            except UnicodeDecodeError:
                print(f"UnicodeDecodeError: {file}")

    def _vtt_to_srt_batch(self, directory: str):
        """Walk down directory searching for vtt files

        Keyword arguments:
        directory -- path to search
        enable_recursive_search -- enable recursive
        """
        top_most_path = directory
        if self.enable_recursive:
            self._walk_tree(top_most_path, self.convert_vtt_to_str)
        else:
            self._walk_dir(top_most_path, self.convert_vtt_to_str)

    def convert(self):
        """Convert vtt files to srt files"""
        self._vtt_to_srt_batch(self.pathname)


def _show_usage():
    """Show a info message about the usage"""
    print("\nUsage:\tvtt_to_srt pathname [-r]\n")
    print("\tpathname\t- a file or directory with files to be converted")
    print("\t-r\t\t- walk path recursively\n")


def _parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Convert vtt files to srt files')
    parser.add_argument(
        "pathname", help="a file or directory with files to be converted")
    parser.add_argument("-r", "--recursive",
                        help="walk path recursively", action="store_true")
    parser.add_argument("-e", "--encoding",
                        help="encoding format for input and output files")

    args = parser.parse_args()
    return args


def main():
    """main

       Keyword arguments:
        pathname - a file or directory with files to be converted
        -r walk path recursively
       """

    args = _parse_args()
    pathname = args.pathname
    recursive = args.recursive
    encoding = args.encoding

    if not encoding:
        encoding = "utf-8"

    if os.path.isfile(pathname):
        print(f"file being converted: {pathname}\n")
        ConvertFile(pathname, encoding).convert()

    if os.path.isdir(pathname):
        print(f"directory being converted: {pathname}\n")
        ConvertDirectories(pathname, recursive, encoding).convert()

    if not os.path.isfile(pathname) and not os.path.isdir(pathname):
        print(f"pathname is not a file or directory: {pathname}\n")
        _show_usage()


if __name__ == "__main__":
    main()
