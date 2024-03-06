1. This vagrant box depends on the libvirt vagrant plugin. The instructions can be
   found at: https://vagrant-libvirt.github.io/vagrant-libvirt/installation.html#ubuntu--debian

2. Once vagrant is installed run: vagrant up.

3. To ssh into the machine: vagrant ssh

4. Configure DNS by specifying your DNS settings in /etc/systemd/resolve.conf
   and restarting the systemd-resolved service.

