// The Swift Programming Language
// https://docs.swift.org/swift-book
import Foundation
import Tauri
import Metal

struct PingResponse: Codable {
    let value: String
}

struct GPUResponse: Codable {
    let value: String
}

class ExamplePlugin: Plugin {
  @objc public func ping(_ invoke: Invoke) {
    invoke.resolve(PingResponse(value: "PONG!"))
  }

  @objc public func graphics(_ invoke: Invoke) {
    let allInfo: String;

    if let device = MTLCreateSystemDefaultDevice() {
        let gpuName = device.name
        
        allInfo = gpuName
    } else {
        allInfo = "No GPU available"
    }

    invoke.resolve(GPUResponse(value: allInfo));
  }
}
@_cdecl("init_plugin_swift")
func initPlugin() -> Plugin {
  return ExamplePlugin()
}
