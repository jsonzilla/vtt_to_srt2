#!/usr/bin/python
# Jansen A. Simanullang / Jeison Cardoso

"""Convert of vtt to srt format"""

import os
import re
import argparse
from string import Template
from stat import S_ISDIR, ST_MODE, S_ISREG

import io 

class VttToStr:
    """Convert vtt to srt"""

    def __init__(self) :
        pass

    def convert_header(self, contents) :
        """Convert of vtt header to srt format

        :contents -- contents of vtt file
        """
        replacement = re.sub(r"WEBVTT\n", "", contents)
        replacement = re.sub(r"Kind:[ \-\w]+\n", "", replacement)
        replacement = re.sub(r"Language:[ \-\w]+\n", "", replacement)
        return replacement

    def add_padding_to_timestamp(self, contents) :
        """Add 00 to padding timestamp of to srt format

        :contents -- contents of vtt file
        """
        find_srt = Template(r'$a,$b --> $a,$b(?:[ \-\w]+:[\w\%\d:,.]+)*\n')
        minute = r"((?:\d\d:){1}\d\d)"
        second = r"((?:\d\d:){0}\d\d)"
        padding_minute = find_srt.substitute(a=minute, b=r"(\d{0,3})")
        padding_second = find_srt.substitute(a=second, b=r"(\d{0,3})")
        replacement = re.sub(
            padding_minute, r"00:\1,\2 --> 00:\3,\4\n", contents)
        return re.sub(padding_second, r"00:00:\1,\2 --> 00:00:\3,\4\n", replacement)

    def convert_timestamp(self, contents) :
        """Convert timestamp of vtt file to srt format

        :contents -- contents of vtt file
        """
        find_vtt = Template(r'$a.$b --> $a.$b(?:[ \-\w]+:[\w\%\d:,.]+)*\n')
        all_timestamp = find_vtt.substitute(
            a=r"((?:\d\d:){0,2}\d\d)", b=r"(\d{0,3})")
        return self.add_padding_to_timestamp(re.sub(all_timestamp, r"\1,\2 --> \3,\4\n", contents))

    def convert_content(self, contents) : 
        """Convert content of vtt file to srt format

        :contents -- contents of vtt file
        """
        replacement = self.convert_timestamp(contents)
        replacement = self.convert_header(replacement)
        replacement = re.sub(r"<c[.\w\d]*>", "", replacement)
        replacement = re.sub(r"</c>", "", replacement)
        replacement = re.sub(r"<\d\d:\d\d:\d\d.\d\d\d>", "", replacement)
        replacement = re.sub(
            r"::[\-\w]+\([\-.\w\d]+\)[ ]*{[.,:;\(\) \-\w\d]+\n }\n", "", replacement)
        replacement = re.sub(r"Style:\n##\n", "", replacement)
        replacement = self.remove_blank_lines(replacement)
        replacement = self.remove_simple_identifiers(replacement)
        replacement = self.add_sequence_numbers(replacement)

        return replacement

    def has_timestamp(self, content) : 
        """Check if line is a timestamp srt format

        :contents -- contents of vtt file
        """
        return re.match(r"((\d\d:){2}\d\d),(\d{3}) --> ((\d\d:){2}\d\d),(\d{3})", content) is not None

    def add_sequence_numbers(self, contents) : 
        """Adds sequence numbers to subtitle contents and returns new subtitle contents

        :contents -- contents of vtt file
        """
        lines = contents.split('\n')
        out = ''
        counter = 1
        for line in lines:
            if self.has_timestamp(line):
                out += str(counter) + '\n'
                counter += 1
            out += line + '\n'
        return out
    
    def remove_blank_lines(self, contents): 
        # Remove useless blank lines from the vtt file 
        lines = contents.split('\n')
        lines = [x for x in lines if x != '']
        lines.append('')
        out = []
        num = 0
        while num < len(lines) :
            if re.match(r"^\d+$", lines[num]) and self.has_timestamp(lines[num + 1]):
                if num == 0 :
                    pass
                else:
                    out.append('')
                out.append(lines[num])
                out.append(lines[num + 1])
                num += 2
            elif self.has_timestamp(lines[num]): 
                if num == 0 :
                    pass
                else :
                    out.append('')
                out.append(lines[num])
                num += 1
            else:
                out.append(lines[num])
                num += 1
        out.pop()
        return '\n'.join(out)
        
    def remove_simple_identifiers(self, contents) : 
        """Remove simple identifiers of vtt file

        :contents -- contents of vtt file
        """
        lines = contents.split('\n')
        out = []
        for i, line in enumerate(lines):
            if self.has_timestamp(line):
                if re.match(r"^\d+$", lines[i - 1]):
                    out.pop()
            out.append(line)
        return '\n'.join(out)

    def write_file(self, filename, data, encoding_format = "utf-8"):
        """Create a file with some data

        :filename -- filename pat
        :data -- data to write
        :encoding_format -- encoding format
        """
        try:
           
            with io.open(filename, "w", encoding=encoding_format) as file:
                file.writelines(data)
             
        except IOError:
            filename = filename.split(os.sep)[-1]
            with open(filename, "w") as file:
                file.writelines(str(data.encode(encoding_format)))
        print("file created {0}\n".format(filename))

    def read_file(self, filename, encoding_format = "utf-8"):
        """Read a file text

        :filename -- filename path
        :encoding_format -- encoding format
        """
        content = ''
        
        with io.open(filename, mode="r", encoding=encoding_format) as file:
            print("file being read: {0}\n".format(filename))
            content = file.read()
        return content

    def process(self, filename, encoding_format = "utf-8"):
        """Convert vtt file to a srt file

        :str_name_file -- filename path
        :encoding_format -- encoding format
        """
        file_contents = self.read_file(filename, encoding_format)
        str_data = ""
        str_data = str_data + self.convert_content(file_contents)
        filename = filename.replace(".vtt", ".srt")
        self.write_file(filename, str_data, encoding_format)


