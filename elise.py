import os
import sys


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'src'))

from elise.cli import main
from elise.config import ELISE_ENV, ELISE_ENV_CARTRIDGE

__all__ = ['ELISE_ENV', 'ELISE_ENV_CARTRIDGE']


if __name__ == '__main__':
    main()
