# ******************************************************************************
# Copyright (c) 2026 RoXimn <roximn148@gmail.com> Licensed under the MIT License
# ******************************************************************************
from romanalfaz import urduspell
from romanalfaz.normalization import NORMALIZATION_METHODS, NormalizationMethod


# ******************************************************************************
class TestRegistry:
    def testUrduSpellRegistered(self):
        """The registry exposes the urdu-spell method backed by urduspell.normalize."""
        method = NORMALIZATION_METHODS["urdu-spell"]
        assert isinstance(method, NormalizationMethod)
        assert method.name == "urdu-spell"
        assert method.function is urduspell.normalize

    def testMethodDescribesScopeAndStages(self):
        """Each entry states its scope and its ordered pipeline stages."""
        method = NORMALIZATION_METHODS["urdu-spell"]
        assert method.description.strip()
        assert len(method.stages) >= 1
        assert all(isinstance(stage, str) and stage.strip() for stage in method.stages)
