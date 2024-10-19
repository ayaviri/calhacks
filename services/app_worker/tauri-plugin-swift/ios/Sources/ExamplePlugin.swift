// The Swift Programming Language
// https://docs.swift.org/swift-book
import Foundation
import Tauri

struct PingResponse: Codable {
    let value: String
}

class ExamplePlugin: Plugin {
  @objc public func ping(_ invoke: Invoke) {
    invoke.resolve(PingResponse(value: "PONG!"))
  }
}
@_cdecl("init_plugin_swift")
func initPlugin() -> Plugin {
  return ExamplePlugin()
}
 