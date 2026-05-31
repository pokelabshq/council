class CouncilAgent < Formula
  include Language::Python::Virtualenv

  desc "Self-improving AI agent that creates skills from experience"
  homepage "https://ai-council.pokelabs.com"
  # Stable source should point at the semver-named sdist asset attached by
  # scripts/release.py, not the CalVer tag tarball.
  url "https://github.com/pokelabshq/council/releases/download/v2026.3.30/ai_council-0.6.0.tar.gz"
  sha256 "<replace-with-release-asset-sha256>"
  license "MIT"

  depends_on "certifi" => :no_linkage
  depends_on "cryptography" => :no_linkage
  depends_on "libyaml"
  depends_on "python@3.14"

  pypi_packages ignore_packages: %w[certifi cryptography pydantic]

  # Refresh resource stanzas after bumping the source url/version:
  #   brew update-python-resources --print-only ai-council

  def install
    venv = virtualenv_create(libexec, "python3.14")
    venv.pip_install resources
    venv.pip_install buildpath

    pkgshare.install "skills", "optional-skills"

    %w[council ai-council council-acp].each do |exe|
      next unless (libexec/"bin"/exe).exist?

      (bin/exe).write_env_script(
        libexec/"bin"/exe,
        COUNCIL_BUNDLED_SKILLS: pkgshare/"skills",
        COUNCIL_OPTIONAL_SKILLS: pkgshare/"optional-skills",
        COUNCIL_MANAGED: "homebrew"
      )
    end
  end

  test do
    assert_match "Poke Council v#{version}", shell_output("#{bin}/council version")

    managed = shell_output("#{bin}/council update 2>&1")
    assert_match "managed by Homebrew", managed
    assert_match "brew upgrade ai-council", managed
  end
end
