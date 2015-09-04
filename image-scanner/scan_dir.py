import os
import platform
import subprocess
import xml.etree.ElementTree as ET
import collections
import json
from sys import exit
from get_cve_input import getInputCVE


class Scan(object):
    TMP_DIR = "/var/tmp/image-scanner"
    CVEs = collections.namedtuple('CVEs', 'title, severity,'
                                  'cve_ref_id, cve_ref_url,'
                                  'rhsa_ref_id, rhsa_ref_url')
    if not os.path.exists(TMP_DIR):
        os.makedirs(TMP_DIR)

    def __init__(self, scan_dir, hours_old=2):
        self.scan_dir = scan_dir
        cve = getInputCVE(self.TMP_DIR)
        cve.fetch_dist_data(hours_old)
        self.os_release = None
        self.scan_xml = os.path.join(self.TMP_DIR, 'results.xml')
        self.CVE_list = []

    def get_release(self):
        etc_release_path = os.path.join(self.scan_dir,
                                        "etc/redhat-release")

        if not os.path.exists(etc_release_path):
            return False

        self.os_release = open(etc_release_path).read()

        rhel = 'Red Hat Enterprise Linux'

        if rhel in self.os_release:
            return True
        else:
            return False

    def scan(self):

        is_RHEL = self.get_release()
        if not is_RHEL:
            print "Chroot is not based on RHEL"
            exit(3)

        hostname = open("/etc/hostname").read().rstrip()
        os.environ["OSCAP_PROBE_ARCHITECTURE"] = platform.processor()
        os.environ["OSCAP_PROBE_ROOT"] = self.scan_dir
        os.environ["OSCAP_PROBE_OS_NAME"] = platform.system()
        os.environ["OSCAP_PROBE_OS_VERSION"] = platform.release()
        os.environ["OSCAP_PROBE_PRIMARY_HOST_NAME"] = "{0}".format(hostname)

        # We only support RHEL 6|7 in containers right now

        if "Red Hat Enterprise Linux" in self.os_release:
            if "7." in self.os_release:
                self.chroot_cve_file = os.path.join(
                    self.TMP_DIR, "Red_Hat_Enterprise_Linux_7.xml")
            elif "6." in self.os_release:
                self.chroot_cve_file = os.path.join(
                    self.TMP_DIR, "Red_Hat_Enterprise_Linux_6.xml")
        cmd = ['oscap', 'oval', 'eval', '--results', self.scan_xml,
               self.chroot_cve_file]

        self.result = subprocess.check_output(cmd)

    def report_results(self, details=False):
        cve_tree = ET.parse(self.chroot_cve_file)
        self.cve_root = cve_tree.getroot()

        for line in self.result.splitlines():
            split_line = line.split(':')
            # Not in love with how I did this
            # Should find a better marked to know if it is a line
            # a parsable line.
            if (len(split_line) == 5) and ('true' in split_line[4]):
                self._return_xml_values(line.split()[1][:-1])

        # We found CVEs
        if len(self.CVE_list) > 0:
            if details:
                self._report_json()
            exit(1)
        else:
            exit(0)

    def _report_json(self):
        j_dict = {}
        for cve in self.CVE_list:
            j_dict[cve.cve_ref_id] = {'title': cve.title,
                                      'severity': cve.severity,
                                      'cve_ref_url': cve.cve_ref_url,
                                      'rhsa_ref_id': cve.rhsa_ref_id,
                                      'rhsa_ref_url': cve.rhsa_ref_url
                                      }
        self.debug_json(j_dict)

    @staticmethod
    def debug_json(json_data):
        ''' Pretty prints a json object for debug purposes '''
        print json.dumps(json_data, indent=4, separators=(',', ': '))

    def _return_xml_values(self, cve):
        cve_string = ("{http://oval.mitre.org/XMLSchema/oval-definitions-5}"
                      "definitions/*[@id='%s']" % cve)
        cve_xml = self.cve_root.find(cve_string)
        title = cve_xml.find("{http://oval.mitre.org/XMLSchema/oval-"
                             "definitions-5}metadata/"
                             "{http://oval.mitre.org/XMLSchema/"
                             "oval-definitions-5}title")
        cve_id = cve_xml.find("{http://oval.mitre.org/XMLSchema/"
                              "oval-definitions-5}metadata/{http://oval.mitre."
                              "org/XMLSchema/oval-definitions-5}reference"
                              "[@source='CVE']")
        sev = (cve_xml.find("{http://oval.mitre.org/XMLSchema/oval-definitions"
                            "-5}metadata/{http://oval.mitre.org/XMLSchema/oval"
                            "-definitions-5}advisory/")).text

        if cve_id is not None:
            cve_ref_id = cve_id.attrib['ref_id']
            cve_ref_url = cve_id.attrib['ref_url']
        else:
            cve_ref_id = None
            cve_ref_url = None

        rhsa_id = cve_xml.find("{http://oval.mitre.org/XMLSchema/oval-"
                               "definitions-5}metadata/{http://oval.mitre.org"
                               "/XMLSchema/oval-definitions-5}reference"
                               "[@source='RHSA']")

        if rhsa_id is not None:
            rhsa_ref_id = rhsa_id.attrib['ref_id']
            rhsa_ref_url = rhsa_id.attrib['ref_url']
        else:
            rhsa_ref_id = None
            rhsa_ref_url = None

        self.CVE_list.append(self.CVEs(title=title.text, cve_ref_id=cve_ref_id,
                             cve_ref_url=cve_ref_url, rhsa_ref_id=rhsa_ref_id,
                             rhsa_ref_url=rhsa_ref_url, severity=sev))
