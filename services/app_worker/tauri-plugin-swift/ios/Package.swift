// swift-tools-version:5.3
import PackageDescription

let package = Package(
    name: "tauri-plugin-swift",  // Updated package name
    platforms: [
        .macOS(.v10_13),
        .iOS(.v13),
    ],
    products: [
        .library(
            name: "tauri-plugin-swift",  // Updated product name
            type: .static,
            targets: ["tauri-plugin-swift"]  // Updated target name
        )
    ],
    dependencies: [
        .package(name: "Tauri", path: "../.tauri/tauri-api")  // Adjust this path if necessary
    ],
    targets: [
        .target(
            name: "tauri-plugin-swift",  // Updated target name
            dependencies: [
                .byName(name: "Tauri")
            ],
            path: "Sources"  // Ensure this is the correct path to your source files
        )
    ]
)
