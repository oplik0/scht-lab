from typing import TypedDict, Optional, Literal, Union, final

@final
class OutputInstruction(TypedDict):
    type: Literal["OUTPUT"]
    port: str
@final
class TableInstruction(TypedDict):
    type: Literal["TABLE"]
    tableId: int
@final
class GroupInstruction(TypedDict):
    type: Literal["GROUP"]
    groupId: int

@final
class MeterInstruction(TypedDict):
    type: Literal["METER"]
    meterId: int
@final
class QueueInstruction(TypedDict):
    type: Literal["QUEUE"]
    queueId: int
    port: int

@final
class L0ModificationLambdaInstruction(TypedDict("L0ModificationLambdaInstruction", {
    "lambda": int
})):
    type: Literal["L0MODIFICATION"]
    subtype: Literal["LAMBDA"]

@final
class L0ModificationOCHInstruction(TypedDict):
    type: Literal["L0MODIFICATION"]
    subtype: Literal["OCH"]
    gridType: str
    channelSpacing: int
    spacingMultiplier: int
    slotGranularity: int

class OduSignalId(TypedDict):
    tributaryPortNumber: int
    tributarySlotLength: int
    tributarySlotBitmap: str  # replace with actual type

@final
class L1ModificationODUSIGIDInstruction(TypedDict):
    type: Literal["L1MODIFICATION"]
    subtype: Literal["ODU_SIGID"]
    oduSignalId: OduSignalId

@final
class L2ModificationVLANPUSHInstruction(TypedDict):
    type: Literal["L2MODIFICATION"]
    subtype: Literal["VLAN_PUSH"]

@final
class L2ModificationVLANIDInstruction(TypedDict):
    type: Literal["L2MODIFICATION"]
    subtype: Literal["VLAN_ID"]
    vlanId: int

@final
class L2ModificationVLANPCPInstruction(TypedDict):
    type: Literal["L2MODIFICATION"]
    subtype: Literal["VLAN_PCP"]
    vlanPcp: int

@final
class L2ModificationETHSRCInstruction(TypedDict):
    type: Literal["L2MODIFICATION"]
    subtype: Literal["ETH_SRC"]
    mac: str

@final
class L2ModificationETHDSTInstruction(TypedDict):
    type: Literal["L2MODIFICATION"]
    subtype: Literal["ETH_DST"]
    mac: str

@final
class L2ModificationMPLSLABELInstruction(TypedDict):
    type: Literal["L2MODIFICATION"]
    subtype: Literal["MPLS_LABEL"]
    label: int

@final
class L2ModificationMPLSPUSHInstruction(TypedDict):
    type: Literal["L2MODIFICATION"]
    subtype: Literal["MPLS_PUSH"]
    ethernetType: int

@final
class L2ModificationTUNNELIDInstruction(TypedDict):
    type: Literal["L2MODIFICATION"]
    subtype: Literal["TUNNEL_ID"]
    tunnelId: int

@final
class L3ModificationIPV4SRCInstruction(TypedDict):
    type: Literal["L3MODIFICATION"]
    subtype: Literal["IPV4_SRC"]
    ip: str

@final
class L3ModificationIPV4DSTInstruction(TypedDict):
    type: Literal["L3MODIFICATION"]
    subtype: Literal["IPV4_DST"]
    ip: str

@final
class L3ModificationIPV6SRCInstruction(TypedDict):
    type: Literal["L3MODIFICATION"]
    subtype: Literal["IPV6_SRC"]
    ip: str

@final
class L3ModificationIPV6DSTInstruction(TypedDict):
    type: Literal["L3MODIFICATION"]
    subtype: Literal["IPV6_DST"]
    ip: str

@final
class L3ModificationIPV6FLABELInstruction(TypedDict):
    type: Literal["L3MODIFICATION"]
    subtype: Literal["IPV6_FLABEL"]
    flowLabel: int

@final
class L4ModificationTCPSRCInstruction(TypedDict):
    type: Literal["L4MODIFICATION"]
    subtype: Literal["TCP_SRC"]
    tcpPort: int

