fn main() {
    // Search for static library. If you are recompiling, comment the next link and uncomment the build script
    println!("cargo:rustc-link-search=native=src/cpp/etc1_encoder/lib/release/");
    // Link the static library.
    println!("cargo:rustc-link-lib=static=etc1_encoder");

    /* BUILD SCRIPT . If you have issues compiling, refer to https://github.com/alexcrichton/cc-rs/#compile-time-requirements
    let files = vec!["src/cpp/etc1_encoder/rg_etc1.cpp", "src/cpp/etc1_encoder/etc1_encoder.cpp"];
    cc::Build::new()
    .cpp(true)
    .files(files)
    .include("src/cpp/etc1_encoder/include")
    .compile("etc1_encoder");
    */
}