fn main() {
    // Search for static library. If you are recompiling, comment out the next line and uncomment the build script
    println!("cargo:rustc-link-search=native=src/cpp/etc1_encoder/lib/release/");
    // Link the static library.
    println!("cargo:rustc-link-lib=static=etc1_encoder");

    // BUILD SCRIPT . If you have issues compiling, refer to https://github.com/alexcrichton/cc-rs/#compile-time-requirements
    /*
    let files = vec!["src/cpp/etc1_encoder/src/rg_etc1.cpp", "src/cpp/etc1_encoder/src/etc1_encoder.cpp"];
    cc::Build::new()
    .cpp(true)
    .files(files)
    .include("src/cpp/etc1_encoder")
    .compile("etc1_encoder");
    */
}