@final
class L4ModificationUDPSRCInstruction(TypedDict):
    type: Literal["L4MODIFICATION"]
    subtype: Literal["UDP_SRC"]
    udpPort: int

Instruction = Union[
    OutputInstruction, 
    TableInstruction, 
    GroupInstruction, 
    MeterInstruction, 
    QueueInstruction, 
    L0ModificationLambdaInstruction, 
    L0ModificationOCHInstruction, 
    L1ModificationODUSIGIDInstruction, 
    L2ModificationVLANPUSHInstruction, 
    L2ModificationVLANIDInstruction, 
    L2ModificationVLANPCPInstruction, 
    L2ModificationETHSRCInstruction, 
    L2ModificationETHDSTInstruction, 
    L2ModificationMPLSLABELInstruction, 
    L2ModificationMPLSPUSHInstruction, 
    L2ModificationTUNNELIDInstruction, 
    L3ModificationIPV4SRCInstruction, 
    L3ModificationIPV4DSTInstruction, 
    L3ModificationIPV6SRCInstruction, 
    L3ModificationIPV6DSTInstruction, 
    L3ModificationIPV6FLABELInstruction, 
    L4ModificationTCPSRCInstruction, 
    L4ModificationUDPSRCInstruction
]

"""
Criteria
"selector": {
    "criteria": [
      {
        "type": "ETH_TYPE",
        "ethType": "0x88cc"
      },
      {
        "type": "ETH_DST",
        "mac": "00:00:11:00:00:01"
      },
      {
        "type": "ETH_SRC",
        "mac": "00:00:11:00:00:01"
      },
      {
        "type": "IN_PORT",
        "port": "1"
      },
      {
        "type": "IN_PHY_PORT",
        "port": "1"
      },
      {
        "type": "METADATA",
        "metadata": "0x1000"
      },
      {
        "type": "VLAN_VID",
        "vlanId": "1"
      },
      {
        "type": "VLAN_PCP",
        "priority": "1"
      },
      {
        "type": "INNER_VLAN_VID",
        "innerVlanId": "1"
      },
      {
        "type": "INNER_VLAN_PCP",
        "innerPriority": "1"
      },
      {
        "type": "IP_DSCP",
        "ipDscp": 1
      },
      {
        "type": "IP_ECN",
        "ipEcn": 1
      },
      {
        "type": "IP_PROTO",
        "protocol": 1
      },
      {
        "type": "IPV4_SRC",
        "ip": "10.1.1.0/24"
      },
      {
        "type": "IPV4_DST",
        "ip": "10.1.1.0/24"
      },
      {
        "type": "TCP_SRC",
        "tcpPort": 1
      },
      {
        "type": "TCP_DST",
        "tcpPort": 1
      },
      {
        "type": "UDP_SRC",
        "udpPort": 1
      },
      {
        "type": "UDP_DST",
        "udpPort": 1
      },
      {
        "type": "SCTP_SRC",
        "sctpPort": 1
      },
      {
        "type": "SCTP_DST",
        "sctpPort": 1
      },
      {
        "type": "ICMPV4_TYPE",
        "icmpType": "1"
      },
      {
        "type": "ICMPV4_CODE",
        "icmpCode": 1
      },
      {
        "type": "IPV6_SRC",
        "ip": "1111::2222/64"
      },
      {
        "type": "IPV6_DST",
        "ip": "1111::2222/64"
      },
      {
        "type": "IPV6_FLABEL",
        "flowlabel": 1
      },
      {
        "type": "ICMPV6_TYPE",
        "icmpv6Type": 1
      },
      {
        "type": "ICMPV6_CODE",
        "icmpv6Code": 1
      },
      {
        "type": "IPV6_ND_TARGET",
        "targetAddress": "1111::2222"
      },
      {
        "type": "IPV6_ND_SLL",
        "mac": "00:00:11:00:00:01"
      },
      {
        "type": "IPV6_ND_TLL",
        "mac": "00:00:11:00:00:01"
      },
      {
        "type": "MPLS_LABEL",
        "label": 1
      },
      {
        "type": "IPV6_EXTHDR",
        "exthdrFlags": 1
      },
      {
        "type": "OCH_SIGID",
        "lambda": 1
      },
      {
        "type": "GRID_TYPE",
        "gridType": DWDM
      },
      {
        "type": "CHANNEL_SPACING",
        "channelSpacing": 100
      },
      {
        "type": "SPACING_MULIPLIER",
        "spacingMultiplier": 4
      },
      {
        "type": "SLOT_GRANULARITY",
        "slotGranularity": 8
      },
      {
        "type": "OCH_SIGID",
        "ochSignalId": 1
      },
      {
        "type": "TUNNEL_ID",
        "tunnelId": 5
      },
      {
        "type": "OCH_SIGTYPE",
        "ochSignalType": 1
      },
      {
        "type": "ODU_SIGID",
        "oduSignalId": 1
        "tributaryPortNumber": 11
        "tributarySlotBitmap": bitmap
        "type": "ETH_TYPE",
        "tributarySlotLen": 1
      },
      {
        "type": "ODU_SIGTYPE",
        "oduSignalType": 4
      },
    ]
"""

