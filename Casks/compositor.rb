cask "compositor" do
  version "1.2.2"
  sha256 "e96d70a5b835ced1844b9f0f10527530d4e00a49e1695835de2f7873288c6e96"

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
