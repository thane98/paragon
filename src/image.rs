use std::io::Result;
use std::cmp::*;

pub fn fade(pixel_data_ptr: &[u8]) -> Result<Vec<u8>> {
    let black_a = 113.0/255.0;
    let mut pixel_data = pixel_data_ptr.to_vec();
    for i in (0..pixel_data_ptr.len()).step_by(4) {
        if pixel_data[i+3] <= 0 {continue};
        let dst_a = (pixel_data[i+3] as f64) / 255.0;
        pixel_data[i+0] = ((((pixel_data[i+0] as f64) / 255.0) * dst_a * (1.0 - black_a) * 255.0).round()) as u8;
        pixel_data[i+1] = ((((pixel_data[i+1] as f64) / 255.0) * dst_a * (1.0 - black_a) * 255.0).round()) as u8;
        pixel_data[i+2] = ((((pixel_data[i+2] as f64) / 255.0) * dst_a * (1.0 - black_a) * 255.0).round()) as u8;
    }
    Ok(pixel_data)
}

pub fn recolor(pixel_data_ptr: &[u8], color: raster::Color) -> Result<Vec<u8>> {
    let mut pixel_data = pixel_data_ptr.to_vec();
    for i in (0..pixel_data_ptr.len()).step_by(4) {
        if pixel_data[i+3] > 0 {
            pixel_data[i+0] = blend_overlay(color.r, pixel_data[i+0])?;
            pixel_data[i+1] = blend_overlay(color.g, pixel_data[i+1])?;
            pixel_data[i+2] = blend_overlay(color.b, pixel_data[i+2])?;
        }
    }
    Ok(pixel_data)
} 
fn blend_overlay(src: u8, dst : u8) -> Result<u8> {
    if dst < 128 {
        Ok(max(min(((src as f64 / 255.0 * dst as f64 / 255.0) * 255.0 * 2.0) as u8, 255), 0) as u8)
    }
    else {
        Ok(max(min((255.0 - ((255 - src) as f64 / 255.0 * (255 - dst) as f64 / 255.0) * 255.0 * 2.0) as u8, 255), 0) as u8)
    }
}