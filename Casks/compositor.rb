cask "compositor" do
  version "1.2.1"
  sha256 "c6988499c6295be954ada48447e79734f85ef70a3edb0be69913e7c76bb04d0f"

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
