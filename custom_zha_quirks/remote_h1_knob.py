import math
from typing import Optional, Union, List, Any

import zigpy.types as t
from zigpy.profiles import zha
from zigpy.zcl import foundation
from zigpy.zcl.clusters.general import Basic, Identify, OnOff, \
    PowerConfiguration, Ota
from zigpy.zdo.types import NodeDescriptor, LogicalType

from zhaquirks.const import (
    ALT_DOUBLE_PRESS,
    ARGS,
    BUTTON,
    COMMAND,
    COMMAND_OFF,
    COMMAND_TOGGLE,
    DEVICE_TYPE,
    DOUBLE_PRESS,
    ENDPOINT_ID,
    ENDPOINTS,
    INPUT_CLUSTERS,
    LONG_PRESS,
    MODELS_INFO,
    OUTPUT_CLUSTERS,
    PROFILE_ID,
    SHORT_PRESS,
    LONG_RELEASE,
    ZHA_SEND_EVENT, ALT_LONG_PRESS, NODE_DESCRIPTOR, ROTATED,
)
from zhaquirks.xiaomi import (
    LUMI,
    BasicCluster,
    XiaomiAqaraE1Cluster,
    XiaomiCustomDevice,
)
from zhaquirks.xiaomi.aqara.opple_remote import (
    COMMAND_1_DOUBLE,
    COMMAND_1_HOLD,
    COMMAND_1_SINGLE,
    MultistateInputCluster, COMMAND_1_RELEASE,
)
from zhaquirks.xiaomi.aqara.remote_h1 import PowerConfigurationClusterH1Remote

START_ROTATION = "start_rotation"
ROTATION = "rotation"
STOP_ROTATION = "stop_rotation"
HOLD_START_ROTATION = "hold_start_rotation"
HOLD_ROTATION = "hold_rotation"
HOLD_STOP_ROTATION = "hold_stop_rotation"

ROTATE_RIGHT = "rotate_right"
ROTATE_LEFT = "rotate_left"
HOLD_ROTATE_LEFT = "hold_rotate_left"
HOLD_ROTATE_RIGHT = "hold_rotate_right"

ARG_DIRECTION = 'rotation_direction'

class KnobAction(t.enum8):
    """Knob action mode enum."""

    off = 0x00
    start_rotation = 0x01
    rotation = 0x02
    stop_rotation = 0x03
    hold_start_rotation = 0x81
    hold_rotation = 0x82
    hold_stop_rotation = 0x83


class AqaraRemoteManuSpecificCluster(XiaomiAqaraE1Cluster):
    """Aqara manufacturer specific settings."""

    ep_attribute = "aqara_cluster"

    # manufacture override code: 4447 (0x115f)
    # to get/set this attribute, you might need to click the button 5 times
    # quickly.
    attributes = XiaomiAqaraE1Cluster.attributes.copy()
    attributes.update(
        {
            # operation_mode:
            # 0 means "command" mode.
            # 1 means "event" mode.
            0x0009: ("operation_mode", t.uint8_t, True),
        }
    )

class KnobManuSpecificCluster(XiaomiAqaraE1Cluster):
    """Aqara manufacturer specific settings."""

    ep_attribute = "aqara_cluster"

    attributes = XiaomiAqaraE1Cluster.attributes.copy()
    attributes.update(
        {
            0x022C: ("rotation_time_delta", t.uint16_t, True),
            0x0231: ("rotation_time", t.uint32_t, True),
            #0x0238: ("unknown_0238", t.uint8_t, True), # always value=12,
            0x0230: ("rotation_angle_delta", t.Single, True),
            0x022E: ("rotation_angle", t.Single, True),
            0x0232: ("rotation_percent_delta", t.Single, True),
            0x0233: ("rotation_percent", t.Single, True),
            0x023A: ("action", KnobAction, True),
        }
    )

    def handle_cluster_general_request(
        self,
        header: foundation.ZCLHeader,
        args: List[Any],
        *,
        dst_addressing: Optional[
            Union[t.Addressing.Group, t.Addressing.IEEE, t.Addressing.NWK]
        ] = None,
    ):
        """Handle the cluster command."""
        self.info(
            "H1 knob general request - handle_cluster_general_request: header: %s - args: [%s]",
            header,
            args,
        )

        super().handle_cluster_general_request(header, args, dst_addressing=dst_addressing)

        if header.command_id != foundation.GeneralCommand.Report_Attributes:
            return

        event_args = {}
        for attr in args.attribute_reports:
            if attr.attrid in self.attributes:
                attr_name = self.attributes[attr.attrid].name
                try:
                    value = self.attributes[attr.attrid].type(attr.value.value)
                except ValueError:
                    self.debug(
                        "Couldn't normalize %s attribute with %s value",
                        attr_name,
                        attr.value.value,
                        exc_info=True,
                    )
                    value = attr.value.value
                event_args[attr_name] = value

        action = event_args.get("action")

        if not action:
            return

        command = action.name

        is_stop_action = action in (
            KnobAction.stop_rotation, KnobAction.hold_stop_rotation
        )

        # delta attributes are outdated (or 0) on stop_rotation, don't send them
        if is_stop_action:
            for attr in list(event_args.keys()):
                if attr.endswith("_delta"):
                    del event_args[attr]
            angle = event_args.get("rotation_angle", 0)
            event_args[ARG_DIRECTION] = math.copysign(1, angle)

        self.listener_event(ZHA_SEND_EVENT, command, event_args)

