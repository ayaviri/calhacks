use tauri::{
  plugin::{Builder, TauriPlugin},
  Manager, Runtime,
};

pub use models::*;

#[cfg(desktop)]
mod desktop;
#[cfg(mobile)]
mod mobile;

mod commands;
mod error;
mod models;

pub use error::{Error, Result};

#[cfg(desktop)]
use desktop::Swift;
#[cfg(mobile)]
use mobile::Swift;

/// Extensions to [`tauri::App`], [`tauri::AppHandle`] and [`tauri::Window`] to access the swift APIs.
pub trait SwiftExt<R: Runtime> {
  fn swift(&self) -> &Swift<R>;
}

impl<R: Runtime, T: Manager<R>> crate::SwiftExt<R> for T {
  fn swift(&self) -> &Swift<R> {
    self.state::<Swift<R>>().inner()
  }
}

/// Initializes the plugin.
pub fn init<R: Runtime>() -> TauriPlugin<R> {
  Builder::new("swift")
    .invoke_handler(tauri::generate_handler![commands::ping])
    .invoke_handler(tauri::generate_handler![commands::graphics])
    .setup(|app, api| {
      #[cfg(mobile)]
      let swift = mobile::init(app, api)?;
      #[cfg(desktop)]
      let swift = desktop::init(app, api)?;
      app.manage(swift);
      Ok(())
    })
    .build()
}
