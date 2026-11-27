# -*- coding: utf-8 -*-
import importlib.metadata

# Récupération de la version
try:
  __version__ = importlib.metadata.version("pynsee")
except importlib.metadata.PackageNotFoundError:
  __version__ = "0.3.1"

# Définition unique des headers pour toutes les requêtes du module melodi
HEADERS = {"User-Agent": f"pynsee {__version__}"}
