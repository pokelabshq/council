# nix/tui.nix — Council TUI (Ink/React) compiled with tsc and bundled
{ pkgs, councilNpmLib, ... }:
let
  src = ../ui-tui;
  npmDeps = pkgs.fetchNpmDeps {
    inherit src;
    hash = "sha256-F6/MzZOWc0zhW9mIfnaY+PrllPvJcsA/OdFdEM+NpLY=";
  };

  npm = councilNpmLib.mkNpmPassthru { folder = "ui-tui"; attr = "tui"; pname = "council-tui"; };

  packageJson = builtins.fromJSON (builtins.readFile (src + "/package.json"));
  version = packageJson.version;
in
pkgs.buildNpmPackage (npm // {
  pname = "council-tui";
  inherit src npmDeps version;

  doCheck = false;
  npmFlags = [ "--legacy-peer-deps" ];

  installPhase = ''
    runHook preInstall

    mkdir -p $out/lib/council-tui

    # Single self-contained bundle built by scripts/build.mjs (esbuild).
    cp -r dist $out/lib/council-tui/dist

    # package.json kept for "type": "module" resolution on `node dist/entry.js`.
    cp package.json $out/lib/council-tui/

    runHook postInstall
  '';
})
