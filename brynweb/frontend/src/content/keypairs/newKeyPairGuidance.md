### SSH key help

A quick guide on how to create SSH keys.

##### Create a new key pair on your machine:

If you don't have one yet, you'll need to create one. Open a terminal and run:

```
ssh-keygen
```

Follow the prompts to give the key a name and save the key (or accept the defaults). You are advised to protect your key with a passphrase.

```
Generating public/private rsa key pair. Enter file in which to save the key (/Users/USER/.ssh/id_rsa):
```

This will generate two files (in `/Users/USER/.ssh/`, if you accepted the defaults). `id_rsa` is your private key, and `id_rsa.pub` is your public key. It's the contents of the public key file that you'll need for this form.

To output the contents of this file to your teminal, run:

```
cat ~/.ssh/id_rsa.pub
```

You can copy this output and paste it into the form on the left.
