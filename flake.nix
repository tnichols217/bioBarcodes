{
  description = "Dev shell";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = nixpkgs.legacyPackages.${system};
    in {
      devShell = pkgs.mkShell {
        nativeBuildInputs = with pkgs; [
          python310
          python310Packages.cairosvg
          python310Packages.pypdf2
          python310Packages.qrcode
          python310Packages.python-barcode
          python310Packages.svgwrite
        ];
        buildInputs = [ ];
      };
    });
}