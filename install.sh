#!/usr/bin/env bash

repo_url="https://github.com/immortal-forest/gtk-emoji-keyboard.git"
install_dir="/opt/gtk-emoji-keyboard"
user_name="$(whoami)"  # Get current username

echo "Installing GTK Emoji Keyboard to $install_dir"

echo "=> Cloning the repo"
# Clone the repository
sudo git clone $repo_url $install_dir

echo "=> Creating a virtual environment"
# Create virtual environment
sudo python -m venv $install_dir/venv

echo "=> Updating folder ownership"
# Update folder ownership
sudo chown -R $user_name $install_dir

echo "=> Installing dependencies"
# Install requirements
source $install_dir/venv/bin/activate  # Activate virtual environment
pip install -r $install_dir/requirements.txt  # Install dependencies

echo "=> Copying to /usr/bin"
# creating a link to emoji.sh
sudo cp -f $install_dir/emoji_keyboard.sh /usr/bin/emoji_keyboard.sh

echo "=> Updating file permissions"
# updating permissions
#sudo chmod +x $install_dir/*.sh
sudo chmod 755 /usr/bin/emoji_keyboard.sh

echo "Installation complete!"
