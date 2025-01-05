{
  description = "Development shell.";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
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
      debug = false;

      perSystem =
        {
          pkgs,
          lib,
          self',
          ...
        }:
        {
          packages = rec {
            default = ai-summary;
            ai-summary = pkgs.python3Packages.buildPythonApplication {
              pname = "ai-summary";
              version = "0.1.0";
              pyproject = true;

              src = ./.;

              build-system = with pkgs.python3Packages; [ setuptools ];

              dependencies = with pkgs.python3Packages; [
                openai
                python-frontmatter
              ];

            };
          };
          devShells.default = pkgs.mkShell {
            venvDir = ".venv";
            inputsFrom = [ self'.packages.default ];
            packages =
              with pkgs;
              [
                python3
                self'.packages.default
              ]
              ++ (with pkgs.python3Packages; [
                pip
                venvShellHook
              ]);

            # postVenvCreation = ''
            #   unset SOURCE_DATE_EPOCH
            #   pip install .
            # '';
            #
            # postShellHook = ''
            #   # allow pip to install wheels
            #   unset SOURCE_DATE_EPOCH
            # '';
          };
        };
    };
}
