cask "compositor" do
  version "1.4.8"
  sha256 "c0a33fc100619978b7a7fe27ab26c9b41d39202666edf73f246ce1d25c9b0f9b"

  url "https://github.com/robbietilton/Compositor/releases/download/v#{version}/Compositor.dmg"
  name "Compositor"
  desc "Image editor"
  homepage "https://github.com/robbietilton/Compositor"

  livecheck do
    url :url
    strategy :github_latest
  end

  auto_updates true
  depends_on macos: :tahoe

  app "Compositor.app"

  caveats <<~EOS
    Compositor requires macOS 26.5 or later.
  EOS
end
