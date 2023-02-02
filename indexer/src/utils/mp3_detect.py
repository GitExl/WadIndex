MP3_BITRATES = [
    # Version 2.5
    [
        [0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0, 0], # Reserved
        [0,   8000,  16000,  24000,  32000,  40000,  48000,  56000,  64000,  80000,  96000, 112000, 128000, 144000, 160000, 0],  # Layer 3
        [0,   8000,  16000,  24000,  32000,  40000,  48000,  56000,  64000,  80000,  96000, 112000, 128000, 144000, 160000, 0],  # Layer 2
        [0,  32000,  48000,  56000,  64000,  80000,  96000, 112000, 128000, 144000, 160000, 176000, 192000, 224000, 256000, 0],  # Layer 1
    ],
    # Reserved
    [
        [0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0, 0],  # Invalid
        [0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0, 0],  # Invalid
        [0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0, 0],  # Invalid
        [0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0, 0],  # Invalid
    ],
    # Version 2
    [
        [0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0, 0],  # Reserved
        [0,   8000,  16000,  24000,  32000,  40000,  48000,  56000,  64000,  80000,  96000, 112000, 128000, 144000, 160000, 0],  # Layer 3
        [0,   8000,  16000,  24000,  32000,  40000,  48000,  56000,  64000,  80000,  96000, 112000, 128000, 144000, 160000, 0],  # Layer 2
        [0,  32000,  48000,  56000,  64000,  80000,  96000, 112000, 128000, 144000, 160000, 176000, 192000, 224000, 256000, 0],  # Layer 1
    ],
    # Version 1
    [
        [0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0, 0],  # Reserved
        [0,  32000,  40000,  48000,  56000,  64000,  80000,  96000, 112000, 128000, 160000, 192000, 224000, 256000, 320000, 0],  # Layer 3
        [0,  32000,  48000,  56000,  64000,  80000,  96000, 112000, 128000, 160000, 192000, 224000, 256000, 320000, 384000, 0],  # Layer 2
        [0,  32000,  64000,  96000, 128000, 160000, 192000, 224000, 256000, 288000, 320000, 352000, 384000, 416000, 448000, 0],  # Layer 1
    ]
]


MP3_BYTES_PER_SAMPLE = [
    # Rsv 3   2     1 < Layer  v Version
    [0,  72, 144,  48],  # 2.5
    [0,   0,   0,   0],  # Reserved
    [0,  72, 144,  48],  # 2
    [0, 144, 144,  48],  # 1
]

MP3_SAMPLE_RATE = [
    [11025, 12000, 8000,  0],  # MPEG 2.5
    [0,     0,     0,     0],  # Reserved
    [22050, 24000, 16000, 0],  # MPEG 2
    [44100, 48000, 32000, 0],  # MPEG 1
]


def mp3_detect(input_data: memoryview) -> bool:
    if len(input_data) < 5:
        return False

    if input_data[:3] == b'ID3':
        return True

    consecutive_frames = 0
    i = 0
    scan_len = min(4096, len(input_data) - 4)

    while i < scan_len:
        data = input_data[i:i + 3]
        i += 1

        # Frame sync
        if data[0] != 0xFF and data[1] & 0xE0 != 0xE0:
            consecutive_frames = 0
            continue

        mpeg_version = (data[1] & 0x18) >> 3
        if mpeg_version == 1:
            consecutive_frames = 0
            continue
        mpeg_layer = (data[1] & 0x06) >> 1
        if mpeg_layer == 0:
            consecutive_frames = 0
            continue
        bit_rate = (data[2] & 0xF0) >> 4
        if bit_rate == 15 or bit_rate == 0:
            consecutive_frames = 0
            continue
        sample_rate = (data[2] & 0x0C) >> 2
        if sample_rate == 3:
            consecutive_frames = 0
            continue
        padding = (data[2] & 0x02) >> 1

        sample_rate = MP3_SAMPLE_RATE[mpeg_version][sample_rate]
        bit_rate = MP3_BITRATES[mpeg_version][mpeg_layer][bit_rate]
        bytes_per_sample = MP3_BYTES_PER_SAMPLE[mpeg_version][mpeg_layer]

        if mpeg_layer == 3 and padding:
            padding = 4
        elif padding:
            padding = 1
        else:
            padding = 0

        frame_size = int(((bytes_per_sample * bit_rate) / sample_rate) + padding)
        i += frame_size - 1

        consecutive_frames += 1
        if consecutive_frames > 2:
            return True

    return False
