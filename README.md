# st-archive

Script that takes a file and hardlinks / copies it to a folder based on certain rules.

Originally written for use with Syncthing to preserve files on my NAS.

## Usage

Create a `config.ini` file in `$HOME/.config/st-archive` (obeys `$XDG_CONFIG_HOME`).
See the example file for details.

To run, execute the script and pass the path of a file to it:

```
python3 /path/to/st-archive.py $FILENAME
```

My remote machine uses `incron` to process incoming files; an example `incrontab` entry I use is
this (`st-archive` being executable):

```
/srv/share/.syncthing-targets/my-phone-DCIM/Camera IN_MOVED_TO /home/me/.local/bin/st-archive $@/$#
```

In this instance, Syncthing is configured to share
`/srv/share/.syncthing-targets/my-phone-DCIM` with `/storage/emulated/0/DCIM`.

I also have `crontab` configured to remove files older than two weeks from
`/srv/share/.syncthing-targets/my-phone-DCIM/Camera`, and those deletes are synchronized
to my phone.

## License

Released under BSD0.

Feel free to fork and patch.  I don't intend to do maintenance or add features to this.
