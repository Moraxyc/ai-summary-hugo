{
  description = "Generate summary.json for Hugo sites with LLM-generated article summaries.";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    systems.url = "github:nix-systems/triplet";
    flake-parts = {
      url = "github:hercules-ci/flake-parts";
      inputs.nixpkgs-lib.follows = "nixpkgs";
    };
    git-hooks = {
      url = "github:cachix/git-hooks.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    {
      flake-parts,
      pyproject-nix,
      uv2nix,
      pyproject-build-systems,
      ...
    }@inputs:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = import inputs.systems;

      perSystem =
        {
          pkgs,
          lib,
          config,
          system,
          ...
        }:
        let
          python = pkgs.python3;

          inherit (pkgs.callPackages pyproject-nix.build.util { }) mkApplication;

          workspace = uv2nix.lib.workspace.loadWorkspace {
            workspaceRoot = ./.;
          };

          overlay = workspace.mkPyprojectOverlay {
            sourcePreference = "wheel";
          };

          pythonSet =
            (pkgs.callPackage pyproject-nix.build.packages {
              inherit python;
            }).overrideScope
              (
                lib.composeManyExtensions [
                  pyproject-build-systems.overlays.wheel
                  overlay
                ]
              );
        in
        {
          packages = {
            default = config.packages.ai-summary;
            ai-summary = mkApplication {
              venv = pythonSet.mkVirtualEnv "ai-summary-env" workspace.deps.default;
              package = pythonSet."ai-summary";
            };
          };

          checks = {
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
          };

          devShells.default = pkgs.mkShell {
            name = "ai-summary-dev";
            packages = [
              pkgs.uv
            ];
            inputsFrom = [ config.checks.pre-commit-check ];
          };
        };
    };
}
