import importlib.resources

import pytest

from src.checkmate.models.Option import Option
from src.checkmate.util.ConfigurationSpaceReader import ConfigurationSpaceReader


@pytest.fixture()
def sample_config_space():
    return ConfigurationSpaceReader().read_configuration_space(
        str(importlib.resources.path("tests.resources", "SampleConfig.json")))


def test_from_json(sample_config_space):
    assert (sample_config_space.name == "SampleTool" and
            len(sample_config_space.options) == 2)


def test_soundness_optionA(sample_config_space):
    a: Option = sample_config_space.get_option("A")
    assert (a.is_more_sound("A1", "A2") and
            a.is_more_sound("A2", "A3") and
            a.is_more_sound("A1", "A3") and
            a.is_more_sound("A3", "A2") and
            a.is_more_sound("A2", "A1") and
            a.is_more_sound("A3", "A1"))


def test_precision_optionA(sample_config_space):
    a: Option = sample_config_space.get_option("A")
    assert (a.is_more_precise("A3", "A2") and
            a.is_more_precise("A2", "A1") and
            a.is_more_precise("A3", "A1") and
            (not a.is_more_precise("A1", "A2")) and
            (not a.is_more_precise("A2", "A3")) and
            (not a.is_more_precise("A1", "A3")))


def test_soundness_optionB(sample_config_space):
    b: Option = sample_config_space.get_option("B")
    assert (b.is_more_sound(5, 4) and
            b.is_more_sound(112, 7) and
            b.is_more_sound(-1, 10000) and
            b.is_more_sound(-2, -4) and
            (not b.is_more_sound(5, 6)) and
            (not b.is_more_sound(65, -1)) and
            (not b.is_more_sound(-7, 0))
            )
