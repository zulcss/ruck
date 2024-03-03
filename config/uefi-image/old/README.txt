How to run this demo.

1. Make sure you have systemd-nspawn installed:

   sudo apt-get install -y systemd-container

2. Install ruck:

    sudo pip install -e https://github.com/zulcss/ruck#egg=ruck

3. Run the following commands:

   sudo ruck build --config treefile.yaml
   sudo ruck build --config disk.yaml
   sudo ruck build --config deploy.yaml

3. Run systemd-nspawn

    sudo systemd-nspawn -b -i /var/ruck/exampleos/demo.img
