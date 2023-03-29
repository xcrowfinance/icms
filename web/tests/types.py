import dataclasses
from typing import Literal

from web.permissions import ExporterObjectPermissions, ImporterObjectPermissions


@dataclasses.dataclass
class ImporterContact:
    username: str
    permissions: list[ImporterObjectPermissions]


@dataclasses.dataclass
class ExporterContact:
    username: str
    permissions: list[ExporterObjectPermissions]


@dataclasses.dataclass
class Office:
    address_1: str
    address_2: str
    postcode: str
    # Exporters don't have an EORI
    eori_number: str | None = None


@dataclasses.dataclass
class AgentImporter:
    importer_name: str
    offices: list[Office]
    contacts: list[ImporterContact]
    type: Literal["INDIVIDUAL", "ORGANISATION"] = "ORGANISATION"
    region: Literal[None, "E", "O"] = None


@dataclasses.dataclass
class TestImporter:
    importer_name: str
    eori_number: str
    offices: list[Office]
    contacts: list[ImporterContact]
    agents: list[AgentImporter]
    type: Literal["INDIVIDUAL", "ORGANISATION"] = "ORGANISATION"
    region: Literal[None, "E", "O"] = None


@dataclasses.dataclass
class AgentExporter:
    exporter_name: str
    registered_number: str
    offices: list[Office]
    contacts: list[ExporterContact]


@dataclasses.dataclass
class TestExporter:
    exporter_name: str
    registered_number: str
    offices: list[Office]
    contacts: list[ExporterContact]
    agents: list[AgentExporter]
