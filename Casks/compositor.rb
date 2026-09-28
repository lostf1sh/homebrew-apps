cask "compositor" do
  version "1.4"
  sha256 "6815b1515c9d7d222228b21643f49c5f38a5ea391c29d38af6bfe16c6a3c2c31"

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
