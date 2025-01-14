# Copyright: (c) 2023, Dell Technologies

# Apache License version 2.0 (see MODULE-LICENSE or http://www.apache.org/licenses/LICENSE-2.0.txt)

"""Unit Tests for replication pair module on PowerFlex"""

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import pytest
from mock.mock import MagicMock
from ansible_collections.dellemc.powerflex.tests.unit.plugins.module_utils.mock_replication_pair_api import MockReplicationPairApi
from ansible_collections.dellemc.powerflex.tests.unit.plugins.module_utils.mock_api_exception \
    import MockApiException
from ansible_collections.dellemc.powerflex.plugins.module_utils.storage.dell \
    import utils

utils.get_logger = MagicMock()
utils.get_powerflex_gateway_host_connection = MagicMock()
utils.PowerFlexClient = MagicMock()

from ansible.module_utils import basic
basic.AnsibleModule = MagicMock()
from ansible_collections.dellemc.powerflex.plugins.modules.replication_pair import PowerFlexReplicationPair


class TestPowerflexReplicationPair():

    get_module_args = MockReplicationPairApi.REPLICATION_PAIR_COMMON_ARGS

    @pytest.fixture
    def replication_pair_module_mock(self):
        replication_pair_module_mock = PowerFlexReplicationPair()
        replication_pair_module_mock.get_rcg = MagicMock(return_value={"id": 123})
        replication_pair_module_mock.module.check_mode = False
        return replication_pair_module_mock

    def test_get_pair_details(self, replication_pair_module_mock):
        self.get_module_args.update({
            "pair_name": "test_pair",
            "pairs": None,
            "state": "present"
        })
        replication_pair_module_mock.module.params = self.get_module_args
        replication_pair_resp = MockReplicationPairApi.get_pair_details()
        replication_pair_module_mock.powerflex_conn.replication_pair.get = MagicMock(
            return_value=replication_pair_resp
        )
        replication_pair_module_mock.perform_module_operation()
        replication_pair_module_mock.powerflex_conn.replication_pair.get.assert_called()

    def test_get_pair_details_with_exception(self, replication_pair_module_mock):
        self.get_module_args.update({
            "pair_name": "test_pair",
            "pairs": None,
            "state": "present"
        })
        replication_pair_module_mock.module.params = self.get_module_args
        replication_pair_module_mock.powerflex_conn.replication_pair.get = MagicMock(
            side_effect=MockApiException)
        replication_pair_module_mock.perform_module_operation()
        assert "Failed to get the replication pair" in \
            replication_pair_module_mock.module.fail_json.call_args[1]['msg']

    def test_create_pairs(self, replication_pair_module_mock):
        self.get_module_args.update({
            "rcg_name": "test_rcg",
            "pairs": [{"source_volume_id": "123", "target_volume_id": "345", "source_volume_name": None,
                       "target_volume_name": None, "copy_type": "OnlineCopy", "name": "test_pair"}],
            "state": "present"
        })
        replication_pair_module_mock.module.params = self.get_module_args
        replication_pair_resp = MockReplicationPairApi.get_pair_details()
        replication_pair_module_mock.powerflex_conn.replication_pair.get = MagicMock(
            return_value=replication_pair_resp
        )
        replication_pair_module_mock.perform_module_operation()
        replication_pair_module_mock.powerflex_conn.replication_pair.add.assert_called()

    def test_create_pairs_with_volume_name(self, replication_pair_module_mock):
        self.get_module_args.update({
            "rcg_name": "test_rcg",
            "pairs": [{"source_volume_name": "src_vol", "target_volume_name": "dest_vol", "source_volume_id": None,
                       "target_volume_id": None, "copy_type": "OnlineCopy", "name": "test_pair"}],
            "state": "present"
        })
        replication_pair_module_mock.module.params = self.get_module_args
        replication_pair_module_mock.powerflex_conn.volume.get = MagicMock(
            return_value=MockReplicationPairApi.get_volume_details()
        )
        replication_pair_module_mock.perform_module_operation()
        replication_pair_module_mock.powerflex_conn.replication_pair.add.assert_called()

    def test_create_pairs_exception(self, replication_pair_module_mock):
        self.get_module_args.update({
            "rcg_name": "test_rcg",
            "pairs": [{"source_volume_id": "123", "target_volume_id": "345", "source_volume_name": None,
                       "target_volume_name": None, "copy_type": "OnlineCopy", "name": "test_pair"}],
            "state": "present"
        })
        replication_pair_module_mock.module.params = self.get_module_args
        replication_pair_resp = MockReplicationPairApi.get_pair_details()
        replication_pair_module_mock.powerflex_conn.replication_pair.get = MagicMock(
            return_value=replication_pair_resp
        )
        replication_pair_module_mock.powerflex_conn.replication_pair.add = MagicMock(
            side_effect=MockApiException
        )
        replication_pair_module_mock.perform_module_operation()
        assert "Create replication pairs failed with error" \
            in replication_pair_module_mock.module.fail_json.call_args[1]['msg']

    def test_pause_replication_pair(self, replication_pair_module_mock):
        self.get_module_args.update({"pair_name": "test_pair", "pause": True, "state": "present"})
        replication_pair_module_mock.module.params = self.get_module_args
        replication_pair_module_mock.powerflex_conn.replication_pair.get = MagicMock(
            return_value=MockReplicationPairApi.get_pair_details("Uninitialized")
        )
        replication_pair_module_mock.perform_module_operation()
        replication_pair_module_mock.powerflex_conn.replication_pair.pause.assert_called()

    def test_pause_rcg_throws_exception(self, replication_pair_module_mock):
        self.get_module_args.update({"pair_id": MockReplicationPairApi.PAIR_ID, "pause": True, "state": "present"})
        replication_pair_module_mock.module.params = self.get_module_args
        replication_pair_module_mock.powerflex_conn.replication_pair.get = MagicMock(
            return_value=MockReplicationPairApi.get_pair_details("Uninitialized"))
        replication_pair_module_mock.powerflex_conn.replication_pair.pause = \
            MagicMock(side_effect=MockApiException)
        replication_pair_module_mock.perform_module_operation()
        assert "Pause replication pair " + MockReplicationPairApi.PAIR_ID \
            + MockReplicationPairApi.FAIL_MSG in \
            replication_pair_module_mock.module.fail_json.call_args[1]['msg']

    def test_resume_replication_pair(self, replication_pair_module_mock):
        self.get_module_args.update({"pair_name": "test_pair", "pause": False, "state": "present"})
        replication_pair_module_mock.module.params = self.get_module_args
        replication_pair_module_mock.powerflex_conn.replication_pair.get = MagicMock(
            return_value=MockReplicationPairApi.get_pair_details("Paused")
        )
        replication_pair_module_mock.perform_module_operation()
        replication_pair_module_mock.powerflex_conn.replication_pair.resume.assert_called()

    def test_resume_rcg_throws_exception(self, replication_pair_module_mock):
        self.get_module_args.update({"pair_id": MockReplicationPairApi.PAIR_ID, "pause": False, "state": "present"})
        replication_pair_module_mock.module.params = self.get_module_args
        replication_pair_module_mock.powerflex_conn.replication_pair.get = MagicMock(
            return_value=MockReplicationPairApi.get_pair_details("Paused"))
        replication_pair_module_mock.powerflex_conn.replication_pair.resume = \
            MagicMock(side_effect=MockApiException)
        replication_pair_module_mock.perform_module_operation()
        assert "Resume replication pair " + MockReplicationPairApi.PAIR_ID \
            + MockReplicationPairApi.FAIL_MSG in \
            replication_pair_module_mock.module.fail_json.call_args[1]['msg']

    def test_delete_replication_pair(self, replication_pair_module_mock):
        self.get_module_args.update({"pair_name": "test_pair", "pairs": None, "state": "absent"})
        replication_pair_module_mock.module.params = self.get_module_args
        replication_pair_module_mock.powerflex_conn.replication_pair.get = MagicMock(
            return_value=MockReplicationPairApi.get_pair_details()
        )
        replication_pair_module_mock.perform_module_operation()
        replication_pair_module_mock.powerflex_conn.replication_pair.remove.assert_called()

    def test_delete_replication_pair_throws_exception(self, replication_pair_module_mock):
        self.get_module_args.update({"pair_id": MockReplicationPairApi.PAIR_ID, "pairs": None, "state": "absent"})
        replication_pair_module_mock.module.params = self.get_module_args
        replication_pair_module_mock.powerflex_conn.replication_pair.get = MagicMock(
            return_value=MockReplicationPairApi.get_pair_details())
        replication_pair_module_mock.powerflex_conn.replication_pair.remove = \
            MagicMock(side_effect=MockApiException)
        replication_pair_module_mock.perform_module_operation()
        assert "Delete replication pair " + MockReplicationPairApi.PAIR_ID \
            + MockReplicationPairApi.FAIL_MSG in \
            replication_pair_module_mock.module.fail_json.call_args[1]['msg']

    def test_create_replication_pair_src_validation(self, replication_pair_module_mock):
        self.get_module_args.update({
            "rcg_name": "test_rcg",
            "pairs": [{"source_volume_id": "123", "target_volume_id": "345", "source_volume_name": "abc",
                       "target_volume_name": None, "copy_type": "OnlineCopy", "name": "test_pair"}],
            "state": "present"
        })
        replication_pair_module_mock.module.params = self.get_module_args
        replication_pair_module_mock.powerflex_conn.replication_pair.get = MagicMock(
            return_value=MockReplicationPairApi.get_pair_details())
        replication_pair_module_mock.create_replication_pairs = MagicMock(return_value=None)
        replication_pair_module_mock.perform_module_operation()
        assert "Specify either source_volume_id or source_volume_name" in \
            replication_pair_module_mock.module.fail_json.call_args[1]['msg']

    def test_create_replication_pair_target_validation(self, replication_pair_module_mock):
        self.get_module_args.update({
            "rcg_name": "test_rcg",
            "pairs": [{"source_volume_id": "123", "target_volume_id": "345", "source_volume_name": None,
                       "target_volume_name": "abc", "copy_type": "OnlineCopy", "name": "test_pair"}],
            "state": "present"
        })
        replication_pair_module_mock.module.params = self.get_module_args
        replication_pair_module_mock.powerflex_conn.replication_pair.get = MagicMock(
            return_value=MockReplicationPairApi.get_pair_details())
        replication_pair_module_mock.create_replication_pairs = MagicMock(return_value=None)
        replication_pair_module_mock.perform_module_operation()
        assert "Specify either target_volume_id or target_volume_name" in \
            replication_pair_module_mock.module.fail_json.call_args[1]['msg']

    def test_replication_pair_pause_validation(self, replication_pair_module_mock):
        self.get_module_args.update({
            "rcg_name": "test_rcg",
            "pairs": None, "pause": True,
            "state": "present"
        })
        replication_pair_module_mock.module.params = self.get_module_args
        replication_pair_module_mock.powerflex_conn.replication_pair.get = MagicMock(
            return_value=MockReplicationPairApi.get_pair_details())
        replication_pair_module_mock.perform_pause_or_resume = MagicMock()
        replication_pair_module_mock.perform_module_operation()
        assert "Specify a valid pair_name or pair_id to perform pause or resume" in \
            replication_pair_module_mock.module.fail_json.call_args[1]['msg']

    def test_get_rcg_replication_pairs_throws_exception(self, replication_pair_module_mock):
        self.get_module_args.update({
            "rcg_name": "test_rcg",
            "pairs": [{"source_volume_id": "123", "target_volume_id": "345", "source_volume_name": None,
                       "target_volume_name": None, "copy_type": "OnlineCopy", "name": "test_pair"}],
            "state": "present"
        })
        replication_pair_module_mock.module.params = self.get_module_args
        replication_pair_module_mock.powerflex_conn.replication_pair.get = MagicMock(
            return_value=MockReplicationPairApi.get_pair_details())
        replication_pair_module_mock.powerflex_conn.replication_consistency_group.get_replication_pairs = MagicMock(
            side_effect=MockApiException)
        replication_pair_module_mock.create_replication_pairs = MagicMock(return_value=None)
        replication_pair_module_mock.perform_module_operation()
        assert "Failed to get the replication pairs for replication consistency group" in \
            replication_pair_module_mock.module.fail_json.call_args[1]['msg']