@final
class EthTypeCriteria(TypedDict):
    type: Literal["ETH_TYPE"]
    ethType: str

@final
class EthDstCriteria(TypedDict):
    type: Literal["ETH_DST"]
    mac: str

@final
class EthSrcCriteria(TypedDict):
    type: Literal["ETH_SRC"]
    mac: str

@final
class InPortCriteria(TypedDict):
    type: Literal["IN_PORT"]
    port: str

@final
class InPhyPortCriteria(TypedDict):
    type: Literal["IN_PHY_PORT"]
    port: str

@final
class MetadataCriteria(TypedDict):
    type: Literal["METADATA"]
    metadata: str

@final
class VlanVidCriteria(TypedDict):
    type: Literal["VLAN_VID"]
    vlanId: str

@final
class VlanPcpCriteria(TypedDict):
    type: Literal["VLAN_PCP"]
    priority: str

@final
class InnerVlanVidCriteria(TypedDict):
    type: Literal["INNER_VLAN_VID"]
    innerVlanId: str

@final
class InnerVlanPcpCriteria(TypedDict):
    type: Literal["INNER_VLAN_PCP"]
    innerPriority: str

@final
class IpDscpCriteria(TypedDict):
    type: Literal["IP_DSCP"]
    ipDscp: int

@final
class IpEcnCriteria(TypedDict):
    type: Literal["IP_ECN"]
    ipEcn: int

@final
class IpProtoCriteria(TypedDict):
    type: Literal["IP_PROTO"]
    protocol: int

@final
class Ipv4SrcCriteria(TypedDict):
    type: Literal["IPV4_SRC"]
    ip: str

@final
class Ipv4DstCriteria(TypedDict):
    type: Literal["IPV4_DST"]
    ip: str

@final
class TcpSrcCriteria(TypedDict):
    type: Literal["TCP_SRC"]
    tcpPort: int

@final
class TcpDstCriteria(TypedDict):
    type: Literal["TCP_DST"]
    tcpPort: int

@final
class UdpSrcCriteria(TypedDict):
    type: Literal["UDP_SRC"]
    udpPort: int

@final
class UdpDstCriteria(TypedDict):
    type: Literal["UDP_DST"]
    udpPort: int

@final
class SctpSrcCriteria(TypedDict):
    type: Literal["SCTP_SRC"]
    sctpPort: int

@final
class SctpDstCriteria(TypedDict):
    type: Literal["SCTP_DST"]
    sctpPort: int

@final
class Icmpv4TypeCriteria(TypedDict):
    type: Literal["ICMPV4_TYPE"]
    icmpType: str

@final
class Icmpv4CodeCriteria(TypedDict):
    type: Literal["ICMPV4_CODE"]
    icmpCode: int

@final
class Ipv6SrcCriteria(TypedDict):
    type: Literal["IPV6_SRC"]
    ip: str

@final
class Ipv6DstCriteria(TypedDict):
    type: Literal["IPV6_DST"]
    ip: str

@final
class Ipv6FlabelCriteria(TypedDict):
    type: Literal["IPV6_FLABEL"]
    flowlabel: int

