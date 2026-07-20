{
  description = "Generate summary.json for Hugo sites with LLM-generated article summaries.";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-parts = {
      url = "github:hercules-ci/flake-parts";
      inputs.nixpkgs-lib.follows = "nixpkgs";
    };
    git-hooks = {
      url = "github:cachix/git-hooks.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    {
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

      perSystem =
        {
          pkgs,
          lib,
          self',
          system,
          ...
        }:
        let
          pythonPackages = pkgs.python3Packages;

          pre-commit-check = inputs.git-hooks.lib.${system}.run {
            src = ./.;
            hooks = {
              ruff.enable = true;
              ruff-format.enable = true;
              end-of-file-fixer.enable = true;
              trim-trailing-whitespace.enable = true;
              mixed-line-endings.enable = true;
              check-added-large-files.enable = true;
              check-merge-conflicts.enable = true;
              check-toml.enable = true;
              check-yaml.enable = true;
            };
          };
        in
        {
          packages = rec {
            default = ai-summary;

            ai-summary = pythonPackages.buildPythonApplication {
              pname = "ai-summary";
              version = "0.1.0";
              pyproject = true;

              src = ./.;

              build-system = [ pythonPackages.setuptools ];

              dependencies = [
                pythonPackages.openai
                pythonPackages.python-frontmatter
              ];
            };
          };

          checks = {
            inherit pre-commit-check;
          };

          devShells.default = pkgs.mkShell {
            name = "ai-summary-dev";
            packages = [
              pkgs.uv
            ];
            inputsFrom = [ pre-commit-check ];
          };
        };
    };
}
