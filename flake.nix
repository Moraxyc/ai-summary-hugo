{
  description = "Development shell.";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    pre-commit-hooks = {
      url = "github:cachix/pre-commit-hooks.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    {
      self,
      nixpkgs,
      poetry2nix,
      flake-parts,
      ...
    }@inputs:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      debug = false;

      perSystem =
        {
          pkgs,
          lib,
          self',
          system,
          ...
        }:
        {
          checks = {
            pre-commit-check = inputs.pre-commit-hooks.lib.${system}.run {
              src = ./.;
              hooks = {
                black.enable = true;
                check-builtin-literals.enable = true;
                check-python.enable = true;
                check-added-large-files.enable = true;
                check-merge-conflicts.enable = true;
                detect-private-keys.enable = true;
                commitizen.enable = true;
              };
            };
          };
          devShells.default = pkgs.mkShell {
            inherit (self.checks.${system}.pre-commit-check) shellHook;
            buildInputs = self.checks.${system}.pre-commit-check.enabledPackages ++ [
              (pkgs.writeShellScriptBin "ai-summary" ''
                exec python -m app "$@"
              '')
            ];
            packages =
              let
                p2n = poetry2nix.lib.mkPoetry2Nix { inherit pkgs; };
                pythonEnv = p2n.mkPoetryEnv {
                  python = pkgs.python312;
                  projectDir = ./.;
                  overrides = p2n.overrides.withDefaults (
                    _final: prev: {
                      openai = prev.openai.overridePythonAttrs (_old: {
                        buildInputs = _old.buildInputs ++ (with pkgs.python312Packages; [ hatch-fancy-pypi-readme ]);
                      });
                    }

                  );
                };
              in
              with pkgs;
              [
                poetry
                #pythonEnv
              ];
          };
        };
    };
}
