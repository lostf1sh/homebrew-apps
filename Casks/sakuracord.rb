cask "sakuracord" do
  version "0.1.6"
  sha256 "4a2c3cf2494b3ad3862d9cec83d9c4efea7a25cd821acc00ba8cf16ab441bd9a"

  url "https://github.com/SakuraCordApp/SakuraCord/releases/download/v#{version}/SakuraCord.v#{version}.dmg"
  name "SakuraCord"
  desc "Native Discord client"
  homepage "https://github.com/SakuraCordApp/SakuraCord"

  livecheck do
    url :url
    strategy :github_latest
  end

  auto_updates true
  depends_on arch: :arm64
  depends_on macos: :golden_gate

  app "SakuraCord.app"

  postflight_steps do
    run "/usr/bin/xattr",
        args:           ["-cr", "{{appdir}}/SakuraCord.app"],
        writable_paths: ["SakuraCord.app"],
        writable_base:  :appdir
  end
end
