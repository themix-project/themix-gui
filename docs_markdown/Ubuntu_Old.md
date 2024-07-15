Installation in Ubuntu
======================

For Debian 9+, Ubuntu 17.04+ or Linux Mint 19+ you can download `oomox.deb` package here:
https://github.com/themix-project/oomox/releases
Make sure what `universe` repository is enabled.

```sh
sudo apt install ./oomox_VERSION_17.04+.deb  # or ./oomox_VERSION_18.10+.deb for Ubuntu 18.10+
```

Or, if you don't want to install third-party binary package you can build it on your own:

```sh
# with docker:
sudo systemctl start docker
sudo ./packaging/ubuntu/docker_ubuntu_package.sh  # sudo is not needed if your user is in docker group

# or directly from ubuntu host if you don't like docker:
./packaging/ubuntu/create_ubuntu_package.sh control
# or ./packaging/ubuntu/create_ubuntu_package.sh control_1810
```


For older releases install the dependencies manually and next follow general installation instructions [below](#installation-1 "").
 - [List of dependencies](https://github.com/themix-project/oomox/blob/master/packaging/ubuntu/control#L5)
 - [How to install `sassc>=3.4`](https://askubuntu.com/questions/849057/how-to-install-libsass-on-ubuntu-16-04)
