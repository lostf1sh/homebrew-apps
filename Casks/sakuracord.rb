cask "sakuracord" do
  version "0.1.5"
  sha256 "14f368797d8b6baf6a171f8fff9d7d496fadd3da07a9f731e71b788a63db0a64"

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
