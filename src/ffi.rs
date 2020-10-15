pub mod etc1_encoder {
    #[link(name = "etc1_encoder", kind="static")]
    extern "C" {
        pub fn encodeETC1(input_data: *const u8, output_data: &mut *mut u8, width: u16, height: u16, has_alpha: bool);
        pub fn free_ptr(res: *mut u8);
    }    
}
