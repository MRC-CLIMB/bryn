### Server guidelines

##### Flavor

The flavor determines the virtualised resources that are allocated to your server (vCPU cores, RAM). For most use cases, `climb.user` should be selected.

#### Image

The image to use for your boot disk, choose whichever operating system suits your needs. If you're not sure, select the latest version of Ubuntu.

##### SSH Key

Choose one of your public SHH keys. This will be added to the `~/.ssh/authorized_keys` file on you new server instance, allowing you to connect via SSH.

##### Server name

A descriptive name for this server. It can contain letters, numbers and hyphens, and it needs to be unique on your tenant.
