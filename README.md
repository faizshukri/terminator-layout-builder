# Terminator Layout Builder

Manage [Terminator](https://terminator-gtk3.readthedocs.io/en/latest/) layouts easily using YAML file.

![Terminator Layout Builder](https://s3-ap-southeast-1.amazonaws.com/com.faizsh.misc/terminator-layout-builder.gif#1)

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
  - root: $HOME/project # root for this window
    vertical:
      panes:
        - cmd: pwd && echo $SHELL
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
            ratio: 0.5
            panes:
              - vertical:
                  ratio: 0.67
                  panes:
                    - title: "some title"
                      cmd: pwd
                    - root: "~" # overwrite window's root
                      cmd: pwd
              - cmd: tail -f /var/log/syslog
        - horizontal:
            panes:
              - cmd: tail -f /dev/null
              - cmd: tail -f /dev/null
        - cmd: htop
```

Next, run `tlb` and the layouts will be merge into your Terminator config, and you can start your layout by using Terminator Layout Launcher.

Alternatively, you can also use `tlb -l <layout>` (alias to `terminator -u -m -b -l <layout>`) to launch your Terminator with the layout.

## Inspirations

- [Tmuxinator](https://github.com/tmuxinator/tmuxinator)
- [Terminator layout builder gist](https://gist.github.com/bancek/3838394)