class ConvertFile:
    """Convert vtt file to srt file"""

    def __init__(self, pathname, encoding_format):
        """Constructor

        :pathname -- path to file or directory
        :encoding_format -- encoding format
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

    def __init__(self, pathname , enable_recursive , encoding_format ):
        """Constructor

        pathname -- path to file or directory
        :enable_recursive -- enable recursive
        :encoding_format -- encoding format
        """
        self.pathname = pathname
        self.enable_recursive = enable_recursive
        self.encoding_format = encoding_format
        self.vtt_to_str = VttToStr()

    def _walk_dir(self, top_most_path, callback):
        """Walk a directory

        :top_most_path -- parent directory
        :callback -- function to call
        """
        for file in os.listdir(top_most_path):
            pathname = os.path.join(top_most_path, file)
            if not os.path.isdir(pathname):
                # It"s a file, call the callback function
                callback(pathname)

    def _walk_tree(self, top_most_path, callback):
        """Recursively descend the directory tree rooted at top_most_path,
        calling the callback function for each regular file

        :top_most_path -- parent directory
        :callback -- function to call
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
                print("Skipping {0}".format(pathname))

    def convert_vtt_to_str(self, file):
        """Convert vtt file to string

        :file -- file to convert
        """
        if ".vtt" in file:
            try:
                self.vtt_to_str.process(file, self.encoding_format)
            except UnicodeDecodeError:
                print("UnicodeDecodeError: {0}".format(file))

    def _vtt_to_srt_batch(self, directory):
        """Walk down directory searching for vtt files

        :directory -- path to search
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
    """main function"""

    args = _parse_args()
    pathname = args.pathname
    recursive = args.recursive
    encoding = args.encoding

    if not encoding:
        encoding = "utf-8"

    if os.path.isfile(pathname):
        print("file being converted: {0}\n".format(pathname))
        ConvertFile(pathname, encoding).convert()

    if os.path.isdir(pathname):
        print("directory being converted: {0}\n".format(pathname))
        ConvertDirectories(pathname, recursive, encoding).convert()

    if not os.path.isfile(pathname) and not os.path.isdir(pathname):
        print("pathname is not a file or directory: {0}\n".format(pathname))
        _show_usage()


if __name__ == "__main__":
    main()
