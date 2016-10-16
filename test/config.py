from test.models import get_without_failing, Config
from test.utils import scrap_jars_and_save


def install_if_required():
    if get_without_failing(Config, (Config.name == 'password'), None) is None:
        scrap_jars_and_save()
