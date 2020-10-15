#pragma once
#include <stdint.h>
#include <stdlib.h>
#include <memory>
#include "rg_etc1.h"

extern "C" {
    uint16_t g_height;
    uint16_t g_width;
    bool g_hasAlpha;
    rg_etc1::etc1_pack_params g_etc1params;

	void encodeETC1Block(int blockX, int blockY, const uint8_t *inputData, uint8_t *outputData);
	void encodeETC1(const uint8_t *inputData, uint8_t **outputData, uint16_t width, uint16_t height, bool hasAlpha);
}