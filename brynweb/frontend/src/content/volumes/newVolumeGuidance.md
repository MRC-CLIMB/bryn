#### How to use a volume after attachment

First, find the device ID of the volume that you’ve just attached:

```
lsblk
```

You'll see something like

```
sda    253:0    0  120G  0 disk
└─sda1 253:1    0  120G  0 part /
sdb    253:16   0    2T  0 disk /home/ubuntu/sdb
sdc    253:32   0    2T  0 disk
```

Here the there are two attached volumes: `/dev/sdb`, which is already mounted, and `dev/sdc`, which has just been attached.

Next, create a filesystem on the newly attached volume…

**Creating a filesystem on a volume is DESTRUCTIVE, see the WARNING below!**

To create a filesystem, run the command:

```
sudo mkfs.xfs /dev/sdc
```

This will create the filesystem. Then you can mount the volume in your space:

```
mkdir example
sudo mount /dev/sdc example/
```

because the volume will have been mounted as root, you need to make sure that your user has ownership. In this example the user is ubuntu:

```
sudo chown ubuntu:ubuntu example/
```

At that point you should be able to use the volume you have created;

```
lsblk

NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
sda    253:0    0  120G  0 disk
└─sda1 253:1    0  120G  0 part /
sdb    253:16   0    2T  0 disk /home/ubuntu/sdb
sdc    253:32   0    2T  0 disk /home/ubuntu/example
```

**WARNING!**
**After you reboot your instance, your volumes will be UNMOUNTED but still ATTACHED.**

To remount them, simply

```
lsblk
```

To find the device name (looks like /dev/sdX), then

```
mount /dev/sdX [mountpoint]
```

**DO NOT RUN `mkfs.xfs` OR `fdisk` ON A VOLUME THAT CONTAINS DATA, IT WILL DESTROY ALL DATA ON THE VOLUME!**
