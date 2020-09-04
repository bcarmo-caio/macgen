import secrets


# lib Levenshtein
# lib levenshtein_fallback
# lib Levenshtein is way faster than lib levenshtein_fallback
#
# time ./nmgen.py -pv -ll 4 -v tplink -l
# real    0m0.325s
# user    0m0.266s
# sys     0m0.056s
#
# time ./nmgen.py -pv -ll 4 -v tplink -l
# real    0m0.898s
# user    0m0.873s
# sys     0m0.030s
try:
    from Levenshtein import distance as levenshtein_dist
except ModuleNotFoundError:
    try:
        from ilevenshtein_fallback import levenshtein_dist
    except ModuleNotFoundError:
        from levenshtein_fallback_for_real import levenshtein_dist


class MAC:
    _levenshtein_max_dist_allowed = None
    _macs = None

    @classmethod
    def set_macs(cls, macs):
        cls._macs = macs

    @classmethod
    def set_levenshtein_max_dist_allowed(cls, max_dist_allowed):
        cls._levenshtein_max_dist_allowed = max_dist_allowed

    def __init__(self,
                 OUI: str,
                 vendor: str,
                 full_vendor_name: str,
                 comment: str):
        self.OUI = OUI
        self._OUI_as_list = self.OUI.split(':')
        self.vendor = vendor
        self.full_vendor_name = full_vendor_name
        self.comment = comment

    @classmethod
    def get_any(cls):
        return secrets.choice(cls._macs)

    @classmethod
    def _generate_random_hex(cls):
        return str(hex(secrets.randbelow(256))[2:].upper()).zfill(2)

    def generate_random_mac(self, separator):
        p_4 = self.__class__._generate_random_hex()
        p_5 = self.__class__._generate_random_hex()
        p_6 = self.__class__._generate_random_hex()
        return f'{self._OUI_as_list[0]}{separator}' \
               f'{self._OUI_as_list[1]}{separator}' \
               f'{self._OUI_as_list[2]}{separator}' \
               f'{p_4}{separator}' \
               f'{p_5}{separator}' \
               f'{p_6}'

    @classmethod
    def find_by_OUI(cls, OUI: str):
        OUI = OUI.replace(' ', ':') \
                 .replace('-', ':')
        for mac in cls._macs:
            if mac.OUI == OUI:
                return mac

    @classmethod
    def _find_by_vendor_no_levenshtein(cls, vendor):
        matched_macs = []
        for mac in cls._macs:
            if mac.vendor.lower() == vendor:
                matched_macs.append(mac)
        return matched_macs

    @classmethod
    def _find_by_vendor_levenshtein(cls, vendor):
        matched_macs = []
        for mac in cls._macs:
            lev_dist = levenshtein_dist(vendor, mac.vendor.lower())
            if lev_dist <= cls._levenshtein_max_dist_allowed:
                matched_macs.append(mac)
        return matched_macs

    @classmethod
    def find_by_vendor(cls, vendor, no_levenshtein):
        vendor = vendor.lower().strip()
        macs = cls._find_by_vendor_no_levenshtein(vendor)
        if macs:
            return macs
        if not no_levenshtein:
            return cls._find_by_vendor_levenshtein(vendor)
