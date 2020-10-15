fn main() {
    println!("cargo:rustc-link-lib=static=etc1_encoder");
    let files = vec!["src/cpp/etc1_encoder/rg_etc1.cpp", "src/cpp/etc1_encoder/etc1_encoder.cpp"];
    cc::Build::new()
    .cpp(true)
    .files(files)
    .include("src/cpp/etc1_encoder/include")
    .compile("etc1_encoder");
}