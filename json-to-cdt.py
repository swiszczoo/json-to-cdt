import argparse
from dataclasses import dataclass
import json
import jsonschema
from typing import Optional

@dataclass
class ConverterConfig:
    mb_strings: bool
    copyrighted: bool
    language: str
    seq: int
    tracks_ordered: list[object]

class CdtException(Exception):
    pass

ENUM_GENRES = [
    "not_used",
    "not_defined",
    "adult_contemporary",
    "alternative_rock",
    "childrens_music",
    "classical",
    "contemporary_christian",
    "country",
    "dance",
    "easy_listening",
    "erotic",
    "folk",
    "gospel",
    "hip_hop",
    "jazz",
    "latin",
    "musical",
    "new_age",
    "opera",
    "operetta",
    "pop",
    "rap",
    "reggae",
    "rock",
    "rhythm_and_blues",
    "sound_effects",
    "spoken_word",
    "world_music"
]

ENUM_LANGUAGES = [
    "unknown",
    "albanian",
    "breton",
    "catalan",
    "croatian",
    "welsh",
    "czech",
    "danish",
    "german",
    "english",
    "spanish",
    "esperanto",
    "estonian",
    "basque",
    "faroese",
    "french",
    "frisian",
    "irish",
    "gaelic",
    "galician",
    "iceland",
    "italian",
    "lappish",
    "latin",
    "latvian",
    "luxembourgian",
    "lithuanian",
    "hungarian",
    "maltese",
    "dutch",
    "norwegian",
    "occitan",
    "polish",
    "portugese",
    "romanian",
    "romanish",
    "serbian",
    "slovak",
    "slovenian",
    "finnish",
    "swedish",
    "turkish",
    "flemish",
    "wallon",
    "zulu",
    "vietnamese",
    "uzbek",
    "urdu",
    "ukrainian",
    "thai",
    "telugu",
    "tatar",
    "tamil",
    "tadzhik",
    "swahili",
    "sranan_tongo",
    "somali",
    "sinhalese",
    "shona",
    "serbo-croat",
    "ruthenian",
    "russian",
    "quechua",
    "pushtu",
    "punjabi",
    "persian",
    "papamiento",
    "oriya",
    "nepali",
    "ndebele",
    "marathi",
    "moldavian",
    "malaysian",
    "malagasay",
    "macedonian",
    "laotian",
    "korean",
    "khmer",
    "kazakh",
    "kannada",
    "japanese",
    "indonesian",
    "hindi",
    "hebrew",
    "hausa",
    "gurani",
    "gujurati",
    "greek",
    "georgian",
    "fulani",
    "dari",
    "churash",
    "chinese",
    "burmese",
    "bulgarian",
    "bengali",
    "bielorussian",
    "bambora",
    "azerbaijani",
    "assamese",
    "armenian",
    "arabic",
    "amharic"
]

# https://stackoverflow.com/questions/25239423/crc-ccitt-16-bit-python-manual-calculation
POLYNOMIAL = 0x1021
PRESET = 0

def _initial(c):
    crc = 0
    c = c << 8
    for _ in range(8):
        if (crc ^ c) & 0x8000:
            crc = (crc << 1) ^ POLYNOMIAL
        else:
            crc = crc << 1
        c = c << 1
    return crc

_tab = [ _initial(i) for i in range(256) ]

def _update_crc(crc, c):
    cc = 0xff & c

    tmp = (crc >> 8) ^ cc
    crc = (crc << 8) ^ _tab[tmp & 0xff]
    crc = crc & 0xffff

    return crc

def crcb(i):
    crc = PRESET
    for c in i:
        crc = _update_crc(crc, c)
    return crc

def append_crc(input: bytes):
    return input + (0xffff - crcb(input)).to_bytes(2, 'big')

