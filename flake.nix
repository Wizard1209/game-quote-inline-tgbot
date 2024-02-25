{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        packages = with pkgs; [
          python3Packages.aiogram
        ];

        dev_packages = with pkgs; [
          pdm
          ruff
        ];

        game-quote-inline-tgbot = with pkgs.python3Packages;
          buildPythonApplication {
            pname = "game-quote-inline-tgbot";
            version = "0.1dev";
            pyproject = false;

            src = ./.;

            nativeBuildInputs = [
              pdm-backend
            ];

            propagatedBuildInputs = packages;

            doCheck = false;

            meta = {
              description = "";
              license = pkgs.lib.licenses.mit;
            };
          };
      in
      {
        packages.game-quote-inline-tgbot = game-quote-inline-tgbot;
        packages.default = self.packages.${system}.game-quote-inline-tgbot;

        apps.game-quote-inline-tgbot = {
          type = "app";
          program = "${self.packages.${system}.game-quote-inline-tgbot}/bin/game-quote-inline-tgbot";
        };

        apps.default = self.apps.${system}.game-quote-inline-tgbot;
        defaultPackage = self.packages.${system}.game-quote-inline-tgbot;

        devShells.default = pkgs.mkShell {
          allowBroken = true;
          packages = with pkgs; [
            python312
          ] ++ packages ++ dev_packages;
        };
      });
}
