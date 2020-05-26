# Terminator Layout Builder

Manage [Terminator](https://terminator-gtk3.readthedocs.io/en/latest/) layouts easily using YAML file.

## Installation

```bash
pip install terminator-layout-builder
```

## Usage

Create a layout file in `~/.config/terminator/layout.yaml`.

The file can contain a layout as simplest as this.

```yaml
layoutA:
  - cmd: pwd
```

or as complex as this

```yaml
layoutA:
  - cmd: pwd

layoutB:
  # A window
  - root: "/home/user" # root for this window
    vertical:
      panes:
        - cmd: pwd
        - cmd: whoami

  # Another window
  - root: "/tmp"
    tabs:
      labels:
        - Logs
        - Services
        - Monitoring
      items:
        - horizontal:
            ratio: 0.66
            panes:
              - vertical:
                  ratio: 0.5
                  panes:
                    - title: "some title"
                      cmd: pwd
                    - root: /home/faiz # overwrite window's root
                      cmd: pwd
              - cmd: tail -f /dev/null
        - horizontal:
            panes:
              - cmd: tail -f /dev/null
              - cmd: tail -f /dev/null
        - cmd: htop
```

Next, run `tlb` and the layouts will be merge into your Terminator config, and you and start your layout by using Terminator Layout Launcher.

## Inspirations

- [Tmuxinator](https://github.com/tmuxinator/tmuxinator)
- [Terminator layout builder gist](https://gist.github.com/bancek/3838394)