@final
class Icmpv6TypeCriteria(TypedDict):
    type: Literal["ICMPV6_TYPE"]
    icmpv6Type: int

@final
class Icmpv6CodeCriteria(TypedDict):
    type: Literal["ICMPV6_CODE"]
    icmpv6Code: int

@final
class Ipv6NdTargetCriteria(TypedDict):
    type: Literal["IPV6_ND_TARGET"]
    targetAddress: str

@final
class Ipv6NdSllCriteria(TypedDict):
    type: Literal["IPV6_ND_SLL"]
    mac: str

@final
class Ipv6NdTllCriteria(TypedDict):
    type: Literal["IPV6_ND_TLL"]
    mac: str

@final
class MplsLabelCriteria(TypedDict):
    type: Literal["MPLS_LABEL"]
    label: int

@final
class Ipv6ExthdrCriteria(TypedDict):
    type: Literal["IPV6_EXTHDR"]
    exthdrFlags: int

@final
class OchSigIdCriteria(TypedDict("OchSigIdCriteria", {"lambda": Optional[int]})):
    type: Literal["OCH_SIGID"]
    ochSignalId: Optional[int]


@final
class GridTypeCriteria(TypedDict):
    type: Literal["GRID_TYPE"]
    gridType: str

@final
class ChannelSpacingCriteria(TypedDict):
    type: Literal["CHANNEL_SPACING"]
    channelSpacing: int

@final
class SpacingMultiplierCriteria(TypedDict):
    type: Literal["SPACING_MULIPLIER"]
    spacingMultiplier: int

@final
class SlotGranularityCriteria(TypedDict):
    type: Literal["SLOT_GRANULARITY"]
    slotGranularity: int

@final
class TunnelIdCriteria(TypedDict):
    type: Literal["TUNNEL_ID"]
    tunnelId: int

@final
class OchSigTypeCriteria(TypedDict):
    type: Literal["OCH_SIGTYPE"]
    ochSignalType: int

@final
class OduSigIdCriteria(TypedDict):
    type: Literal["ODU_SIGID"]
    oduSignalId: int
    tributaryPortNumber: int
    tributarySlotBitmap: str  # replace with actual type
    tributarySlotLen: int

@final
class OduSigTypeCriteria(TypedDict):
    type: Literal["ODU_SIGTYPE"]
    oduSignalType: int


class Treatment(TypedDict):
    instructions: list[Instruction]


Criteria = Union[
    EthTypeCriteria,
    EthDstCriteria, 
    EthSrcCriteria, 
    InPortCriteria, 
    InPhyPortCriteria, 
    MetadataCriteria, 
    VlanVidCriteria, 
    VlanPcpCriteria, 
    InnerVlanVidCriteria, 
    InnerVlanPcpCriteria, 
    IpDscpCriteria, 
    IpEcnCriteria, 
    IpProtoCriteria, 
    Ipv4SrcCriteria, 
    Ipv4DstCriteria, 
    TcpSrcCriteria, 
    TcpDstCriteria, 
    UdpSrcCriteria, 
    UdpDstCriteria, 
    SctpSrcCriteria, 
    SctpDstCriteria, 
    Icmpv4TypeCriteria, 
    Icmpv4CodeCriteria, 
    Ipv6SrcCriteria, 
    Ipv6DstCriteria, 
    Ipv6FlabelCriteria, 
    Icmpv6TypeCriteria, 
    Icmpv6CodeCriteria, 
    Ipv6NdTargetCriteria, 
    Ipv6NdSllCriteria, 
    Ipv6NdTllCriteria, 
    MplsLabelCriteria, 
    Ipv6ExthdrCriteria, 
    OchSigIdCriteria, 
    GridTypeCriteria, 
    ChannelSpacingCriteria, 
    SpacingMultiplierCriteria, 
    SlotGranularityCriteria, 
    TunnelIdCriteria, 
    OduSigIdCriteria, 
    OduSigTypeCriteria
]

class Selector(TypedDict):
    criteria: list[Criteria]

class Flow(TypedDict):
    deviceId: str
    priority: int
    timeout: int
    isPermanent: bool
    treatment: Treatment
    selector: Selector

