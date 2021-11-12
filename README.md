# detection
Detection de personnes avec Realsense et Coral

### Installation
Testée avec Debian 11 Bullseye

Les packages python sont installés dans un virtualenv parce que c'est facile, ça marche bien, c'est la bonne façon de procéder.

#### RealSense D 455

``` bash
sudo apt-key adv --keyserver keys.gnupg.net --recv-key F6E65AC044F831AC80A06380C8B3A55A6F3EFCDE || sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-key F6E65AC044F831AC80A06380C8B3A55A6F3EFCDE
sudo apt install software-properties-common
sudo add-apt-repository "deb https://librealsense.intel.com/Debian/apt-repo focal main" -u
sudo apt install librealsense2-dkms
```

#### Coral

``` bash
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
sudo apt install curl
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt update
sudo apt install python3-tflite-runtime edgetpu-compiler gasket-dkms
sudo apt install python3-pycoral libedgetpu1-std
```

#### Python
Installe tous les packages nécessaires dans un dossier /mon_env dans le dossier /grande_echelle

``` bash
# Mise à jour de pip
sudo apt install python3-pip
python3 -m pip install --upgrade pip

# Installation de venv
sudo apt install python3-venv

# Installation de l'environnement
cd /le/dossier/de/grande_echelle/

# Création du dossier environnement si pas encore créé, l'argument --system-site-packages permet d'utiliser les packages système où est pycoral
python3 -m venv --system-site-packages mon_env

# Activation
source mon_env/bin/activate

# Installation des packages, numpy, opencv-python, pyrealsense2, kivy
python3 -m pip install -r requirements.txt
```


### LICENSE

#### Apache License, Version 2.0

* pose_engine.py
* posenet_histopocene.py
* pyrealsense2

#### Licence GPL v3

* tous les autres fichiers

#### Creative Commons

[Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International Public License](http://oer2go.org/mods/en-boundless/creativecommons.org/licenses/by-nc-nd/4.0/legalcode.html)
