cask "sakuracord" do
  version "0.1.6"
  sha256 "6e9513a4d0c4bbbf13db107b3566dcfb995d478448df82271fc529202b6b0389"

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
