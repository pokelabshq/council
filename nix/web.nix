# nix/web.nix — Council Web Dashboard (Vite/React) frontend build
{ pkgs, councilNpmLib, ... }:
let
  src = ../web;
  npmDeps = pkgs.fetchNpmDeps {
    inherit src;
    hash = "sha256-HV0aISBVjwbGqDj8qQynSxGFrrZDzuYAW3D3lB/x3zo=";
  };

  npm = councilNpmLib.mkNpmPassthru { folder = "web"; attr = "web"; pname = "council-web"; };

  packageJson = builtins.fromJSON (builtins.readFile (src + "/package.json"));
  version = packageJson.version;
in
pkgs.buildNpmPackage (npm // {
  pname = "council-web";
  inherit src npmDeps version;

  doCheck = false;

  buildPhase = ''
    npx tsc -b
    npx vite build --outDir dist
  '';

  installPhase = ''
    runHook preInstall
    cp -r dist $out
    runHook postInstall
  '';
})
