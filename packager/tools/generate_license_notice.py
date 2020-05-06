#!/usr/bin/python
#
# Copyright 2018 Google Inc. All rights reserved.
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd
"""This script is used to generate license notice string for packager."""

import argparse
import os
import sys

LICENSE_FILES = set(['LICENSE', 'LICENSE.TXT', 'COPYING'])
PRUNE_PATHS = [
    # Identical to third_party/icu.
    os.path.join('base', 'third_party', 'icu'),

    # Comes with Chromium base, not used in packager.
    os.path.join('base', 'third_party', 'libevent'),
    os.path.join('base', 'third_party', 'nspr'),
    os.path.join('base', 'third_party', 'superfasthash'),
    os.path.join('base', 'third_party', 'xdg_mime'),
    os.path.join('base', 'third_party', 'xdg_user_dirs'),

    # Used for development and test, not in the binary build.
    os.path.join('buildtools', 'third_party', 'libc++', 'trunk', 'utils',
                 'google-benchmark'),
    os.path.join('testing', 'gmock'),
    os.path.join('testing', 'gtest'),
    os.path.join('third_party', 'binutils'),
    os.path.join('third_party', 'boringssl', 'src', 'third_party',
                 'googletest'),
    os.path.join('third_party', 'gold'),
    os.path.join('tools', 'gyp'),

    # Comes with Boringssl, not used in packager.
    os.path.join('third_party', 'boringssl', 'src', 'third_party',
                 'android-cmake'),
    # Comes with ICU, not used in packager.
    os.path.join('third_party', 'icu', 'scripts'),
    # Required by Chromium base, but not used in packager.
    os.path.join('third_party', 'libevent'),
]

CC_FILE_TEMPLATE = """
// Generated by tools/generate_license_notice.py. Do not modify.

namespace shaka {{

const char* kLicenseNotice[] = {{
{}
}};

}}  // namespace shaka"""

H_FILE_TEMPLATE = """
// Generated by tools/generate_license_notice.py. Do not modify.

#ifndef PACKAGER_TOOLS_LICENSE_NOTICE_H_
#define PACKAGER_TOOLS_LICENSE_NOTICE_H_

namespace shaka {{
extern const char* kLicenseNotice[{}];
}}  // namespace shaka

#endif  // PACKAGER_TOOLS_LICENSE_NOTICE_H_"""


def _FindLicenseFiles(root):
  """Finds and returns all license files."""
  result = []
  for path, dirs, files in os.walk(root):
    path = path[len(root) + 1:]  # Change to relative path.

    if path in PRUNE_PATHS:
      dirs[:] = []
      continue

    license_files = LICENSE_FILES.intersection(files)
    if license_files:
      result.append(os.path.join(path, license_files.pop()))
  return result


def _GetModuleName(path):
  """Find third_party module name from file path."""
  while True:
    path = os.path.dirname(path)
    base_name = os.path.basename(path)
    if base_name not in ['src', 'source', 'trunk']:
      return base_name


def _ReadFile(path):
  """Reads a file from disk."""
  with open(path, 'rb') as f:
    return f.read().splitlines()


def GenerateLicenseNotice(output_dir, output_license_file_name):
  """Generate plain-text license notice embedded in C++ code.

  The output file contains licenses of both Shaka Packager and third-party
  libraries used in Shaka Packager.

  Args:
    output_dir: Output directory path. If not specified, no output is produced.
    output_license_file_name: Whether to output license file names.
  """

  script_dir = os.path.dirname(os.path.realpath(__file__))
  packager_dir = os.path.abspath(os.path.join(script_dir, os.pardir))

  license_files = _FindLicenseFiles(packager_dir)
  license_files.sort()

  if output_license_file_name:
    print('Num License Files: {}\n'.format(len(license_files)))
    for license_file in license_files:
      print(license_file)

  # Include the main license file.
  content = _ReadFile(os.path.join(packager_dir, os.pardir, 'LICENSE'))
  for license_file in license_files:
    content.append('-' * 20)
    content.append(_GetModuleName(license_file))
    content.append('-' * 20)
    content.extend(_ReadFile(os.path.join(packager_dir, license_file)))

  # MSVC does not like long strings (Error C2026, C1091), so we have to break
  # them into multiple strings.
  content_array_text = '\n'.join(map('    R"shaka({})shaka",'.format, content))

  if output_dir:
    cc_file_path = os.path.join(output_dir, 'license_notice.cc')
    with open(cc_file_path, 'w') as output:
      output.write(CC_FILE_TEMPLATE.format(content_array_text))

    h_file_path = os.path.join(output_dir, 'license_notice.h')
    with open(h_file_path, 'w') as output:
      output.write(H_FILE_TEMPLATE.format(len(content)))


def main():
  parser = argparse.ArgumentParser()

  parser.add_argument(
      '--output-license-file-name',
      dest='output_license_file_name',
      action='store_true')
  parser.set_defaults(output_license_file_name=False)

  parser.add_argument('output_dir', nargs='?')
  args = parser.parse_args()

  GenerateLicenseNotice(args.output_dir, args.output_license_file_name)
  return 0


if __name__ == '__main__':
  sys.exit(main())
