// Include path declared in build.rs
#include "include/etc1_encoder.h"

// Source: https://github.com/Cruel/3dstex/blob/5cdd9a149239a54242368e604810ed0de6ae040c/src/Encoder.cpp
extern "C" {	
	void encodeETC1(const uint8_t *inputData, uint8_t **outputData, uint16_t width, uint16_t height, bool hasAlpha)
	{
		*outputData = new uint8_t[(width * height * 4)/8];
		uint8_t *ptrOut = *outputData;
		g_width = width;
		g_height = height;
		g_hasAlpha = hasAlpha; 
		g_etc1params.m_quality = static_cast<rg_etc1::etc1_quality>(0);
		rg_etc1::pack_etc1_block_init();
		
		// Loop through 8x8 blocks
		for (int y = 0; y < g_height; y += 8)
			for (int x = 0; x < g_width; x += 8)
				// Loop through the four 4x4 sub-blocks that will be compressed
				for (int i = 0; i < 8; i += 4)
					for (int j = 0; j < 8; j += 4)
					{
						// TODO: Add threading to block packing
						encodeETC1Block(x + j, y + i, inputData, ptrOut);
						ptrOut += (g_hasAlpha == true) ? 16 : 8;
					}
	}

	void encodeETC1Block(int blockX, int blockY, const uint8_t *inputData, uint8_t *ptrOut)
	{
		const uint32_t *data32 = reinterpret_cast<const uint32_t*>(inputData);

		uint64_t block = 0;
		uint32_t pixels[4 * 4] = {0};
		
		uint8_t alpha;
		uint32_t alphaCount = 0;

		for (int y = 0; y < 4; y++)
			for (int x = 0; x < 4; x++)
			{
				int posX = blockX + x;
				int posY = g_height - 1 - (blockY + y);
				
				// Make sure pixel is in bounds of original dimensions
				if (posX < g_width && posY < g_height)
					pixels[y * 4 + x] = data32[posY * g_width + posX];
				
				if (g_hasAlpha == true)
				{
					// Invert x/y axis for alpha block order
					posX = blockX + y;
					posY = g_height - 1 - (blockY + x);
					alpha = 0;
					if (posX < g_width && posY < g_height)
						alpha = inputData[(posY * g_width + posX) * 4 + 3];
					alpha >>= 4;
					block |= static_cast<uint64_t>(alpha) << (alphaCount * 4);
					alphaCount++;
				}	
			}
		
		if (g_hasAlpha == true)
		{
			std::memcpy(ptrOut, &block, 8);
			ptrOut += 8;
		}

		rg_etc1::pack_etc1_block(&block, pixels, g_etc1params);
		block = _byteswap_uint64(block);
		std::memcpy(ptrOut, &block, 8);
	}

	void free_ptr(uint8_t *res)
    {
        delete[] res;
    }
}