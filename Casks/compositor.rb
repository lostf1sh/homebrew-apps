cask "compositor" do
  version "1.4.6"
  sha256 "9c8ce0f8f4f936a2a044215f3966045d8f8b346db0906b55b66173f60fc1ba46"

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