def write_text_packs(output: list[bytes], config: ConverterConfig, code: int, start_track: int, data: list[str], mb_strings: Optional[bool] = None):
    if mb_strings is None:
        mb_strings = config.mb_strings

    index = 0
    buffer = b''
    previous_chars = 0
    encoding = 'cp952' if mb_strings else 'latin_1'
    terminator = b'\x00\x00' if mb_strings else b'\x00'
    bncpi_encoding = 0x80 if mb_strings else 0x00

    while index < len(data) or len(buffer) > 0:
        current_buffer = b''

        if len(buffer) > 0:
            header = (
                code.to_bytes(1, 'little') 
                + (index + start_track - 1).to_bytes(1, 'little') 
                + config.seq.to_bytes(1, 'little') 
                + (previous_chars | bncpi_encoding).to_bytes(1, 'little')
            )

            current_buffer += buffer[:12]
            buffer = buffer[12:]

            previous_chars += len(current_buffer)
            if previous_chars > 15: previous_chars = 15
        else:
            header = (
                code.to_bytes(1, 'little') 
                + (index + start_track).to_bytes(1, 'little') 
                + config.seq.to_bytes(1, 'little') 
                + bncpi_encoding.to_bytes(1, 'little')
            )


        while len(current_buffer) < 12 and index < len(data):
            this_str = data[index]
            index += 1

            buffer = this_str.encode(encoding) + terminator
            characters_left = 12 - len(current_buffer)

            current_buffer += buffer[:characters_left]
            buffer = buffer[characters_left:]
            previous_chars = characters_left

        if len(current_buffer) > 0:
            output.append(append_crc(header + current_buffer + ((12 - len(current_buffer)) * b'\x00')))
            config.seq += 1


def make_text_pack_writer(tag_name: str, code: int):
    def function(output: list[bytes], config: ConverterConfig, input_data: object) -> None:
        has_album = tag_name in input_data['album'] and len(input_data['album'][tag_name]) > 0
        has_tracks = False

        for track in config.tracks_ordered:
            has_tracks = has_tracks or (tag_name in track and len(track[tag_name])) > 0

        if not (has_album or has_tracks):
            return
        
        contents = []
        
        if has_album:
            contents.append(input_data['album'][tag_name])

        for track in config.tracks_ordered:
            if tag_name in track and len(track[tag_name]) > 0:
                contents.append(track[tag_name])
            else:
                track_no = track['number']
                raise(CdtException(f'Track {track_no} has no {tag_name}'))
            
        write_text_packs(output, config, code, 0 if has_album else 1, contents)

    return function


write_title_packs = make_text_pack_writer('title', 0x80)
write_performer_packs = make_text_pack_writer('performer', 0x81)
write_songwriter_packs = make_text_pack_writer('songwriter', 0x82)
write_composer_packs = make_text_pack_writer('composer', 0x83)
write_arranger_packs = make_text_pack_writer('arranger', 0x84)
write_message_packs = make_text_pack_writer('message', 0x85)

def write_disc_identification_packs(output: list[bytes], config: ConverterConfig, input_data: object) -> None:
    if 'catalog' not in input_data['album'] or len(input_data['album']['catalog']) == 0:
        return
    
    write_text_packs(output, config, 0x86, 0, 
                     [input_data['album']['catalog'].encode('ascii').decode('ascii')], False)
    

def write_genre_identification_packs(output: list[bytes], config: ConverterConfig, input_data: object) -> None:
    has_genre = 'genre' in input_data['album']
    has_genre_supplementary = 'genre_sup' in input_data['album'] and len(input_data['album']['genre_sup']) > 0

    if not (has_genre or has_genre_supplementary):
        return
    
    genre_code = ENUM_GENRES.index(input_data['album']['genre_sup']) if has_genre else 0
    genre_text = input_data['album']['genre_sup'] if has_genre_supplementary else ''
    genre_combined = genre_code.to_bytes(2, 'big') + genre_text.encode('ascii')

    write_text_packs(output, config, 0x87, 0, [genre_combined.decode('ascii')], False)


