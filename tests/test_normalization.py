# ******************************************************************************
# Copyright (c) 2026 RoXimn <roximn148@gmail.com>
# This source code is licensed under the MIT license found in the
# LICENSE.txt file in the root directory of this source tree.
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
        assert method.normalize is urduspell.normalize

    def testMethodDescribesScopeAndStages(self):
        """Each entry states its scope and its ordered pipeline stages."""
        method = NORMALIZATION_METHODS["urdu-spell"]
        assert method.description.strip()
        assert len(method.stages) >= 1
        assert all(isinstance(stage, str) and stage.strip() for stage in method.stages)