class AqaraH1KnobWireless(XiaomiCustomDevice):
    """Aqara H1 Knob (Wireless)"""
    signature = {
        # NodeDescriptor(logical_type=<LogicalType.EndDevice: 2>, complex_descriptor_available=0, user_descriptor_available=0, reserved=0, aps_flags=0, frequency_band=<FrequencyBand.Freq2400MHz: 8>, mac_capability_flags=<MACCapabilityFlags.AllocateAddress|MainsPowered: 132>, manufacturer_code=4447, maximum_buffer_size=127, maximum_incoming_transfer_size=100, server_mask=11264, maximum_outgoing_transfer_size=100, descriptor_capability_field=<DescriptorCapability.NONE: 0>, *allocate_address=True, *is_alternate_pan_coordinator=False, *is_coordinator=False, *is_end_device=True, *is_full_function_device=False, *is_mains_powered=True, *is_receiver_on_when_idle=False, *is_router=False, *is_security_capable=False)
        MODELS_INFO: [(LUMI, "lumi.remote.rkba01")],
        ENDPOINTS: {
            # "1": {
            #     "profile_id": 260,
            #     "device_type": "0x0103",
            #     "in_clusters": ["0x0000","0x0001","0x0003"],
            #     "out_clusters": ["0x0003","0x0006","0x0019"]
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.ON_OFF_LIGHT_SWITCH,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    PowerConfiguration.cluster_id,
                    Identify.cluster_id,
                ],
                OUTPUT_CLUSTERS: [
                    Identify.cluster_id,
                    OnOff.cluster_id,
                    Ota.cluster_id,
                ],
            },
        },
    }
    replacement = {
        # use custom NodeDescriptor to remove MainsPowered flag
        NODE_DESCRIPTOR: NodeDescriptor(
            logical_type=LogicalType.EndDevice,
            complex_descriptor_available=0,
            user_descriptor_available=0,
            reserved=0,
            aps_flags=0,
            frequency_band=NodeDescriptor.FrequencyBand.Freq2400MHz,
            mac_capability_flags=NodeDescriptor.MACCapabilityFlags.AllocateAddress, # not MainsPowered,
            manufacturer_code=4447,
            maximum_buffer_size=127,
            maximum_incoming_transfer_size=100,
            server_mask=11264,
            maximum_outgoing_transfer_size=100,
            descriptor_capability_field=NodeDescriptor.DescriptorCapability.NONE,
        ),
        ENDPOINTS: {
            1: {
                INPUT_CLUSTERS: [
                    BasicCluster,
                    Identify.cluster_id,
                    PowerConfigurationClusterH1Remote,
                    MultistateInputCluster,
                    AqaraRemoteManuSpecificCluster,
                ],
                OUTPUT_CLUSTERS: [
                    Identify.cluster_id,
                    OnOff.cluster_id,
                    Ota.cluster_id,
                ],
            },
            71: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.DIMMER_SWITCH,
                INPUT_CLUSTERS: [
                    KnobManuSpecificCluster,
                ],
            },
            72: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.SHADE_CONTROLLER,
                INPUT_CLUSTERS: [
                    KnobManuSpecificCluster,
                ],
            }
        },
    }

    device_automation_triggers = {
        # triggers when operation_mode == event
        (SHORT_PRESS, BUTTON): {COMMAND: COMMAND_1_SINGLE},
        (DOUBLE_PRESS, BUTTON): {COMMAND: COMMAND_1_DOUBLE},
        (LONG_PRESS, BUTTON): {COMMAND: COMMAND_1_HOLD},
        (LONG_RELEASE, BUTTON): {COMMAND: COMMAND_1_RELEASE},
        (ROTATED, BUTTON): {COMMAND: STOP_ROTATION},
        (ROTATE_LEFT, BUTTON): {COMMAND: STOP_ROTATION, ARGS: {ARG_DIRECTION: -1}},
        (ROTATE_RIGHT, BUTTON): {COMMAND: STOP_ROTATION, ARGS: {ARG_DIRECTION: 1}},
        (HOLD_ROTATE_LEFT, BUTTON): {COMMAND: HOLD_STOP_ROTATION, ARGS: {ARG_DIRECTION: -1}},
        (HOLD_ROTATE_RIGHT, BUTTON): {COMMAND: HOLD_STOP_ROTATION, ARGS: {ARG_DIRECTION: 1}},
        # triggers when operation_mode == command
        ## single press does not trigger anything
        (ALT_DOUBLE_PRESS, BUTTON): {COMMAND: COMMAND_TOGGLE, ENDPOINT_ID: 1, ARGS: []},
        (ALT_LONG_PRESS, BUTTON): {COMMAND: COMMAND_OFF, ENDPOINT_ID: 1, ARGS: []},
    }