def write_isrc_packs(output: list[bytes], config: ConverterConfig, input_data: object) -> None:
    has_album = 'upc' in input_data['album'] and len(input_data['album']['upc']) > 0
    has_tracks = False

    for track in config.tracks_ordered:
        has_tracks = has_tracks or ('isrc' in track and len(track['isrc'])) > 0

    if not (has_album or has_tracks):
        return
    
    contents = []
    
    if has_album:
        contents.append(input_data['album']['upc'])

    for track in config.tracks_ordered:
        if 'isrc' in track and len(track['isrc']) > 0:
            contents.append(track['isrc'])
        else:
            track_no = track['number']
            raise(CdtException(f'Track {track_no} has no ISRC'))
        
    write_text_packs(output, config, 0x8e, 0 if has_album else 1, contents, False)


def write_block_size_info_packs(output: list[bytes], config: ConverterConfig, input_data: object) -> None:
    pack_counts = 16 * [0]

    for line in output:
        pack_type = line[0] - 0x80
        pack_counts[pack_type] += 1

    pack_counts[15] = 3                                         # always 3 packs of type 0x8f

    pack_counts_bytes = b''.join(map(lambda x: x.to_bytes(1, 'big'), pack_counts))
    max_sequence = config.seq + 2

    output.append(append_crc(
        b'\x8f\x00'
        + config.seq.to_bytes(1, 'little')
        + b'\x00'
        + (b'\x80' if config.mb_strings else b'\x00')           # charset
        + b'\x01'                                               # number of first track
        + len(config.tracks_ordered).to_bytes(1, 'big')         # number of last track
        + (b'\x03' if config.copyrighted else b'\x00')          # is copyrighted?
        + pack_counts_bytes[:8]                                 # pack count, types 0-7
    ))

    config.seq += 1

    output.append(append_crc(
        b'\x8f\x01'
        + config.seq.to_bytes(1, 'little')
        + b'\x00'
        + pack_counts_bytes[8:]                                 # pack count, types 7-f
        + max_sequence.to_bytes(1, 'little')                    # max sequence number
        + b'\x00\x00\x00'
    ))

    config.seq += 1

    output.append(append_crc(
        b'\x8f\x02'
        + config.seq.to_bytes(1, 'little')
        + b'\x00'
        + b'\x00\x00\x00\x00'
        + ENUM_LANGUAGES.index(config.language).to_bytes(1, 'little')   # language code for block 1
        + b'\x00\x00\x00\x00\x00\x00\x00'
    ))

    config.seq += 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simple JSON to CD-Text converter utility')
    parser.add_argument('input', help='path to input JSON file')
    parser.add_argument('output', help='path to save generated CDT file')
    args = parser.parse_args()

    with open('schema.json', 'rb') as schema_file:
        input_schema = json.load(schema_file)

    with open(args.input) as json_file:
        input_data = json.load(json_file)

    jsonschema.validate(input_data, input_schema)

    config = ConverterConfig(
        input_data['meta']['codepage'] == 'ms-jis', # mb_strings
        input_data['meta']['copyrighted'],          # copyrighted
        input_data['meta']['language'],             # language
        0,                                          # seq
        [],                                         # tracks_ordered
    )

    tracks_count = len(input_data['tracks'])

    for i in range(tracks_count):
        track_number = i + 1
        track_found = False
        for track in input_data['tracks']:
            if track['number'] != track_number:
                continue

            config.tracks_ordered.append(track)
            track_found = True
            break

        if not track_found:
            raise(CdtException(f'No metadata found for track {track_number}'))
        
    if tracks_count > 99:
        raise(CdtException('The Compact Disc can\'t have more than 99 tracks'))
    
    output_data: list[bytes] = []

    write_title_packs(output_data, config, input_data)
    write_performer_packs(output_data, config, input_data)
    write_songwriter_packs(output_data, config, input_data)
    write_composer_packs(output_data, config, input_data)
    write_arranger_packs(output_data, config, input_data)
    write_message_packs(output_data, config, input_data)
    write_disc_identification_packs(output_data, config, input_data)
    write_genre_identification_packs(output_data, config, input_data)
    write_isrc_packs(output_data, config, input_data)
    write_block_size_info_packs(output_data, config, input_data)

    if config.seq > 256:
        raise(CdtException('CD-Text data to big (max sequence number exceeded 255)'))

    with open(args.output, 'wb') as output_file:
        for pack in output_data:
            output_file.write(pack)
